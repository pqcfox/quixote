import game
import bot
import display
import experiment

exp_bot = bot.RandomBot()
exp_game = game.Game()
exp_display = display.Display()

exp = experiment.Experiment(exp_bot, exp_game, exp_display)
print([state for state in exp.run(verbose=True, epochs=2)])
