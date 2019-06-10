import curses


class Display:
    def __init__(self, current_game):
        self.current_game = current_game
        self.running = True

    def start(self):
        self.stdscr = curses.initscr()
        self.stdscr.nodelay(True)
        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)
        self.running = True

    def update(self):
        if self.stdscr.getch() == ord('q'):
            self.current_game.running = False
        else:
            game_display = self.current_game.get_screen()
            for line, row in enumerate(game_display):
                self.stdscr.addstr(line, 0, row)
            self.stdscr.refresh()

    def stop(self):
        curses.nocbreak()
        curses.echo()
        curses.curs_set(1)
        curses.endwin()
        self.running = False


