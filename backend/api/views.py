from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status, views, viewsets
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from recipes import services
from recipes.models import Favorite, Ingredient, Recipe, Tag
from .filters import IngredientFilter, RecipeFilter
from .permissions import IsAuthorOrReadOnly
from .serializers import (FavoriteSerializer, IngredientSerializer, PurchaseSerializer, RecipeSerializer,
                          ShortRecipeSerializer, SubscribeSerializer, SubscriptionSerializer, TagSerializer)

User = get_user_model()


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [AllowAny]
    pagination_class = None
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientFilter


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny]
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    http_method_names = ['get', 'post', 'patch', 'delete']
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        return serializer.save(author=self.request.user)

    def get_queryset(self):
        return (Recipe
                .objects
                .annotated(user=self.request.user)
                .prefetch_related('ingredients_in_recipe__ingredient',
                                  'tags',
                                  'author'))


class FavoriteView(views.APIView):
    permission_classes = [IsAuthenticated]

    @staticmethod
    def delete(request, recipe_id):
        try:
            favorite = Favorite.objects.get(user=request.user,
                                            recipe=recipe_id)
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ObjectDoesNotExist:
            return Response('Рецепт не найден в избранном',
                            status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def post(request, recipe_id):
        serializer = FavoriteSerializer(
            data={'user': request.user.pk, 'recipe': recipe_id}
        )
        if serializer.is_valid():
            favorite = serializer.save()
            return Response(ShortRecipeSerializer(favorite.recipe).data,
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)


class SubscribeView(views.APIView):
    permission_classes = [IsAuthenticated]

    @staticmethod
    def delete(request, author_id):
        try:
            services.delete_subscription(user=request.user, author=author_id)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ObjectDoesNotExist:
            return Response('Подписка не найдена',
                            status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def post(request, author_id):
        serializer = SubscribeSerializer(
            data={'user': request.user.pk,
                  'author': author_id}
        )
        if serializer.is_valid():
            author = serializer.save().author
            author.is_subscribed = True
            return Response(SubscriptionSerializer(author).data,
                            status.HTTP_201_CREATED)
        return Response(serializer.errors,
                        status.HTTP_400_BAD_REQUEST)


class SubscriptionsView(mixins.ListModelMixin,
                        viewsets.GenericViewSet):
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (User
                .objects
                .annotated(user=self.request.user)
                .filter(is_subscribed=True)
                .prefetch_related('recipes'))


class PurchaseView(views.APIView):
    permission_classes = [IsAuthenticated]

    @staticmethod
    def delete(request, recipe_id):
        try:
            services.delete_purchase(user=request.user,
                                     recipe=recipe_id)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ObjectDoesNotExist:
            return Response('Покупка не найдена в корзине.',
                            status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def post(request, recipe_id):
        serializer = PurchaseSerializer(
            data={'user': request.user.pk,
                  'recipe': recipe_id}
        )
        if serializer.is_valid():
            purchase = serializer.save()
            return Response(ShortRecipeSerializer(purchase.recipe).data,
                            status.HTTP_201_CREATED)
        return Response(serializer.errors,
                        status.HTTP_400_BAD_REQUEST)


class ShoppingCartView(views.APIView):
    permission_classes = [IsAuthenticated]

    @staticmethod
    def get(request):
        shoppinglist = services.get_shoppinglist(request.user)
        return HttpResponse(
            shoppinglist,
            headers={
                'Content-Type': 'text/plain',
                'Content-Disposition':
                    f'attachment; '
                    f'filename={settings.SHOPPINGLIST_FILENAME}'
            }
        )
