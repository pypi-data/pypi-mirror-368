from __future__ import annotations
from enum import Enum
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import random
import time
from abc import ABC, abstractmethod


class Smell(Enum):
    HEAVENLY = "heavenly"
    PLEASANT = "pleasant"
    NEUTRAL = "neutral"
    BAD = "bad"
    HORRIBLE = "horrible"
    PUTRID = "putrid"
    TOXIC = "toxic"
    NUCLEAR = "nuclear"

    @classmethod
    def get_random(cls) -> Smell:
        return random.choice(list(cls))

    def get_intensity_multiplier(self) -> float:
        multipliers = {
            self.HEAVENLY: 0.1,
            self.PLEASANT: 0.3,
            self.NEUTRAL: 0.5,
            self.BAD: 0.7,
            self.HORRIBLE: 1.0,
            self.PUTRID: 1.5,
            self.TOXIC: 2.0,
            self.NUCLEAR: 3.0,
        }
        return multipliers[self]


class FartType(Enum):
    SILENT = "silent but deadly"
    SQUEAKY = "squeaky"
    TRUMPET = "trumpet"
    THUNDER = "thunderous"
    RAPID_FIRE = "rapid fire"
    LONG_WINDED = "long and winded"
    WET = "suspiciously wet"
    DRY = "bone dry"
    MUSICAL = "surprisingly musical"


class Duration(Enum):
    QUICK = (0.5, 1.0)  # seconds
    NORMAL = (1.0, 3.0)
    EXTENDED = (3.0, 6.0)
    EPIC = (6.0, 12.0)
    LEGENDARY = (12.0, 30.0)

    def get_random_duration(self) -> float:
        min_dur, max_dur = self.value
        return random.uniform(min_dur, max_dur)


@dataclass
class FartStats:
    total_farts: int = 0
    total_power: int = 0
    loudest_fart: int = 0
    smelliest_fart: Smell = field(default_factory=lambda: Smell.NEUTRAL)
    longest_duration: float = 0.0
    favorite_type: Optional[FartType] = None
    gas_expelled: float = 0.0  # in cubic centimeters

    def add_fart(self, fart: Fart, duration: float) -> None:
        self.total_farts += 1
        self.total_power += fart.power
        self.gas_expelled += fart.volume

        if fart.power > self.loudest_fart:
            self.loudest_fart = fart.power

        if (
            fart.smell.get_intensity_multiplier()
            > self.smelliest_fart.get_intensity_multiplier()
        ):
            self.smelliest_fart = fart.smell

        if duration > self.longest_duration:
            self.longest_duration = duration

    def get_average_power(self) -> float:
        return self.total_power / self.total_farts if self.total_farts > 0 else 0.0

    def __str__(self) -> str:
        return f"""
🎯 FART STATISTICS 🎯
Total Farts: {self.total_farts:,}
Average Power: {self.get_average_power():.1f}
Loudest Fart: {self.loudest_fart}
Smelliest Fart: {self.smelliest_fart.value}
Longest Duration: {self.longest_duration:.2f}s
Total Gas Expelled: {self.gas_expelled:.1f} cc
        """


class FartEffect(ABC):
    @abstractmethod
    def apply(self, fart: Fart) -> str:
        pass


class EchoEffect(FartEffect):
    def apply(self, fart: Fart) -> str:
        return f"*echo* {fart.get_sound_description()} *echo*"


class ReverbEffect(FartEffect):
    def apply(self, fart: Fart) -> str:
        return f"{fart.get_sound_description()}...{fart.get_sound_description()[:-3]}...{fart.get_sound_description()[:-6]}..."


class AmplifyEffect(FartEffect):
    def __init__(self, multiplier: float = 2.0):
        self.multiplier = multiplier

    def apply(self, fart: Fart) -> str:
        amplified_power = min(100, int(fart.power * self.multiplier))
        return f"**AMPLIFIED** {fart.get_sound_description()} (Power boosted to {amplified_power}!)"


@dataclass
class FartEvent:
    timestamp: datetime
    fart: Fart
    duration: float
    location: str = "unknown"
    witnesses: int = 0

    def get_embarrassment_level(self) -> str:
        if self.witnesses == 0:
            return "private relief"
        elif self.witnesses <= 2:
            return "slightly awkward"
        elif self.witnesses <= 5:
            return "moderately embarrassing"
        else:
            return "maximum mortification"


