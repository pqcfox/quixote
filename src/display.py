import curses


class Display:
    def __init__(self):
        self.running = True

    def start(self):
        self.stdscr = curses.initscr()
        self.stdscr.nodelay(True)
        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)
        self.running = True

    def update(self, game_screen, status):
        if self.stdscr.getch() == ord('q'):
            self.running = False
        else:
            self.stdscr.clear()
            for line, row in enumerate(game_screen):
                self.stdscr.addstr(line, 0, row)
            self.stdscr.addstr(len(game_screen), 0, 'STATUS: {}'.format(status))
            self.stdscr.refresh()

    def stop(self):
        curses.nocbreak()
        curses.echo()
        curses.curs_set(1)
        curses.endwin()
        self.running = False
