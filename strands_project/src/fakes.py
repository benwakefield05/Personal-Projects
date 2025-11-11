"""
Game logic for Milestone 1:
Pos, StrandFake, BoardFake, StrandsGameFake
"""

"""
Abstract base classes for Strands game.

There are four ABCs:
- PosBase, which represents positions,
- StrandBase, which represents individual strands,
- BoardBase, which represents boards for the game, and
- StrandsGameBase, which represents the game logic.

Throughout the implementation, PosBase values consist
of 0-indexed Row and Col values.

Do not modify this file.
"""
from abc import ABC, abstractmethod
from enum import Enum
from typing import TypeAlias
from base import PosBase, StrandBase, BoardBase, StrandsGameBase, Step
from collections import defaultdict

usable_words = defaultdict(lambda: defaultdict(list))
with open('assets/web2.txt') as file:
    for line in file:
        word = line.strip()
        if len(word) > 3:
            first = word[0].lower()
            first_two = word[:2].lower()
            usable_words[first][first_two].append(word)

Row: TypeAlias = int
Col: TypeAlias = int


######################################################################


class Pos(PosBase):
    """
    Positions on a board, represented as pairs of 0-indexed
    row and column integers. Position (0, 0) corresponds to
    the top-left corner of a board, and row and column
    indices increase down and to the right, respectively.
    """
    DIRECTIONS: dict[Step, tuple[int, int]] = {
        'n' : (-1, 0),
        's' : (1, 0),
        'e': (0, 1), 
        'w' : (0, -1),
        'nw' : (-1, -1), 
        'ne' : (-1, 1), 
        'se' : (1, 1),
        'sw' : (1, -1)
    }

    def take_step(self, step: Step) -> "Pos":
        """
        Compute the position that results from starting at
        the current position and taking the specified step.
        """
        row_move, col_move = self.DIRECTIONS[step.value]
        return Pos(self.r + row_move, self.c + col_move)

    def step_to(self, other: "Pos") -> Step:
        """
        Compute the difference in two positions, represented
        as a step from the current position to the other.

        Raises ValueError if the other position is more
        than two steps away from self.
        """
        row_move = other.r - self.r
        col_move = other.c - self.c
        for direction, (dir_row, dir_col) in self.DIRECTIONS.items():
            if (dir_row, dir_col) == (row_move, col_move):
                return Step(direction)
        raise ValueError
    
    def is_adjacent_to(self, other: "Pos") -> bool:
        """
        Decide whether or not the two positions are
        neighbors (that is, connected by a single step).
        """
        try:
            return self.step_to(other) in self.directions
        except ValueError:
            return False

    def __eq__(self, other: object) -> bool:
        """
        Decide whether or not two positions have
        equal row and column values.

        Raises NotImplementedError if other is not
        a position.
        """
        if isinstance(other, Pos):
            return self.r == other.r and self.c == other.c
        else:
            return False

    def __str__(self) -> str:
        """
        Display the position as a string.
        """
        return f"({self.r}, {self.c})"


######################################################################


class StrandFake(StrandBase):
    """
    Strands, represented as a start position
    followed by a sequence of steps.
    """

    def positions(self) -> list[Pos]:
        """
        Compute the absolute positions represented by the
        strand. These positions are independent of any
        particular board size. That is, the resulting
        positions assume a board of infinite size in all
        directions.
        """
        positions_list = []
        positions_list.append(self.start)
        current_location = self.start
        for step in self.steps:
            new_location = current_location.take_step(step)
            positions_list.append(new_location)
            current_location = new_location
        return positions_list
    
    def is_cyclic(self) -> bool:
        """
        Decide whether or not the strand is cyclic. That is,
        check whether or not any position appears multiple
        times in the strand.
        """
        raise NotImplementedError

    def is_folded(self) -> bool:
        """
        Decide whether or not the strand is folded. That is,
        check whether or not any connection in the strand
        crosses over another connection in the strand.
        """
        raise NotImplementedError

    def __eq__(self, other: object) -> bool:
        """
        Decide whether or not two strands have
        equal start and steps values.

        Raises NotImplementedError if other is not
        a strand.
        """
        if isinstance(other, StrandFake):
            return self.start == other.start and self.steps == other.steps
        else:
            raise NotImplementedError


######################################################################


