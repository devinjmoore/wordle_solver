from typing import List
from wordle_answers import ALL_WORDLE_ANSWERS


class Wordle:
    class Guess:
        """A class to represent an incorrect guess in a Wordle game. A guess
        object contains the word which was guessed along with a list of five
        bools. These bools indicate whether the corresponding letter in the word
        is
            a. in the solution and in the correct place (True)
            b. in the solution, but in the wrong place (False)
            a. not in the solution at all (None)
        """
        _LETTER_NOT_IN_WORD = None
        _LETTER_CORRECT = True
        _LETTER_WRONG_PLACE = False
        
        def __init__(self, word: str, hints: List[bool]) -> None:
            self.word = word
            self.hints = hints

    def __init__(self, guesses_made) -> None:
        self.guesses_made: List[Wordle.Guess] = guesses_made
        
    def get_guesses_made(self) -> List[Guess]:
        return self.guesses_made


class WordleSolver:
    _LEN_GUESS = 5

    def __init__(self, wordle: Wordle) -> None:
        self.wordle = wordle

    def _check_solution(self, solution: str) -> bool:
        """
        Args:
            solution (str): The proposed Wordle solution

        Returns:
            bool: Indicates if a proposed solution follows all known hints in
            this Wordle
        """

        # Check that the solution utilizes all the hints from previous guesses
        for guess in self.wordle.get_guesses_made():
            # Check letter by letter
            for i in range(self._LEN_GUESS):
                if guess.hints[i] == guess._LETTER_CORRECT:
                    # Verify that the solution uses the correct letter here
                    if solution[i] != guess.word[i]:
                        return False

                elif guess.hints[i] == guess._LETTER_WRONG_PLACE:
                    # region Verify that the solution uses this letter
                    letter_match_indices = [
                        index for (index, letter) in enumerate(solution)
                        if letter == guess.word[i]
                    ]
                    
                    # Remove indices of already-correct letters
                    for index in letter_match_indices:
                        if guess.hints[index] == guess._LETTER_CORRECT:
                            letter_match_indices.remove(index)

                    if not len(letter_match_indices) > 0:
                        return False
                    # endregion

                    # Verify that the solution only uses this letter elsewhere
                    if solution[i] == guess.word[i]:
                        return False

                elif guess.hints[i] == guess._LETTER_NOT_IN_WORD:
                    # Verify that the solution does not contain this letter
                    if guess.word[i] in solution:
                        return False

        return True

    def get_valid_answers(self) -> List[str]:
        """
        Returns:
            List[str]: A list of all possible solutions to this Wordle which
            utilize all known hints
        """
        valid_answers = []
        for answer in ALL_WORDLE_ANSWERS:
            if self._check_solution(answer):
                valid_answers.append(answer)

        return valid_answers
