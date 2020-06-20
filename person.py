from datetime import timedelta, datetime
from pickle import load, dump, HIGHEST_PROTOCOL
from os import makedirs
from os.path import isfile, join
from random import randint

import config
from exceptions import assert_person
from time_lib import parse_timestamp
from logs import Logs


class Person:

    def __init__(self, player_name, email):

        self.player_name = player_name
        self.email = email
        self.saves_folder = config.SAVES_FOLDER
        self.quests = {}

        self.save_bin_path = join(self.saves_folder, '{0}.bin'.format(self.player_name))
        self.logs_path = join(self.saves_folder, '{0}.logs.db'.format(self.player_name))

    # PUBLIC:

    def load_progress(self):
        if not self.profile_exists():
            self.__save_progress()
        else:
            with open(self.save_bin_path, 'rb') as f:
                self.quests = load(f)

    def start_work(self, quest_name, timestamp=None):
        timestamp = timestamp or parse_timestamp(str(datetime.today()))
        if isinstance(timestamp, str):
            timestamp = parse_timestamp(timestamp)

        self.__start_work(quest_name, timestamp)
        self.__save_progress()

    def log_work(self, quest_name, points, bookmark, timestamp=None):
        timestamp = timestamp or parse_timestamp(datetime.today())
        if isinstance(timestamp, str):
            timestamp = parse_timestamp(timestamp)

        self.__log_work(quest_name, timestamp, points, bookmark)
        self.__save_progress()

    def add_quest(self, quest_name, points, instruction, color=None):
        self.__add_quest(quest_name, points, instruction, color=color)
        self.__save_progress()

    def edit_quest_meta(self, quest_name, instruction=None, color=None):
        self.__edit_quest_meta(quest_name, instruction=instruction, color=color)
        self.__save_progress()

    def remove_quest(self, quest_name):
        self.__remove_quest(quest_name)
        self.__save_progress()

    def profile_exists(self):
        makedirs(self.saves_folder, exist_ok=True)
        return isfile(self.save_bin_path)

    def show_quests(self):
        self.__update_quests()
        return self.quests

    def show_logs(self, limit):
        logs_obj = Logs(self.logs_path)
        logs = logs_obj.get_logs(where=f'1 LIMIT {int(limit)}')
        return logs

    # PRIVATE:

    def __save_progress(self):
        makedirs(self.saves_folder, exist_ok=True)
        with open(self.save_bin_path, 'wb') as wb:
            dump(self.quests, wb, protocol=HIGHEST_PROTOCOL)

    def __add_quest(self, quest_name, points, instruction, color=None):
        """
        Структура квестов:
        quests = {
            'quest_name': {                     # [str] видимое имя квеста
                'id': 000000000000              # [int] id квеста, использующееся в БД
                'start_timestamp': None,        # [Timestamp] время начала выполнения (если квест сейчас выполняется)
                'first_date': None,             # [date] дата окончания первого выполнения квеста (если был выполнен)
                'last_date': None,              # [date] дата окончания последнего выполнения квеста (если был выполнен)
                'points': {                     # [dict] все подсчеты по выполнению квеста
                    'point_name': {             # [str] видимое название этого подсчета
                        'norm': 60,             # [int] норма очков в день по выполнению квеста
                        'type': 'int',          # [str] тип подсчета (int, bool)
                        'total_points': 0,      # [int] всего очков по этому квесту с самого начала
                        'points_to_do': 0,      # [int] очки, которых не хватает по расчету прямо сейчас
                        'recommended': 0}       # [int] рекомендуемое количество очков для выполнения прямо сейчас
                    },
                'instruction': 'instruction',   # [str] краткая инструкция, как начать выполнение
                'color': color or '#000000',    # [str] цвет квеста (только для графического интерфейса)
            }
        }

        :param quest_name: 'name'
        :param points: {'Minuten': {'norm': 60, 'type': 'minutes'}, ...}
        :param instruction: 'how to start work easily'
        :param color: '#0099FF' hex RGB color
        """
        assert_person(quest_name not in self.quests,
                      f'quest named {quest_name} already exists')
        assert_person(points,
                      'empty dict "points"')
        assert_person(all(('norm' in v and 'type' in v and len(v) == 2 for v in points.values())),
                      'incorrect points structure')

        self.quests.update({
            quest_name: {
                'id': randint(100000000000, 999999999999),
                'start_timestamp': None,
                'first_date': None,
                'last_date': None,
                'points': points,
                'instruction': instruction,
                'color': color or '#000000',
            }
        })

        for point in points:
            point_obj = self.quests[quest_name]['points'][point]
            point_obj.update({'total_points': 0, 'points_to_do': 0, 'recommended': 0})

    def __update_quests(self):
        # update points_to_do
        for name in self.quests:
            quest = self.quests[name]
            if quest['first_date'] is not None:
                for point_name in quest['points']:
                    point = quest['points'][point_name]
                    point['points_to_do'] = (datetime.today().date() - quest['first_date'] + timedelta(days=1)
                                             ).days * point['norm'] - point['total_points']
            else:
                for point_name in quest['points']:
                    point = quest['points'][point_name]
                    point['points_to_do'] = point['norm']

        # update recommended
        # for name in self.quests:
        #     quest = self.quests[name]
        #     if quest['first_date'] is None:
        #         for point_name in quest['points']:
        #             point = quest['points'][point_name]
        #             point['recommended'] = point['norm']
        #     else:
        #         for point_name in quest['points']:
        #             point = quest['points'][point_name]
        #             if point['points_to_do'] >= 0:
        #                 if quest['last_date'] == datetime.today().date():
        #                     point['recommended'] = 0
        #                 else:
        #                     point['recommended'] = point['norm'] / 2
        #             else:
        #                 point['recommended'] = -point['points_to_do']

    def __edit_quest_meta(self, quest_name, instruction=None, color=None):
        assert_person(quest_name in self.quests,
                      f'quest named "{quest_name}" not found')
        if instruction is not None:
            self.quests[quest_name]['instruction'] = str(instruction)
        if color is not None:
            self.quests[quest_name]['color'] = str(color)

    def __start_work(self, quest_name, timestamp):
        assert_person(quest_name in self.quests,
                      f'quest named {quest_name} not found')
        assert_person(self.quests[quest_name]['start_timestamp'] is None,
                      f'quest named {quest_name} is already started')

        quest = self.quests[quest_name]

        # проверить, что указанное время старта равно или позже последнего лога по этому квесту
        logs_obj = Logs(self.logs_path)
        logs = logs_obj.get_logs(select=['timestamp'],
                                 where=f'quest_id="{quest["id"]}" AND action="log_work"')
        if logs:
            last_log_timestamp = logs[-1][0]
            last_log_timestamp = parse_timestamp(last_log_timestamp)
            assert_person(last_log_timestamp <= timestamp,
                          f'the given start datetime ({timestamp})'
                          f' is before a last log of the quest ({last_log_timestamp})')

        quest['start_timestamp'] = timestamp

        logs_obj.log(
            timestamp=str(timestamp),
            quest_id=quest['id'],
            action='start_work',
            points={},
            bookmark='')
        logs_obj.close()

    def __log_work(self, quest_name, timestamp, points, bookmark):
        """
        :param quest_name: 'name'
        :param timestamp: pandas.Timestamp object
        :param points: {'Minuten': 48, }
        :param bookmark: 'any text'
        """
        assert_person(quest_name in self.quests,
                      f'quest named {quest_name} not found')

        quest = self.quests[quest_name]

        assert_person(quest['start_timestamp'] is not None,
                      f'quest named {quest_name} is not started')
        assert_person(quest['start_timestamp'] <= timestamp,
                      f'the given log timestamp ({timestamp})'
                      f' is after a start timestamp of the quest ({quest["start_timestamp"]})')

        for point_name in points:
            assert_person(point_name in quest['points'],
                          f'point named {point_name} is not in quest {quest_name} points')

        quest['bookmark'] = bookmark
        for point_name in points:
            point = quest['points'][point_name]
            point['total_points'] += points[point_name]

        date = timestamp.date()
        if quest['first_date'] is None:
            quest['first_date'] = date
        quest['last_date'] = date

        quest['start_timestamp'] = None

        logs_obj = Logs(self.logs_path)
        logs_obj.log(
            timestamp=str(timestamp),
            quest_id=quest['id'],
            action='log_work',
            points=points,
            bookmark=bookmark)
        logs_obj.close()

    def __remove_quest(self, quest_name):
        assert_person(quest_name in self.quests,
                      f'quest named {quest_name} not found')
        self.quests.pop(quest_name)


