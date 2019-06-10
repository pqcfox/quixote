import curses


class Display:
    def __init__(self):
        self.running = True
        self.paused = False

    def start(self):
        self.stdscr = curses.initscr()
        self.stdscr.nodelay(True)
        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)
        self.running = True

    def update(self, game_screen, status):
        char = self.stdscr.getch()
        if char == ord('q'):
            self.running = False
        else:
            if char == ord(' '):
                self.paused = not self.paused
            self.stdscr.clear()
            for line, row in enumerate(game_screen):
                self.stdscr.addstr(line, 0, row)
            self.stdscr.addstr(len(game_screen), 0, 'STATUS: {}'.format(status))
            if self.paused:
                self.stdscr.addstr(0, 0, 'PAUSE', curses.A_REVERSE)
            self.stdscr.refresh()

    def stop(self):
        curses.nocbreak()
        curses.echo()
        curses.curs_set(1)
        curses.endwin()
        self.running = False
