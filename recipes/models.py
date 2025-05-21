from django.db import models

class Ingredient(models.Model):
    name = models.CharField(max_length=100, unique=True)
    quantity = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.name

class Recipe(models.Model):
    name = models.CharField(max_length=200)
    ingredients = models.ManyToManyField(Ingredient, related_name='recipes')

    def __str__(self):
        return self.name