if __name__ == '__main__':

    person = Person('hakerok_igorek', 'hack@gmail.com')
    # загружаем прогресс
    person.__load_progress()

    # создаем новый квест
    person.__add_quest(
        quest_name='hack_americans',
        points={'Minuten': {'norm': 15, 'type': 'minutes'}},
        instruction='just bruteforce penta(gon)',
        color='#fc0fc0')

    # позже редактируем этот квест, если нужно
    # person.edit_quest(name='english', instruction='chill and read', color=None)

    # перед работой пересчитываем недостающие очки квеста на данный момент
    # и рекомендуемые объемы работы на данный момент
    person.__update_quests()

    # начинаем выполнение квеста
    person.__start_work(quest_name='hack_americans', timestamp=datetime.today() - timedelta(minutes=15))

    # заканчиваем выполнение квеста
    person.__log_work(
        quest_name='hack_americans',
        timestamp=datetime.today(),
        points={'Minuten': 15},
        bookmark='this time was the easiest; the key is to make a coffee')

    # после работы пересчитываем недостающие очки квеста на данный момент
    # и рекомендуемые объемы работы на данный момент
    person.__update_quests()

    # при необходимости удаляем квест
    # person.remove_quest(name='english')

    # сохраняем прогресс
    person.__save_progress()
