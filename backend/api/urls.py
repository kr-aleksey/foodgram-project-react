from django.urls import include, path
from rest_framework import routers

from .views import (FavoriteView, IngredientViewSet, PurchaseView,
                    RecipeViewSet, ShoppingCartView, SubscribeView,
                    SubscriptionsViewSet, TagViewSet)

router = routers.DefaultRouter()

router.register('ingredients', IngredientViewSet)
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('tags', TagViewSet)
router.register('users/subscriptions',
                SubscriptionsViewSet,
                basename='subscriptions')

urlpatterns = [
    path('recipes/<int:recipe_id>/favorite/', FavoriteView.as_view()),
    path('recipes/<int:recipe_id>/shopping_cart/', PurchaseView.as_view()),
    path('recipes/download_shopping_cart/', ShoppingCartView.as_view()),
    path('users/<int:author_id>/subscribe/', SubscribeView.as_view()),
    path('', include(router.urls)),
]
