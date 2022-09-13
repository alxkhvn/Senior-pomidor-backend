from django.test import TestCase

from django.contrib.auth.models import User
from django.db.models import Count, Case, When, Avg

from store.models import Book, UserBookRelation
from store.serializers import BookSerializer, BookReaderSerializer


class BookSerializerTestCase(TestCase):
    def test_ok(self):
        user1 = User.objects.create(username='user1', first_name='userbek', last_name='userbekov')
        user2 = User.objects.create(username='user2', first_name='userzhan', last_name='userzhanov')
        user3 = User.objects.create(username='user3', first_name='userhan', last_name='userhanov')

        book_1 = Book.objects.create(name='Test book 1', price=25,
                                     author_name='Test author', owner=user1)
        book_2 = Book.objects.create(name='Test book 2', price=55,
                                     author_name='Test author')

        UserBookRelation.objects.create(user=user1, book=book_1, like=True, rate=5)
        UserBookRelation.objects.create(user=user2, book=book_1, like=True, rate=4)
        user_book_3 = UserBookRelation.objects.create(user=user3, book=book_1, like=True)
        user_book_3.rate = 4
        user_book_3.save()

        UserBookRelation.objects.create(user=user1, book=book_2, like=True, rate=3)
        UserBookRelation.objects.create(user=user2, book=book_2, like=True, rate=4)
        UserBookRelation.objects.create(user=user3, book=book_2, like=False)

        books = Book.objects.all().annotate(
            annotated_likes=Count(Case(When(userbookrelation__like=True, then=1)))
        ).order_by('id')
        data = BookSerializer(books, many=True).data

        expected_data = [
            {
                'id': book_1.id,
                'name': 'Test book 1',
                'price': '25.00',
                'author_name': 'Test author',
                'annotated_likes': 3,
                'rating': '4.33',
                'owner_name': 'user1',
                'readers': [
                    {
                        'id': user1.id,
                        'username': 'user1',
                        'first_name': 'userbek',
                        'last_name': 'userbekov'
                    },
                    {
                        'id': user2.id,
                        'username': 'user2',
                        'first_name': 'userzhan',
                        'last_name': 'userzhanov'
                    },
                    {
                        'id': user3.id,
                        'username': 'user3',
                        'first_name': 'userhan',
                        'last_name': 'userhanov'
                    }
                ]
            },
            {
                'id': book_2.id,
                'name': 'Test book 2',
                'price': '55.00',
                'author_name': 'Test author',
                'annotated_likes': 2,
                'rating': '3.50',
                'owner_name': '',
                'readers': [
                    {
                        'id': user1.id,
                        'username': 'user1',
                        'first_name': 'userbek',
                        'last_name': 'userbekov'
                    },
                    {
                        'id': user2.id,
                        'username': 'user2',
                        'first_name': 'userzhan',
                        'last_name': 'userzhanov'
                    },
                    {
                        'id': user3.id,
                        'username': 'user3',
                        'first_name': 'userhan',
                        'last_name': 'userhanov'
                    }
                ]
            }
        ]

        self.assertEqual(expected_data, data)
