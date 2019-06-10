import game
import bot

current_game = game.Game()
bot = bot.RandomBot()
print(bot.play(current_game, show=True))
