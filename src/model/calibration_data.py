from dataclasses import dataclass

@dataclass
class CalibrationData:
    fit_type: str
    A: float = 0.0
    B: float = 0.0
    C: float = 0.0
    D: float = 0.0

    @property
    def order(self) -> int:
        if "3rd" in self.fit_type: return 3
        if "2nd" in self.fit_type: return 2
        return 1