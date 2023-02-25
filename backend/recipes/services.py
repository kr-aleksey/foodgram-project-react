from typing import Any

from django.db.models import Exists, OuterRef

from .models import Favorite, Recipe, RecipeIngredient


def create_recipe(data: dict[str, Any]) -> Recipe:
    ingredients = data.pop('ingredients_in_recipe')
    tags = data.pop('tags')
    recipe = Recipe.objects.create(**data)
    add_recipe_related_objs(recipe, tags, ingredients)
    return recipe


def update_recipe(recipe: Recipe, data: dict[str, Any]) -> Recipe:
    ingredients = data.pop('ingredients_in_recipe')
    tags = data.pop('tags')
    for attr, value in data.items():
        setattr(recipe, attr, value)
    recipe.save()
    recipe.ingredients.clear()
    add_recipe_related_objs(recipe, tags, ingredients)
    return recipe


def add_recipe_related_objs(recipe: Recipe, tags, ingredients):
    recipe.tags.set(tags)
    RecipeIngredient.objects.bulk_create(
        [RecipeIngredient(recipe=recipe, **params)
         for params in ingredients]
    )


def get_annotated_recipes(user):
    user_favorites = Favorite.objects.filter(user=user,
                                             recipe=OuterRef('pk'))
    return Recipe.objects.annotate(is_favorited=Exists(user_favorites))