class BoardFake(BoardBase):
    """
    Boards for the Strands game, consisting of a
    rectangular grid of letters.
    """

    letters: list[list[str]]

    def __init__(self, letters: list[list[str]]):
        """
        Constructor

        The two-dimensional matrix of strings (letters)
        is valid if (a) each row is non-empty and has
        the same length as other rows, and (b) each string
        is a single, lowercase, alphabetical character.

        Raises ValueError if the matrix is invalid.
        """
        self.board = letters

    def num_rows(self) -> int:
        """
        Return the number of rows on the board.
        """
        return len(self.board)

    def num_cols(self) -> int:
        """
        Return the number of columns on the board.
        """
        return len(self.board[0])

    def get_letter(self, pos: Pos) -> str:
        """
        Return the letter at a given position on the board.

        Raises ValueError if the position is not within the
        bounds of the board.
        """
        row_num = pos.r
        col_num = pos.c
        return self.board[row_num][col_num]

    def evaluate_strand(self, strand: StrandFake) -> str:
        """
        Evaluate a strand, returning the string of
        corresponding letters from the board.

        Raises ValueError if any of the strand's positions
        are not within the bounds of the board.
        """
        strand_word = ''
        for position in strand.positions():
            strand_word += self.get_letter(position)
        return strand_word
        


######################################################################


