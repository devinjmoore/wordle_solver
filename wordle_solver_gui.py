import sys
from PySide6 import QtCore, QtGui, QtWidgets

from wordle_solver import Wordle, WordleSolver

_COLOR_LETTER_NOT_IN_WORD = "#202020"
_COLOR_LETTER_CORRECT = "#009600"
_COLOR_LETTER_WRONG_PLACE = "#ffc425"

class LetterTile(QtWidgets.QPushButton):
    
    _STYLE_HIGHLIGHTED = "border-color: white; border-width: 2px;"

    letter_clicked = QtCore.Signal(QtWidgets.QPushButton)
    hint_changed = QtCore.Signal(QtWidgets.QPushButton)

    def __init__(self, parent) -> None:
        super().__init__(parent=parent)

        self.line_number:int = None
        self.letter_index:int = None

    def _change_style_property(self, property: str, value: str) -> None:
        stylesheet = self.styleSheet().split()
        value_index = stylesheet.index(property + ':') + 1
        stylesheet[value_index] = value + ';'
        self.setStyleSheet(' '.join(stylesheet))

    def change_bg_color(self, color: str):
        self._change_style_property("background-color", color)

    def hint(self) -> bool:
        stylesheet = self.styleSheet().split()
        
        letter_color = stylesheet[stylesheet.index("background-color:") + 1].strip(';')
        if letter_color == _COLOR_LETTER_CORRECT:
            return Wordle.Guess._LETTER_CORRECT
        elif letter_color == _COLOR_LETTER_WRONG_PLACE:
            return Wordle.Guess._LETTER_WRONG_PLACE
        else:
            return Wordle.Guess._LETTER_NOT_IN_WORD
        
    def is_empty(self) -> bool:
        return self.text() == ''

    def mousePressEvent(self, e: QtGui.QMouseEvent) -> None:
        self.hint_changed.emit(self)
        self.letter_clicked.emit(self)

    def setHighlight(self, active: bool) -> None:
        if active:
            self.setStyleSheet(self.styleSheet() + ' ' + self._STYLE_HIGHLIGHTED)
        else:
            self.setStyleSheet(
                self.styleSheet().replace(self._STYLE_HIGHLIGHTED, "")
            )


