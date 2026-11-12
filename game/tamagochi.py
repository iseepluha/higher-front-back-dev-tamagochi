"""Модуль с интерфейсом и реализациями класса тамагочи"""

import random
from abc import ABC, abstractmethod

from .exceptions import TamagochiIsGone, TamagochiIsTired
from .models import Food, Medicine

MAX_STAT = 100

# Как меняются показатели за один тик (вызов update)
HUNGER_PER_TICK = 3
ENERGY_LOSS_PER_TICK = 3
FATIGUE_PER_TICK = 3

# Урон здоровью за один тик при плохом состоянии
STARVATION_DAMAGE = 10  # голод на максимуме
EXHAUSTION_DAMAGE = 5  # энергия на нуле
OVERWORK_DAMAGE = 5  # усталость на максимуме
SICKNESS_DAMAGE = 5  # питомец болеет

# Болезнь
SICKNESS_BASE_CHANCE = 0.05  # шанс заболеть за тик
SICKNESS_RISK_CHANCE = 0.10  # прибавка к шансу за каждый фактор риска
RISK_THRESHOLD = 70  # с этого значения голод и усталость опасны
SICK_EXTRA_FATIGUE = 3  # болезнь сильнее утомляет
SICK_EXTRA_ENERGY_LOSS = 3  # и быстрее отнимает силы

# Действия
FEED_ENERGY_COST = 3  # после еды питомца клонит в сон
PLAY_ENERGY_COST = 20
PLAY_HUNGER = 10
PLAY_FATIGUE = 10
PLAY_HP_BONUS = 5  # подвижные игры укрепляют здоровье
REST_RECOVERY = 30  # больному питомцу отдых помогает вдвое хуже


