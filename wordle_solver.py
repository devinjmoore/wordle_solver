from typing import List
import sys

import wordle_solver_gui as gui
import easygui


class Wordle:
    class Guess:
        """A class to represent a an incorrect guess in a Wordle game.

        Returns:
            [type]: [description]
        """
        _LETTER_NOT_IN_WORD = None
        _LETTER_CORRECT = True
        _LETTER_IN_WRONG_PLACE = False
        
        def __init__(self, word:str, hints: List[bool]) -> None:
            self.word = word
            self.hints = hints
            
    def __init__(self) -> None:
        self.guessed: List[Wordle.Guess] = []

    def set_guesses(self, guesses:List[Guess]):
        self.guesses = guesses


class WordleSolver:
    _LEN_GUESS = 5
    
    answers: List[str] = open("answers.txt").read().split('\n')

    def __init__(self, wordle:Wordle) -> None:
        self.wordle = wordle
    
    def _check_new_guess(self, new_guess:str) -> bool:
        """Determine if a new guess follows all known hints in this Wordle

        Args:
            new_guess (str): The proposed Wordle solution

        Returns:
            bool: Indicates whether the new guess uses all of this Wordle's
            guesses' hints
        """
        for guess in self.wordle.guessed:
            for i in range(self._LEN_GUESS):
                if new_guess[i] == guess.word[i]:
                    # Check if we already know that this letter shouldn't be here
                    if (guess.hints[i] == guess._LETTER_NOT_IN_WORD or
                        guess.hints[i] == guess._LETTER_IN_WRONG_PLACE):
                        return False
                else:
                    # Check if we already know which letter should be here
                    if guess.hints[i] == guess._LETTER_CORRECT:
                        return False
        
        return True
    
    def get_valid_answers(self) -> List[str]:
        """Get a list of all possible solutions to this Wordle based on all
        known hints

        Returns:
            List[str]: A list containing all valid Wordle words which adhere to
            all hints from current guesses
        """
        valid_answers = []
        for answer in self.answers:
            if self._check_new_guess(answer):
                valid_answers.append(answer)
                
        return valid_answers

        
if __name__ == '__main__':
    sys.exit(gui.app.exec())