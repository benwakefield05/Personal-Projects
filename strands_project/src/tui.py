import click
import random
import os
import sys
from typing import Any, cast

from art_tui import (
    ArtTUIWrappers,
    ArtTUICat2,
    ArtTUISpecial,
    ArtTUICat4,
    ArtTUIBase
                    )

from strands import Pos, Strand, Board, StrandsGame, Step
from colorama import init, Fore, Style, Back
import tty
import termios

init(autoreset=True)

COLORS = [
    Fore.BLUE,
    Fore.MAGENTA,
    Fore.CYAN,
    Fore.LIGHTGREEN_EX,
    Fore.LIGHTYELLOW_EX,
    Fore.LIGHTBLUE_EX,
    Fore.LIGHTCYAN_EX,
    Fore.LIGHTMAGENTA_EX,
]

DIRECTIONS: dict[str, tuple[tuple[int, int], str]] = {
    "1": ((-1, -1), "NW"),
    "2": ((-1, 0), "Up"),
    "3": ((-1, 1), "NE"),
    "4": ((0, -1), "Left"),
    "6": ((0, 1), "Right"),
    "7": ((1, -1), "SW"),
    "8": ((1, 0), "Down"),
    "9": ((1, 1), "SE"),
}

CONNECTIONS: dict[tuple[int, int], str] = {
    (0, 1): "-",
    (0, -1): "-",
    (1, 0): "|",
    (-1, 0): "|",
    (1, 1): "\\",
    (-1, -1): "\\",
    (1, -1): "/",
    (-1, 1): "/",
    (0, 0): " ",
}

SUPPORTED_FRAMES: dict[str, type[ArtTUIBase]] = {
    "cat2": ArtTUICat2,
    "stub": ArtTUIWrappers,
    "cat0": ArtTUIWrappers,
    "cat4": ArtTUICat4,
    "special": ArtTUISpecial,
}


