import tkinter as tk
import pickle
import jarl_classes as jc
import datetime as dt
import descriptions


class MapButton(tk.Button):
    def __init__(self, mapp, index, **kw):
        super().__init__(**kw)
        self.map = mapp
        self.index = index
        maps_dict[mapp]['map_button'] = self
        MapIndicator(mapp)

    def map_button(self):
        set_map(self.index)

    def update_elo(self):
        if self.map.stability < 0.9:
            self['text'] = self.map.name.upper() + '\n' \
                           + '(stab.: ' \
                           + str(int(100 * self.map.stability) / 100) + ')' \
                           + '\n' + str(int(self.map.gain))
        else:
            self['text'] = self.map.name.upper() + '\n\n' + str(round(self.map.gain))


class MapIndicator(tk.Label):
    def __init__(self, mapp, **kw):
        super().__init__(**kw)
        self.mapp = mapp
        self.color = 0.1
        self.highlighted = False
        maps_dict[mapp]['indicator'] = self
        self.refresh()
        self.place(x=0, y=61, relx=maps.index(mapp) / len(maps), relwidth=1 / len(maps), width=0, height=9)

    def refresh(self):
        self.mapp.refresh()

        if not self.highlighted:
            just_calculate_quests(self.mapp)
            self.configure(bd=0, bg=color_dict_blue[maps_dict[self.mapp]['max_r']])

    def flag_on(self):
        self.highlighted = True
        self.configure(bd=0, bg='#F5C65B')

    def flag_off(self):
        self.highlighted = False
        self.refresh()


class QuestImage(tk.Frame):
    def __init__(self, quest, **kwargs):
        super().__init__(**kwargs)
        self.quest = quest
        quests_dict[quest] = {}
        quests_dict[quest]['quest_image'] = self
        self.place(x=0, y=blue.y_pos, height=15 + self.quest.level * 20, relwidth=1)

        # label квеста:
        self.quest_label = LabelButton(quest, master=self)
        self.refresh_label_desc()
        # кнопка выполнения:
        self.plus_button = PlusButton(quest, master=self)
        # кнопка доп. меню квеста:
        self.plus_menubutton = TimestampLabel(quest, master=self)
        # счетчик заполненных пикселей:
        blue.y_pos += 16 + quest.level * 20
        self.refresh()

    def refresh(self):
        quests_dict[self.quest]['quest_image'].quest_label.configure(bg=color_dict_blue[self.quest.relevance])

        quests_dict[self.quest]['quest_image'].plus_button.refresh()

        quests_dict[self.quest]['quest_image'].plus_menubutton.refresh()

    def refresh_label_desc(self):
        descriptions.button_description(self.quest_label, 'best time:\n' + self.quest.description[0], self)


class LabelButton(tk.Button):
    def __init__(self, quest, **kw):
        super().__init__(**kw)
        self.quest = quest
        self.configure(text=self.quest.name, bd=0, bg='#00B5D7', foreground='white', activeforeground='white',
                       activebackground='#00CEF0', command=lambda: QuestDescriptionWindow(self.quest))
        quests_dict[quest]['quest_image'].label_button = self
        self.place(x=0, y=0, relheight=1, width=-50, relwidth=0.9)


class PlusButton(tk.Button):
    def __init__(self, quest, **kw):
        super().__init__(**kw)
        self.quest = quest
        self.configure(bd=0, activebackground='#00CC00', foreground='white', activeforeground='white',
                       command=lambda: CustomTimeOfPerformingWindow(self.quest))
        quests_dict[quest]['quest_image'].plus_button = self
        self.place(anchor=tk.NE, x=-40, relx=1, y=0, relheight=1, width=10, relwidth=0.1)

    def press(self, desc, time=None):
        if not time:
            time = dt.datetime.today()
        self.quest.do_perform(time)
        self.quest.history.append([time, desc])
        maps_dict[maps[selected_map]]['map_button'].update_elo()
        do_reload_quests()

        # timestamp:
        quests_dict[self.quest]['plus_menubutton']['text'] = quests_dict[self.quest]['plus_menubutton'].generate_text()

        # и самое главное:
        save_progress()

    def refresh(self):
        quests_dict[self.quest]['quest_image'].plus_button.configure(text='+' + str(int(self.quest.plus)),
                                                                     bg=color_dict_green[self.quest.relevance])


