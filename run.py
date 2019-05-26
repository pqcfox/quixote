import pexpect
import pyte

COMMAND = 'nethack'
WIDTH, HEIGHT = 80, 24
ROLE = 'v'
RACE = 'h'
ALIGNMENT = 'n'
MAX_READ = 1000000000

child = pexpect.spawn(COMMAND)
screen = pyte.Screen(WIDTH, HEIGHT)
stream = pyte.Stream(screen)
index = child.expect(['Shall I pick', 'Restoring save file'])

if index == 1:
    child.sendline()
    child.sendline('#quit')
    child.expect('Really quit?')
    child.send('y')
    child.expect('Do you want your possessions identified?')
    child.send('n')
    child.expect('Do you want to see your attributes?')
    child.send('n')
    child.expect('Do you want to see your conduct?')
    child.send('n')
    child.expect('Do you want to see the dungeon overview?')
    child.send('n')
    child.expect('You quit')
    child.sendline()
    child = pexpect.spawn(COMMAND)

child.send('n')
child.expect('Pick a role or profession')
child.send(ROLE)
child.expect('Pick a race or species')
child.send(RACE)
child.expect('Pick an alignment or creed')
child.send(ALIGNMENT)
child.expect('Is this ok?')
child.send('y')
child.sendline()
text = child.read_nonblocking(size=MAX_READ)
stream.feed(text.decode())
for line in screen.display:
    print(line)

