from person import Person
from datetime import datetime
from collections import OrderedDict

import config
from time_lib import parse_timestamp
from exceptions import PersonError

# TODO: handle core exceptions like timestamps comparison


class Session:
    def __init__(self, name=None, email=None):
        self.ps = None
        self.name = name
        self.email = email
        self.__start()

    def __start(self):
        dt = datetime.today()
        a = dt.time().hour
        greet = None
        if 0 <= a < 4:
            greet = 'Gute Nacht'
        elif 4 <= a < 12:
            greet = 'Guten Morgen'
        elif 12 <= a < 18:
            greet = 'Guten Tag'
        elif 8 <= a < 24:
            greet = 'Guten Abend'
        text = f'{greet}, mein Jarl!\n'
        self.__print(text)
        self.__ask_for_person()
        self.__run()

    def __ask_for_person(self):
        if self.name and self.email:
            self.__print(f'Logging as {self.name} ({self.email})...\n')
        else:
            text = 'Please type your profile name\n'
            self.__print(text)
            self.name = self.__input()
            text = 'Please type your profile email\n'
            self.__print(text)
            self.email = self.__input()

        self.ps = Person(self.name, self.email)
        profile_exists = self.ps.profile_exists()
        if profile_exists:
            text = 'Loading existing profile...\n'
        else:
            text = 'Create new profile...\n'
        self.__print(text)
        self.ps.load_progress()

    def __run(self):
        while True:
            text = "\nWas wollen Sie?\n"
            prompt = OrderedDict((
                ('1', 'start work'),
                ('2', 'log work'),
                ('3', 'show quests'),
                ('4', 'add quest'),
                ('5', 'edit quest meta'),
                ('6', 'remove quest'),
            ))
            prompt.update({'x': 'exit'})
            text += self.__construct_prompt(prompt)
            self.__print(text)
            i = self.__input(values=prompt)

            if i == '1':
                self.__start_work()
            elif i == '2':
                self.__log_work()
            elif i == '3':
                self.__show_quests()
            elif i == '4':
                self.__add_quest()
            elif i == '5':
                self.__edit_quest_meta()
            elif i == '6':
                self.__remove_quest()
            elif i == 'x':
                break

        self.__exit()

    def __start_work(self):
        enumeration = enumerate((q for q in self.ps.quests if self.ps.quests[q]['start_timestamp'] is None), 1)
        quests_dict = OrderedDict((str(i), name) for i, name in enumeration)
        if quests_dict:
            text = 'Which quest you want to start?\n'
            quests_dict.update({'x': 'exit'})
            text += self.__construct_prompt(quests_dict)
            self.__print(text)
            i = self.__input(values=quests_dict)
            if i == 'x':
                return
            quest_name = quests_dict[i]

            timestamp = None
            while True:
                text = "When you gonna start it?\n"
                prompt = OrderedDict((
                    ('1', 'now'),
                    ('2', 'custom time in the past'),
                ))
                prompt.update({'x': 'exit'})
                text += self.__construct_prompt(prompt)
                self.__print(text)
                i = self.__input(values=prompt)
                if i == '2':
                    timestamp = self.__input_timestamp()
                elif i == 'x':
                    return

                try:
                    self.ps.start_work(quest_name, timestamp=timestamp)
                except PersonError as e:
                    text = f'{e}\n'
                    self.__print(text)
                    continue

                break
        else:
            text = 'No quests that can be started. You should create a quest first\n'
            self.__print(text)

    def __log_work(self):
        enumeration = enumerate((q for q in self.ps.quests if self.ps.quests[q]['start_timestamp'] is not None), 1)
        quests_dict = OrderedDict((str(i), name) for i, name in enumeration)
        if quests_dict:
            quests_dict.update({'x': 'exit'})
            text = 'Which quest you want to stop?\n'
            text += self.__construct_prompt(quests_dict)
            self.__print(text)
            i = self.__input(values=quests_dict)
            if i == 'x':
                return
            quest_name = quests_dict[i]
            quest = self.ps.quests[quest_name]

            timestamp = None
            text = "When you gonna stop it?\n"
            prompt = OrderedDict((
                ('1', 'now'),
                ('2', 'custom time in the past'),
            ))
            prompt.update({'x': 'exit'})
            text += self.__construct_prompt(prompt)
            self.__print(text)
            i = self.__input(values=prompt)
            if i == '2':
                timestamp = self.__input_timestamp()
            elif i == 'x':
                return

            bookmark = ''
            while True:
                text = 'Please type a description of that time evaluation\n'
                self.__print(text)
                i = self.__input()
                if not i:
                    continue
                bookmark = i
                break

            points = {}
            for point_name in quest['points']:
                point = quest['points'][point_name]
                typ = point['type']
                if typ == 'int':
                    while True:
                        text = f'How much {point_name} did you earn?\n'
                        self.__print(text)
                        i = self.__input()
                        try:
                            i = int(i)
                        except ValueError:
                            self.__print(f'Please type exact number of {point_name}')
                            continue
                        break
                elif typ == 'bool':
                    text = f'Have you done {point_name}?\n'
                    prompt = OrderedDict((
                        ('y', 'yes'),
                        ('n', 'no'),
                    ))
                    prompt.update({'x': 'exit'})
                    text += self.__construct_prompt(prompt)
                    self.__print(text)
                    i = self.__input(values=prompt)
                    if i == 'x':
                        return
                    i = i == 'y'
                points[point_name] = i

            self.ps.log_work(quest_name, points, bookmark, timestamp=timestamp)
        else:
            text = 'No started quests.\n'
            self.__print(text)

    def __show_quests(self):
        quests = self.ps.show_quests()
        if quests:
            text = 'Current quests:\n'
            for quest_name in quests:
                quest = quests[quest_name]
                started_mark = "not started"
                if quest["start_timestamp"] is not None:
                    started_mark = "STARTED"
                    if quest["start_timestamp"].date() < datetime.today().date():
                        started_mark += f' {quest["start_timestamp"].date()}'
                    started_mark += f' at {quest["start_timestamp"].time()} {quest["start_timestamp"].tzinfo}'
                text += f' > {quest_name} [{started_mark}]:\n' \
                        f'   {quest["instruction"]}\n' \
                        f'   points:\n'
                for point_name in quest['points']:
                    point = quest['points'][point_name]
                    text += f'      {point["recommended"]} {point_name} recommended\n' \
                            f'      total {point["points_to_do"]} to do ({point["norm"]} per day)\n'
        else:
            text = 'No quests.\n'
        self.__print(text)

    def __add_quest(self):
        while True:
            text = '\nPlease type a new quest name\n'
            self.__print(text)
            quest_name = self.__input()
            if not quest_name:
                continue
            break

        while True:
            text = '\nPlease type a new quest start instruction\n'
            self.__print(text)
            instruction = self.__input()
            if not instruction:
                continue
            break

        points = self.__input_new_points()
        if points:
            self.ps.add_quest(quest_name, points, instruction)

    def __edit_quest_meta(self):
        quests_dict = OrderedDict((str(i), name) for i, name in enumerate(self.ps.quests, 1))
        if quests_dict:
            quests_dict.update({'x': 'exit'})
            text = 'Which quest you want to edit?\n'
            text += self.__construct_prompt(quests_dict)
            self.__print(text)
            i = self.__input(values=quests_dict)
            if i == 'x':
                return
            quest_name = quests_dict[i]
            quest = self.ps.quests[quest_name]

            instruction = None
            text = f'Do you want to change this quest instruction?\n' \
                   f'(current: {quest["instruction"]})\n'
            prompt = OrderedDict((
                ('y', 'yes'),
                ('n', 'no'),
            ))
            prompt.update({'x': 'exit'})
            text += self.__construct_prompt(prompt)
            self.__print(text)
            i = self.__input(values=prompt)
            if i == 'x':
                return
            if i == 'y':
                text = 'Please type a new instruction\n'
                self.__print(text)
                i = self.__input()
                instruction = i

            self.ps.edit_quest_meta(quest_name, instruction=instruction)
            self.__print('The quest meta updated.\n')
        else:
            text = 'No quests. You should create a quest first\n'
            self.__print(text)

    def __remove_quest(self):
        quests_dict = OrderedDict((str(i), name) for i, name in enumerate(self.ps.quests, 1))
        if quests_dict:
            quests_dict.update({'x': 'exit'})
            text = '\nWhich quest you want to remove?\n'
            text += self.__construct_prompt(quests_dict)
            self.__print(text)
            i = self.__input(values=quests_dict)
            if i == 'x':
                return
            quest_name = quests_dict[i]

            text = f'\nRemove quest {quest_name}. Are you sure?\n'
            prompt = OrderedDict((
                ('y', 'yes'),
                ('n', 'no'),
            ))
            text += self.__construct_prompt(prompt)
            self.__print(text)
            i = self.__input(values=prompt)
            if i == 'y':
                self.ps.remove_quest(quest_name)
                self.__print('Quest removed.\n')
        else:
            text = 'No quests. You should create a quest first\n'
            self.__print(text)

    def __exit(self):
        text = 'Auf wiedersehen, mein Jarl\n'
        self.__print(text)
        exit(88)

    def __input(self, values=None):
        while True:
            i = input()
            if values is not None and i not in values:
                text = f'Please type one of the following:\n'
                text += self.__construct_prompt(values)
                self.__print(text)
                continue
            break
        return i

    def __input_timestamp(self):
        text = 'Which date?\n'
        prompt = OrderedDict((
            ('1', 'today'),
            ('2', 'other date'),
        ))
        text += self.__construct_prompt(prompt)
        self.__print(text)
        i = self.__input(values=prompt)
        str_date = ''
        if i == '1':
            str_date = str(datetime.today().date())
        elif i == '2':
            while True:
                text = 'Please type exact date in format dd-mm-yyyy\n'
                self.__print(text)
                i = self.__input()
                try:
                    parse_timestamp(f'{i} 00:00')
                except ValueError:
                    text = 'Incorrect date format.\n'
                    self.__print(text)
                    continue
                str_date = i
                break

        str_time = ''
        while True:
            text = 'Please type exact time in format HH:MM or HH:MM:SS\n'
            self.__print(text)
            i = self.__input()
            try:
                parse_timestamp(f'15-10-1994 {i}')
            except ValueError:
                text = 'Incorrect time format.\n'
                self.__print(text)
                continue
            str_time = i
            break

        str_tz = ''
        if config.ASK_FOR_TIMEZONE:
            while True:
                text = 'Which timezone?\n'
                prompt = OrderedDict((
                    ('1', 'use computer tz'),
                    ('2', 'custom tz'),
                ))
                text += self.__construct_prompt(prompt)
                self.__print(text)
                i = self.__input(values=prompt)
                if i == '2':
                    text = 'Please type timezone in format +(-)H or +(-)HH or +(-)HHMM'
                    self.__print(text)
                    i = self.__input()
                    if i == '0':
                        i = '+0'
                    try:
                        parse_timestamp(f'15-10-1994 21:00:00{i}')
                    except ValueError:
                        text = 'Incorrect timezone format.\n'
                        self.__print(text)
                        continue
                    str_tz = i
                break
        timestamp = parse_timestamp(f'{str_date} {str_time}{str_tz}')

        return timestamp

    def __input_new_points(self):
        points = {}
        while True:
            while True:
                text = '\n' \
                       'Please type a new point name with the following rules:\n' \
                       ' * a numeric point should be called like "minutes" or "sentences"\n' \
                       ' * a boolean point should be called like "learn grammar" or "special exercise"\n'
                self.__print(text)
                point_name = self.__input()
                if not point_name:
                    self.__print('Empty point name given.\n')
                    continue
                if point_name in points:
                    self.__print('A point with that name already exists.\n')
                    continue
                break

            while True:
                text = '\n' \
                       'Please enter a daily rate of this point with the following rules:\n' \
                       ' * the daily rate number means number of some points that you earn, like minutes or sentences\n' \
                       ' * a boolean point should have daily rate about 1-3 depending on how much times in a day you gonna do that action"\n'
                self.__print(text)
                norm = self.__input()
                if not norm:
                    self.__print('Empty daily rate given.\n')
                    continue
                try:
                    norm = int(norm.strip())
                except ValueError:
                    text = 'Daily rate must be an integer.\n'
                    self.__print(text)
                    continue
                break

            text = '\n' \
                   'Please choose type of the new point\n'
            prompt = OrderedDict((
                ('1', 'numeric, integer'),
                ('2', 'boolean, a fact of an action'),
            ))
            text += self.__construct_prompt(prompt)
            self.__print(text)
            typ = self.__input(values=prompt)
            if typ == '1':
                typ = 'int'
            elif typ == '2':
                typ = 'bool'

            text = f'\n' \
                   f'Add point "{point_name}" [{typ}] with daily rate {norm}. Are you sure?\n'
            prompt = OrderedDict((
                ('y', 'yes, add that point'),
                ('n', 'no, skip that point'),
            ))
            text += self.__construct_prompt(prompt)
            self.__print(text)
            i = self.__input(values=prompt)
            if i == 'y':
                points[point_name] = {'norm': norm, 'type': typ}
                text = 'Added that point.\n'
                self.__print(text)

            text = "\nWould you like to add another point?\n"
            prompt = OrderedDict((
                ('y', 'yes'),
                ('n', 'no'),
            ))
            text += self.__construct_prompt(prompt)
            self.__print(text)
            i = self.__input(values=prompt)
            if i == 'n':
                break

        return points

    @staticmethod
    def __print(text):
        print(text, end='')

    @staticmethod
    def __construct_prompt(dictionary):
        text = []
        for i, t in dictionary.items():
            text.append(f'  [{i}] {t}\n')
        text = ''.join(text)
        return text


if __name__ == '__main__':
    s = Session(name='karl', email='killer')
