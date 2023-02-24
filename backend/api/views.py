from django_filters.rest_framework import DjangoFilterBackend
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status, views, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from recipes.models import Favorite, Ingredient, Recipe, Tag
from .filters import IngredientFilter
from .permissions import IsAuthorOrReadOnly
from .serializers import (FavoriteSerializer, IngredientSerializer, RecipeSerializer, ShortRecipeSerializer,
                          TagSerializer)


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
    queryset = (Recipe
                .objects
                .select_related('author')
                .prefetch_related('tags'))
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    http_method_names = ['get', 'post', 'patch', 'delete']

    def perform_create(self, serializer):
        return serializer.save(author=self.request.user)


class FavoriteViewSet(views.APIView):
    permission_classes = [IsAuthenticated]

    @staticmethod
    def delete(request, recipe_id):
        try:
            favorite = Favorite.objects.get(user=request.user,
                                            recipe=recipe_id)
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ObjectDoesNotExist:
            return Response(f'Рецепт не найден в избранном',
                            status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def post(request, recipe_id):
        serializer = FavoriteSerializer(
            data={'user': request.user.pk,
                  'recipe': recipe_id}
        )
        if serializer.is_valid():
            favorite = serializer.save()
            return Response(ShortRecipeSerializer(favorite.recipe).data,
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)
