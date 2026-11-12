"""Модуль с интерфейсом и реализацией кликера"""

import random
from abc import ABC, abstractmethod


class AbstractClicker(ABC):
    """Интерфейс для кликера"""

    @abstractmethod
    def __init__(self) -> None:
        """Абстрактный метод инициализации"""
        raise NotImplementedError

    @abstractmethod
    def click(self) -> None:
        """Абстрактный метод клика для накапливания монет"""
        raise NotImplementedError

    @property
    @abstractmethod
    def income_per_click(self) -> int:
        """
        Абстрактное свойство для доступа к количеству монет за клик

        :return: количество монет, которое принёс клик
        """
        raise NotImplementedError


class SimpleRandomClicker(AbstractClicker):
    """Кликер, который за каждый клик приносит случайное число монет"""

    def __init__(self, min_income: int, max_income: int) -> None:
        """
        Инициализация кликера

        :param min_income: минимальный доход за один клик
        :param max_income: максимальный доход за один клик
        :raises ValueError: если границы дохода отрицательные
            или минимальная граница больше максимальной
        """
        if min_income < 0 or min_income > max_income:
            raise ValueError(
                'Доход за клик должен удовлетворять условию '
                '0 <= min_income <= max_income'
            )
        self._min_income = min_income
        self._max_income = max_income
        self._income_per_click = 0

    @property
    def income_per_click(self) -> int:
        """
        Количество монет, заработанных последним кликом

        :return: доход за последний клик (0, если кликов ещё не было)
        """
        return self._income_per_click

    def click(self) -> None:
        """Совершает клик: определяет, сколько монет он принёс"""
        self._income_per_click = random.randint(
            self._min_income, self._max_income
        )
