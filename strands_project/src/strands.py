from abc import ABC, abstractmethod
from enum import Enum
from typing import TypeAlias
from base import PosBase, StrandBase, BoardBase, StrandsGameBase, Step
from collections import defaultdict

usable_words: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
with open('assets/web2.txt') as file:
    for line in file:
        word = line.strip()
        if len(word) > 3:
            first = word[0].lower()
            first_two = word[:2].lower()
            usable_words[first][first_two].append(word)

Row: TypeAlias = int
Col: TypeAlias = int
"""
Create a file with four classes, Pos, Strand, Board, and
StrandsGame that inherit from the corresponding base classes.
"""
class Pos(PosBase):

    DIRECTIONS: dict[str, tuple[int, int]] = {
        'n' : (-1, 0),
        's' : (1, 0),
        'e': (0, 1), 
        'w' : (0, -1),
        'nw' : (-1, -1), 
        'ne' : (-1, 1), 
        'se' : (1, 1),
        'sw' : (1, -1)
    }
    def __init__(self, r: int, c: int) -> None:
        super().__init__(r, c)

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
        try:
            return self.step_to(other) in self.DIRECTIONS
        except ValueError:
            return False

class Strand(StrandBase):
    def __init__(self, start: Pos, steps: list[Step]) -> None:
        super().__init__(start, steps)

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
        visited: set[tuple[int,int]] = set()
        cur = self.start
        visited.add((cur.r, cur.c))
        for step in self.steps:
            cur = cur.take_step(step)
            key = (cur.r, cur.c)
            if key in visited:
                return True
            visited.add(key)
        return False

    def is_folded(self) -> bool:
        """
        Decide whether or not the strand is folded. That is,
        check whether or not any connection in the strand
        crosses over another connection in the strand.
        """
        if len(self.steps) < 2:
            return False
        pos_list: list[Pos] = [self.start]
        cur = self.start
        for st in self.steps:
            cur = cur.take_step(st)
            pos_list.append(cur)

        mids: list[tuple[float, float]] = []
        for k in range(len(pos_list) - 1):
            cur = pos_list[k]
            next = pos_list[k + 1]
            mids.append(((cur.r + next.r) / 2.0, (cur.c + next.c) / 2.0))

        # now there's a complete list of mid point of every 2
        # adjacent edges
        # For 2 different edges, 
        # if 2 mid points are the same, there's a cross
        # between diagonal path
        # this is valid because the diagonal path can only 
        # go to NE,SE,NW and SW

        for i, m1 in enumerate(mids):
            # check the edges that are at leeast 2 letters away
            # so that we are not counting the same edge
            # or 2 edges with a communal letter vertex
            for j in range(i+2, len(mids)):
                if m1 == mids[j]:
                    return True         
        return False

class Board(BoardBase):
    def __init__(self, letters: list[list[str]]):
        """
        Furthermore, the constructor should now check 
        whether the input game file represents a valid 
        Strands board. If not, you should explicitly raise 
        ValueError exceptions.
        """
        if not letters:
            raise ValueError("There's no letters")
        
        # check that every line has same length,
        # and the elements are letter in letters
        first_len = len(letters[0])
        for row in letters:
            if len(row) != first_len:
                raise ValueError("length of rows don't match")
            
            for elem in row:
                if len(elem) != 1 or not elem.isalpha():
                    raise ValueError
                
        # store the board
        self._rows = []
        for row in letters:
            new_row = []
            for elem in row:
                new_row.append(elem.lower())
            self._rows.append(new_row)

    def num_rows(self) -> int:
        return len(self._rows)

    def num_cols(self) -> int:
        return len(self._rows[0])

    def get_letter(self, pos: Pos) -> str:
        # check if the position is in bound
        if pos.r < 0 or pos.r >= len(self._rows):
            raise ValueError("p out of bounds")
        if pos.c < 0 or pos.c >= len(self._rows[pos.r]):
            raise ValueError("p out of bounds")
        return self._rows[pos.r][pos.c]

    def evaluate_strand(self, strand: Strand) -> str:
        letters: list[str] = []
        positions = strand.positions()    
        for pos in positions:
            '''
            if not (0 <= pos.r < self.num_rows()):
                raise ValueError("Position row out of bounds")
            if not (0 <= pos.c < self.num_cols()):
                raise ValueError("Position col out of bounds")
            '''
            letter = self.get_letter(pos).lower()
            letters.append(letter)

        result = ""
        for ch in letters:
            result += ch
        return result

