import tqdm

class Experiment:
    def __init__(self, exp_bot, exp_game, exp_display):
        self.exp_bot = exp_bot
        self.exp_game = exp_game
        self.exp_display = exp_display

    def run(self, verbose=False, show=False):
        if verbose and show:
            raise ValueError('Experiment can either be run in verbose or show mode')
        try:
            self.exp_game.start()
            if show:
                self.exp_display.start()
            while self.exp_game.running:
                if show:
                    game_screen = self.exp_game.get_screen()
                    self.exp_display.update(game_screen)
                    if not self.exp_display.running:
                        self.exp_game.running = False
                        break
                state = self.exp_game.get_state()
                act = self.exp_bot.choose_action(state)
                self.exp_game.do_action(act)
            return state
        except Exception as e:
            raise e
        finally:
            if show:
                self.exp_display.stop()

        # TODO: tell bot what episode
