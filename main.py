"""Точка входа в игру «Тамагочи-кликер»"""

import os

from game.clicker import SimpleRandomClicker
from game.exceptions import TamagochiGameError, TamagochiIsGone
from game.game import AbstractGame, SimpleGame
from game.models import Food, Medicine
from game.tamagochi import SimpleTamagochi

PET_NAME = 'Малёк'

STATUS_LABELS = {
    'hunger': 'голод',
    'fatigue': 'усталость',
    'hp': 'здоровье',
    'energy': 'энергия',
    'coins': 'монет',
}


def clear_screen() -> None:
    """Очищает консоль (Windows и Unix)"""
    os.system('cls' if os.name == 'nt' else 'clear')


def format_status(status: dict[str, int]) -> str:
    """
    Форматирует статус игры для вывода в консоль

    :param status: словарь со статусом игры
    :return: строка вида «голод 20, здоровье 100, ...»
    """
    return ', '.join(
        f'{STATUS_LABELS.get(key, key)} {value}'
        for key, value in status.items()
    )


def print_dashboard(game: AbstractGame, output: str) -> None:
    """
    Выводит результат прошлого действия, сумки, статус и меню

    :param game: объект игры
    :param output: сообщение о результате прошлого действия
    """
    print(output)

    print(f"Сумка с едой: {game.food}")
    print(f"Сумка с лекарствами: {game.medicine}")

    print(f"\nСтатус: {format_status(game.get_status())}\n")
    if game.tamagochi.is_sick():
        print("=======Тамагочи болеет======")
        print("=======Отдых действует менее эффективно=======")
    print("1. Пойти на работу")
    print("2. Купить еду")
    print("3. Купить лекарство")
    print("4. Покормить")
    print("5. Вылечить")
    print("6. Играть")
    print("7. Отдых")
    print("0. Выход")


def handle_action(game: AbstractGame, choice: str) -> str:
    """
    Выполняет выбранное игроком действие

    :param game: объект игры
    :param choice: номер действия, введённый игроком
    :return: сообщение о результате действия
    :raises TamagochiGameError: если действие не удалось выполнить
    """
    match choice:
        case "1":
            income = game.work()
            game.tamagochi.update()
            return f'Вы заработали {income} монет'
        case "2":
            game.buy_food()
        case "3":
            game.buy_medicine()
        case "4":
            game.feed_tamagochi()
        case "5":
            game.heal_tamagochi()
        case "6":
            game.play_with_tamagochi()
            return 'Вы поиграли с питомцем'
        case "7":
            game.rest_tamagochi()
            return 'Питомец отдохнул'
        case _:
            return "Неверная команда"
    return ''


def main() -> None:
    """Запускает игровой цикл"""
    all_food = [
        Food(name='Бургер', satiety=20, price=40),
        Food(name='Салат', satiety=10, price=20),
        Food(name='Яблоко', satiety=10, price=15)
    ]

    all_medicine = [
        Medicine(name='Ибупрофен', price=30, heal_hp=20, number_of_uses=2)
    ]

    tamagochi = SimpleTamagochi(name=PET_NAME)
    clicker = SimpleRandomClicker(10, 20)
    game = SimpleGame(
        tamagochi,
        clicker,
        all_food=all_food,
        all_medicine=all_medicine
    )

    print("Добро пожаловать в Тамагочи-кликер!")
    output = f'Знакомьтесь, ваш питомец — {PET_NAME}. Берегите его!'

    while True:
        print_dashboard(game, output)

        choice = input("Выберите действие: ").strip()
        if choice == "0":
            break

        try:
            output = handle_action(game, choice)
        except TamagochiIsGone as error:
            clear_screen()
            print(error)
            print(f"Итоговый статус: {format_status(game.get_status())}")
            print("Игра окончена.")
            break
        except TamagochiGameError as error:
            output = str(error)

        clear_screen()


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nДо встречи!")
