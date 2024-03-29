from textwrap import dedent

HELLO_MESSAGE = dedent(
    """
    Привет!
    Я кулинарный бот и я лучший су-шеф в интернете!

    Я могу:
      - помочь с выбором рецепта
      - составить меню
      - составить список покупок

    Я помню какие рецепты вам понравились, а какие нет.

    Сообщу если в блюде присутствуют аллергены.

    И вообще, довольно слов - внизу появилась клавиатура на которой есть все доступные действия.

    Приятного аппетита!
    """
)

MAIN_TEXTS = {
  '/start': HELLO_MESSAGE,
  'вернуться на главную': 'Возвращаемся на главную'
}

GET_RECIPE_MESSAGE = dedent(
  """
  Сейчас я подберу для тебя произвольный рецепт.

  Но сперва, выбери категорию блюда.
  """
)
