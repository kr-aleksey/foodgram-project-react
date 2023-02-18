from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    email = models.EmailField('Email',
                              unique=True)
    first_name = models.CharField('Имя',
                                  max_length=150)
    last_name = models.CharField('Фамилия',
                                 max_length=150)


class Follow(models.Model):
    follower = models.ForeignKey(User,
                                 on_delete=models.CASCADE,
                                 related_name='follower',
                                 verbose_name='Подписчик')
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='following',
                               verbose_name='Автор')

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['follower', 'author'],
                name='unique_follow'
            ),
        ]
