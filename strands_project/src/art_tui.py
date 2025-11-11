"""
File containing ArtTUIWrappers, ArtTUICat2, Art TUICat4, and ArtTUISpecial
classes, which extend ArtTUIBase,that draw a given pattern for the TUI display.
"""
from ui import ArtTUIBase, TUIStub
import click

class ArtTUIWrappers(ArtTUIBase):
    """
    Class that draws a given number of nested "wrappers" around the interior
    of the TUI display.
    """
    frame_width: int
    interior_width: int
    color_dict: dict[int, str]
    reset: str

    def __init__(self, frame_width: int, interior_width: int):
        """
        Constructor
        """
        self.frame_width = frame_width
        self.interior_width = interior_width
        self.reset = "\033[0m"
        self.color_dict = {
                            0: "\033[48;5;245m",
                            1: "\033[103m",
                            2: "\033[102m",
                            3: "\033[101m",
                            4: "\033[104m",
                            5: "\033[105m",
                            6: "\033[106m",
                            7: "\033[100m",
                            8: "\033[107m",
                            9: "\033[48;5;208m"
                        }


    def print_top_edge(self) -> None:
        """
        Print the top edge of the overall text display.
        Depending on the frame_width, multiple lines
        may be printed.
        """
        for frame in range(self.frame_width):
            line = ""
            for i in range(frame):
                color = self.color_dict[i]
                line += color + "  " + self.reset

            center_width = \
                (self.interior_width) + ((self.frame_width - frame) * 4)
            color = self.color_dict[frame]
            line += f"{color}{" " * center_width}{self.reset}"

            for i in reversed(range(frame)):
                color = self.color_dict[i]
                line += color + "  " + self.reset
            print(line)


    def print_bottom_edge(self) -> None:
        """
        Print the bottom edge of the overall text display.
        Depending on the frame_width, multiple lines
        may be printed.
        """
        for frame in reversed(range(self.frame_width)):
            line = ""
            for i in range(frame):
                color = self.color_dict[i]
                line += color + "  " + self.reset

            center_width = \
                (self.interior_width) + ((self.frame_width - frame) * 4)
            color = self.color_dict[frame]
            line += f"{color}{" " * center_width}{self.reset}"

            for i in reversed(range(frame)):
                color = self.color_dict[i]
                line += color + "  " + self.reset
            print(line)

    def print_left_bar(self) -> None:
        """
        Print a single line of the left bar to precede a
        line of the TUI display. The left bar should not
        conclude with a newline.
        """
        for frame in range(self.frame_width):
            color = self.color_dict[frame]
            print(color + "  " + self.reset, end="")


    def print_right_bar(self) -> None:
        """
        Print a single line of the right bar to follow a
        line of the TUI display. The right bar should
        conclude with a newline.
        """
        for frame in reversed(range(self.frame_width)):
            color = self.color_dict[frame]
            print(color + "  " + self.reset, end="")
        print()

class ArtTUICat2(ArtTUIBase):
    """
    Class to draw a TUI window with a chevron pattern.
    """
    frame_width: int
    interior_width: int
    color_dict: dict[int, str]
    reset: str
    total_width: int
    row: int

    def __init__(self, frame_width: int, interior_width: int):
        """
        Constructor
        """
        self.frame_width = frame_width
        self.interior_width = interior_width
        self.reset = "\033[0m"
        self.total_width = \
            self.interior_width + (4 * self.frame_width)
        self.row = 0
        self.color_dict = {
                            0: "\033[38;5;245m",
                            1: "\033[93m",
                            2: "\033[92m",
                            3: "\033[91m",
                            4: "\033[94m",
                            5: "\033[95m",
                            6: "\033[96m",
                            7: "\033[90m",
                            8: "\033[97m",
                            9: "\033[38;5;208m"
                            }


    def print_top_edge(self) -> None:
        """
        Print the top edge of the overall text display.
        Depending on the frame_width.
        """
        for frame in range(self.frame_width):
            row = ""
            color = self.color_dict[frame]
            for col in range(self.total_width):
                if col % 2 == 0:
                    row += "/"
                else:
                    row += "\\"
            print(color + row + self.reset)


    def print_bottom_edge(self) -> None:
        """
        Print the bottom edge of the overall text display.
        Depending on the frame_width, multiple lines
        may be printed.
        """
        self.print_top_edge()


    def print_left_bar(self) -> None:
        """
        Print a single line of the left bar to precede a
        line of the TUI display. The left bar should not
        conclude with a newline. Print pattern.
        """
        if self.row < self.frame_width:
            color = self.color_dict[self.row]
        else:
            self.row = 0
            color = self.color_dict[self.row]

        row = ""
        for _ in range(self.frame_width):
            row += "/\\"   
        print(color + row + self.reset, end = "")


    def print_right_bar(self) -> None:
        """
        Increment row and line.
        """
        self.print_left_bar()
        self.row+=1
        print()


