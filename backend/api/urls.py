from django.urls import include, path
from rest_framework import routers

from .views import (FavoriteView, IngredientViewSet, RecipeViewSet,
                    PurchaseView, SubscribeView, TagViewSet, ShoppingCartView)

router = routers.DefaultRouter()

router.register('ingredients', IngredientViewSet)
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('tags', TagViewSet)

urlpatterns = [
    path('recipes/<int:recipe_id>/favorite/', FavoriteView.as_view()),
    path('recipes/<int:recipe_id>/shoping_cart/', PurchaseView.as_view()),
    path('recipes/download_shoping_cart/', ShoppingCartView.as_view()),
    path('users/<int:author_id>/subscribe/', SubscribeView.as_view()),
    path('', include(router.urls)),
]
