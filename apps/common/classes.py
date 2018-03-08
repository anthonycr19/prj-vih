from enum import Enum


class EnumChoices(Enum):

    @classmethod
    def to_choice(cls):
        return list(map(lambda e: e.describe(), cls))

    def describe(self):
        return self.name, self.value
