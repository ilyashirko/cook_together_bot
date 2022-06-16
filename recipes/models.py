from django.db import models
import uuid
from django.core.validators import MinLengthValidator
from phonenumber_field.modelfields import PhoneNumberField

# Recipes models

class Recipe(models.Model):
    uuid = models.CharField(
        "id",
        unique=True,
        default=uuid.uuid1,
        max_length=36,
        validators=[MinLengthValidator(36)],
        primary_key=True,
        editable=False
    )
    title = models.CharField('Название блюда', max_length=100)
    image = models.ImageField('Главное изображение')
    dish_types = models.ManyToManyField(
        'DishType',
        related_name='recipes',
        verbose_name='Тип(-ы) блюда'
    )
    description = models.CharField('Краткое описание', max_length=1000)
    full_time = models.SmallIntegerField('Общее время приготовления')
    stove_time = models.SmallIntegerField('Время "у плиты"')
    complexity = models.SmallIntegerField( 'Сложность')
    is_spicy = models.BooleanField('Острое')
    allergens = models.ManyToManyField(
        'Allergen',
        related_name='recipes',
        verbose_name='Аллергены',
    )
    proteins = models.SmallIntegerField('Белки',)
    fats = models.SmallIntegerField('Жиры',)
    carbohydrates = models.SmallIntegerField('Углеводы',)
    calories = models.SmallIntegerField('Калории',)


class Allergen(models.Model):
    title = models.CharField(
        'Аллерген',
        max_length=50,
    )


class DishType(models.Model):
    title = models.CharField('Тип блюда', max_length=50)


class IngredientGroup(models.Model):
    recipe = models.ForeignKey(
        'Recipe',
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='recipe1'
    )
    title = models.CharField('Название группы', max_length=50)
    dish_ingredients = models.ManyToManyField(
        'DishIngredient',
        related_name='groups',
        verbose_name='Ингредиенты'
    )


class DishIngredient(models.Model):
    ingredient = models.ManyToManyField(
        'Ingredient',
        related_name='dish_ingredient',
        verbose_name='Ингредиент'
    )
    value = models.SmallIntegerField('Количество')


class Ingredient(models.Model):
    title = models.CharField('Ингредиент', max_length=50)
    unit = models.ForeignKey(
        'Unit',
        on_delete=models.PROTECT,
        related_name='ingredients',
        verbose_name='Единица измерения'
    )


class Unit(models.Model):
    title = models.CharField('Единица измерения', max_length=50)
    shorten = models.CharField('Сокращенно', max_length=10)


class Step(models.Model):
    recipe = models.ForeignKey(
        'Recipe',
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='which_recipe'
    )
    image = models.ImageField('Изображение', blank=True)
    description = models.CharField('Описание', max_length=1000)


# User's models


class User(models.Model):
    first_name = models.CharField('Имя', max_length=30, blank=True)
    second_name = models.CharField('Фамилия', max_length=30, blank=True)
    patronymic = models.CharField('Отчество', max_length=30, blank=True)

    phone = PhoneNumberField('Номер телефона', blank=True)
    mail = models.EmailField('E-mail', blank=True)

    telegram_id = models.SmallIntegerField('Telegram ID', unique=True)
    telegram_first_name = models.CharField('Telegram Имя', max_length=30, blank=True)
    telegram_username = models.CharField('Telegram username', max_length=30, blank=True)

    favorite_recipes = models.ManyToManyField(
        'Recipe',
        verbose_name='Любимые рецепты',
        related_name='liked_by_users',
        blank=True
    )
    disliked_recipes = models.ManyToManyField(
        'Recipe',
        verbose_name='Стоп-лист рецептов',
        related_name='disliked_by_users',
        blank=True
    )
    disliked_ingredients = models.ManyToManyField(
        'Ingredient',
        verbose_name='Стоп-лист рецептов',
        related_name='disliked_by_users',
        blank=True
    )
    is_admin = models.BooleanField('Администратор', default=False)