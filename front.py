import tkinter as tk


def run():
    root = tk.Tk()
    root.title('Jarl')
    root.geometry('650x450+200+200')

    tk.Label(root, bg='green').place(relwidth=0.5, relheight=0.25)

    root.mainloop()


if __name__ == '__main__':
    run()
