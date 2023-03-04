from django.contrib import admin

from .models import (Favorite, Ingredient, Purchase, Recipe, RecipeIngredient,
                     Tag)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)
    fields = ('name', 'measurement_unit')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'color')
    fields = ('name', 'slug', 'color')


class RecipeIngredientsInline(admin.TabularInline):
    model = RecipeIngredient


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'published_at')
    list_filter = ('tags',)
    search_fields = ('author__username', 'name', 'tags__name')
    date_hierarchy = 'published_at'
    fields = ('published_at',
              'name',
              'author',
              'text',
              'cooking_time',
              'tags',
              'image')
    readonly_fields = ('published_at', )
    inlines = [RecipeIngredientsInline]


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    search_fields = ('user__username', 'user__email')
    fields = ('user', 'recipe')


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    search_fields = ('user__username', 'user__email')
    fields = ('user', 'recipe')
