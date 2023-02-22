import base64

from django.core.exceptions import ObjectDoesNotExist
from django.core.files.base import ContentFile
from rest_framework import serializers

from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from recipes.services import create_recipe, update_recipe
from users.serializers import UserSerializer


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

    class Meta:
        model = Recipe
        fields = ['id',
                  'tags',
                  'author',
                  'ingredients',
                  'name',
                  'image',
                  'text',
                  'cooking_time']
        read_only_fields = ['id', 'author']

    def __init__(self, *args, **kwargs):
        kwargs['partial'] = False
        super().__init__(*args, **kwargs)

    def create(self, validated_data):
        return create_recipe(validated_data)

    def update(self, instance, validated_data):
        return update_recipe(instance, validated_data)
