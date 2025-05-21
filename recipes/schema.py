import graphene
from graphene_django import DjangoObjectType
import graphql_jwt
from graphql_jwt.decorators import login_required
from django_filters import FilterSet, CharFilter
from graphene_django.filter import DjangoFilterConnectionField
from graphql_relay import from_global_id
from .models import Ingredient, Recipe
from .serializers import IngredientSerializer, RecipeSerializer



# Nodes
class IngredientNode(DjangoObjectType):
    class Meta:
        model = Ingredient
        filter_fields = {'name': ['exact', 'icontains', 'istartswith']}
        interfaces = (graphene.relay.Node,)

class RecipeNode(DjangoObjectType):
    ingredient_count = graphene.Int()

    class Meta:
        model = Recipe
        interfaces = (graphene.relay.Node,)

    def resolve_ingredient_count(self, info):
        return self.ingredients.count()

# Filters
class IngredientFilter(FilterSet):
    name = CharFilter(field_name='name', lookup_expr='icontains')
    class Meta:
        model = Ingredient
        fields = ['name']

class RecipeFilter(FilterSet):
    name = CharFilter(field_name='name', lookup_expr='icontains')
    class Meta:
        model = Recipe
        fields = ['name']

# Ingredient mutations
class IngredientCreate(graphene.Mutation):
    ingredient = graphene.Field(IngredientNode)
    ok = graphene.Boolean()

    class Arguments:
        name = graphene.String(required=True)
        quantity = graphene.String()

    @login_required
    def mutate(self, info, name, quantity=None):
        serializer = IngredientSerializer(data={'name': name, 'quantity': quantity})
        if serializer.is_valid():
            ingredient = serializer.save()
            return IngredientCreate(ingredient=ingredient, ok=True)
        return IngredientCreate(ingredient=None, ok=False)

class IngredientUpdate(graphene.Mutation):
    ingredient = graphene.Field(IngredientNode)
    ok = graphene.Boolean()

    class Arguments:
        id = graphene.ID(required=True)
        name = graphene.String()
        quantity = graphene.String()

    @login_required
    def mutate(self, info, id, name=None, quantity=None):
        try:
            pk = from_global_id(id)[1]
            ingredient = Ingredient.objects.get(pk=pk)
        except Ingredient.DoesNotExist:
            return IngredientUpdate(ingredient=None, ok=False)

        data = {}
        if name is not None:
            data['name'] = name
        if quantity is not None:
            data['quantity'] = quantity

        serializer = IngredientSerializer(ingredient, data=data, partial=True)
        if serializer.is_valid():
            ingredient = serializer.save()
            return IngredientUpdate(ingredient=ingredient, ok=True)
        return IngredientUpdate(ingredient=None, ok=False)

class IngredientDelete(graphene.Mutation):
    ok = graphene.Boolean()
    class Arguments:
        id = graphene.ID(required=True)

    @login_required
    def mutate(self, info, id):
        try:
            pk = from_global_id(id)[1]
            ingredient = Ingredient.objects.get(pk=pk)
            ingredient.delete()
            return IngredientDelete(ok=True)
        except Ingredient.DoesNotExist:
            return IngredientDelete(ok=False)

# Recipe mutations
class RecipeCreate(graphene.Mutation):
    recipe = graphene.Field(RecipeNode)
    ok = graphene.Boolean()

    class Arguments:
        name = graphene.String(required=True)
        ingredient_ids = graphene.List(graphene.ID, required=True)

    @login_required
    def mutate(self, info, name, ingredient_ids):
        pks = [from_global_id(i)[1] for i in ingredient_ids]
        ingredients = Ingredient.objects.filter(pk__in=pks)
        if len(ingredients) != len(ingredient_ids):
            raise Exception("Some ingredients not found")
        recipe = Recipe.objects.create(name=name)
        recipe.ingredients.set(ingredients)
        recipe.save()
        return RecipeCreate(recipe=recipe, ok=True)

class AddIngredientToRecipe(graphene.Mutation):
    recipe = graphene.Field(RecipeNode)
    ok = graphene.Boolean()

    class Arguments:
        recipe_id = graphene.ID(required=True)
        ingredient_id = graphene.ID(required=True)

    @login_required
    def mutate(self, info, recipe_id, ingredient_id):
        try:
            recipe = Recipe.objects.get(pk=from_global_id(recipe_id)[1])
            ingredient = Ingredient.objects.get(pk=from_global_id(ingredient_id)[1])
            recipe.ingredients.add(ingredient)
            return AddIngredientToRecipe(recipe=recipe, ok=True)
        except:
            return AddIngredientToRecipe(recipe=None, ok=False)

class RemoveIngredientFromRecipe(graphene.Mutation):
    recipe = graphene.Field(RecipeNode)
    ok = graphene.Boolean()

    class Arguments:
        recipe_id = graphene.ID(required=True)
        ingredient_id = graphene.ID(required=True)

    @login_required
    def mutate(self, info, recipe_id, ingredient_id):
        try:
            recipe = Recipe.objects.get(pk=from_global_id(recipe_id)[1])
            ingredient = Ingredient.objects.get(pk=from_global_id(ingredient_id)[1])
            recipe.ingredients.remove(ingredient)
            return RemoveIngredientFromRecipe(recipe=recipe, ok=True)
        except:
            return RemoveIngredientFromRecipe(recipe=None, ok=False)

# Query and Mutation classes
class Query(graphene.ObjectType):
    ingredient = graphene.relay.Node.Field(IngredientNode)
    all_ingredients = DjangoFilterConnectionField(IngredientNode, filterset_class=IngredientFilter)

    recipe = graphene.relay.Node.Field(RecipeNode)
    all_recipes = DjangoFilterConnectionField(RecipeNode, filterset_class=RecipeFilter)

class Mutation(graphene.ObjectType):
    create_ingredient = IngredientCreate.Field()
    update_ingredient = IngredientUpdate.Field()
    delete_ingredient = IngredientDelete.Field()
    create_recipe = RecipeCreate.Field()
    add_ingredient_to_recipe = AddIngredientToRecipe.Field()
    remove_ingredient_from_recipe = RemoveIngredientFromRecipe.Field()
 
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)




class AuthMutations(graphene.ObjectType):
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()

 