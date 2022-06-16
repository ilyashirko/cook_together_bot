from django.contrib import admin
from .models import Allergen, DishType, Recipe, User


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    raw_id_fields = ("dish_types", "allergens",)

@admin.register(Allergen)
class AllergenAdmin(admin.ModelAdmin):
    pass

@admin.register(DishType)
class DishTypeAdmin(admin.ModelAdmin):
    pass

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    raw_id_fields = ("favorite_recipes", "disliked_recipes", 'disliked_ingredients')