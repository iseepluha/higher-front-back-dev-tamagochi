"""Модуль с интерфейсом и реализацией класса игры"""

from abc import ABC, abstractmethod
from typing import Any

from .tamagochi import AbstractTamagochi
from .clicker import AbstractClicker
from .exceptions import EmptyInventory, NotEnoughMoney, TamagochiIsGone
from .models import Food, Medicine

START_COINS = 0  # сколько монет у игрока в начале игры


class AbstractGame(ABC):
    """Интерфейс для логики игры"""

    @abstractmethod
    def __init__(
        self,
        tamagochi: AbstractTamagochi,
        clicker: AbstractClicker,
        all_food: list[Food],
        all_medicine: list[Medicine]
    ) -> None:
        """
        Абстрактный метод инициализации класса игры

        :param tamagochi: экземпляр тамагочи
        :param clicker: экземпляр кликера
        :param all_food: все доступные варианты еды
        :param all_medicine: все доступные варианты лекарств
        """
        raise NotImplementedError

    @abstractmethod
    def work(self) -> int:
        """
        Абстрактный метод для логики действия «работа»

        :return: количество заработанных монет
        """
        raise NotImplementedError

    @abstractmethod
    def buy_food(self) -> None:
        """Абстрактный метод для покупки еды"""
        raise NotImplementedError

    @abstractmethod
    def buy_medicine(self) -> None:
        """Абстрактный метод для покупки лекарства"""
        raise NotImplementedError

    @abstractmethod
    def feed_tamagochi(self) -> None:
        """Абстрактный метод для кормления тамагочи"""
        raise NotImplementedError

    @abstractmethod
    def heal_tamagochi(self) -> None:
        """Абстрактный метод для лечения тамагочи"""
        raise NotImplementedError

    @abstractmethod
    def rest_tamagochi(self) -> None:
        """Абстрактный метод для отдыха тамагочи"""
        raise NotImplementedError

    @abstractmethod
    def play_with_tamagochi(self) -> None:
        """Абстрактный метод для игры с тамагочи"""
        raise NotImplementedError

    @abstractmethod
    def get_status(self) -> dict[str, int]:
        """
        Абстрактный метод для получения статуса игры:
        всех характеристик тамагочи и количества монет

        :return: словарь с характеристиками тамагочи и ключом coins
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def food(self) -> list[Food]:
        """
        Абстрактное свойство для доступа к сумке с едой

        :return: список с имеющимися (купленными) объектами еды
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def medicine(self) -> list[Medicine]:
        """
        Абстрактное свойство для доступа к сумке с лекарствами

        :return: список с имеющимися (купленными) объектами лекарств
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def tamagochi(self) -> AbstractTamagochi:
        """
        Абстрактное свойство для доступа к питомцу

        :return: экземпляр тамагочи, за которым следит игра
        """
        raise NotImplementedError


class SimpleGame(AbstractGame):
    """
    Игра: связывает питомца с кликером и управляет ресурсами —
    монетами, сумкой с едой и сумкой с лекарствами.

    Каждое взаимодействие с питомцем занимает один тик времени.
    """

    def __init__(
        self,
        tamagochi: AbstractTamagochi,
        clicker: AbstractClicker,
        all_food: list[Food],
        all_medicine: list[Medicine]
    ) -> None:
        """
        Инициализация игры

        :param tamagochi: экземпляр тамагочи
        :param clicker: экземпляр кликера
        :param all_food: все доступные в магазине варианты еды
        :param all_medicine: все доступные в магазине варианты лекарств
        """
        self._tamagochi = tamagochi
        self._clicker = clicker
        self._all_food = list(all_food)
        self._all_medicine = list(all_medicine)
        self._coins = START_COINS
        self._food_bag: list[Food] = []
        self._medicine_bag: list[Medicine] = []

    @property
    def tamagochi(self) -> AbstractTamagochi:
        """
        Питомец, за которым следит игра

        :return: экземпляр тамагочи
        """
        return self._tamagochi

    @property
    def food(self) -> list[Food]:
        """
        Сумка с едой

        :return: копия списка купленной еды
        """
        return list(self._food_bag)

    @property
    def medicine(self) -> list[Medicine]:
        """
        Сумка с лекарствами

        :return: копия списка купленных лекарств
        """
        return list(self._medicine_bag)

    def work(self) -> int:
        """
        Работа: один клик кликера, заработанные монеты идут в кошелёк

        :return: количество заработанных монет
        :raises TamagochiIsGone: если питомец погиб и игра окончена
        """
        self._ensure_game_is_on()
        self._clicker.click()
        income = self._clicker.income_per_click
        self._coins += income
        return income

    def buy_food(self) -> None:
        """
        Покупка еды: игрок выбирает еду в магазине, она кладётся в сумку

        :raises TamagochiIsGone: если питомец погиб и игра окончена
        :raises NotEnoughMoney: если на выбранную еду не хватает монет
        """
        self._ensure_game_is_on()
        index = self._choose_item('Магазин еды:', self._all_food)
        if index is None:
            return
        food = self._all_food[index]
        self._pay(food.price)
        self._food_bag.append(food)

    def buy_medicine(self) -> None:
        """
        Покупка лекарства: игрок выбирает лекарство в аптеке,
        в сумку кладётся новая (ещё не начатая) упаковка

        :raises TamagochiIsGone: если питомец погиб и игра окончена
        :raises NotEnoughMoney: если на выбранное лекарство не хватает монет
        """
        self._ensure_game_is_on()
        index = self._choose_item('Аптека:', self._all_medicine)
        if index is None:
            return
        medicine = self._all_medicine[index]
        self._pay(medicine.price)
        # Кладём в сумку новую упаковку, а не сам товар с витрины:
        # иначе все купленные упаковки делили бы один счётчик uses
        new_package = Medicine(
            name=medicine.name,
            price=medicine.price,
            heal_hp=medicine.heal_hp,
            number_of_uses=medicine.number_of_uses,
        )
        self._medicine_bag.append(new_package)

    def feed_tamagochi(self) -> None:
        """
        Кормление: игрок выбирает еду из сумки, питомец её съедает

        :raises TamagochiIsGone: если питомец погиб
        :raises EmptyInventory: если в сумке нет еды
        """
        self._ensure_game_is_on()
        if not self._food_bag:
            raise EmptyInventory('Сумка с едой пуста — сначала купите еду')
        index = self._choose_item('Чем покормить питомца?', self._food_bag)
        if index is None:
            return
        self._tamagochi.feed(self._food_bag[index])
        del self._food_bag[index]
        self._pass_time()

    def heal_tamagochi(self) -> None:
        """
        Лечение: игрок выбирает лекарство из сумки, питомец его принимает.
        Закончившееся лекарство убирается из сумки

        :raises TamagochiIsGone: если питомец погиб
        :raises EmptyInventory: если в сумке нет лекарств
        """
        self._ensure_game_is_on()
        if not self._medicine_bag:
            raise EmptyInventory(
                'Сумка с лекарствами пуста — сначала купите лекарство'
            )
        index = self._choose_item('Чем лечить питомца?', self._medicine_bag)
        if index is None:
            return
        medicine = self._medicine_bag[index]
        self._tamagochi.heal(medicine)
        medicine.uses += 1
        if medicine.is_empty():
            del self._medicine_bag[index]
        self._pass_time()

    def rest_tamagochi(self) -> None:
        """
        Отдых питомца

        :raises TamagochiIsGone: если питомец погиб
        """
        self._ensure_game_is_on()
        self._tamagochi.rest()
        self._pass_time()

    def play_with_tamagochi(self) -> None:
        """
        Игра с питомцем

        :raises TamagochiIsGone: если питомец погиб
        :raises TamagochiIsTired: если у питомца нет сил играть
        """
        self._ensure_game_is_on()
        self._tamagochi.play()
        self._pass_time()

    def get_status(self) -> dict[str, int]:
        """
        Статус игры: показатели питомца и количество монет

        :return: словарь с показателями питомца и ключом coins
        """
        return {**self._tamagochi.status, 'coins': self._coins}

    def _pay(self, price: int) -> None:
        """
        Списывает монеты из кошелька

        :param price: сколько монет нужно заплатить
        :raises NotEnoughMoney: если монет меньше, чем price
        """
        if price > self._coins:
            raise NotEnoughMoney(
                f'Не хватает монет: нужно {price}, у вас {self._coins}'
            )
        self._coins -= price

    def _pass_time(self) -> None:
        """
        Проживает один тик времени после взаимодействия с питомцем

        :raises TamagochiIsGone: если за этот тик питомец погиб
        """
        self._tamagochi.update()

    def _ensure_game_is_on(self) -> None:
        """
        Проверяет, что игра ещё не окончена

        :raises TamagochiIsGone: если питомец погиб
        """
        if not self._tamagochi.is_alive():
            raise TamagochiIsGone('Игра окончена: питомца больше нет')

    @staticmethod
    def _choose_item(title: str, items: list[Any]) -> int | None:
        """
        Показывает пронумерованный список и спрашивает номер, пока
        пользователь не введёт корректное значение

        :param title: заголовок меню
        :param items: предметы, из которых выбирает пользователь
        :return: индекс выбранного предмета или None, если введён 0
        """
        print(title)
        for number, item in enumerate(items, start=1):
            print(f'{number}. {item}')
        print('0. Назад')
        while True:
            answer = input('Введите номер: ').strip()
            try:
                number = int(answer)
            except ValueError:
                number = -1
            if number == 0:
                return None
            if 1 <= number <= len(items):
                return number - 1
            print(f'Введите число от 0 до {len(items)}')
