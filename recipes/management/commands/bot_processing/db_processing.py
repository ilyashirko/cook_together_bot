from recipes.models import DishType, User


def check_is_admin(telegram_id: str):
    return User.objects.get(telegram_id=telegram_id).is_admin


def get_or_create_user(telegram_id: str):
    user, was_created = User.objects.get_or_create(telegram_id=telegram_id)
    return user, was_created


def get_dish_types_objects():
    return DishType.objects.all()
