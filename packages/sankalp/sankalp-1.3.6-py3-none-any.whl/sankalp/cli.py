# sankalp/cli.py

import curses
import webbrowser
import pygame
import pkg_resources

menu_items = [
    "Sankalp Shrivastava",
    "I'm a technologist and an entrepreneur.",
    # "Some thoughts here.",
    "linkedin.",
    "twitter.",
    "github.",
    "email: 1sankalpshrivastava@gmail.com",
    "exit"
]

links = [
    "",
    "",
    # "https://sankalp.sh/thoughts.html",
    "https://www.linkedin.com/in/shrivastavasankalp/",
    "https://twitter.com/1sankalp",
    "https://github.com/1Sankalp",
    "mailto:1sankalpshrivastava@gmail.com",
    ""
]

def play_music():
    pygame.mixer.init()
    # Use pkg_resources to get the path to the music file within the package
    music_file = pkg_resources.resource_filename(__name__, "blue.mp3")
    pygame.mixer.music.load(music_file)
    pygame.mixer.music.set_volume(0.3)
    pygame.mixer.music.play(-1)


def print_menu(stdscr, selected_row_idx):
    stdscr.clear()
    h, w = stdscr.getmaxyx()

    stdscr.bkgd(' ', curses.color_pair(2))

    for idx, row in enumerate(menu_items):
        # x = w//4 - len(row)//2
        x = w // 3
        y = h//2 - len(menu_items)//2 + idx
        if idx == selected_row_idx:
            stdscr.attron(curses.color_pair(1))
            stdscr.addstr(y, x, row)
            stdscr.attroff(curses.color_pair(1))
        else:
            stdscr.addstr(y, x, row)
    stdscr.refresh()


def main(stdscr):
    curses.curs_set(0)
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLUE)
    current_row = 0

    print_menu(stdscr, current_row)

    while True:
        key = stdscr.getch()
        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(menu_items) - 1:
            current_row += 1
        elif key == curses.KEY_ENTER or key in [10, 13]:
            if menu_items[current_row] == "exit":
                pygame.mixer.music.stop()  # Stop the music on exit
                break
            if links[current_row]:
                webbrowser.open(links[current_row])
        print_menu(stdscr, current_row)

def run_cli():
    play_music()
    curses.wrapper(main)

if __name__ == "__main__":
    run_cli()