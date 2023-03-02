from typing import Any, Union

from django.contrib.auth.models import User
from django.db.models import F, Sum

from users.models import Subscribe
from .models import Purchase, Recipe, RecipeIngredient


def create_recipe(data: dict[str, Any]) -> Recipe:
    ingredients = data.pop('ingredients_in_recipe')
    tags = data.pop('tags')
    recipe = Recipe.objects.create(**data)
    add_recipe_related_objs(recipe, tags, ingredients)
    return recipe


def update_recipe(recipe: Recipe,
                  data: dict[str, Any]) -> Recipe:
    ingredients = data.pop('ingredients_in_recipe')
    tags = data.pop('tags')
    for attr, value in data.items():
        setattr(recipe, attr, value)
    recipe.save()
    recipe.ingredients.clear()
    add_recipe_related_objs(recipe, tags, ingredients)
    return recipe


def add_recipe_related_objs(recipe: Recipe,
                            tags, ingredients) -> None:
    recipe.tags.set(tags)
    RecipeIngredient.objects.bulk_create(
        [RecipeIngredient(recipe=recipe, **params)
         for params in ingredients]
    )


def delete_purchase(user: Union[int, User],
                    recipe: Union[int, Recipe]) -> None:
    (Purchase
     .objects
     .get(user=user, recipe=recipe)
     .delete())


def delete_subscribe(user: Union[int, User],
                     author: Union[int, User]) -> None:
    (Subscribe
     .objects
     .get(user=user, author=author)
     .delete())


def get_shoppinglist(user: User):
    recipes = Purchase.objects.filter(user=user).values('recipe')
    ingredients = (RecipeIngredient
                   .objects
                   .filter(recipe__in=recipes)
                   .values('ingredient_id')
                   .annotate(name=F('ingredient__name'),
                             measurement_unit=F('ingredient__measurement_unit'),
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
