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
    title = models.CharField('Название блюда', max_length=200)
    image = models.ImageField('Главное изображение')
    dish_types = models.ManyToManyField(
        'DishType',
        related_name='recipes',
        verbose_name='Тип(-ы) блюда'
    )
    description = models.TextField('Краткое описание')
    full_time = models.DurationField('Общее время приготовления')
    stove_time = models.DurationField('Время "у плиты"')
    complexity = models.SmallIntegerField( 'Сложность')
    is_spicy = models.BooleanField('Острое')
    allergens = models.ManyToManyField(
        'Allergen',
        related_name='recipes',
        verbose_name='Аллергены',
    )
    proteins = models.FloatField('Белки',)
    fats = models.FloatField('Жиры',)
    carbohydrates = models.FloatField('Углеводы',)
    calories = models.FloatField('Калории',)

    def __str__(self):
        return self.title


class Allergen(models.Model):
    title = models.CharField(
        'Аллерген',
        max_length=50,
    )

    def __str__(self):
        return self.title


class DishType(models.Model):
    title = models.CharField('Тип блюда', max_length=50)

    def __str__(self):
        return self.title


class RecipeIngredientGroup(models.Model):
    recipe = models.ForeignKey(
        'Recipe',
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='ingredients_groups'
    )
    title = models.CharField('Тип блюда', max_length=50)
    ingredients_amount = models.ManyToManyField(
        'RecipeIngredientAmount',
        verbose_name='Ингредиенты',
        related_name='RecipeIngredientAmount'
    )

    def __str__(self):
        return f'"{self.recipe}" - {self.title} ({len(self.ingredients_amount)} ингредиентов)'


class IngredientGroup(models.Model):
    title = models.CharField('Ингредиент', max_length=100)

    def __str__(self):
        return self.title


class Ingredient(models.Model):
    title = models.CharField('Ингредиент', max_length=100)
    group = models.ForeignKey(
        'IngredientGroup',
        on_delete=models.CASCADE,
        verbose_name='Группа',
        related_name='ingredients'
    )

    def __str__(self):
        return f'{self.title} ({self.group})'
    

class RecipeIngredientAmount(models.Model):
    recipe = models.ForeignKey(
        'Recipe',
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='ingredients_amounts'
    )
    ingredient = models.ForeignKey(
        'Ingredient',
        on_delete=models.CASCADE,
        verbose_name='Ingredient',
        related_name='ingredients_amounts'
    )
    amount = models.SmallIntegerField('Amount', null=True, blank=True)
    measure = models.CharField('Measure', max_length=50, null=True, blank=True)

    def __str__(self):
        return f'"{self.recipe}" - {self.ingredient} ({self.amount} {self.measure})'


class Step(models.Model):
    recipe = models.ForeignKey(
        'Recipe',
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='which_recipe'
    )
    image = models.ImageField('Изображение', blank=True)
    description = models.CharField('Описание', max_length=1000)

    def __str__(self):
        return self.recipe


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