class StrandsGameFake(StrandsGameBase):
    """
    Abstract base class for Strands game logic.
    """

    game_file: list[str]
    board_start: int
    answers_start: int
    strands_found: list[StrandFake]
    threshold_hint: int
    meter_hint: int
    hint_active: None | tuple[int, bool]

    def __init__(self, game_file: str | list[str], hint_threshold: int = 3):
        """
        Constructor

        Load the game specified in a given file, and set
        a particular threshold for giving hints. The game
        file can be specified either as a string filename,
        or as the list of lines that result from calling
        readlines() on the file.

        Raises ValueError if the game file is invalid.

        Valid game files include:

          1. a theme followed by a single blank line, then

          2. multiple lines defining the board followed
             by a single blank line, then

          3. multiple lines defining the answers,
             optionally followed by

          4. a blank line and then any number of remaining
             lines which have no semantic meaning.

        Valid game files require:

          - boards to be rectangular

          - boards where each string is a single,
            alphabetical character (either upper- or
            lower case; for example, both "a" and "A"
            denote the same letter, which is stored
            as "a" in the board object)

          - each line for an answer of the form
            "WORD R C STEP1 STEP2 ..." where
              * WORD has at least three letters,
              * the position (R, C) is within bounds
                of the board,
              * the positions implied by the steps are
                all within bounds of the board, and
              * the letters implied by the strand
                spell the WORD (modulo capitalization)
              * the WORDs and STEPs may be spelled with
                either lower- or uppercase letters, but
                regardless the WORDs are stored in the
                game object with only lowercase letters.

           - that each answer strand has no folds
             (edges do not cross)

           - that answers fill the board

        Game files are allowed to use multiple space
        characters to separate tokens on a line. Also,
        leading and trailing whitespace will be ignored.
        """
        if isinstance(game_file, str):
            with open(game_file) as file:
                self.game_file = [line.strip() for line in file.readlines()]
        else:
            self.game_file = [line.strip() for line in game_file]

        num_empty_rows = 0
        check = 0
        for line_num, line in enumerate(self.game_file):
            if not line:
                num_empty_rows += 1
            if num_empty_rows == 1 and check == 0:
                self.board_start = line_num + 1
                check += 1
            elif num_empty_rows == 2:
                self.answers_start = line_num + 1
                break

        self.strands_found = []
        self.threshold_hint = hint_threshold
        self.hint_active = None
        self.meter_hint = 0
        self.attempted_non_strands = []

    def theme(self) -> str:
        """
        Return the theme for the game.
        """
        theme = self.game_file[0]
        theme = theme.lstrip()
        return theme

    def board(self) -> BoardFake:
        """
        Return the board for the game.
        """
        final_board = []
        for row in self.game_file[self.board_start:]:
            if not row:
                break
            row = row.replace(' ', '')
            row = row.lower()
            final_row = []
            for letter in row:
                final_row.append(letter)
            final_board.append(final_row)
        return BoardFake(final_board)

    def answers(self) -> list[tuple[str, StrandFake]]:
        """
        Return the answers for the game. Each answer
        is a pair comprising a theme word and the
        corresponding strand on the board. Words are
        stored using lowercase letters, even if the
        game file used uppercase letters.
        """
        answer_list = []
        for answer in self.game_file[self.answers_start:]:
            answer = answer.lower()
            answer = answer.split()
            if not answer:
                break
            ansr_name = []
            ansr_direct = []
            position = []
            int_count = 0
            for character in answer:
                try:
                    character = int(character)
                except ValueError:
                    pass
                if type(character) is str:
                    if int_count == 0:
                        ansr_name.append(character)
                    if int_count == 2:
                        ansr_direct.append(Step(character))
                else:
                    position.append(character)
                    int_count += 1
            strand_fake = StrandFake(Pos(position[0] - 1, position[1] - 1), ansr_direct)
            answer_list.append((''.join(ansr_name), strand_fake))
        return answer_list
    
    def found_strands(self) -> list[StrandFake]:
        """
        Return the theme words that have been found so far,
        represented as strands. The order of strands in the
        output matches the order in which they were found.

        Note two strands may conflict, meaning they involve
        different sequences of steps yet identify the same
        absolute positions on the board. This method returns
        the strands that have been submitted through the
        user interface (i.e. submit_strand) and thus may
        deviate from the strands stored in answers.
        """
        return self.strands_found

    def game_over(self) -> bool:
        """
        Decide whether or not the game is over, which means
        checking whether or not all theme words have been
        found.
        """
        if len(self.answers()) == len(self.strands_found):
            return True
        return False

    def hint_threshold(self) -> int:
        """
        Return the hint threshold for the game.
        """
        return self.threshold_hint

    def hint_meter(self) -> int:
        """
        Return the current hint meter for the game.
        If it is greater than or equal to the hint
        threshold, then the user can request a hint.
        """
        return self.meter_hint

    def active_hint(self) -> None | tuple[int, bool]:
        """
        Return the active hint, if any.

        Returns None:
            if there is no active hint.

        Returns (i, False):
            if the active hint corresponds to the ith answer
            in the list of answers, but the start and end
            positions _should not_ be shown to the user.

        Returns (i, True):
            if the active hint corresponds to the ith answer
            in the list of answers, and the start and end
            positions _should_ be shown to the user.
        """
        return self.hint_active

    def submit_strand(self, strand: StrandFake) -> tuple[str, bool] | str:
        """
        Play a selected strand.

        Returns (word, True):
            if the strand corresponds to a theme word which
            has not already been found.

        Returns (word, False):
            if the strand does not correspond to a theme
            word but does correspond to a valid dictionary
            word that has not already been found.

        Returns "Already found":
            if the strand corresponds to a theme word or
            dictionary word that has already been found.

        Returns "Too short":
            if the strand corresponds to fewer than four
            letters.

        Returns "Not in word list":
            if the strand corresponds to a string that
            is not a valid dictionary word.
        """
        if len(strand.positions()) < 4:
            return 'Too short'
        for answer in self.answers():
            word, answer_strand = answer
            if answer_strand.positions() == strand.positions():
                if strand in self.strands_found:
                    return 'Already found'
                self.strands_found.append(strand)
                self.hint_active = None
                return (word, True)
        strand_word = self.board().evaluate_strand(strand)
        if self.try_to_find_word(strand_word):
            if strand_word in self.attempted_non_strands:
                return 'Already found'
            else:
                self.meter_hint += 1
                self.attempted_non_strands.append(strand_word)
                return(word, False)
        return 'Not a valid word'
    
    def try_to_find_word(self, word):
        first = word[0]
        first_two = word[:2]
        check = usable_words[first]
        check_two = check[first_two]
        if word in check_two:
            return True
        return False

    def use_hint(self) -> tuple[int, bool] | str:
        """
        Play a hint.

        Returns (i, b):
            if successfully updated the active hint. The new
            hint corresponds to the ith answer in the list of
            all answers, which is the first answer that has
            not already been found. The boolean b describes
            whether there was already an active hint before
            this call to use_hint (and thus whether or not the
            first and last letters of the hint word should be
            highlighted).

        Returns "No hint yet":
            if the current hint meter does not yet warrant
            a hint.

        Returns "Use your current hint":
            if there is already an active hint where the
            first and last letters are being displayed.
        """
        if self.meter_hint >= self.threshold_hint:
            if self.hint_active is None:
                for num_answer, answer in enumerate(self.answers()):
                    _, strand = answer
                    check = False
                    for found_strand in self.strands_found:
                        if found_strand.start == strand.start:
                            check = True
                    if not check:        
                        self.hint_active = (num_answer, False)
                        return (num_answer, False)
            answer_num, boolean = self.hint_active
            if not boolean:
                self.hint_active = (answer_num, True)
                return (answer_num, True)
            if boolean:
                return 'Use your current hint'
        return 'No hint yet'
        