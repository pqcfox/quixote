import game
import bot
import display
import experiment

exp_game = game.Game()
exp_display = display.Display()
for discount in (0.2, 0.4, 0.6, 0.8):
    exp_bot = bot.QLearningBot(discount=discount)
    exp = experiment.Experiment(exp_bot, exp_game, exp_display)
    exp.run(verbose=True, epochs=20)