class WordleSolverGUI(QtWidgets.QWidget):
    _APP_WIDTH = 500
    _APP_HEIGHT = 600
    _LETTER_WIDTH = 100
    _LETTER_HEIGHT = 100

    _LENGTH_ROW = 5
    _NUM_ROWS = 5
    _COLOR_LETTER_NOT_ENTERED = "#121213"

    _RESULTS_VIEWER_GEOMETRY = QtCore.QRect(0, 0, _APP_WIDTH, _APP_WIDTH)
    _SUBMIT_BUTTON_GEOMETRY = QtCore.QRect(
        _APP_WIDTH / 2 - (3 * _LETTER_WIDTH / 2),
        _NUM_ROWS * _LETTER_HEIGHT + _LETTER_HEIGHT / 4,
        3 * _LETTER_WIDTH,
        _LETTER_HEIGHT / 2
    )

    def __init__(self) -> None:
        super().__init__()

        # region Initialize widget layout
        self.setStyleSheet(
            "QPushButton {background-color: #101010; font: 48pt \"Arial\";"
            "border-style: solid; border-width: 3px; border-color: black;}"
        )
        self.setGeometry(500, 300, self._APP_WIDTH, self._APP_HEIGHT)
        # endregion

        # region Initialize letter grid layout
        self.letter_grid = [
            [LetterTile(self) for j in range(self._LENGTH_ROW)]
            for i in range(self._NUM_ROWS)
        ]
        # endregion

        # region Configure each letter tile
        for i in range(self._NUM_ROWS):
            for j in range(self._LENGTH_ROW):
                letter = self.letter_grid[i][j]
                letter.setGeometry(
                    self._LETTER_WIDTH * j,
                    self._LETTER_HEIGHT * i,
                    self._LETTER_WIDTH,
                    self._LETTER_HEIGHT
                )
                letter.line_number = i
                letter.letter_index = j

                letter.setStyleSheet(
                    f"background-color: {self._COLOR_LETTER_NOT_ENTERED};"
                )

                letter.letter_clicked.connect(self._move_cursor_to_letter)
                letter.hint_changed.connect(self._cycle_through_hints)
        # endregion
        
        # region Initialize results viewer
        self.results = QtWidgets.QPlainTextEdit(self)
        self.results.setGeometry(self._RESULTS_VIEWER_GEOMETRY)
        self.results.setReadOnly(True)
        self.results.hide()
        self.results_showing = False
        # endregion

        # region Initialize submit button
        self.submit_button = QtWidgets.QPushButton(self)
        self.submit_button.setText("Get Solutions")
        self.submit_button.setGeometry(self._SUBMIT_BUTTON_GEOMETRY)
        self.submit_button.setStyleSheet("font: 24pt Arial; color: white;")
        self.submit_button.clicked.connect(self._submit_guesses)
        # endregion

        # region Initialize the user's grid cursor
        self.letter_cursor = [0, 0]
        self._current_letter().setHighlight(True)
        # endregion
        
        self.show()

    @QtCore.Slot(LetterTile)
    def _cycle_through_hints(self, letter:LetterTile) -> None:
        if letter.is_empty():
            return
        
        letter_style = letter.styleSheet()
        if _COLOR_LETTER_CORRECT in letter_style:
            letter.change_bg_color(_COLOR_LETTER_WRONG_PLACE)
        elif _COLOR_LETTER_WRONG_PLACE in letter_style:
            letter.change_bg_color(_COLOR_LETTER_NOT_IN_WORD)
        else:
            letter.change_bg_color(_COLOR_LETTER_CORRECT)

    def _delete_current_letter(self) -> None:
        self._current_letter().setText('')
        self._current_letter().change_bg_color(self._COLOR_LETTER_NOT_ENTERED)


    def _move_cursor(move_cursor_in_a_direction):
        def wrapper(*args, **kwargs):
            self: WordleSolverGUI = args[0]

            self._current_letter().setHighlight(False)

            if len(args) == 1:
                move_cursor_in_a_direction(gui)
            else:
                letter: LetterTile = args[1]
                move_cursor_in_a_direction(gui, letter)

            gui._current_letter().setHighlight(True)
        return wrapper

    @_move_cursor
    def _move_cursor_up(self) -> None:
        if self.letter_cursor[0] > 0:
            self.letter_cursor[0] -= 1

    @_move_cursor
    def _move_cursor_down(self) -> None:
        if self.letter_cursor[0] < len(self.letter_grid) - 1:
            self.letter_cursor[0] += 1

    @_move_cursor
    def _move_cursor_left(self) -> None:
        if self.letter_cursor == [0,0]:
            return
        if self.letter_cursor[1] > 0:
            self.letter_cursor[1] -= 1
        else:
            current_line = self.letter_grid[self.letter_cursor[0]]
            self.letter_cursor[1] = len(current_line) - 1
            self._move_cursor_up()

    @_move_cursor
    def _move_cursor_right(self) -> None:
        current_line = self.letter_grid[self.letter_cursor[0]]
        if self.letter_cursor == [
            len(self.letter_grid) - 1,
            len(current_line) - 1
        ]:
            return
        if self.letter_cursor[1] < len(current_line) - 1:
            self.letter_cursor[1] += 1
        else:
            self.letter_cursor[1] = 0
            self._move_cursor_down()

    @_move_cursor
    @QtCore.Slot(LetterTile)
    def _move_cursor_to_letter(self, letter: LetterTile) -> None:
        self.letter_cursor = [letter.line_number, letter.letter_index]

    def _submit_guesses(self):
        # Create a list of Wordle Guesses for the Wordle object
        guesses = []
        for row in self.letter_grid:
            if row[0].is_empty():
                break
            word = ''.join([letter.text() for letter in row])
            hints = [letter.hint() for letter in row]
            guesses.append(Wordle.Guess(word, hints))
            
        wordle = Wordle(guesses)
        wordle_solver = WordleSolver(wordle)
        solutions = wordle_solver.get_valid_answers()
        
        self.results.setPlainText("Possible Solutions: " + repr(solutions))
        self.results.show()
        
        self.results_showing = True

    def _current_letter(self) -> LetterTile:
        return self.letter_grid[self.letter_cursor[0]][self.letter_cursor[1]]

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        if self.results_showing:
            self.results.hide()
            self.results_showing = False
            return
        
        key = event.key()
        if event.text().isalpha():
            if self._current_letter().is_empty():
                self._current_letter().change_bg_color(_COLOR_LETTER_NOT_IN_WORD)
            self._current_letter().setText(event.text().upper())
            self._move_cursor_right()
        elif key == QtCore.Qt.Key_Backspace:
            if self._current_letter().is_empty():
                self._move_cursor_left()
                self._delete_current_letter()
            else:
                self._delete_current_letter()
                self._move_cursor_left()
        elif key == QtCore.Qt.Key_Up:
            self._move_cursor_up()
        elif key == QtCore.Qt.Key_Down:
            self._move_cursor_down()
        elif key == QtCore.Qt.Key_Left:
            self._move_cursor_left()
        elif key == QtCore.Qt.Key_Right:
            self._move_cursor_right()
        elif key == QtCore.Qt.Key_Space:
            self._current_letter().hint_changed.emit(self._current_letter())
        elif key in [QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return]:
            self._submit_guesses()


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    gui = WordleSolverGUI()
    sys.exit(app.exec())