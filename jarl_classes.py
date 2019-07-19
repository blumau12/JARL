from datetime import datetime


class Map:
    def __init__(self, name, color='#CCC'):
        self.name = name
        self.color = color

        self.quests = []
        self.accuracy = 1

    def add_quest(self, quest_id):
        self.quests.append(quest_id)

    def remove_quest(self, quest_id):
        self.quests.remove(quest_id)

    def refresh(self):
        self.accuracy = 1
        for quest in self.quests:
            self.accuracy += quest.accuracy
            self.accuracy /= 2


class Quest:
    def __init__(self, name, period, amount, unit_name, start_instruction):
        self.name = name
        self.period = period
        self.amount = amount
        self.unit_name = unit_name
        self.start_instruction = start_instruction

        self.accuracy = 1
        self.total_wins = 0
        self.first_win_timestamp = None
        self.last_win_timestamp = None
        self.last_win_amount = None
        self.next_win_time = None

    def win(self):
        if self.total_wins:
            # TODO: accuracy calculation
            pass

    def __lt__(self, other):
        # TODO: self_time_left calculation
        self_time_left = (self.next_win_time - self.last_win_timestamp) / self.period
        return self.next_win_time - self.last_win_timestamp - self.period > other.time_delta

    def __gt__(self, other):
        return self.time_delta < other.time_delta


# test:
maps = []
refresh_rate = 200  # ms


Map(maps, 'alle Werke', '#CAE8FF')


maps[0].new_quest('mobile', 3, dt.timedelta(hours=12), 0)
maps[0].new_quest('neuronale Netze', 1, dt.timedelta(days=3), 0)

