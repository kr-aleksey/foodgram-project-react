from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Exists, OuterRef

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField('Название',
                            max_length=200,
                            unique=True)
    measurement_unit = models.CharField('Единица измерения',
                                        max_length=50)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.measurement_unit})'


class Tag(models.Model):
    name = models.CharField('Название',
                            max_length=50,
                            unique=True)
    color = models.CharField('Цветовой HEX-код',
                             max_length=7,
                             unique=True)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ['name']

    def __str__(self):
        return self.name


class RecipeManager(models.Manager):
    def with_is_favorited_and_is_in_shopping_cart(self, user):
        if not user.is_authenticated:
            user = None
        user_favorites = Favorite.objects.filter(user=user,
                                                 recipe=OuterRef('pk'))
        user_purchases = Purchase.objects.filter(user=user,
                                                 recipe=OuterRef('pk'))
        return self.annotate(is_favorited=Exists(user_favorites),
                             is_in_shopping_cart=Exists(user_purchases))


class Recipe(models.Model):
    name = models.CharField('Название',
                            max_length=200)
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='recipes',
                               db_index=True,
                               verbose_name='Автор')
    image = models.ImageField('Картинка',
                              upload_to='recipes/')
    tags = models.ManyToManyField(Tag,
                                  db_index=True,
                                  verbose_name='Теги')
    text = models.TextField('Описание')
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления, мин.',
        validators=[MinValueValidator(1)]
    )
    ingredients = models.ManyToManyField(Ingredient,
                                         through='RecipeIngredient',
                                         verbose_name='Ингридиенты')
    published_at = models.DateTimeField('Опубликован',
                                        auto_now_add=True)

    objects = RecipeManager()

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-published_at']

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               related_name='ingredients_in_recipe',
                               db_index=True,
                               verbose_name='Рецепт')
    ingredient = models.ForeignKey(Ingredient,
                                   on_delete=models.PROTECT,
                                   verbose_name='Ингридиент')
    amount = models.PositiveSmallIntegerField(
        'Количество',
        validators=[MinValueValidator(1)]
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.ingredient.name


class Favorite(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='favorites',
                             db_index=True,
                             verbose_name='Пользователь')
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               db_index=True,
                               verbose_name='Рецепт')

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite'
            )
        ]

    def __str__(self):
        return f'{self.user.username} - {self.recipe.name}'


class Purchase(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             db_index=True,
                             verbose_name='Пользователь')
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               verbose_name='Рецепт')

    class Meta:
        verbose_name = 'Покупка'
        verbose_name_plural = 'Корзина покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_purchase'
            )
        ]

    def __str__(self):
        return f'{self.user.username} - {self.recipe.name}'
