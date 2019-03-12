import datetime as dt
import random


class Map:
    def __init__(self, list_of_maps, name, color='#CCC'):
        self.name = name
        self.color = color
        self.id = random.randint(100000000, 999999999)
        list_of_maps.append(self)

        self.quests = {1: [], 2: [], 3: []}
        self.freq_multiplier = 1
        self.last_penalty = None
        self.gain = 0
        self.stability = 1.0
        self.gains_total = 0
        self.first_gain = None

    def new_quest(self, name, level, period, solution, description=('', '')):
        new_q = Quest(name, self, level, period, solution, description)
        self.quests[level].append(new_q)
        self.freq_multiplier = 1000 / (len(self.quests[1])*500 + len(self.quests[2])*1000 + len(self.quests[3])*1500)
        for level in self.quests:
            for quest in self.quests[level]:
                quest.calculate_plus()

    def gain_elo(self, plus, stability):
        # stability:
        if self.last_penalty:
            self.stability = (self.stability * self.gains_total + stability) / (self.gains_total + 1)
        else:
            self.first_gain = dt.datetime.today()  # сохраняет дату первого выполнения квеста на карте
        self.gains_total += 1
        self.gain += plus

    def refresh(self):
        if self.gains_total:
            if self.last_penalty:
                hardness = 0.9  # эта часть от 1000 постепенно убирается каждые сутки
                self.gain -= 1000 * hardness * (dt.datetime.today() - self.last_penalty) / dt.timedelta(days=1)
                self.last_penalty = dt.datetime.today()
            else:
                self.last_penalty = dt.datetime.today()

    def __repr__(self):
        return self.name


class Quest:
    def __init__(self, name, in_map, level, period, solution, description):
        # static attrs:
        self.name = name
        self.in_map = in_map
        self.level = level
        self.period = period
        self.solution = solution
        self.freq_nerfer = dt.timedelta(days=1) / self.period

        # dynamic attrs:
        self.description = description
        self.is_active = True
        self.relevance = 1
        self.performance = 1.0
        self.first_performed = None
        self.num_of_performs = 0
        self.last_performed = None
        self.plus = 0
        self.time_delta = dt.timedelta(0)
        self.history = []

    def refresh(self):
        if self.last_performed:  # если квест хотя бы однажды выполнен:
            # time_delta (отрицательное время до след. совершения (при пропущенном событии становится положительным)):
            self.time_delta = dt.datetime.today() - self.last_performed - self.period
            # соответствие частоты выполнения плановой частоте:
            if self.num_of_performs > 1:  # если первое и последнее выполнения - разные:
                self.performance = int(10 * (self.num_of_performs - 1) /
                                       ((self.last_performed - self.first_performed) / self.period)) / 10
            else:
                self.performance = 1.0
        # relevance:
        if self.time_delta.days < 0:  # еще рано выполнять квест
            self.relevance = int(10 - 10 * abs(self.time_delta / self.period)) / 10
        else:
            self.relevance = 1
        # пределы:
        if self.relevance > 1:
            self.relevance = 1
        elif self.relevance < 0.1:
            self.relevance = 0.1

    def do_perform(self, time):
        if self.last_performed:  # если квест хотя бы однажды выполнен:
            self.time_delta = time - self.last_performed - self.period
        # stability:
        stability = 1 - (abs(self.time_delta / self.period) / (4 - self.level))
        if stability < 0:
            stability = 0
        if stability > 0.8:
            stability = 1
        if not self.first_performed:
            self.first_performed = time
        self.num_of_performs += 1
        self.last_performed = time
        self.calculate_plus()
        self.in_map.gain_elo(self.plus, stability)

    def calculate_plus(self):
        self.plus = self.level * 500 * self.in_map.freq_multiplier / self.freq_nerfer

    def __repr__(self):
        return self.name+', performance:'+str(self.performance)+', relevance:'+str(self.relevance)

    def __lt__(self, other):
        return self.time_delta > other.time_delta

    def __gt__(self, other):
        return self.time_delta < other.time_delta


# test:
maps = []
refresh_rate = 200  # ms


Map(maps, 'alle Werke', '#CAE8FF')


maps[0].new_quest('mobile', 3, dt.timedelta(hours=12), 0)
maps[0].new_quest('neuronale Netze', 1, dt.timedelta(days=3), 0)

