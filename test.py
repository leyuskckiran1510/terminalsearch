import os
import sys
import time
import shutil
import asyncio
from controll import Cursor


QUEUE = []


def termsize():
    return shutil.get_terminal_size()


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
    QUEUE.append(result)


async def screen(lines):
    print(Cursor.termreset(), end="")
    while True:
        await wait_key()
        if QUEUE:
            if QUEUE[0] == "\n":
                break
            if QUEUE[0] == "w":
                lines = lines[1:] + [lines[0]]
            if QUEUE[0] == "s":
                lines = [lines[-1]] + lines[:-1]
            QUEUE.pop(0)
        print(Cursor.move(1, 1), end="")

        print(f"╔{'═'*(Cursor.termsize()[0]-2)}╗")
        for line in lines:
            print("║", line.ljust(22), "║")
        print(f"╚{'═'*(Cursor.termsize()[0]-2)}╝")

        time.sleep(0.1)
        print("\033[K", end="")
        print("\033[F", end="")
        print("\033[{};1H:".format(termsize()[0]), end="")


lines = ["Line 1", "Line 2", "Line 3", "Line 4"]
asyncio.run(screen(lines))
