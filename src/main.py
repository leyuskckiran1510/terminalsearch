import os
import re
import sys
import time
import shutil
import asyncio
from util import search
from bs4 import BeautifulSoup
from util.util import Color, Cursor, Shape, Event, InputBox, OutputBox


QUEUE = []
SCAN_ROW = 0


def cleanurl(url):
    control_char_regex = r"\x1b\[[0-9;]*[mG]"
    return re.sub(control_char_regex, "", url)


def text_dispense(padding, text):
    global SCAN_ROW
    for i in text.split("\n"):
        print(Cursor.move(padding, SCAN_ROW + 1), end="")
        print(i, end="")
        SCAN_ROW += 1


def title(text):
    shape = Shape()
    shape.rectangle(2, 2, Cursor.termsize()[0] - 1, len(text.split("\n")) + 3, "#ffaacc")


def update():
    global SCAN_ROW
    print(Cursor.termreset(), end="")
    d = Shape()
    d.rectangle(1, 1, Cursor.termsize()[0], Cursor.termsize()[1] + 1, "#ffaacc")
    SCAN_ROW = 0


async def screen(search_in_func):
    global SCAN_ROW
    shape = Shape()
    PG_NUM = 0
    PAGES = []
    to_show = search_in_func
    MAX_RESULTS = 5
    CLICK_ABELS = [str(i) for i in range(1, MAX_RESULTS + 1)]
    counter = 0
    QUEUE = ["\\"]
    while True:
        SCAN_ROW += 1
        text_dispense(3, to_show.banner)
        title(to_show.banner)
        if QUEUE:
            if QUEUE[0] == "q":
                break
            elif QUEUE[0] == "s":
                if counter != len(to_show.results):
                    counter += 1
                else:
                    counter = 0
                    PG_NUM += 1
                    if PG_NUM >= len(PAGES):
                        print(Cursor.move(3, SCAN_ROW), end="")
                        print("Loading... Next page..", end="")
                        search_in_func.next()
                        PAGES.append(search_in_func.page())
            elif QUEUE[0] == "w":
                if counter != 0:
                    counter -= 1
                else:
                    counter = len(to_show.results)
                    if PG_NUM > 0:
                        PG_NUM -= 1
            elif QUEUE[0] == "n":
                PG_NUM += 1
                if PG_NUM >= len(PAGES):
                    print(Cursor.move(3, SCAN_ROW), end="")
                    print("Loading... Next page..", end="")
                    search_in_func.next()
                    PAGES.append(search_in_func.page())
            elif QUEUE[0] == "p":
                if PG_NUM > 0:
                    PG_NUM -= 1
            elif QUEUE[0] == "\\":
                i = InputBox(
                    "Search: ",
                    Cursor.termsize()[0] // 2 - 25,
                    Cursor.termsize()[1] // 2 - 5,
                    50,
                    10,
                    "186,186,186",
                    "48,48,38",
                )
                value = str(await i.focus())
                if value == i.CANCLED_VALUE:
                    update()
                    if PAGES:
                        QUEUE.pop(0)
                    continue
                search_in_func = search.Search(value)
                search_in_func.fetch()
                i.close()
                value = None
                PAGES = [search_in_func.page()]
                PG_NUM = 0
                counter = 0
            elif QUEUE[0] in CLICK_ABELS:
                visibels = to_show.results[counter : counter + MAX_RESULTS]
                if len(visibels) >= int(QUEUE[0]):
                    print("Opening...")
                    o = OutputBox(
                        visibels[int(QUEUE[0]) - 1].title, 2, 2, *Cursor.termsize(), "186,186,186", "48,48,38"
                    )
                    response = search.Session()
                    response = response.get(cleanurl(visibels[int(QUEUE[0]) - 1].url))
                    if response:
                        soup = BeautifulSoup(response.text, "html.parser").text
                        await o.render(soup)
                    else:
                        await o.render("Couldnot Load the Page Sorry try Other Pages")
                    o.close()
                    update()
                    if PAGES:
                        QUEUE.pop(0)
                    continue
            QUEUE.pop(0)
        SCAN_ROW += 1
        to_show = PAGES[PG_NUM]
        for n, i in enumerate(to_show.results[counter : counter + MAX_RESULTS]):
            SCAN_ROW += 1
            print(Cursor.move(3, SCAN_ROW), end="")
            print(i.title.strip())
            SCAN_ROW += 1
            print(Cursor.move(3, SCAN_ROW), end="")
            print(i.url.strip())
            SCAN_ROW += 1
            print(Cursor.move(3, SCAN_ROW), end="")
            print(i.description.strip())
            SCAN_ROW += 3
        print("\033[{};1H:".format(Cursor.termsize()[0]), end="")
        QUEUE.append(await Event.wait_key())
        update()


page = search.Page(["Search: "])
asyncio.run(screen(page))
Cursor.visible(True)
Cursor.termreset()
Cursor.clear()
