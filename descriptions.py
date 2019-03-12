import tkinter as tk


def button_description(button, text, self):
    event = None
    self.del_search_description = lambda event=event: del_search_description(self)
    self.search_description = lambda event=event: search_description_delay(self, text, button)
    button.bind("<Enter>", self.search_description)
    button.bind("<Button-1>", self.del_search_description)
    button.bind("<Leave>", self.del_search_description)


def del_search_description(self, event=None):
    try:
        self.search_description_top.destroy()
    except AttributeError:
        pass
    return event


def search_description_delay(self, text, button, event=None):
    button.after(50, search_description(self, text, button, event))


def search_description(self, text, button, event=None):
    self.search_description_top = tk.Toplevel()
    self.search_description_top.wm_overrideredirect(True)
    self.search_description_top_label = tk.Label(self.search_description_top,
                                          text=text, foreground='gold',
                                          justify=tk.LEFT, background=self.quest_label['bg'],
                                          relief=tk.SOLID, borderwidth=0)
    self.search_description_top_label.grid(row=0, column=0)
    x = button.winfo_rootx()
    y = button.winfo_rooty()
    self.search_description_top.geometry("+%s+%s" % (x, y))
    return event
