from pandas import DataFrame, Timedelta, datetime, MultiIndex
from pickle import load, dump, HIGHEST_PROTOCOL
from os import makedirs
from os.path import isfile, join


class Person:

    def __init__(self, player_name, email):

        self.player_name = player_name
        self.email = email
        self.saves_folder = 'saves'  # run configuration variables
        self.quests = {}  # script global variables. points types: minutes, boolean, number, list, entry
        self.logs = DataFrame(columns=['name', 'points', 'bookmark'],
                              index=MultiIndex(levels=[[], []], codes=[[], []]))
        # index: (date, id)

    def load_progress(self, name):
        makedirs(self.saves_folder, exist_ok=True)
        file_path = join(self.saves_folder, '{0}.bin'.format(name))
        if not isfile(file_path):
            return False
        with open(file_path, 'rb') as f:
            self.quests = load(f)
            self.logs = load(f)

    def save_progress(self, name):
        file_path = join(self.saves_folder, '{0}.bin'.format(name))
        for folder in self.saves_folder:
            folder_path = join(*self.saves_folder[:self.saves_folder.index(folder) + 1])
            makedirs(folder_path, exist_ok=True)
        with open(file_path, 'wb') as f:
            dump(self.quests, f, protocol=HIGHEST_PROTOCOL)
            dump(self.logs, f, protocol=HIGHEST_PROTOCOL)

    def add_quest(self, name, points, instruction, color):
        """
        :param name: 'name'
        :param points: {'Minuten': {'norm': 60, 'type': 'minutes'}, }
        :param instruction: 'how to start work easily'
        :param color: '#0099FF' hex RGB color
        """
        if name in self.quests:
            return False
        self.quests.update({name: {'start_timestamp': None,
                                   'first_date': None,
                                   'last_date': None,
                                   'points': points,
                                   'instruction': instruction,
                                   'color': color}})
        for point in points:
            self.quests[name]['points'][point].update({'total_points': 0, 'points_to_do': 0, 'recommended': 0})
        return True

    def update_points_to_do(self):
        for name in self.quests:
            quest = self.quests[name]
            if quest['first_date'] is not None:
                for point_name in quest['points']:
                    point = quest['points'][point_name]
                    point['points_to_do'] = (datetime.today().date() - quest['first_date'] + Timedelta('1 days')
                                             ).days * point['norm'] - point['total_points']

    def update_recommended(self):
        # update_points_to_do first
        for name in self.quests:
            quest = self.quests[name]
            if quest['first_date'] is None:
                for point_name in quest['points']:
                    point = quest['points'][point_name]
                    point['recommended'] = point['norm']
            else:
                for point_name in quest['points']:
                    point = quest['points'][point_name]
                    if point['points_to_do'] >= 0:
                        if quest['last_date'] == datetime.today().date():
                            point['recommended'] = 0
                        else:
                            point['recommended'] = point['norm'] / 2
                    else:
                        point['recommended'] = -point['points_to_do']

    def edit_quest(self, name, instruction=None, color=None):
        if name not in self.quests:
            return False
        if instruction is not None:
            self.quests[name]['instruction'] = str(instruction)
        if color is not None:
            self.quests[name]['color'] = str(color)

    def start_work(self, name, time):
        if name not in self.quests or self.quests[name]['start_timestamp'] is not None:
            raise Exception('bad quest start')
        self.quests[name]['start_timestamp'] = time
        return True

    def log_work(self, name, time, points, bookmark):
        """
        :param name: 'name'
        :param time: datetime.datetime object
        :param points: {'Minuten': 48, }
        :param bookmark: 'any text'
        """
        if name not in self.quests:
            return False
        quest = self.quests[name]
        for point_name in points:
            if point_name not in quest['points']:
                return False
        for point_name in points:
            point = quest['points'][point_name]
            point['total_points'] += points[point_name]
        date = time.date()
        quest['bookmark'] = bookmark
        if quest['first_date'] is None:
            quest['first_date'] = date
        quest['last_date'] = date
        if not self.logs.empty:
            next_index = max(self.logs.index.levels[0]) + 1
        else:
            next_index = 0
        self.logs.loc[(next_index, date), self.logs.columns] = [str(name), str(points), str(bookmark)]
        quest['start_timestamp'] = None

    def remove_quest(self, name):
        if name not in self.quests:
            return False
        self.quests.pop(name)
        return True


if __name__ == '__main__':

    person = Person('hakerok_igorek', 'hack@gmail.com')
    # загружаем данные прошлых сессий
    person.load_progress('hakerok_igorek')

    # создаем новый квест
    person.add_quest(
        name='hack_americans',
        points={'Minuten': {'norm': 15, 'type': 'minutes'}},
        instruction='just bruteforce penta(gon)',
        color='#fc0fc0')

    # позже редактируем этот квест, если нужно
    # person.edit_quest(name='english', instruction='chill and read', color=None)

    # перед работой пересчитываем недостающие очки квеста на данный момент
    person.update_points_to_do()

    # пересчитываем рекомендуемые объемы работы на данный момент
    person.update_recommended()

    # начинаем выполнение квеста
    person.start_work(name='hack_americans', time=datetime.today() - Timedelta(15, 'm'))

    # заканчиваем выполнение квеста
    person.log_work(
        name='hack_americans',
        time=datetime.today(),
        points={'Minuten': 15},
        bookmark='this time was the easiest; the key is to make a coffee')

    # после работы пересчитываем недостающие очки квеста на данный момент
    person.update_points_to_do()

    # пересчитываем рекомендуемые объемы работы на данный момент
    person.update_recommended()

    # при необходимости удаляем квест
    # person.remove_quest(name='english')

    # сохраняем прогресс в базу
    person.save_progress('hakerok_igorek')

    pass
