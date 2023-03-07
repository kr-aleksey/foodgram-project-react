from django.contrib.auth import get_user_model
from django.db.models import F, Prefetch, Sum

from .models import Favorite, Purchase, Recipe, RecipeIngredient

User = get_user_model()


def create_recipe(data):
    """
    Создает рецепт, добавляет теги и ингредиенты.
    """
    ingredients = data.pop('ingredients_in_recipe')
    tags = data.pop('tags')
    recipe = Recipe.objects.create(**data)
    set_recipe_tags_and_ingredients(recipe, tags, ingredients)
    return recipe


def update_recipe(recipe, data):
    """
    Обновляет все поля рецепта.
    """
    ingredients = data.pop('ingredients_in_recipe')
    tags = data.pop('tags')
    for attr, value in data.items():
        setattr(recipe, attr, value)
    recipe.save()
    recipe.ingredients.clear()
    set_recipe_tags_and_ingredients(recipe, tags, ingredients)
    return recipe


def set_recipe_tags_and_ingredients(recipe, tags, ingredients):
    """
    Добавляет теги и ингредиенты рецепта.
    """
    recipe.tags.set(tags)
    RecipeIngredient.objects.bulk_create(
        [RecipeIngredient(recipe=recipe, **params)
         for params in ingredients]
    )


def delete_purchase(user, recipe):
    """
    Удаляет рецепт из списка покупок пользователя.
    """
    return Purchase.objects.filter(user=user, recipe=recipe).delete()


def delete_favorite(user, recipe):
    """
    Удаляет рецепт из избранного пользователя.
    """
    return Favorite.objects.filter(user=user, recipe=recipe).delete()


def get_author_with_annotations(author_id, user):
    """
    Возвращает автора с полями is_subscribed и recipes_count.
    """
    return (User
            .objects
            .with_is_subscribed_and_recipes_count(user=user)
            .get(pk=author_id))


def get_recipes_with_annotations(user):
    """
    Возвращает рецепты с полями is_favorited и is_in_shopping_cart.
    """
    authors = User.objects.with_is_subscribed(user=user)
    return (Recipe
            .objects
            .with_is_favorited_and_is_in_shopping_cart(user=user)
            .prefetch_related(Prefetch('author', queryset=authors),
                              'ingredients_in_recipe__ingredient',
                              'tags'))


def get_author_recipes(author, recipes_limit):
    """
    Возвращает рецепты автора с ограничением количества объектов.
    """
    recipes = author.recipes.all()
    try:
        recipes_limit = int(recipes_limit)
        return recipes[:recipes_limit]
    except (ValueError, TypeError):
        return recipes


def get_subscribed_authors(user):
    """
    Возвращает queryset с авторами, на которых подписан пользователь.
    """
    return (User
            .objects
            .with_is_subscribed_and_recipes_count(user=user)
            .filter(is_subscribed=True)
            .prefetch_related('recipes'))


def get_shoppinglist(user: User):
    """
    Возвращает список покупок в текстовом виде.
    """
    recipes = Purchase.objects.filter(user=user).values('recipe')
    ingredients = (RecipeIngredient
                   .objects
                   .filter(recipe__in=recipes)
                   .values('ingredient_id')
                   .annotate(name=F('ingredient__name'),
                             measurement_unit=F(
                                 'ingredient__measurement_unit'),
                             amount=Sum('amount')))

    shopping_list = ''
    ingredient_line = '{ingredient} ({measurement_unit}) - {amount}\n'
    for ingredient in ingredients:
        shopping_list += ingredient_line.format(
            ingredient=ingredient.get('name'),
            measurement_unit=ingredient.get('measurement_unit'),
            amount=ingredient.get('amount')
        )
    return shopping_list