class TimestampLabel(tk.Label):
    def __init__(self, quest, **kw):
        super().__init__(**kw)
        self.quest = quest
        self.configure(bg='#EAF7F9', bd=0, activebackground='#00D2F4', foreground='#FFF', activeforeground='#FFF')
        quests_dict[quest]['plus_menubutton'] = self

        self['text'] = self.generate_text()
        self.place(x=-40, relx=1, y=0, relheight=1, width=40)

    def generate_text(self):
        if self.quest.last_performed:
            start_t = self.quest.last_performed + self.quest.period
            day = str(start_t.date().day)
            hour = str(start_t.hour)
            minute = str(start_t.minute)
            if len(hour) == 1:
                hour = '0' + hour
            if len(minute) == 1:
                minute = '0' + minute
            if start_t.date() != jc.dt.datetime.today().date():
                text = '{0} {1}\n{2}:{3}'.format(day, months[start_t.date().month], hour, minute)
            else:
                text = '{0}:{1}'.format(hour, minute)
        else:
            text = 'new'
        return text

    def refresh(self):
        self['bg'] = color_dict_blue[self.quest.relevance]


class MapsWindow(tk.Toplevel):
    def __init__(self):
        super().__init__(main_window)

        self.title('JARL - configure maps')
        self.geometry('+832+260')
        self.resizable(False, False)
        self.grab_set()
        self.focus_set()

        self.maps_listbox = tk.Listbox(self, height=8)
        for item in maps:
            self.maps_listbox.insert(tk.END, item)
        self.maps_listbox.grid(row=0, column=0, rowspan=4)
        self.current = None

        tk.Label(self, text='map name:', anchor=tk.E).grid(row=0, column=1)
        self.name_entry = tk.Entry(self, width=11)
        self.name_entry.grid(row=0, column=2)

        tk.Label(self, text='map color:', anchor=tk.E).grid(row=1, column=1)
        self.color_entry = tk.Entry(self, width=11)
        self.color_entry.grid(row=1, column=2)

        tk.Button(self, text='Save changes').grid(row=2, column=1, columnspan=2, sticky=tk.W + tk.E + tk.N + tk.S)
        tk.Button(self, text='New map').grid(row=3, column=1, sticky=tk.W + tk.E + tk.N + tk.S)
        tk.Button(self, text='Remove map').grid(row=3, column=2, sticky=tk.W + tk.E + tk.N + tk.S)

        self.real_time()

    def real_time(self):
        now = self.maps_listbox.curselection()
        if now != self.current:
            self.list_has_changed(now)
            self.current = now
        self.after(100, self.real_time)

    def list_has_changed(self, selection):
        if selection:
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, self.maps_listbox.get(selection[0]))