class Fart:
    _smell_emojis = {
        Smell.HEAVENLY: "😇",
        Smell.PLEASANT: "🌸",
        Smell.NEUTRAL: "😐",
        Smell.BAD: "😷",
        Smell.HORRIBLE: "🤢",
        Smell.PUTRID: "🤮",
        Smell.TOXIC: "☠️",
        Smell.NUCLEAR: "☢️",
    }

    def __init__(
        self,
        smell: Smell,
        fart_type: Optional[FartType] = None,
        duration: Duration = Duration.NORMAL,
        temperature: float = 98.6,  # Fahrenheit
        humidity: float = 85.0,  # percentage
    ) -> None:
        self.smell = smell
        self.fart_type = fart_type or random.choice(list(FartType))
        self.duration_enum = duration
        self.temperature = temperature
        self.humidity = humidity
        self._power: Optional[int] = None
        self._volume: Optional[float] = None
        self.effects: List[FartEffect] = []
        self.creation_time = datetime.now()

    @property
    def power(self) -> int:
        if self._power is None:
            base_power = random.randint(10, 90)
            smell_bonus = int(self.smell.get_intensity_multiplier() * 20)
            type_bonus = self._get_type_power_bonus()
            self._power = min(100, base_power + smell_bonus + type_bonus)
        return self._power

    @power.setter
    def power(self, value: int) -> None:
        if not isinstance(value, int) or value <= 0:
            raise ValueError("Power must be a positive integer.")
        if value > 100:
            raise ValueError("Fart power cannot exceed 100.")
        self._power = value

    @property
    def volume(self) -> float:
        """Volume in cubic centimeters"""
        if self._volume is None:
            base_volume = random.uniform(10.0, 200.0)
            power_multiplier = self.power / 100.0
            self._volume = base_volume * power_multiplier
        return self._volume

    def _get_type_power_bonus(self) -> int:
        bonuses = {
            FartType.SILENT: -10,
            FartType.SQUEAKY: 5,
            FartType.TRUMPET: 15,
            FartType.THUNDER: 25,
            FartType.RAPID_FIRE: 10,
            FartType.LONG_WINDED: 20,
            FartType.WET: 5,
            FartType.DRY: 0,
            FartType.MUSICAL: 8,
        }
        return bonuses.get(self.fart_type, 0)

    def add_effect(self, effect: FartEffect) -> None:
        self.effects.append(effect)

    def get_sound_description(self) -> str:
        sound_map = {
            FartType.SILENT: "...",
            FartType.SQUEAKY: "squeak!",
            FartType.TRUMPET: "HONK!",
            FartType.THUNDER: "BOOOOOM!",
            FartType.RAPID_FIRE: "pop-pop-pop-pop!",
            FartType.LONG_WINDED: "pfffffffffffffff...",
            FartType.WET: "splurt!",
            FartType.DRY: "poof!",
            FartType.MUSICAL: "♪ toot-toot-toooot ♪",
        }
        return sound_map.get(self.fart_type, "fart!")

    def get_smell_emoji(self) -> str:
        return self._smell_emojis.get(self.smell, "💨")

    def calculate_dissipation_time(self) -> float:
        """Calculate how long the smell lingers (in minutes)"""
        base_time = self.smell.get_intensity_multiplier() * 5
        humidity_factor = self.humidity / 100.0
        temperature_factor = (100 - self.temperature) / 100.0
        return base_time * (1 + humidity_factor + temperature_factor)

    def rip(
        self,
        power: Optional[int] = None,
        location: str = "somewhere",
        witnesses: int = 0,
        simulate_duration: bool = True,
    ) -> FartEvent:
        if power is not None:
            self.power = power

        if not self.power or self.power <= 0:
            raise ValueError("Farts must be powerful.")
        elif self.power > 100:
            raise ValueError("Fart too powerful.")

        duration = self.duration_enum.get_random_duration()
        dissipation_time = self.calculate_dissipation_time()

        # Create base description
        description = (
            f"Letting out a {self.smell.value} smelling {self.fart_type.value} fart"
        )

        # Apply effects
        sound_desc = self.get_sound_description()
        for effect in self.effects:
            sound_desc = effect.apply(self)

        # Full output
        output_parts = [
            f"{description} with power score of {self.power:,}",
            f"Sound: {sound_desc}",
            f"Duration: {duration:.1f}s",
            f"Volume: {self.volume:.1f} cc",
            f"Smell will linger for {dissipation_time:.1f} minutes",
            f"Location: {location}",
            self.get_smell_emoji(),
        ]

        if witnesses > 0:
            embarrassment = FartEvent(
                datetime.now(), self, duration, location, witnesses
            ).get_embarrassment_level()
            output_parts.insert(-1, f"Witnesses: {witnesses} ({embarrassment})")

        print(" | ".join(output_parts))

        # Simulate duration if requested
        if simulate_duration and duration > 0:
            time.sleep(min(duration, 3.0))  # Cap at 3 seconds for demo

        return FartEvent(
            timestamp=datetime.now(),
            fart=self,
            duration=duration,
            location=location,
            witnesses=witnesses,
        )

    def __repr__(self) -> str:
        return f"Fart(smell={self.smell}, type={self.fart_type}, power={self.power})"


