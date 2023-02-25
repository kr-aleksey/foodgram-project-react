from django.urls import include, path
from rest_framework import routers

from .views import (FavoriteView, IngredientViewSet, RecipeViewSet,
                    SubscribeView, TagViewSet)

router = routers.DefaultRouter()

router.register('ingredients', IngredientViewSet)
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('tags', TagViewSet)

urlpatterns = [
    path('recipes/<int:recipe_id>/favorite/', FavoriteView.as_view()),
    path('users/<int:author_id>/subscribe/', SubscribeView.as_view()),
    path('', include(router.urls)),
]
