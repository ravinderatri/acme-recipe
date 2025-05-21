from rest_framework import serializers
from .models import Ingredient, Recipe

class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'quantity']

class RecipeSerializer(serializers.ModelSerializer):
    ingredient_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Ingredient.objects.all(), source='ingredients'
    )

    class Meta:
        model = Recipe
        fields = ['id', 'name', 'ingredient_ids']
