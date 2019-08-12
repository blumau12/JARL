from pandas import DataFrame, Timedelta, datetime, MultiIndex
from pickle import load, dump, HIGHEST_PROTOCOL
from os import mkdir
from os.path import isdir, isfile, join

# run configuration variables: -----------------------------------------------------------------------------------------

saves_path = ['saves']

# script global variables: ---------------------------------------------------------------------------------------------

quests = {}
# {'de': {'start_timestamp': None,
#         'first_date': None,
#         'last_date': None,
#         'points': {'Minuten': {'norm': 60, 'type': 'minutes',
#                    'total_points': 0, 'current_points': 0, 'recommended': 60},
#         'instruction': 'Take a book, open last read page and read. Last page number:',
#         'bookmark': '594',
#         'color': '#EE88AA'}}}
# points types: minutes, boolean, number, list, entry

logs = DataFrame(columns=['name', 'points', 'bookmark'],
                 index=MultiIndex(levels=[[], []], codes=[[], []]))
# index: (date, id)

# ----------------------------------------------------------------------------------------------------------------------


def load_progress(name):
    global quests, logs
    file_path = join(join(*saves_path), '{0}.bin'.format(name))
    if not isdir(saves_path) or not isfile(file_path):
        return False
    with open(file_path, 'rb') as f:
        quests = load(f)
        logs = load(f)


def save_progress(name):
    file_path = join(join(*saves_path), '{0}.bin'.format(name))
    for folder in saves_path:
        folder_path = join(*saves_path[:saves_path.index(folder) + 1])
        if not isdir(folder_path):
            mkdir(folder_path)
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
        quests[name]['points'][point].update({'total_points': 0, 'current_points': 0, 'recommended': 0})
    return True


def update_current_points():
    for name in quests:
        quest = quests[name]
        if quest['first_date'] is not None:
            for point_name in quest['points']:
                point = quest['points'][point_name]
                point['current_points'] = (datetime.today().date() - quest['first_date'] + Timedelta('1 days')
                                           ).days * point['norm'] - point['total_points']


def update_recommended():
    # update_current_points first
    for name in quests:
        quest = quests[name]
        if quest['first_date'] is None:
            for point_name in quest['points']:
                point = quest['points'][point_name]
                point['recommended'] = point['norm']
        else:
            for point_name in quest['points']:
                point = quest['points'][point_name]
                if point['current_points'] >= 0:
                    if point['last_date'] == datetime.today().date():
                        point['recommended'] = 0
                    else:
                        point['recommended'] = point['norm'] / 2
                else:
                    point['recommended'] = -point['current_points']


def edit_quest(name, instruction=None, color=None):
    if name not in quests:
        return False
    if instruction is not None:
        quests[name]['instruction'] = str(instruction)
    if color is not None:
        quests[name]['color'] = str(color)


def start_work(name, time):
    if name not in quests or quests[name]['start_timestamp'] is not None:
        return False
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
    quest['last_date'] = date
    next_index = max(logs.index.levels[1]) + 1
    logs.loc[(next_index, date), logs.columns] = [str(name), str(points), str(bookmark)]


def remove_quest(name):
    if name not in quests:
        return False
    quests.pop(name)
    return True
