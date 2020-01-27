from pandas import DataFrame, Timedelta, datetime, MultiIndex
from pickle import load, dump, HIGHEST_PROTOCOL
from os import makedirs
from os.path import isfile, join

# run configuration variables: -----------------------------------------------------------------------------------------

saves_folder = 'saves'

# script global variables: ---------------------------------------------------------------------------------------------

quests = {}
# points types: minutes, boolean, number, list, entry

logs = DataFrame(columns=['name', 'points', 'bookmark'],
                 index=MultiIndex(levels=[[], []], codes=[[], []]))
# index: (date, id)

# ----------------------------------------------------------------------------------------------------------------------


def load_progress(name):
    global quests, logs
    makedirs(saves_folder, exist_ok=True)
    file_path = join(saves_folder, '{0}.bin'.format(name))
    if not isfile(file_path):
        return False
    with open(file_path, 'rb') as f:
        quests = load(f)
        logs = load(f)


def save_progress(name):
    file_path = join(saves_folder, '{0}.bin'.format(name))
    for folder in saves_folder:
        folder_path = join(*saves_folder[:saves_folder.index(folder) + 1])
        makedirs(folder_path, exist_ok=True)
    with open(file_path, 'wb') as f:
        dump(quests, f, protocol=HIGHEST_PROTOCOL)
        dump(logs, f, protocol=HIGHEST_PROTOCOL)


def add_quest(name, points, instruction, color):
    """
    :param name: 'name'
    :param points: {'Minuten': {'norm': 60, 'type': 'minutes'}, }
    :param instruction: 'how to start work easily'
    :param color: '#0099FF' hex RGB color
    """
    if name in quests:
        return False
    quests.update({name: {'start_timestamp': None,
                          'first_date': None,
                          'last_date': None,
                          'points': points,
                          'instruction': instruction,
                          'color': color}})
    for point in points:
        quests[name]['points'][point].update({'total_points': 0, 'points_to_do': 0, 'recommended': 0})
    return True


def update_points_to_do():
    for name in quests:
        quest = quests[name]
        if quest['first_date'] is not None:
            for point_name in quest['points']:
                point = quest['points'][point_name]
                point['points_to_do'] = (datetime.today().date() - quest['first_date'] + Timedelta('1 days')
                                         ).days * point['norm'] - point['total_points']


def update_recommended():
    # update_points_to_do first
    for name in quests:
        quest = quests[name]
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


def edit_quest(name, instruction=None, color=None):
    if name not in quests:
        return False
    if instruction is not None:
        quests[name]['instruction'] = str(instruction)
    if color is not None:
        quests[name]['color'] = str(color)


def start_work(name, time):
    if name not in quests or quests[name]['start_timestamp'] is not None:
        raise Exception('bad quest start')
    quests[name]['start_timestamp'] = time
    return True


def log_work(name, time, points, bookmark):
    """
    :param name: 'name'
    :param time: datetime.datetime object
    :param points: {'Minuten': 48, }
    :param bookmark: 'any text'
    """
    if name not in quests:
        return False
    quest = quests[name]
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
    if not logs.empty:
        next_index = max(logs.index.levels[0]) + 1
    else:
        next_index = 0
    logs.loc[(next_index, date), logs.columns] = [str(name), str(points), str(bookmark)]
    quest['start_timestamp'] = None


def remove_quest(name):
    if name not in quests:
        return False
    quests.pop(name)
    return True


if __name__ == '__main__':
    # загружаем данные прошлых сессий
    load_progress('hakerok_igorek')

    # создаем новый квест
    # add_quest(
    #     name='hack_americans',
    #     points={'Minuten': {'norm': 15, 'type': 'minutes'}},
    #     instruction='just bruteforce penta(gon)',
    #     color='#fc0fc0')

    # позже редактируем этот квест, если нужно
    # edit_quest(name='english', instruction='chill and read', color=None)

    # перед работой пересчитываем недостающие очки квеста на данный момент
    update_points_to_do()

    # пересчитываем рекомендуемые объемы работы на данный момент
    update_recommended()

    # начинаем выполнение квеста
    start_work(name='hack_americans', time=datetime.today() - Timedelta(1, 'm'))

    # заканчиваем выполнение квеста
    log_work(
        name='hack_americans',
        time=datetime.today(),
        points={'Minuten': 15},
        bookmark='this time was an easiest; the key is to make a coffee')

    # после работы пересчитываем недостающие очки квеста на данный момент
    update_points_to_do()

    # пересчитываем рекомендуемые объемы работы на данный момент
    update_recommended()

    # при необходимости удаляем квест
    # remove_quest(name='english')

    # сохраняем прогресс в базу
    save_progress('hakerok_igorek')

    pass
