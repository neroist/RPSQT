from enum import Enum
__all__ = ["Outcomes"]


class Outcomes(Enum):
		Win = 1
		Lose = -1
		Draw = 0.5
		Undetermined = None