class QuestDescriptionWindow(tk.Toplevel):  # do good
    def __init__(self, quest):
        super().__init__(main_window)

        self.title('JARL - desc. of "{0}"'.format(quest.name))
        self.geometry('+832+260')
        self.resizable(False, False)
        self.grab_set()
        self.focus_set()

        self.quest = quest

        # window constructing: -----------------------------------------------------------------------------------------
        self.desc1 = tk.Entry(self, width=40)
        self.desc2 = tk.Text(self, width=30, height=10)
        tk.Label(self, text='approximate time of performing quest:').grid(row=0, column=0, sticky=tk.W)
        self.desc1.grid(row=1, column=0, sticky=tk.W)
        tk.Label(self, text='description of quest:').grid(row=2, column=0, sticky=tk.W)
        self.desc2.grid(row=3, column=0, sticky=tk.W)
        tk.Button(self, text='Show\nhistory', bg='#F3C475', foreground='white', bd=0, activebackground='#FFCE79',
                  activeforeground='white', command=lambda: self.ShowHistory(self.quest)).grid\
            (row=0, column=1, rowspan=4, sticky=tk.N+tk.S+tk.W+tk.E)

        tk.Button(self, text='Apply', bg='#00B5D7', foreground='white', bd=0, command=self.press_apply,
                  activeforeground='white', activebackground='#00CEF0', height=2).\
            grid(row=4, column=0, columnspan=2, sticky=tk.N+tk.S+tk.W+tk.E)
        # --------------------------------------------------------------------------------------------------------------
        self.desc1.insert(0, self.quest.description[0])
        self.desc2.insert('1.0', self.quest.description[1])

    def press_apply(self):
        self.quest.description = [self.desc1.get(), self.desc2.get('1.0', tk.END)]
        quests_dict[self.quest]['quest_image'].refresh_label_desc()
        save_progress()
        self.destroy()

    class ShowHistory(tk.Toplevel):
        def __init__(self, quest):
            super().__init__(main_window)

            self.title('JARL - history of "{0}"'.format(quest.name))
            self.geometry('+832+260')
            self.resizable(False, False)
            self.grab_set()
            self.focus_set()

            self.quest = quest
            history_str = ''
            for time, desc in self.quest.history[::-1]:
                minute = str(time.time().minute)
                if len(minute) == 1:
                    minute = '0' + minute
                history_str += '{0}\n{1} {2} {3} - {4}:{5}\n{6}\n'.format('-'*32, time.date().year, months[time.date().month], time.date().day, time.time().hour, minute, desc)

            scrollbar = tk.Scrollbar(self, orient=tk.VERTICAL)
            history = tk.Text(self, foreground='black', yscrollcommand=scrollbar.set)
            scrollbar.config(command=history.yview)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            history.pack()
            history.insert('1.0', history_str)
            history['state'] = tk.DISABLED


