import os
import sys
import time
import shutil
import asyncio


class Cursor:
    termx = 0
    termy = 0

    @staticmethod
    def clear_line():
        return "\033[K"

    @staticmethod
    def move_up():
        return "\033[F"

    @staticmethod
    def move_down():
        return "\033[E"

    @staticmethod
    def save_position():
        return "\033[s"

    @staticmethod
    def restore_position():
        return "\033[u"

    @staticmethod
    def visible(visible=True):
        if visible:
            return "\033[?25h"
        else:
            return "\033[?25l"

    @staticmethod
    def clear():
        if os.name == "nt":
            os.system("cls")
        else:
            os.system("clear")

    @staticmethod
    def clear_screen():
        return "\033[2J"

    @staticmethod
    def termreset():
        return "\033c"

    @staticmethod
    def clear_above():
        return "\033[1J"

    @staticmethod
    def clear_below():
        return "\033[0J"

    @staticmethod
    def easy_move(direction: str):
        direction_mapping = {"W": "A", "S": "B", "D": "C", "A": "D"}
        char = direction_mapping[direction.upper()]
        return "\033[{}".format(char)

    @staticmethod
    def termsize():
        a, b = shutil.get_terminal_size()
        if a != Cursor.termx or b != Cursor.termy:
            Cursor.clear()
            Cursor.termx = a
            Cursor.termy = b
        return Cursor.termx, Cursor.termy

    @staticmethod
    def move(x, y):
        return f"\033[{y};{x}H"


class Color:
    def __init__(self, color):
        if color == 0:
            self.r = 0
            self.g = 0
            self.b = 0
            return
        if color.startswith("#"):
            self.parse_hex(color)
        else:
            self.parse_rgb(color)

    def rst(self):
        return "\x1b[0m"

    def parse_hex(self, color):
        self.r = int(color[1:3], 16)
        self.g = int(color[3:5], 16)
        self.b = int(color[5:7], 16)

    def parse_rgb(self, color):
        self.r, self.g, self.b = color.split(",")

    def foreground(self, underline=False):
        if underline:
            return f"\x1b[38;2;{self.r};{self.g};{self.b};4;1m"
        return f"\x1b[38;2;{self.r};{self.g};{self.b};1m"

    def background(self):
        return f"\x1b[48;2;{self.r};{self.g};{self.b}m"


class Event:
    @staticmethod
    async def wait_key():
        result = None
        if os.name == "nt":
            import msvcrt

            result = msvcrt.getwch()
        else:
            import termios

            fd = sys.stdin.fileno()
            oldterm = termios.tcgetattr(fd)
            newattr = termios.tcgetattr(fd)
            newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
            termios.tcsetattr(fd, termios.TCSANOW, newattr)
            try:
                result = sys.stdin.read(1)
            except IOError:
                pass
            finally:
                termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)
        return result


class Shape:
    boarders = ["╔", "╗", "║", "╚", "╝", "═"]

    def __init__(self):
        ...

    def rectangle(self, x, y, x2, y2, color, filled=False):
        self.color = Color(color)
        self.x = x
        self.y = y
        self.x2 = x2
        self.y2 = y2
        if not filled:
            self.draw_rec()
        else:
            self.draw_rec_filled()

    def draw_rec(self):
        Cursor.visible(False)
        if not (self.color.r == 0 and self.color.g == 0 and self.color.b == 0):
            print(self.color.foreground(), end="")

        print(f"{Cursor.move(self.x, self.y)}{self.boarders[0]}", end="")
        for i in range(self.x + 1, self.x2):
            print(Cursor.move(i, self.y), end="")
            print(self.boarders[5], end="")

        print(f"{Cursor.move(i+1, self.y)}{self.boarders[1]}", end="")
        for j in range(self.y + 1, self.y2):
            print(Cursor.move(i + 1, j), end="")
            print(self.boarders[2], end="")

        print(f"{Cursor.move(i+1,j)}{self.boarders[4]}", end="")
        for k in range(i, self.x, -1):
            print(Cursor.move(k, j), end="")
            print(self.boarders[5], end="")

        print(f"{Cursor.move(self.x, j)}{self.boarders[3]}", end="")
        for l in range(j - 1, self.y, -1):
            print(Cursor.move(self.x, l), end="")
            print(self.boarders[2], end="")
        Cursor.visible(True)
        self.color.rst()

    def draw_rec_filled(self):
        Cursor.visible(False)
        if not (self.color.r == 0 and self.color.g == 0 and self.color.b == 0):
            print(self.color.background(), end="")

        for j in range(self.y, self.y2):
            for i in range(self.x, self.x2):
                print(Cursor.move(i, j), end="")
                print(" ", end="")
        Cursor.visible(True)
        self.color.rst()


class InputBox:
    CANCLED_VALUE = "-1-><-1+"

    def __init__(self, message, x, y, width, height, color, background):
        self.message = message
        self.cursor_x = x
        self.cursor_y = y
        self.color = color if color else "186,186,186"
        self.background = background if background else "48,48,38"
        self.width = width
        self.height = height

    async def focus(self):
        self.value = ""
        s = Shape().rectangle(
            self.cursor_x,
            self.cursor_y,
            self.cursor_x + self.width,
            self.cursor_y + self.height,
            self.background,
            True,
        )
        s = Shape().rectangle(
            self.cursor_x + 1,
            self.cursor_y + 2,
            self.cursor_x - 1 + self.width,
            self.cursor_y - 1 + self.height,
            "123,213,013",
        )
        print(Cursor.move(self.cursor_x + 2, self.cursor_y + 1), end="")
        print(Color(self.color).foreground(), end="")
        print(self.message, end="")
        print(Cursor.move(self.cursor_x + 2, self.cursor_y + 3), end="")
        print(Cursor.visible(True), end="")
        key = ""
        while True:
            if key == "\r" or key == "\n":
                break
            elif key == "\x1b":
                return self.CANCLED_VALUE
            elif key == "\x7f":
                if len(self.value) > 0:
                    self.value = self.value[:-1]
            else:
                self.value += key
                if not ((len(self.value) + 1) % (self.width - 2)):
                    self.value += "\n"
            for n, i in enumerate(self.value.split("\n")):
                print(Cursor.move(self.cursor_x + 2, self.cursor_y + 3 + n), end="")
                print(" " * (len(i)), end="")
                print(Cursor.move(self.cursor_x + 2, self.cursor_y + 3 + n), end="")
                print(i)
            key = await Event.wait_key()
        return self.value.strip().replace("\n", "")

    def close(self):
        Cursor.clear()


async def main():
    i = InputBox("Enter your name: ", 10, 10, 50, 10, "186,186,186", "48,48,38")
    print("\n")
    print(await i.focus())


if __name__ == "__main__":
    # s = Shape()
    # s.rectangle(1, 1, *Cursor.termsize(), "#ff00ff")
    # s.rectangle(2, 2, Cursor.termsize()[0] - 1, 10, "#ff00cc")
    # s.rectangle(10, 10, 50, 30, "120,90,120", True)
    # s.rectangle(10, 10, 50, 30, "#ff00aa")
    # s.rectangle(10, 10, 50, 30, "#ff00aa")
    asyncio.run(main())
    # s.rectangle(2, 2, 20, 20, "#ff00ff")
    # Cursor.move(10, 30)
    print("\033[30;10H", end="")
    # s.rectangle(20, 20, 30, 30, "#ff00ff")
