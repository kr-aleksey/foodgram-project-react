from rest_framework import serializers

from recipes.models import Ingredient, Tag, Recipe


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'measurement_unit']
        read_only_fields = ['id']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        models = Tag
        fields = ['id', 'name', 'color', 'slug']
        read_only_fields = ['id']
