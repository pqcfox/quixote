import game
import bot
import display
import experiment

exp_game = game.Game()
exp_display = display.Display()
exp_bot = bot.ApproxQLearningBot(discount=0.4, lr=0.1)
exp = experiment.Experiment(exp_bot, exp_game, exp_display)
exp.run(verbose=True, epochs=50)
