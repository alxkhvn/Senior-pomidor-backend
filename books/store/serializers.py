from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from store.models import Book, UserBookRelation


class BookReaderSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name')


class BookSerializer(ModelSerializer):
    # когда мы делаем запрос в базу с помощью annotate к КАЖДОМУ объекту(в нашем случае к каждой книге) который мы получаем,добавляется дополнительное
    # описание(в нашем случае коль-во лайков), это поле не будет храниться базе а будет вычислятся на лету
    annotated_likes = serializers.IntegerField(read_only=True)
    rating = serializers.DecimalField(max_digits=3, decimal_places=2, read_only=True)
    #owner_name = serializers.CharField(read_only=True)
    owner_name = serializers.CharField(source='owner.username', default="",
                                       read_only=True)  # default это то что мы будем отображать если у кноги нету owner(т.к. в модели Book у него null=True)
    readers = BookReaderSerializer(many=True, read_only=True)

    class Meta:
        model = Book
        fields = ('id', 'name', 'price', 'author_name', 'annotated_likes', 'rating', 'owner_name', 'readers')


class UserBookRelationSerializer(ModelSerializer):
    class Meta:
        model = UserBookRelation
        fields = ('book', 'like', 'in_bookmarks', 'rate')