class TUIStub:
    def __init__(self, filename: str, hint_threshold: int, art_frame: str):
        game_files = [f for f in os.listdir("boards")]
        if filename != "assets/special.txt" and filename[7:] not in game_files:
            print()
            print("Not a valid game name, try inputting a valid game name")
            print()
            sys.exit(1)

        if art_frame not in SUPPORTED_FRAMES:
            print(f"TUI does not support art frame: {art_frame}")
            sys.exit(1)
        art_frame_use = SUPPORTED_FRAMES[art_frame]

        self.game: StrandsGame = StrandsGame(filename)
        self.board: Board = self.game.board()
        self.height: int = self.board.num_rows()
        self.width: int = self.board.num_cols()

        self.curr_pos: Pos = Pos(0, 0)
        self.previous_pos: Pos | str = ""
        self.hint_positions: list[Pos] = []
        self.attempting: list[Pos] = []
        self.found_pos: dict[tuple[int, int], int] = {}
        self.action: str = "Good Luck!"
        self.strand_attempt: list[Pos | Step] = []

        self.game.threshold_hint = hint_threshold
        self.art = art_frame_use(self.height, (self.width * 4) - 2)
    
    def render(self) -> None:
        """Print the entire board with framing and highlighting for found strands."""
        total_width = self.width * 2 - 1 
        total_height = self.height * 2 - 1
        find_center = self.width * 4 - 2
        theme = self.game.theme()
        self.art.print_top_edge()

        self.art.print_left_bar()
        print(theme.center(find_center), end="")
        self.art.print_right_bar()

        self.art.print_left_bar()
        print(self.action.center(find_center), end="")
        self.art.print_right_bar()

        self.art.print_left_bar()
        print('  ' * (total_width), end="")
        self.art.print_right_bar()

        grid: list[list[str]] = \
            [[' ' for _ in range(total_width)] for _ in range(total_height)]

        for row in range(self.height):
            for col in range(self.width):
                pos = Pos(row, col)
                letter = self.board.get_letter(pos).upper()

                display = letter
                if pos in self.attempting:
                    display = f'{Back.GREEN}{letter}{Style.RESET_ALL}'
                elif self.curr_pos == pos:
                    display = f'{Back.YELLOW}{letter}{Style.RESET_ALL}'
                elif (row, col) in self.found_pos:
                    color = COLORS[self.found_pos[(pos.r, pos.c)] - 1]
                    display = f'{color}{letter}{Style.RESET_ALL}'
                elif pos in self.hint_positions:
                    display = f'{Fore.RED}{letter}{Style.RESET_ALL}'
                grid[row * 2][col * 2] = display

        for num_pos in range(1, len(self.attempting)):
            prev = self.attempting[num_pos - 1]
            curr = self.attempting[num_pos]
            direction_r = curr.r - prev.r
            direction_c = curr.c - prev.c
            connection = self.connecter_character(prev, curr)
            grid[prev.r * 2 + direction_r][prev.c * 2 + direction_c] = connection

        for _, strand in enumerate(self.game.strands_found, 1):
            positions = strand.positions()
            for num_position in range(1, len(positions)):
                prev = positions[num_position - 1]
                curr = positions[num_position]
                connection = self.connecter_character(prev, curr)
                grid[prev.r * 2 + (curr.r - prev.r)][prev.c * 2 + (curr.c - prev.c)] = connection

        for row in range(len(grid)):
            self.art.print_left_bar()
            for col in range(len(grid[0])):
                print(grid[row][col], end=' ')
            self.art.print_right_bar()

        if self.game.hint_meter() >= self.game.threshold_hint:
            hint_display = self.game.threshold_hint
        else:
            hint_display = self.game.hint_meter()

        found_str = f"Found: {len(self.game.strands_found)} / {len(self.game.answers())}"
        hint_str = f"Hint meter: {hint_display} / {self.game.threshold_hint}"

        self.art.print_left_bar()
        print('  ' * (total_width), end="")
        self.art.print_right_bar()

        self.art.print_left_bar()
        print(found_str.center(find_center), end="")
        self.art.print_right_bar()

        self.art.print_left_bar()
        print(hint_str.center(find_center), end="")
        self.art.print_right_bar()

        self.art.print_bottom_edge()

    def check_curr_pos_valid(self, row: int, col: int) -> bool:
        if row < 0 or row > self.board.num_rows() - 1:
            return False
        if col < 0 or col > self.board.num_cols() - 1:
            return False
        return True

    def connecter_character(self, start_pos: Pos, end_pos: Pos) -> str:
        row_move = start_pos.r - end_pos.r
        col_move = start_pos.c - end_pos.c
        return CONNECTIONS[(row_move, col_move)]

    def get_single_character(self) -> str:
        fdInput = sys.stdin.fileno()
        termAttr = termios.tcgetattr(0)
        tty.setraw(fdInput)
        ch = sys.stdin.buffer.raw.read(4).decode(sys.stdin.encoding)
        if len(ch) == 1:
            if ord(ch) < 32 or ord(ch) > 126:
                ch = ord(ch)
        elif ord(ch[0]) == 27:
            ch = "\033" + ch[1:]
        termios.tcsetattr(fdInput, termios.TCSADRAIN, termAttr)
        return ch

    def get_input(self) -> str:
        '''
        Prompta an input from the player
        '''
        return self.get_single_character()
    
    def hint_in_use(self) -> None:
        if self.game.hint_active is None: 
            self.action = 'no current hint'
        else:
            num_strand, status = self.game.hint_active
            if not status:
                self.action = 'Using a Hint'
                hint_in_use = self.game.answers()[num_strand][1]
                self.hint_positions.append(hint_in_use.positions()[0])
                self.hint_positions.append(hint_in_use.positions()[-1])
            else:
                self.action = 'Use current hint'

    def run_event_loop(self) -> None:
        '''
        checks if the input is valid and completes the action of the valid input
        '''
        while True:
            input = self.get_input()
            if input == 'h':
                self.game.use_hint()
                self.hint_in_use()
            if input == 'q':
                self.quit_game(0)
                self.action = 'Ending Game'
            if input == ' ':
                attempt_len = len(self.strand_attempt)
                if attempt_len == 0:
                    self.strand_attempt.append(self.curr_pos)
                else:
                    self.strand_attempt.append(self.attempting[attempt_len - 1].step_to(self.curr_pos))
                self.attempting.append(self.curr_pos)
                self.action = 'Inputting Letter'
            if input == 13:
                try:
                    if self.previous_pos == self.curr_pos:
                        self.previous_pos = ''
                        start_pos = cast(Pos, self.strand_attempt[0])
                        steps: list[Step] = self.strand_attempt[1:]
                        answer = self.game.submit_strand(Strand(start_pos, steps))
                        if isinstance(answer, str):
                            self.action = answer
                        else:
                            word, boolian = answer
                            if boolian:
                                self.action = f'{word} is a strand'
                                num_found = len(self.game.strands_found)
                                for pos in self.attempting:
                                    self.found_pos[(pos.r, pos.c)] = num_found
                            else:
                                self.action = f'not a strand'
                        self.attempting = []
                        self.strand_attempt = []
                    else:
                        self.previous_pos = self.curr_pos
                        attempt_len = len(self.strand_attempt)
                        if attempt_len == 0:
                            self.strand_attempt.append(self.curr_pos)
                        else:
                            self.strand_attempt.append(self.attempting[attempt_len - 1].step_to(self.curr_pos))
                        self.attempting.append(self.curr_pos)
                        self.action = 'Inputting Letter'
                except:
                    self.action = 'not a valid move'
                    self.attempting = []
                    self.strand_attempt = []
                if len(self.game.strands_found) == len(self.game.answers()):
                        self.quit_game(1)
            if input == 27:
                self.attempting = []
                self.previous_pos = ''
                self.strand_attempt = []
            if input in DIRECTIONS:
                r_move, c_move = DIRECTIONS[input][0]
                r_curr = self.curr_pos.r
                c_curr = self.curr_pos.c
                if self.check_curr_pos_valid(r_curr + r_move, c_curr + c_move):
                    self.curr_pos = Pos(r_curr + r_move, c_curr + c_move)
                    self.action = f'Moved {DIRECTIONS[input][1]}'
                else:
                    self.action = 'Invalid Move'
            self.render()

    def quit_game(self, code: int) -> None:
        if code == 0:
            self.action = 'Exiting Strands...'
        if code == 1:
            self.action = 'You Win!!!'
        self.curr_pos = ''
        self.render()
        sys.exit()

    def run(self) -> None:
        self.render()
        self.run_event_loop()
    
    def show_board(self) -> None:
        for num_answer, answer in enumerate(self.game.answers()):
            for position in answer[1].positions():
                self.found_pos[(position.r, position.c)] = num_answer
            self.game.strands_found.append(answer[1])
        self.curr_pos = ''
        self.render()

    def run_title_screen(self) -> None:
        self.title_screen()
        self.title_screen_event_loop()
    
    def title_screen(self) -> None:
        total_width = self.width * 2 - 1 
        total_height = self.height * 2 - 1
        find_center = self.width * 4 - 2
        theme = self.game.theme()
        self.art.print_top_edge()

        self.art.print_left_bar()
        print(theme.center(find_center), end="")
        self.art.print_right_bar()

        self.art.print_left_bar()
        print('Press Enter'.center(find_center), end="")
        self.art.print_right_bar()
        self.art.print_left_bar()
        print('To Begin'.center(find_center), end="")
        self.art.print_right_bar()
        self.art.print_left_bar()
        print('  ' * (total_width), end="")
        self.art.print_right_bar()

        grid = [[f'{Fore.LIGHTBLUE_EX}-' for _ in range(total_width)] for _ in range(total_height)]

        for row in range(len(grid) - 1):
            self.art.print_left_bar()
            for col in range(len(grid[0])):
                print(grid[row][col], end=' ')
            self.art.print_right_bar()

        found_str = f"Strands: {len(self.game.answers())}"
        hint_str = f"Hint meter: {self.game.threshold_hint}"

        self.art.print_left_bar()
        print('  ' * (total_width), end="")
        self.art.print_right_bar()

        self.art.print_left_bar()
        print(found_str.center(find_center), end="")
        self.art.print_right_bar()

        self.art.print_left_bar()
        print(hint_str.center(find_center), end="")
        self.art.print_right_bar()

        self.art.print_bottom_edge()
    
    def title_screen_event_loop(self) -> None:
        '''
        checks if the input is valid and completes the action of the valid input
        '''
        while True:
            input = self.get_input()
            if input == 13:
                self.run()
            if input == 'q':
                self.quit_game(0)

@click.command()
@click.option('--show', is_flag=True, help="Only shows board answers")
@click.option('-g', '--game', help="Which game file to load")
@click.option('-h', '--hint', 'hint_threshold', default=3, help="Set the hint threshold.")
@click.option('-a', '--art', 'art_frame', default='stub', help="Art frame to use.")
@click.option('--title_screen', is_flag=True, help="Displays a title screen.")
@click.option('--special', is_flag=True, help="Plays special made board.")
def main(show: str, game: str, hint_threshold: int, art_frame: str, title_screen: str, special: str) -> None:

    if game is None:
        game_files = [f[:-4] for f in os.listdir('boards')]
        game = random.choice(game_files)

    if special:
        filename = 'assets/special.txt'
        art_frame = 'special'
    else:
        filename = f'boards/{game}.txt'

    tui = TUIStub(filename, hint_threshold, art_frame)


    if show:
        tui.show_board()
    elif title_screen:
        tui.run_title_screen()
    else:
        tui.run()

if __name__ == "__main__":
    main()