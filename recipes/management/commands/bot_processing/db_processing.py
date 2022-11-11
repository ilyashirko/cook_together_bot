from recipes.models import DishType, User, Recipe


def update_dish_types(dish_types_objs=DishType.objects.all()):
    global dish_types
    dish_types = [dish_type.title for dish_type in dish_types_objs]
    return dish_types


def update_recipes_titles(recipes=Recipe.objects.all()):
    global recipes_titles
    recipes_titles = [recipe.title for recipe in recipes]
    return recipes_titles


recipes_titles = update_recipes_titles()

dish_types = update_dish_types()


def check_is_admin(telegram_id: str):
    return User.objects.get(telegram_id=telegram_id).is_admin


def get_or_create_user(telegram_id: str):
    user, was_created = User.objects.get_or_create(telegram_id=telegram_id)
    return user, was_created


def get_dish_types_objects():
    return DishType.objects.all()
