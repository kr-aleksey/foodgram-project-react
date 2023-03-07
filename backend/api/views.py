from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status, views, viewsets
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from recipes import services as recipe_services
from recipes.models import Ingredient, Tag
from users import services as user_services
from .filters import IngredientFilter, RecipeFilter
from .permissions import IsAuthorOrReadOnly
from .serializers import (FavoriteSerializer, IngredientSerializer,
                          PurchaseSerializer, RecipeSerializer,
                          ShortRecipeSerializer, SubscribeSerializer,
                          SubscriptionSerializer, TagSerializer)

User = get_user_model()


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Ингредиенты.
    """
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [AllowAny]
    pagination_class = None
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientFilter


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Теги.
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny]
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """
    Рецепты.
    """
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    http_method_names = ['get', 'post', 'patch', 'delete']
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        return serializer.save(author=self.request.user)

    def get_queryset(self):
        return recipe_services.get_recipes_with_annotations(self.request.user)


class FavoriteView(views.APIView):
    """
    Добавление и удаление избранных рецептов.
    """
    permission_classes = [IsAuthenticated]

    @staticmethod
    def delete(request, recipe_id):
        result = recipe_services.delete_favorite(request.user, recipe_id)
        if result[0] == 0:
            return Response('Рецепт не найден в избранном',
                            status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @staticmethod
    def post(request, recipe_id):
        serializer = FavoriteSerializer(
            data={'user': request.user.pk, 'recipe': recipe_id}
        )
        serializer.is_valid(raise_exception=True)
        favorite = serializer.save()
        return Response(ShortRecipeSerializer(favorite.recipe).data,
                        status=status.HTTP_201_CREATED)


class SubscribeView(views.APIView):
    """
    Добавление и удаление подписки на автора.
    """
    permission_classes = [IsAuthenticated]

    @staticmethod
    def delete(request, author_id):
        result = user_services.delete_subscription(user=request.user,
                                                   author=author_id)
        if result[0] == 0:
            return Response('Подписка не найдена', status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @staticmethod
    def post(request, author_id):
        serializer = SubscribeSerializer(
            data={'user': request.user.pk, 'author': author_id},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        author = (recipe_services.get_author_with_annotations(
            author_id=author_id, user=request.user))
        serializer = SubscriptionSerializer(author,
                                            context={'request': request})
        return Response(serializer.data, status.HTTP_201_CREATED)


class SubscriptionsViewSet(mixins.ListModelMixin,
                           viewsets.GenericViewSet):
    """
    Список подписок на автора.
    """
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return recipe_services.get_subscribed_authors(self.request.user)


class PurchaseView(views.APIView):
    """
    Добавление и удаление рецептов в списке покупок.
    """
    permission_classes = [IsAuthenticated]

    @staticmethod
    def delete(request, recipe_id):
        result = recipe_services.delete_purchase(user=request.user,
                                                 recipe=recipe_id)
        if result[0] == 0:
            return Response('Покупка не найдена в корзине.',
                            status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @staticmethod
    def post(request, recipe_id):
        serializer = PurchaseSerializer(
            data={'user': request.user.pk,
                  'recipe': recipe_id}
        )
        serializer.is_valid(raise_exception=True)
        purchase = serializer.save()
        return Response(ShortRecipeSerializer(purchase.recipe).data,
                        status.HTTP_201_CREATED)


class ShoppingCartView(views.APIView):
    """
    Скачивание файла со списком покупок.
    """
    permission_classes = [IsAuthenticated]

    @staticmethod
    def get(request):
        shoppinglist = recipe_services.get_shoppinglist(request.user)
        return HttpResponse(
            shoppinglist,
            headers={'Content-Type': 'text/plain'}
        )
