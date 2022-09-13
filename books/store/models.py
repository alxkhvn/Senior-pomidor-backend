from django.contrib.auth.models import User
from django.db import models


# При редактировании файла models.py необходимо будет создать новую миграцию с помощью команды makemigrations

class Book(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    author_name = models.CharField(max_length=255)
    # благодаря related_name можно обратится User.my_books.all() и получить информацию о тех книгах которые он создал
    owner = models.ForeignKey(User, on_delete=models.SET_NULL,
                              null=True, related_name='my_books')
    readers = models.ManyToManyField(User, through='UserBookRelation',
                                     related_name='books')  # загуглить подробно through
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=None, null=True)

    def __str__(self):
        return f'Id {self.id}: {self.name}'


class UserBookRelation(models.Model):
    def __init__(self, *args, **kwargs):
        super(UserBookRelation, self).__init__(*args, **kwargs)
        self.old_rate = self.rate

    RATE_CHOICES = (
        (1, 'Ok'),
        (2, 'Fine'),
        (3, 'Good'),
        (4, 'Amazing'),
        (5, 'Incredible')
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    like = models.BooleanField(default=False)
    in_bookmarks = models.BooleanField(default=False)
    rate = models.PositiveSmallIntegerField(choices=RATE_CHOICES, null=True)

    def __str__(self):
        return f'{self.user.username}: {self.book.name}, RATE {self.rate}'

    def save(self, *args, **kwargs):
        """Функция save вызывается при создании и обновлении данной модели"""
        # мы пишем super чтобы не перезаписовать метод save у родительского элемента

        creating = not self.pk

        super().save(*args, **kwargs)

        new_rating = self.rate
        if self.old_rate != new_rating or creating:
            from store.logic import set_rating
            set_rating(self.book)

