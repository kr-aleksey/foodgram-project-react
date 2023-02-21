from .models import Recipe, RecipeIngredient


def create_recipe(data):
    ingredients = data.pop('ingredient_set')
    tags = data.pop('tags')
    recipe = Recipe.objects.create(**data)
    recipe.tags.set(tags)
    RecipeIngredient.objects.bulk_create(
        [RecipeIngredient(recipe=recipe, **params)
         for params in ingredients]
    )
    return recipe