class ArtTUICat4(ArtTUIBase):
    """
    Class that draws a given number of nested "wrappers" around the interior
    of the TUI display using emojis that envoke Trees, Graphs, and Strands.
    """
    frame_width: int
    interior_width: int
    color_dict: dict[int, str]
    reset: str

    def __init__(self, frame_width: int, interior_width: int):
        """
        Constructor
        """
        self.frame_width = frame_width
        self.interior_width = interior_width
        self.emoji_dict = {
                            0: "🌲",
                            1: "📈",
                            2: "🌴",
                            3: "📉",
                            4: "🌳",
                            5: "📊",
                            6: "🎄",
                            7: "🧶",
                        }


    def print_top_edge(self) -> None:
        """
        Print the top edge of the overall text display.
        Depending on the frame_width, multiple lines
        may be printed.
        """
        for frame in range(self.frame_width):
            line = ""
            for i in range(frame):
                emoji = self.emoji_dict[i]
                line += emoji

            center_width = \
                (self.interior_width) + ((self.frame_width - frame * 2)) - 3
            emoji = self.emoji_dict[frame]
            line += emoji * center_width

            for i in reversed(range(frame)):
                emoji = self.emoji_dict[i]
                line += emoji
            print(line)


    def print_bottom_edge(self) -> None:
        """
        Print the bottom edge of the overall text display.
        Depending on the frame_width, multiple lines
        may be printed.
        """
        for frame in reversed(range(self.frame_width)):
            line = ""
            for i in range(frame):
                emoji = self.emoji_dict[i]
                line += emoji

            center_width = \
                (self.interior_width) + ((self.frame_width - frame * 2)) - 3
            emoji = self.emoji_dict[frame]
            line += emoji * center_width

            for i in reversed(range(frame)):
                emoji = self.emoji_dict[i]
                line += emoji
            print(line)


    def print_left_bar(self) -> None:
        """
        Print a single line of the left bar to precede a
        line of the TUI display. The left bar should not
        conclude with a newline.
        """
        for frame in range(self.frame_width):
            emoji = self.emoji_dict[frame]
            print(emoji, end="")


    def print_right_bar(self) -> None:
        """
        Print a single line of the right bar to follow a
        line of the TUI display. The right bar should
        conclude with a newline.
        """
        for frame in reversed(range(self.frame_width)):
            emoji = self.emoji_dict[frame]
            print(emoji, end="")
        print()


class ArtTUISpecial(ArtTUIBase):
    """
    Class that draws a given number of nested "wrappers" around the interior
    of the TUI display using special Emojis.
    """
    frame_width: int
    interior_width: int
    color_dict: dict[int, str]
    reset: str

    def __init__(self, frame_width: int, interior_width: int):
        """
        Constructor
        """
        self.frame_width = frame_width
        self.interior_width = interior_width
        self.emoji_dict = {
                            0: "🥞",
                            1: "🥯",
                            2: "🧇",
                            3: "🥓",
                            4: "🍳",
                            5: "🍞",
                            6: "🥚",
                            7: "🧈",
                            8: "🍩",
                            9: "☕"
                        }


    def print_top_edge(self) -> None:
        """
        Print the top edge of the overall text display.
        Depending on the frame_width, multiple lines
        may be printed.
        """
        for frame in range(self.frame_width):
            line = ""
            for i in range(frame):
                emoji = self.emoji_dict[i]
                line += emoji

            center_width = \
                (self.interior_width) + ((self.frame_width - frame * 2)) - 3
            emoji = self.emoji_dict[frame]
            line += emoji * center_width

            for i in reversed(range(frame)):
                emoji = self.emoji_dict[i]
                line += emoji
            print(line)


    def print_bottom_edge(self) -> None:
        """
        Print the bottom edge of the overall text display.
        Depending on the frame_width, multiple lines
        may be printed.
        """
        for frame in reversed(range(self.frame_width)):
            line = ""
            for i in range(frame):
                emoji = self.emoji_dict[i]
                line += emoji

            center_width = \
                (self.interior_width) + ((self.frame_width - frame * 2)) - 3
            emoji = self.emoji_dict[frame]
            line += emoji * center_width

            for i in reversed(range(frame)):
                emoji = self.emoji_dict[i]
                line += emoji
            print(line)


    def print_left_bar(self) -> None:
        """
        Print a single line of the left bar to precede a
        line of the TUI display. The left bar should not
        conclude with a newline.
        """
        for frame in range(self.frame_width):
            emoji = self.emoji_dict[frame]
            print(emoji, end="")


    def print_right_bar(self) -> None:
        """
        Print a single line of the right bar to follow a
        line of the TUI display. The right bar should
        conclude with a newline.
        """
        for frame in reversed(range(self.frame_width)):
            emoji = self.emoji_dict[frame]
            print(emoji, end="")
        print()


@click.command()
@click.option("--art", "cat", required = True)
@click.option("-f", "fw", default = 3)
@click.option("-w", "iw", default = 12)
@click.option("-h", "ih", default = 8)
def cmd(cat: str, fw: str, iw: str, ih: str) -> None:
    """
    Assign the chosen pattern into TUIStub.
    Only wrappers and cat2 are implemented;
    everything else prints a not supported message.
    """
    fw_int = int(fw)
    iw_int = int(iw)
    ih_int = int(ih)
    if cat == "cat0":
        tui = ArtTUIWrappers(fw_int, iw_int)
    elif cat == "cat2":
        tui = ArtTUICat2(fw_int, iw_int)
    elif cat == "cat4":
        tui = ArtTUICat4(fw_int, iw_int)
    else:
        print(f"TUI pattern from {cat} is not supported.")
        return
    TUIStub(tui, iw_int, ih_int)
if __name__ == "__main__":
    cmd()