import base64

from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.base import ContentFile
from rest_framework import serializers

from recipes.models import Favorite, Ingredient, Purchase, Recipe, RecipeIngredient, Tag
from recipes.services import create_recipe, update_recipe
from users.models import Subscribe
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
    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'measurement_unit']
        read_only_fields = ['id']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'color', 'slug']
        read_only_fields = fields


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(source='ingredient',
                                            queryset=Ingredient.objects.all())
    name = serializers.SlugRelatedField(source='ingredient',
                                        slug_field='name',
                                        read_only=True)
    measurement_unit = serializers.SlugRelatedField(
        source='ingredient', read_only=True, slug_field='measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'name', 'measurement_unit', 'amount']


class TagListingField(serializers.RelatedField):
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
                f'Недопустимый первичный ключ "{data}" '
                f'- объект не существует.'
            )


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagListingField(many=True, queryset=Tag.objects.all())
    ingredients = RecipeIngredientSerializer(many=True,
                                             source='ingredients_in_recipe')
    image = Base64ImageField()
    author = UserSerializer(read_only=True)
    is_favorited = serializers.BooleanField(read_only=True)
    is_in_shopping_cart = serializers.BooleanField(read_only=True)

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

    def __init__(self, *args, **kwargs):
        kwargs['partial'] = False
        super().__init__(*args, **kwargs)

    def create(self, validated_data):
        return create_recipe(validated_data)

    def update(self, instance, validated_data):
        return update_recipe(instance, validated_data)


class ShortRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time']


class FavoriteSerializer(serializers.ModelSerializer):
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


class SubscribeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscribe
        fields = ['user', 'author']
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Subscribe.objects.all(),
                fields=['user', 'author'],
                message='Эта подписка уже существует.'
            )
        ]

    def validate(self, attrs):
        if attrs.get('author') == attrs.get('user'):
            raise serializers.ValidationError(
                'Подписка на самого себя запрещена!')
        return attrs


class SubscribeReadSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.BooleanField()
    recipes = ShortRecipeSerializer(many=True)

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
        ]
        read_only_fields = ['id', 'is_subscribed']


class PurchaseSerializer(serializers.ModelSerializer):
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
