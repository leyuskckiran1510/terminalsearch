import shutil


class Cursor:
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
    def set_cursor_visibility(visible=True):
        if visible:
            return "\033[?25h"
        else:
            return "\033[?25l"

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
        return shutil.get_terminal_size()

    @staticmethod
    def move(x, y):
        return "\033[{0};{1}H".format(x, y)
