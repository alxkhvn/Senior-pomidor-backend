from django.db.models import Count, Case, When, Avg
from django.db.models.functions import Coalesce
from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.mixins import UpdateModelMixin
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from store.models import Book, UserBookRelation
from store.permissions import IsOwnerOrStaffOrReadOnly
from store.serializers import BookSerializer, UserBookRelationSerializer


class BookViewSet(ModelViewSet):
    queryset = Book.objects.all().annotate(
        annotated_likes=Count(Case(When(userbookrelation__like=True, then=1)))
    ).select_related('owner').prefetch_related('readers').order_by('id')
    # select_related оптимизирует sql запрос в базу создавая join между таблицами book и user(owner это ForeignKey
    # от таблицы user). Без этого мы бы делали отдельные запросы по каждому owner-у.
    # Prefetch_related делает тоже самое только для связи ManyToMany
    serializer_class = BookSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    permission_classes = [IsOwnerOrStaffOrReadOnly]
    filter_fields = ['price']  # со стороны клиента запрос выглядит как url/book/?price=1000
    search_fields = ['name', 'author_name']  # поиск имеет смысл когда мы ищем по 2+ полям (url/book/?search=Alikhan)
    ordering_fields = ['price', 'author_name']  # обычная сортировка, (запрос - url/book/?ordering=author_name)

    def perform_create(self, serializer):
        # данный метод мы скопировали из родительского класса и дополнили функционалом
        # который добавляет текущего юзера как оунера объекта
        serializer.validated_data['owner'] = self.request.user
        serializer.save()


class UserBooksRelationView(UpdateModelMixin, GenericViewSet):
    permission_classes = [IsAuthenticated]
    queryset = UserBookRelation.objects.all()
    serializer_class = UserBookRelationSerializer
    lookup_field = 'book'

    def get_object(self):
        # get_or_create is django builtin method
        obj, created = UserBookRelation.objects.get_or_create(user=self.request.user,
                                                              book_id=self.kwargs['book'])
        print(created)
        return obj


def auth(request):
    return render(request, 'oauth.html')
