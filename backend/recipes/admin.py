from django.contrib import admin

from .models import Favorite, Ingredient, Recipe, RecipeIngredient, Tag


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'color')


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'author', 'published_at')
    search_fields = ('author__username', 'name', 'tags__name')
    date_hierarchy = 'published_at'
    fields = ('name',
              'author',
              'text',
              'cooking_time',
              'tags',
              'image',
              'published_at')
    readonly_fields = ('published_at', )


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    fields = ('recipe', 'ingredient', 'amount')


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
