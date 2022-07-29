from django.contrib import admin

from .models import (Allergen, DishType, Ingredient, IngredientGroup, Recipe,
                     RecipeIngredientGroup, User, RecipeIngredientAmount, Step)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    raw_id_fields = ("dish_types", "allergens",)

@admin.register(Allergen)
class AllergenAdmin(admin.ModelAdmin):
    pass

@admin.register(DishType)
class DishTypeAdmin(admin.ModelAdmin):
    pass

@admin.register(RecipeIngredientGroup)
class RecipeIngredientGroupAdmin(admin.ModelAdmin):
    pass

@admin.register(IngredientGroup)
class IngredientGroupAdmin(admin.ModelAdmin):
    pass

@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    pass

@admin.register(RecipeIngredientAmount)
class RecipeIngredientAmountAdmin(admin.ModelAdmin):
    pass

@admin.register(Step)
class StepAdmin(admin.ModelAdmin):
    pass

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    raw_id_fields = ("favorite_recipes", "disliked_recipes", 'disliked_ingredients')
