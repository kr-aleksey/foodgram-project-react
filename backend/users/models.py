from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.db.models import Count, Exists, OuterRef


class CustomUserManager(UserManager):

    def with_is_subscribed(self, user):
        if not user.is_authenticated:
            user = None
        user_subscriptions = (Subscription
                              .objects
                              .filter(user=user,
                                      author=OuterRef('pk')))
        return self.annotate(is_subscribed=Exists(user_subscriptions))

    def with_is_subscribed_and_recipes_count(self, user):
        return (self
                .with_is_subscribed(user=user)
                .annotate(recipes_count=Count('recipes')))


class User(AbstractUser):
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    email = models.EmailField('Email',
                              unique=True)
    first_name = models.CharField('Имя',
                                  max_length=150)
    last_name = models.CharField('Фамилия',
                                 max_length=150)

    objects = CustomUserManager()

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['username']


class Subscription(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='subscriptions',
                             db_index=True,
                             verbose_name='Подписчик')
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='subscribers',
                               db_index=True,
                               verbose_name='Автор')

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_subscribe'
            ),
        ]

    def __str__(self):
        return f'{self.user.username} - {self.author.username}'
