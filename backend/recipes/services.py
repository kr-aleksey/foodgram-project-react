from typing import Any

from .models import Recipe, RecipeIngredient


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