class AbstractTamagochi(ABC):
    """Интерфейс логики тамагочи"""

    @abstractmethod
    def feed(self, food: Food) -> None:
        """
        Абстрактный метод для кормления тамагочи

        :param food: объект еды для кормления
        """
        raise NotImplementedError

    @abstractmethod
    def play(self) -> None:
        """Абстрактный метод для игры с тамагочи"""
        raise NotImplementedError

    @abstractmethod
    def rest(self) -> None:
        """Абстрактный метод для отдыха тамагочи"""
        raise NotImplementedError

    @abstractmethod
    def heal(self, medicine: Medicine) -> None:
        """
        Абстрактный метод для лечения тамагочи

        :param medicine: лекарство для лечения
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def status(self) -> dict[str, int]:
        """
        Абстрактное свойство для доступа ко всем состояниям тамагочи

        :return: словарь со всеми состояниями тамагочи
        """
        raise NotImplementedError

    @abstractmethod
    def is_alive(self) -> bool:
        """
        Абстрактный метод для проверки жив ли тамагочи

        :return: True если жив, иначе False
        """
        raise NotImplementedError

    @abstractmethod
    def is_sick(self) -> bool:
        """
        Абстрактный метод для проверки, не заболел ли тамагочи

        :return: True если тамагочи болеет, иначе False
        """
        raise NotImplementedError

    @abstractmethod
    def update(self) -> None:
        """
        Абстрактный метод для обновления состояний тамагочи.
        Должен использоваться после каждого взаимодействия с тамагочи
        """
        raise NotImplementedError


class SimpleTamagochi(AbstractTamagochi):
    """
    Питомец с четырьмя показателями: голод, усталость, здоровье, энергия.

    Все показатели — целые числа от 0 до MAX_STAT. Для голода и усталости
    чем больше значение, тем хуже; для здоровья и энергии — наоборот.
    Когда здоровье падает до нуля, питомец погибает.
    """

    def __init__(self, name: str = 'Малёк') -> None:
        """
        Создаёт сытого, бодрого и здорового питомца

        :param name: имя питомца
        """
        self._name = name
        self._hunger = 20
        self._fatigue = 0
        self._hp = MAX_STAT
        self._energy = MAX_STAT
        self._sick = False

    @property
    def name(self) -> str:
        """
        Имя питомца

        :return: имя питомца
        """
        return self._name

    @property
    def status(self) -> dict[str, int]:
        """
        Текущие показатели питомца

        :return: словарь с ключами hunger, fatigue, hp, energy
        """
        return {
            'hunger': self._hunger,
            'fatigue': self._fatigue,
            'hp': self._hp,
            'energy': self._energy,
        }

    def feed(self, food: Food) -> None:
        """
        Кормит питомца: голод уменьшается, но немного падает энергия

        :param food: еда, которую съест питомец
        :raises TamagochiIsGone: если питомец уже погиб
        """
        self._ensure_alive()
        self._hunger = self._clamp(self._hunger - food.satiety)
        self._energy = self._clamp(self._energy - FEED_ENERGY_COST)

    def play(self) -> None:
        """
        Играет с питомцем: прибавляет здоровья здоровому питомцу,
        но отнимает энергию, повышает голод и усталость

        :raises TamagochiIsGone: если питомец уже погиб
        :raises TamagochiIsTired: если у питомца не хватает энергии на игру
        """
        self._ensure_alive()
        if self._energy < PLAY_ENERGY_COST:
            raise TamagochiIsTired(
                f'{self._name} слишком устал для игр — дайте ему отдохнуть'
            )
        self._energy -= PLAY_ENERGY_COST
        self._hunger = self._clamp(self._hunger + PLAY_HUNGER)
        self._fatigue = self._clamp(self._fatigue + PLAY_FATIGUE)
        if not self._sick:
            self._hp = self._clamp(self._hp + PLAY_HP_BONUS)

    def rest(self) -> None:
        """
        Укладывает питомца отдыхать: энергия растёт, усталость падает.
        Больному питомцу отдых помогает вдвое слабее

        :raises TamagochiIsGone: если питомец уже погиб
        """
        self._ensure_alive()
        recovery = REST_RECOVERY
        if self._sick:
            recovery //= 2
        self._energy = self._clamp(self._energy + recovery)
        self._fatigue = self._clamp(self._fatigue - recovery)

    def heal(self, medicine: Medicine) -> None:
        """
        Лечит питомца: восстанавливает здоровье и излечивает болезнь

        :param medicine: лекарство, которым лечат питомца
        :raises TamagochiIsGone: если питомец уже погиб
        """
        self._ensure_alive()
        self._hp = self._clamp(self._hp + medicine.heal_hp)
        self._sick = False

    def is_alive(self) -> bool:
        """
        Проверяет, жив ли питомец

        :return: True, если здоровье больше нуля, иначе False
        """
        return self._hp > 0

    def is_sick(self) -> bool:
        """
        Проверяет, болеет ли питомец

        :return: True, если питомец болеет, иначе False
        """
        return self._sick

    def update(self) -> None:
        """
        Проживает один тик времени: питомец голодает, устаёт и теряет
        энергию, получает урон от плохого состояния и может заболеть

        :raises TamagochiIsGone: если питомец погиб (в том числе раньше)
        """
        self._ensure_alive()
        energy_loss = ENERGY_LOSS_PER_TICK
        fatigue_gain = FATIGUE_PER_TICK
        if self._sick:
            energy_loss += SICK_EXTRA_ENERGY_LOSS
            fatigue_gain += SICK_EXTRA_FATIGUE

        self._hunger = self._clamp(self._hunger + HUNGER_PER_TICK)
        self._energy = self._clamp(self._energy - energy_loss)
        self._fatigue = self._clamp(self._fatigue + fatigue_gain)
        self._hp = self._clamp(self._hp - self._calculate_damage())
        self._ensure_alive()
        self._maybe_get_sick()

    def _calculate_damage(self) -> int:
        """
        Считает урон здоровью за тик по текущему состоянию питомца

        :return: сколько здоровья питомец потеряет за тик
        """
        damage = 0
        if self._hunger >= MAX_STAT:
            damage += STARVATION_DAMAGE
        if self._energy <= 0:
            damage += EXHAUSTION_DAMAGE
        if self._fatigue >= MAX_STAT:
            damage += OVERWORK_DAMAGE
        if self._sick:
            damage += SICKNESS_DAMAGE
        return damage

    def _maybe_get_sick(self) -> None:
        """
        Случайно решает, заболеет ли питомец.
        Сильный голод и усталость повышают шанс заболеть
        """
        if self._sick:
            return
        chance = SICKNESS_BASE_CHANCE
        if self._hunger >= RISK_THRESHOLD:
            chance += SICKNESS_RISK_CHANCE
        if self._fatigue >= RISK_THRESHOLD:
            chance += SICKNESS_RISK_CHANCE
        self._sick = random.random() < chance

    def _ensure_alive(self) -> None:
        """
        Проверяет, что с питомцем ещё можно взаимодействовать

        :raises TamagochiIsGone: если питомец погиб
        """
        if not self.is_alive():
            raise TamagochiIsGone(
                f'{self._name} покинул этот мир: здоровье упало до нуля'
            )

    @staticmethod
    def _clamp(value: int) -> int:
        """
        Ограничивает значение показателя диапазоном от 0 до MAX_STAT

        :param value: новое значение показателя
        :return: значение в допустимом диапазоне
        """
        return max(0, min(MAX_STAT, value))
