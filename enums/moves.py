from enum import IntEnum
from .outcomes import Outcomes

__all__ = ["Moves", "all_moves", "play"]

class Moves(IntEnum):
		NoMove = 0x00
		Rock = 0x526f636b
		Paper = 0x5061706572
		Scissors = 0x53636973736f727320
	
	
all_moves = (Moves.NoMove, Moves.Rock, Moves.Paper, Moves.Scissors)


def play(opponent, player):
		if opponent == player:
			return Outcomes.Draw
	
		if opponent == Moves.Rock and player == Moves.Scissors:
			return Outcomes.Lose
		elif opponent == Moves.Rock and player == Moves.Paper:
			return Outcomes.Win
		elif opponent == Moves.Paper and player == Moves.Scissors:
			return Outcomes.Win
		elif opponent == Moves.Paper and player == Moves.Rock:
			return Outcomes.Lose
		elif opponent == Moves.Scissors and player == Moves.Paper:
			return Outcomes.Lose
		elif opponent == Moves.Scissors and player == Moves.Rock:
			return Outcomes.Win
		else:
			return Outcomes.Undetermined
	
		print(opponent, player)