class CustomTimeOfPerformingWindow(tk.Toplevel):
    def __init__(self, quest):
        super().__init__(main_window)

        self.title('JARL - time of performing')
        self.geometry('+832+260')
        self.resizable(False, False)
        self.grab_set()
        self.focus_set()

        self.quest = quest

        # window constructing: -----------------------------------------------------------------------------------------
        def check(source, form):
            data = source.get()
            if not ((len(data) in form['len']) and (int(data) in form['vals'])):
                source['fg'] = 'red'
                source['validate'] = 'focusout'
            return True

        tk.Label(self, bg='#BCE7EE').grid(row=0, column=2, columnspan=3, rowspan=2, sticky=tk.W + tk.E + tk.N + tk.S)
        tk.Label(self, text='h', bg='#BCE7EE').grid(row=0, column=2)
        tk.Label(self, text='m', bg='#BCE7EE').grid(row=0, column=4)
        tk.Label(self, text='dd').grid(row=0, column=6)
        tk.Label(self, text='mo').grid(row=0, column=8)
        tk.Label(self, text='year').grid(row=0, column=10)
        tk.Label(self, text=self.quest.name+':').grid(row=0, column=0)
        tk.Label(self, text='quest completed').grid(row=1, column=0)
        tk.Label(self).grid(row=0, column=1, rowspan=2, sticky=tk.W + tk.E + tk.N + tk.S)
        self.hour_entry = tk.Entry(self, width=3, bg='#DDF2F6', justify=tk.CENTER, validate='focusout', vcmd=lambda: check(self.hour_entry, {'len':range(1, 3), 'vals':range(0, 24)}))
        self.hour_entry.grid(row=1, column=2)
        tk.Label(self, text=':', bg='#BCE7EE').grid(row=1, column=3)
        self.minute_entry = tk.Entry(self, width=3, bg='#DDF2F6', justify=tk.CENTER, validate='focusout', vcmd=lambda: check(self.minute_entry, {'len':range(1, 3), 'vals':range(0, 60)}))
        self.minute_entry.grid(row=1, column=4)

        tk.Label(self).grid(row=1, column=5)

        self.day_entry = tk.Entry(self, width=3, justify=tk.CENTER, validate='focusout', vcmd=lambda: check(self.day_entry, {'len':range(1, 3), 'vals':range(0, 32)}))
        self.day_entry.grid(row=1, column=6)
        tk.Label(self, text='.').grid(row=1, column=7)
        self.month_entry = tk.Entry(self, width=3, justify=tk.CENTER, validate='focusout', vcmd=lambda: check(self.month_entry, {'len':range(1, 3), 'vals':range(0, 13)}))
        self.month_entry.grid(row=1, column=8)
        tk.Label(self, text='.').grid(row=1, column=9)
        self.year_entry = tk.Entry(self, width=5, justify=tk.CENTER, validate='focusout', vcmd=lambda: check(self.year_entry, {'len':range(1, 5), 'vals':range(1970, 10000)}))
        self.year_entry.grid(row=1, column=10)

        scrollbar = tk.Scrollbar(self, orient=tk.VERTICAL)
        self.desc_text = tk.Text(self, width=28, height=4, yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.desc_text.yview)
        scrollbar.grid(row=4, column=10, sticky=tk.W+tk.E+tk.N+tk.S)
        self.desc_text.grid(row=4, column=0, columnspan=10)

        tk.Button(self, text='Apply', bg='#22B14C', foreground='#FFF', activeforeground='white', bd=0,
                  command=self.press_apply,
                  activebackground='#00CC00').grid(row=5, column=0, columnspan=16, sticky=tk.W + tk.E + tk.N + tk.S)
        # --------------------------------------------------------------------------------------------------------------
        self.hour_entry.insert(0, dt.datetime.today().hour)
        self.minute_entry.insert(0, dt.datetime.today().minute)
        if len(self.minute_entry.get()) == 1:
            self.minute_entry.insert(0, 0)
        self.day_entry.insert(0, dt.datetime.today().day)
        self.month_entry.insert(0, dt.datetime.today().month)
        if len(self.month_entry.get()) == 1:
            self.month_entry.insert(0, 0)
        self.year_entry.insert(0, dt.datetime.today().year)
        self.year_entry.selection_range(0, tk.END)

        entries = [self.hour_entry, self.minute_entry, self.day_entry, self.month_entry, self.year_entry]

        def entry_callback(event):
            if self.hour_entry['fg'] == 'red':
                self.hour_entry.delete(0, tk.END)
                self.hour_entry['fg'] = 'black'
            else:
                self.hour_entry.selection_range(0, tk.END)

        self.hour_entry.bind("<FocusIn>", entry_callback)

        def entry_callback(event):
            if self.minute_entry['fg'] == 'red':
                self.minute_entry.delete(0, tk.END)
                self.minute_entry['fg'] = 'black'
            else:
                self.minute_entry.selection_range(0, tk.END)

        self.minute_entry.bind("<FocusIn>", entry_callback)

        def entry_callback(event):
            if self.day_entry['fg'] == 'red':
                self.day_entry.delete(0, tk.END)
                self.day_entry['fg'] = 'black'
            else:
                self.day_entry.selection_range(0, tk.END)

        self.day_entry.bind("<FocusIn>", entry_callback)

        def entry_callback(event):
            if self.month_entry['fg'] == 'red':
                self.month_entry.delete(0, tk.END)
                self.month_entry['fg'] = 'black'
            else:
                self.month_entry.selection_range(0, tk.END)

        self.month_entry.bind("<FocusIn>", entry_callback)

        def entry_callback(event):
            if self.year_entry['fg'] == 'red':
                self.year_entry.delete(0, tk.END)
                self.year_entry['fg'] = 'black'
            else:
                self.year_entry.selection_range(0, tk.END)

        self.year_entry.bind("<FocusIn>", entry_callback)

    class Entry(tk.Entry):
        def __init__(self, length, max_range, **kwargs):
            super().__init__(**kwargs)

    def press_apply(self):
        desc = self.desc_text.get('1.0', tk.END).strip()
        if desc:
            res_time = dt.datetime(int(self.year_entry.get()), int(self.month_entry.get()), int(self.day_entry.get()),
                                   int(self.hour_entry.get()), int(self.minute_entry.get()))
            if self.quest.last_performed:
                if res_time > self.quest.last_performed:
                    quests_dict[self.quest]['quest_image'].plus_button.press(desc, res_time)
                    self.destroy()
            else:
                quests_dict[self.quest]['quest_image'].plus_button.press(desc, res_time)
                self.destroy()


