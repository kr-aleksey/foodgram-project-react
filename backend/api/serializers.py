import base64

from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.base import ContentFile
from rest_framework import serializers

from recipes import services
from recipes.models import (Favorite, Ingredient, Purchase, Recipe,
                            RecipeIngredient, Tag)
from users.models import Subscription
from users.serializers import UserSerializer

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            img_format, img_str = data.split(';base64,')
            ext = img_format.split('/')[-1]
            data = ContentFile(base64.b64decode(img_str), name='img.' + ext)
        return super().to_internal_value(data)


class IngredientSerializer(serializers.ModelSerializer):
    """
    Сериализатор ингредиентов.
    """
    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'measurement_unit']
        read_only_fields = ['id']


class TagSerializer(serializers.ModelSerializer):
    """
    Сериализатор тегов.
    """
    class Meta:
        model = Tag
        fields = ['id', 'name', 'color', 'slug']
        read_only_fields = fields


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """
    Сериализатор ингредиентов рецепта.
    """
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        queryset=Ingredient.objects.all()
    )
    name = serializers.SlugRelatedField(
        source='ingredient',
        slug_field='name',
        read_only=True
    )
    measurement_unit = serializers.SlugRelatedField(
        source='ingredient',
        read_only=True,
        slug_field='measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'name', 'measurement_unit', 'amount']


class TagField(serializers.RelatedField):

    def to_representation(self, value):
        return {
            'id': value.id,
            'name': value.name,
            'color': value.color,
            'slug': value.slug,
        }

    def to_internal_value(self, data):
        try:
            return self.queryset.get(pk=int(data))
        except (ObjectDoesNotExist, ValueError):
            raise serializers.ValidationError(
                f'Недопустимый первичный ключ "{data}" - тег не найден.'
            )


class RecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор рецептов.
    """
    tags = TagField(many=True, queryset=Tag.objects.all())
    ingredients = RecipeIngredientSerializer(many=True,
                                             source='ingredients_in_recipe')
    image = Base64ImageField()
    author = UserSerializer(read_only=True)
    is_favorited = serializers.BooleanField(read_only=True, default=False)
    is_in_shopping_cart = serializers.BooleanField(read_only=True,
                                                   default=False)

    class Meta:
        model = Recipe
        fields = ['id',
                  'tags',
                  'author',
                  'ingredients',
                  'is_favorited',
                  'is_in_shopping_cart',
                  'name',
                  'image',
                  'text',
                  'cooking_time']
        read_only_fields = ['id',
                            'author',
                            'is_favorited',
                            'is_in_shopping_cart']

    def create(self, validated_data):
        return services.create_recipe(validated_data)

    def update(self, instance, validated_data):
        return services.update_recipe(instance, validated_data)


class ShortRecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор рецептов для сокращенного представления.
    """
    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time']


class FavoriteSerializer(serializers.ModelSerializer):
    """
    Сериализатор избранных рецептов.
    """
    class Meta:
        model = Favorite
        fields = ['user', 'recipe']
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=['user', 'recipe'],
                message='Это рецепт уже есть в избранном.'
            )
        ]


class SubscribeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания подписки на автора.
    """
    class Meta:
        model = Subscription
        fields = ['user', 'author']
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=['user', 'author'],
                message='Эта подписка уже существует.'
            )
        ]

    def validate(self, attrs):
        if attrs.get('author') == attrs.get('user'):
            raise serializers.ValidationError(
                'Подписка на самого себя запрещена!')
        return attrs


class SubscriptionSerializer(serializers.ModelSerializer):
    """
    Сериализатор для чтения подписок.
    """
    is_subscribed = serializers.BooleanField(default=False)
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = User
        fields = [
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        ]
        read_only_fields = ['id', 'is_subscribed']

    def get_recipes(self, author):
        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit')
        recipes = services.get_author_recipes(author=author,
                                              recipes_limit=recipes_limit)
        return ShortRecipeSerializer(recipes, many=True).data


class PurchaseSerializer(serializers.ModelSerializer):
    """
    Сериализатор для добавления рецепта в корзину покупок.
    """
    class Meta:
        model = Purchase
        fields = ['user', 'recipe']
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Purchase.objects.all(),
                fields=['user', 'recipe'],
                message='Это рецепт уже есть в корзине покупок.'
            )
        ]
