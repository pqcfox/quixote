import pexpect
import pyte

COMMAND = 'nethack'
WIDTH, HEIGHT = 80, 24
ROLE = 'v'
RACE = 'h'
ALIGNMENT = 'n'
MAX_READ = 1000000000


class Game:
    def __init__(self):
        pass

    def start(self):
        self.child = pexpect.spawn(COMMAND)
        self.screen = pyte.Screen(WIDTH, HEIGHT)
        self.stream = pyte.Stream(self.screen)

        index = self.child.expect(['Shall I pick', 'Restoring save file'])
        if index == 1:
            self.child.sendline()
            self.quit()
            self.child = pexpect.spawn(COMMAND)

        self.child.send('n')
        self.child.expect('Pick a role or profession')
        self.child.send(ROLE)
        self.child.expect('Pick a race or species')
        self.child.send(RACE)
        self.child.expect('Pick an alignment or creed')
        self.child.send(ALIGNMENT)
        self.child.expect('Is this ok?')
        self.child.send('y')
        self.child.sendline()

    def quit(self):
        self.child.sendline('#quit')
        self.child.expect('Really quit?')
        self.child.send('y')
        self.child.expect('Do you want your possessions identified?')
        self.child.send('n')
        self.child.expect('Do you want to see your attributes?')
        self.child.send('n')
        self.child.expect('Do you want to see your conduct?')
        self.child.send('n')
        self.child.expect('Do you want to see the dungeon overview?')
        self.child.send('n')
        self.child.expect('You quit')
        self.child.sendline()

    def get_screen(self):
        text = self.child.read_nonblocking(size=MAX_READ)
        self.stream.feed(text.decode())
        return self.screen.display


if __name__ == '__main__':
    game = Game()
    game.start()
    print(game.get_screen())