class StrandsGame(StrandsGameBase):
    def __init__(self, game_file: str | list[str], hint_threshold: int = 3):

        if isinstance(game_file, str):
            with open(game_file) as file:
                raw_lines = file.readlines()
        else:
            raw_lines = game_file

        self.game_file: list[str] = []
        for ln in raw_lines:
            self.game_file.append(ln.rstrip("\n"))
        # now, the lines are handled

        num_empty_rows = 0
        check_flag = 0
        self.board_start = None
        self.answers_start = None

        for line_num, line in enumerate(self.game_file):
            if line.strip() == "":
                num_empty_rows += 1

            if num_empty_rows == 1 and check_flag == 0:
                # first time seeing an empty row, 
                # next line should be board
                self.board_start = line_num + 1
                check_flag = 1
            
            elif num_empty_rows == 2:
                # similarly, but next line is answer
                self.answers_start = line_num + 1
                break

        # 1. handle theme
        self.theme_line = self.game_file[0].strip()
        if self.theme_line == "":
            raise ValueError("Theme line is empty")
        
        # 2. lack enough blank rows, raise value error
        if self.board_start is None or self.answers_start is None:
            raise ValueError("Game file missing blank-line separators")

        self._board = self.board()

        answer_lines: list[str] = []
        i_ans = self.answers_start
        while i_ans < len(self.game_file) and self.game_file[i_ans].strip() != "":
            answer_lines.append(self.game_file[i_ans])
            i_ans += 1

        if len(answer_lines) == 0:
            raise ValueError("Answers block is empty")

        self._answers: list[tuple[str, Strand]] = []

        for ln in answer_lines:
            toks = ln.split()
            if len(toks) < 4:
                # we need at least answer, 2 start positions
                # and a step at least
                raise ValueError("No enough elements in Answer")

            word = toks[0].lower()

            r = int(toks[1]) - 1
            c = int(toks[2]) - 1
            # check if any strand has out of bound element
            steps = [Step(tok.lower()) for tok in toks[3:]]
            strand = Strand(Pos(r, c), steps)

            spelled = self._board.evaluate_strand(strand)
            if spelled != word:
                raise ValueError("Wrong Spelling!")
            if strand.is_folded():
                raise ValueError("No Folding!")

            self._answers.append((word, strand))

        self.strands_found: list[Strand] = []
        self.threshold_hint = hint_threshold
        self.hint_active: None | tuple[int, bool] = None
        self.meter_hint = 0
        self.attempted_non_strands = []

    def theme(self) -> str:
        """
        Return the theme for the game.
        """
        # debugged: strip the """ mark
        return self.theme_line.strip().strip('"')

    def board(self) -> Board:
        """
        Return the board for the game.
        """
        final_board = []
        for row in self.game_file[self.board_start:]:
            if row.strip() == "":
                break
            # drop all spaces, lowercase, split into letters
            tokens = row.split()
            clean_row = [token.lower() for token in tokens if token.isalpha()]
            final_board.append(clean_row)
        return Board(final_board)
    
    def answers(self) -> list[tuple[str, Strand]]:
        """
        Return the answers for the game. Each answer
        is a pair comprising a theme word and the
        corresponding strand on the board. Words are
        stored using lowercase letters, even if the
        game file used uppercase letters.
        """
        answer_list = []
        for line in self.game_file[self.answers_start:]:
            toks = line.lower().split()
            if not toks:
                break
            word = toks[0]                              # theme word
            r, c = int(toks[1]) - 1, int(toks[2]) - 1   # start position 0-based
            steps = [Step(tok) for tok in toks[3:]]
            strand = Strand(Pos(r, c), steps)
            answer_list.append((word, strand))
        return answer_list

    def found_strands(self) -> list[Strand]:
        return self.strands_found

    def game_over(self) -> bool:
        if len(self.answers()) == len(self.strands_found):
            return True
        return False

    def hint_threshold(self) -> int:
        return self.threshold_hint

    def hint_meter(self) -> int:
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

    def submit_strand(self, strand: Strand) -> tuple[str, bool] | str:
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
        # handle each of the circumstance in the requirement
        
        # first, the "too short"
        if len(strand.positions()) < 4:
            return 'Too short'
        #change made, delete this # before submission
        input_strand = self.board().evaluate_strand(strand)
        for answer in self.answers():
            word, _ = answer
            if word == input_strand:
                if strand in self.strands_found:
                    return 'Already found'
                self.strands_found.append(strand)
                if self.hint_active is not None:
                    word_num, _ = self.hint_active
                #change made, delete this # before submission
                    if strand.start == self.answers()[word_num][1].start:
                        self.hint_active = None
                return (word, True)
        strand_word = self.board().evaluate_strand(strand)
        if self.try_to_find_word(strand_word):
            if strand_word in self.attempted_non_strands:
                return 'Already found'
            else:
                self.meter_hint += 1
                self.attempted_non_strands.append(strand_word)
                #change made, delete this # before submission
                return(strand_word, False)
        return 'Not a valid word'
    
    def try_to_find_word(self, word):
        #change made, delete this # before submission
        '''
        checks to see if a word is a valid dictionary word

        uses the usable_words variable that stores a nested dictionary of all 
        valid words in the assets/web2.txt file. 

        returns True
            if the word is in the valid_words nested dictionary

        returns False
            if the word is not in the valid_words nested dictionary
        '''
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
                    #change made, delete this # before submission
                    for found_strand in self.strands_found:
                        if found_strand.start == strand.start:
                            check = True
                    if not check: 
                        self.meter_hint -= self.threshold_hint       
                        self.hint_active = (num_answer, False)
                        return (num_answer, False)
            answer_num, boolean = self.hint_active
            if not boolean:
                self.hint_active = (answer_num, True)
                return (answer_num, True)
            if boolean:
                return 'Use your current hint'
        return 'No hint yet'
    