from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Exists, OuterRef


class UserManager(models.Manager):

    def annotated(self, user):
        if not user.is_authenticated:
            user = None
        user_subscribes = Subscribe.objects.filter(user=user,
                                                   author=OuterRef('pk'))
        return self.annotate(is_subscribed=Exists(user_subscribes))


class User(AbstractUser):
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    email = models.EmailField('Email',
                              unique=True)
    first_name = models.CharField('Имя',
                                  max_length=150)
    last_name = models.CharField('Фамилия',
                                 max_length=150)

    objects = UserManager()


class Subscribe(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='subscribes',
                             verbose_name='Подписчик')
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='subscribers',
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
