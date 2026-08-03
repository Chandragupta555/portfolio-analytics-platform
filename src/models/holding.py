from dataclasses import dataclass
from typing import Optional


@dataclass
class Holding:
    ticker: str
    weight: float
    shares: Optional[float] = None

    def __post_init__(self) -> None:
        self.ticker = self.ticker.upper()
        if self.weight <= 0:
            raise ValueError(f"Holding weight must be greater than 0, got {self.weight}")