class About(tk.Toplevel):
    def __init__(self):
        super().__init__(main_window)

        self.title('JARL - about')
        self.geometry('200x100+832+260')
        self.resizable(False, False)
        self.grab_set()
        self.focus_set()

        tk.Label(self, text='All 4 u dude').pack(anchor=tk.NW)


def open_progress():  # только при запуске программы с пустым списком maps
    global maps, quests, quests_dict
    try:
        f = open('jarl_db.ja', 'rb')
        maps = pickle.load(f)
        f.close()
    except FileNotFoundError:
        f = open('jarl_db.ja', 'wb')
        pickle.dump([], f)
        f.close()
    quests = []
    quests_dict = {}
    refresh_maps_bar()
    set_map(0)


def save_progress():
    global maps
    if maps:
        f = open('jarl_db.ja', 'wb')
        pickle.dump(maps, f)
        f.close()
    print('saved:', maps)


def set_map(index):
    global selected_map, maps_bar
    if maps:
        maps_dict[maps[selected_map]]['indicator'].flag_off()
        selected_map = index
        maps_dict[maps[selected_map]]['indicator'].flag_on()
        do_reload_quests()
    else:
        maps_bar = tk.Label(text='   ↑   to add some maps, plus_button Profile - Maps', anchor=tk.NW)
        maps_bar.place(x=0, y=0, relwidth=1, height=60)


def do_reload_quests():
    global blue, quests, maps
    mapp = maps[selected_map]

    # получение актуального упорядоченного списка квестов:
    loc_quests = []
    for level in mapp.quests:
        for quest in mapp.quests[level]:
            quest.refresh()
            loc_quests.append(quest)
    loc_quests.sort()

    # если обновленный список квестов имеет другой порядок, нежели старый список:
    if loc_quests != quests:
        quests = loc_quests
        quests_dict.clear()
        def_blue()
        blue.y_pos = 0
        for quest in quests:  # displaying quests-----------------------------------------------------------------------
            QuestImage(quest, master=blue)
    else:
        for quest in loc_quests:
            quests_dict[quest]['quest_image'].refresh()

    for mapp in maps_dict:
        maps_dict[mapp]['indicator'].refresh()
        maps_dict[mapp]['map_button'].update_elo()


def just_calculate_quests(mapp):
    loc_quests = []
    for level in mapp.quests:
        for quest in mapp.quests[level]:
            quest.refresh()
            loc_quests.append(quest)
    max_r = 0.1
    for quest in loc_quests:
        if quest.relevance > max_r:
            max_r = quest.relevance
    maps_dict[mapp]['max_r'] = max_r


def real_time():
    if len(maps) > 0:
        do_reload_quests()
    main_window.after(jc.refresh_rate, real_time)


