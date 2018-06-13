from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants
import json


class WorkPage(Page):
    timer_text = 'Time left to complete the task:'
    timeout_seconds = 3000

    def vars_for_template(self):
        return {'num_digits': range(Constants.num_digits), }

    def before_next_page(self):
        self.player.dump_tasks = json.dumps(list(self.player.tasks.all().values()))


class Results(Page):
    pass


page_sequence = [
    WorkPage,
    Results,
]
