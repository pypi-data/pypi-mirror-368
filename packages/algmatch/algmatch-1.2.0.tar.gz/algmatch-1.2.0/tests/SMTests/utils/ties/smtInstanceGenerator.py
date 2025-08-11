import random

from tests.abstractTestClasses.abstractTieGenerator import AbstractTieGenerator
from tests.SMTests.utils.generic.smGenericGenerator import SMGenericGenerator


class SMTInstanceGenerator(SMGenericGenerator, AbstractTieGenerator):
    def __init__(self, men, women, lower_bound, upper_bound):
        SMGenericGenerator.__init__(self, men, women, lower_bound, upper_bound)
        AbstractTieGenerator.__init__(self)

    def _generate_men_lists(self):
        for man_list in self.instance["men"].values():
            random.shuffle(self.available_women)
            length = random.randint(self.li, self.lj)

            self._generate_tied_list(
                man_list,
                self.available_women[:length],
            )

    def _generate_women_lists(self):
        for woman_list in self.instance["women"].values():
            random.shuffle(self.available_men)
            length = random.randint(self.li, self.lj)

            self._generate_tied_list(
                woman_list,
                self.available_men[:length],
            )
