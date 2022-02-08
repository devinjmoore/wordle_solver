from typing import List
from PySide6 import QtCore, QtGui, QtWidgets

_COLOR_LETTER_CORRECT = "#009600"
_COLOR_LETTER_WRONG_PLACE = "#ffc425"
_COLOR_LETTER_NOT_IN_WORD = "#202020"
_COLOR_LETTER_NOT_ENTERED = "#121213"


class LetterTile(QtWidgets.QPushButton):
    _STYLE_HIGHLIGHTED = "border-color: white; border-width: 2px;"

    letter_clicked = QtCore.Signal(QtWidgets.QPushButton)
    change_hint = QtCore.Signal(QtWidgets.QPushButton)

    def __init__(self, parent) -> None:
        super().__init__(parent=parent)

        self.line_number:int = None
        self.letter_index:int = None

    def _change_style_property(self, property: str, value: str) -> None:
        stylesheet = self.styleSheet().split()
        value_index = stylesheet.index(property + ':') + 1
        stylesheet[value_index] = value + ';'
        self.setStyleSheet(' '.join(stylesheet))

    def change_background_color(self, color: str):
        self._change_style_property("background-color", color)

    def clear(self) -> None:
        self.setText("")
        self.change_background_color()

    def is_empty(self) -> bool:
        return self.text() == ''

    def mousePressEvent(self, e: QtGui.QMouseEvent) -> None:
        self.change_hint.emit(self)
        self.letter_clicked.emit(self)

    def setHighlight(self, active: bool) -> None:
        if active:
            self.setStyleSheet(self.styleSheet() + ' ' + self._STYLE_HIGHLIGHTED)
        else:
            self.setStyleSheet(
                self.styleSheet().replace(self._STYLE_HIGHLIGHTED, "")
            )
        pass


class WordleSolverGUI(QtWidgets.QWidget):
    _APP_WIDTH = 500
    _APP_HEIGHT = 600
    _LETTER_WIDTH = 100
    _LETTER_HEIGHT = 100

    _LETTER_LINE_LENGTH = 5
    _NUM_LETTER_LINES = 5

    _SUBMIT_BUTTON_GEOMETRY = QtCore.QRect(
        _APP_WIDTH / 2 - (3 * _LETTER_WIDTH / 2),
        _NUM_LETTER_LINES * _LETTER_HEIGHT + _LETTER_HEIGHT / 4,
        3 * _LETTER_WIDTH,
        _LETTER_HEIGHT / 2
    )

    def __init__(self) -> None:
        super().__init__()

        # region Initialize widget layout
        self.setStyleSheet(open("stylesheet.txt").read())
        self.setGeometry(500, 300, self._APP_WIDTH, self._APP_HEIGHT)
        # endregion

        # region Initialize letter grid layout
        self.letter_lines = [
            [
                LetterTile(self) for j in range(self._LETTER_LINE_LENGTH)
            ] for i in range(self._NUM_LETTER_LINES)
        ]
        # endregion

        # region Configure each letter tile
        for i in range(len(self.letter_lines)):
            for j in range(len(self.letter_lines[i])):
                letter = self.letter_lines[i][j]
                letter.setGeometry(
                    self._LETTER_WIDTH * j,
                    self._LETTER_HEIGHT * i,
                    self._LETTER_WIDTH,
                    self._LETTER_HEIGHT
                )
                letter.line_number = i
                letter.letter_index = j

                letter.setStyleSheet(f"background-color: {_COLOR_LETTER_NOT_ENTERED};")

                letter.letter_clicked.connect(self._move_cursor_to_letter)
                letter.change_hint.connect(self._cycle_through_hints)
        # endregion

        # region Initialize submit button
        self.submit_button = QtWidgets.QPushButton(
            text="Submit Guesses",
            parent=self
        )
        self.submit_button.setGeometry(self._SUBMIT_BUTTON_GEOMETRY)
        self.submit_button.setStyleSheet("font: 24pt Arial; color: white;")
        # endregion

        # region Initialize the user cursor
        self.letter_cursor = [0, 0]
        self.current_letter().setHighlight(True)
        # endregion
        
        self.show()

    @QtCore.Slot(LetterTile)
    def _cycle_through_hints(self, letter:LetterTile) -> None:
        if letter.is_empty():
            return
        letter_style = letter.styleSheet()
        if _COLOR_LETTER_CORRECT in letter_style:
            letter.change_background_color(_COLOR_LETTER_WRONG_PLACE)
        elif _COLOR_LETTER_WRONG_PLACE in letter_style:
            letter.change_background_color(_COLOR_LETTER_NOT_IN_WORD)
        else:
            letter.change_background_color(_COLOR_LETTER_CORRECT)

    def _delete_current_letter(self) -> None:
        self.current_letter().setText('')
        self.current_letter().change_background_color(
            _COLOR_LETTER_NOT_ENTERED
        )


    def _move_cursor(move_cursor_in_a_direction):
        def wrapper(*args, **kwargs):
            gui: WordleSolverGUI = args[0]

            gui.current_letter().setHighlight(False)

            if len(args) == 1:
                move_cursor_in_a_direction(gui)
            else:
                letter: LetterTile = args[1]
                move_cursor_in_a_direction(gui, letter)

            gui.current_letter().setHighlight(True)
        return wrapper

    @_move_cursor
    def _move_cursor_up(self) -> None:
        if self.letter_cursor[0] > 0:
            self.letter_cursor[0] -= 1

    @_move_cursor
    def _move_cursor_down(self) -> None:
        if self.letter_cursor[0] < len(self.letter_lines) - 1:
            self.letter_cursor[0] += 1

    @_move_cursor
    def _move_cursor_left(self) -> None:
        if self.letter_cursor == [0,0]:
            return
        if self.letter_cursor[1] > 0:
            self.letter_cursor[1] -= 1
        else:
            current_line = self.letter_lines[self.letter_cursor[0]]
            self.letter_cursor[1] = len(current_line) - 1
            self._move_cursor_up()

    @_move_cursor
    def _move_cursor_right(self) -> None:
        current_line = self.letter_lines[self.letter_cursor[0]]
        if self.letter_cursor == [
            len(self.letter_lines) - 1,
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


    def current_letter(self) -> LetterTile:
        return self.letter_lines[self.letter_cursor[0]][self.letter_cursor[1]]

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        key = event.key()
        if event.text().isalpha():
            if self.current_letter().is_empty():
                self.current_letter().change_background_color(
                    _COLOR_LETTER_NOT_IN_WORD
                )
            self.current_letter().setText(event.text().upper())
            self._move_cursor_right()
        elif key == QtCore.Qt.Key_Backspace:
            if self.current_letter().is_empty():
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
            self.current_letter().change_hint.emit(self.current_letter())
        elif key == QtCore.Qt.Key_Enter:
            self.submit_button.clicked.emit()

    def letter_grid(self) -> List[List[str]]:
        return [
            [
                letter.text() for letter in self.letter_lines[i]
            ] for i in range(self._NUM_LETTER_LINES)
        ]

app = QtWidgets.QApplication([])
gui = WordleSolverGUI()