class FartMachine:
    """A sophisticated fart generation and tracking system"""

    def __init__(self, name: str = "Anonymous Farter"):
        self.name = name
        self.stats = FartStats()
        self.history: List[FartEvent] = []
        self.gas_tank = 100.0  # percentage
        self.dietary_influences: Dict[str, float] = {}

    def eat_food(self, food: str, gas_factor: float) -> None:
        """Add dietary influence on gas production"""
        self.dietary_influences[food] = gas_factor
        self.gas_tank = min(100.0, self.gas_tank + gas_factor * 10)
        print(f"Consumed {food}. Gas tank now at {self.gas_tank:.1f}%")

    def generate_random_fart(self) -> Fart:
        """Generate a random fart influenced by diet"""
        if self.gas_tank < 10:
            raise ValueError("Gas tank too low! Need to eat more beans.")

        # Diet influences smell
        if self.dietary_influences:
            avg_gas_factor = sum(self.dietary_influences.values()) / len(
                self.dietary_influences
            )
            if avg_gas_factor > 0.7:
                smell_choices = [Smell.HORRIBLE, Smell.PUTRID, Smell.TOXIC]
            elif avg_gas_factor > 0.4:
                smell_choices = [Smell.BAD, Smell.HORRIBLE]
            else:
                smell_choices = [Smell.PLEASANT, Smell.NEUTRAL, Smell.BAD]
            smell = random.choice(smell_choices)
        else:
            smell = Smell.get_random()

        fart = Fart(
            smell=smell,
            fart_type=random.choice(list(FartType)),
            duration=random.choice(list(Duration)),
        )

        # Consume gas
        self.gas_tank -= random.uniform(2, 8)
        self.gas_tank = max(0, self.gas_tank)

        return fart

    def auto_fart(
        self,
        location: str = "somewhere",
        witnesses: int = 0,
        add_random_effects: bool = True,
    ) -> FartEvent:
        """Generate and release a random fart"""
        fart = self.generate_random_fart()

        if add_random_effects and random.random() < 0.3:  # 30% chance of effects
            effect_choices = [EchoEffect(), ReverbEffect(), AmplifyEffect()]
            fart.add_effect(random.choice(effect_choices))

        event = fart.rip(location=location, witnesses=witnesses)
        self.stats.add_fart(fart, event.duration)
        self.history.append(event)

        return event

    def fart_session(self, count: int = 5, location: str = "bathroom") -> None:
        """Release multiple farts in succession"""
        print(f"\n🎭 {self.name} is having a {count}-fart session at {location}!")
        print("=" * 50)

        for i in range(count):
            try:
                print(f"\nFart #{i + 1}:")
                self.auto_fart(location=location, witnesses=0)
                time.sleep(random.uniform(0.5, 2.0))
            except ValueError as e:
                print(f"Session ended early: {e}")
                break

        print(f"\n🏁 Session complete! Gas tank: {self.gas_tank:.1f}%")

    def get_history_summary(self, last_n: int = 10) -> str:
        """Get summary of recent fart history"""
        if not self.history:
            return "No fart history available."

        recent = self.history[-last_n:]
        summary = f"\n📜 RECENT FART HISTORY (Last {len(recent)} farts):\n"
        summary += "=" * 50 + "\n"

        for i, event in enumerate(recent, 1):
            summary += f"{i}. {event.timestamp.strftime('%H:%M:%S')} - "
            summary += f"{event.fart.fart_type.value} ({event.fart.power} power) "
            summary += f"at {event.location}"
            if event.witnesses > 0:
                summary += f" with {event.witnesses} witnesses"
            summary += "\n"

        return summary

    def __str__(self) -> str:
        return f"FartMachine(name='{self.name}', gas_tank={self.gas_tank:.1f}%)"


# Example usage and demo
if __name__ == "__main__":
    # Create a fart machine
    machine = FartMachine("Sir Farts-a-Lot")

    # Add some dietary influences
    machine.eat_food("beans", 0.8)
    machine.eat_food("broccoli", 0.6)
    machine.eat_food("eggs", 0.7)

    print(f"\n{machine}")
    print("🚀 FART SIMULATION STARTING!\n")

    # Single farts with effects
    fart1 = Fart(Smell.PUTRID, FartType.THUNDER)
    fart1.add_effect(EchoEffect())
    fart1.rip(power=85, location="elevator", witnesses=3)

    print("\n" + "-" * 50)

    # Random fart session
    machine.fart_session(count=3, location="office")

    # Show statistics
    print(machine.stats)
    print(machine.get_history_summary())

    # Create some specialty farts
    print("\n🎪 SPECIALTY FARTS:")
    silent_killer = Fart(Smell.TOXIC, FartType.SILENT)
    silent_killer.add_effect(AmplifyEffect(3.0))
    silent_killer.rip(power=95, location="library", witnesses=0)

    musical_fart = Fart(Smell.PLEASANT, FartType.MUSICAL)
    musical_fart.add_effect(ReverbEffect())
    musical_fart.rip(power=60, location="concert hall", witnesses=50)
