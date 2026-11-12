"""Модуль с исключениями"""


class TamagochiGameError(Exception):
    """Базовое исключение игры: его наследники можно ловить одним except"""


class TamagochiIsGone(TamagochiGameError):
    """Ошибка при смерти тамагочи"""


class NotEnoughMoney(TamagochiGameError):
    """Ошибка когда не хватает монет для покупки"""


class EmptyInventory(TamagochiGameError):
    """Ошибка когда в сумке нет нужных предметов (еды или лекарств)"""


class TamagochiIsTired(TamagochiGameError):
    """Ошибка когда у питомца не хватает энергии на действие"""