def refresh_maps_bar():  # при вызове этой функции список maps должен быть уже готов
    global maps_bar
    maps_dict.clear()
    if maps_bar:
        maps_bar.place_forget()
    maps_bar = tk.Frame(main_window, bg='#EAF7F9')
    not_first = False
    for mapp in maps:
        maps_dict[mapp] = {}
        new_map_btn = MapButton(mapp, maps.index(mapp), master=maps_bar,
                                text=mapp.name.upper() + '\n\n' + str(int(mapp.gain)), bd=0, bg=mapp.color,
                                activebackground=mapp.color)
        new_map_btn['command'] = new_map_btn.map_button
        if not_first:
            tk.Label(main_window, bd=0, bg='#DDF2F6').place(x=-1, y=0, relx=maps.index(mapp) / len(maps), width=2,
                                                            height=70)
        new_map_btn.place(x=1, y=0, relx=maps.index(mapp) / len(maps), relwidth=1 / len(maps), width=-2, relheight=1)
        not_first = True
    maps_bar.place(x=0, y=0, relwidth=1, height=60)


def def_blue():
    global blue
    if blue:
        blue.place_forget()
    blue = tk.Frame(main_window, bg='#EAF7F9')
    blue.y_pos = 0
    blue.place(x=0, y=91, relwidth=1, relheight=1)


def start():
    global maps
    main_window.hided = False
    main_window.title('JARL')
    main_window.geometry('400x500+720+240')

    # описание главного меню:-------------------------------------------------------------------------------------------
    menubar = tk.Menu(main_window)

    filemenu = tk.Menu(menubar, tearoff=0)
    filemenu.add_command(label="Maps", command=MapsWindow)
    filemenu.add_separator()
    filemenu.add_command(label="Undo: "+"последний квест", state=tk.DISABLED)
    filemenu.add_command(label="Save all", command=save_progress)
    filemenu.add_separator()
    filemenu.add_command(label="Exit", command=main_window.quit)
    menubar.add_cascade(label="Profile", menu=filemenu)

    editmenu = tk.Menu(menubar, tearoff=0)
    editmenu.add_command(label="Theme")
    editmenu.add_command(label="Refresh rate")
    editmenu.add_command(label="Stability cap")
    menubar.add_cascade(label="View", menu=editmenu)

    helpmenu = tk.Menu(menubar, tearoff=0)
    helpmenu.add_command(label="Window settings")
    menubar.add_cascade(label="Window", menu=helpmenu)

    helpmenu = tk.Menu(menubar, tearoff=0)
    helpmenu.add_command(label="About", command=About)
    menubar.add_cascade(label="Help", menu=helpmenu)

    main_window.config(menu=menubar)

    # обрамление меню карт:---------------------------------------------------------------------------------------------
    separ = tk.Frame(main_window, bg='#AAAAAA')
    separ.place(x=0, y=60, relwidth=1, height=1)

    def_blue()

    # maps = jc.maps
    eval(['open_progress()', 'refresh_maps_bar()'][0])

    set_map(0)
    main_window.update()

    real_time()
    main_window.mainloop()


# variables:------------------------------------------------------------------------------------------------------------
main_window = tk.Tk()

blue = maps_bar = None
color_dict_blue = \
    {1: '#00A3BE',
     0.9: '#17ABC4',
     0.8: '#58C3D4',
     0.7: '#70CBDA',
     0.6: '#84D2DF',
     0.5: '#95D8E4',
     0.4: '#A4DEE8',
     0.3: '#B1E3EB',
     0.2: '#BCE7EE',
     0.1: '#DDF2F6'}
color_dict_green = \
    {1: '#22B14C',
     0.9: '#37B85D',
     0.8: '#42BC66',
     0.7: '#5DC67C',
     0.6: '#75CE8F',
     0.5: '#89D59F',
     0.4: '#9ADBAD',
     0.3: '#A9E0B9',
     0.2: '#B5E4C3',
     0.1: '#D9F1E0'}
months = \
    {1: 'jan',
     2: 'feb',
     3: 'mar',
     4: 'apr',
     5: 'may',
     6: 'jun',
     7: 'jul',
     8: 'aug',
     9: 'sep',
     10: 'oct',
     11: 'nov',
     12: 'dec'}
selected_map = 0
quests = []
quests_dict = {}

# start:----------------------------------------------------------------------------------------------------------------
maps = []
maps_dict = {}  # {map_object: {'map_button': ..., "max_r": ..., "indicator": ...}, ...}

start()
