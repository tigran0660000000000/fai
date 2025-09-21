import tkinter as tk
from tkinter import scrolledtext, messagebox
import shlex
import getpass
import socket
import datetime
import os
import pathlib

class MiniShellGUI:
    def __init__(self, root):
        self.root = root
        username = getpass.getuser()
        hostname = socket.gethostname()
        root.title(f"Эмулятор - [{username}@{hostname}]")

        # GUI layout
        self.output = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=20, state=tk.DISABLED)
        self.output.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        entry_frame = tk.Frame(root)
        entry_frame.pack(fill=tk.X, padx=6, pady=(0,6))

        self.prompt_var = tk.StringVar()
        self.cwd = pathlib.Path("/")  # виртуальный текущий каталог (строго внутренняя переменная)
        self.update_prompt()

        self.prompt_label = tk.Label(entry_frame, textvariable=self.prompt_var)
        self.prompt_label.pack(side=tk.LEFT)

        self.input_var = tk.StringVar()
        self.entry = tk.Entry(entry_frame, textvariable=self.input_var)
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.entry.bind("<Return>", self.on_enter)
        self.entry.focus_set()

        # command history
        self.history = []
        self.hist_index = None
        self.entry.bind("<Up>", self.history_up)
        self.entry.bind("<Down>", self.history_down)

        # initial greeting
        self.echo(f"Мини-эмулятор shell (Этап 1) — GUI REPL\nВводите команды: ls, cd, exit\n{self.prompt_var.get()}")

    def update_prompt(self):
        # отображаем виртуальный текущий путь в приглашении
        # Для простоты — отображаем строковое представление
        self.prompt_var.set(f"{str(self.cwd)} $ ")

    def write(self, text):
        self.output.configure(state=tk.NORMAL)
        self.output.insert(tk.END, text + "\n")
        self.output.see(tk.END)
        self.output.configure(state=tk.DISABLED)

    def echo(self, text):
        # печать без дополнительной обработки
        self.write(text)

    def on_enter(self, event=None):
        line = self.input_var.get()
        if line.strip() == "":
            self.input_var.set("")
            return
        # сохранить в историю
        self.history.append(line)
        self.hist_index = None

        # показать ввод в выходной окне
        self.write(self.prompt_var.get() + line)
        self.input_var.set("")

        # парсинг с поддержкой кавычек
        try:
            parts = shlex.split(line, posix=True)
        except ValueError as e:
            # shlex выдаёт ValueError при незакрытых кавычках
            self.write(f"Парсер: ошибка разбора аргументов: {e}")
            return

        if len(parts) == 0:
            return

        cmd, *args = parts
        # маршрутизация команд
        if cmd == "exit":
            self.cmd_exit(args)
        elif cmd == "ls":
            self.cmd_ls(args)
        elif cmd == "cd":
            self.cmd_cd(args)
        elif cmd == "date":
            self.cmd_date(args)
        elif cmd == "echo":
            self.cmd_echo(args)
        elif cmd == "cal":
            self.cmd_cal(args)
        else:
            self.write(f"Неизвестная команда: {cmd}")

    # ===== команды (stage 1: в основном заглушки) =====
    def cmd_ls(self, args):
        # заглушка: просто выводим имя команды и аргументы
        self.write(f"[ls] args: {args}")
        # дополнительно: показать (для демонстрации) содержимое реальной cwd если указан флаг --real
        if args and args[0] == "--real":
            try:
                files = os.listdir(".")
                self.write("Содержимое реального локального каталога:")
                for f in files:
                    self.write("  " + f)
            except Exception as e:
                self.write(f"Ошибка чтения реального каталога: {e}")

    def cmd_cd(self, args):
        # заглушка: печатаем имя и аргументы, но также обновляем внутренний виртуальный cwd
        self.write(f"[cd] args: {args}")
        if len(args) == 0:
            # cd в домашний (виртуально)
            self.cwd = pathlib.Path("/home") / getpass.getuser()
        else:
            target = args[0]
            # простая логика: поддерживаем абсолютные пути и относительные, но не трогаем реальную FS
            tpath = pathlib.Path(target)
            if tpath.is_absolute():
                new_cwd = tpath
            else:
                new_cwd = (self.cwd / tpath).resolve()
            # Для демонстрации: не проверяем существование; просто присваиваем
            self.cwd = new_cwd
        self.update_prompt()

    def cmd_exit(self, args):
        self.write("[exit] выход из эмулятора. Bye!")
        self.root.after(200, self.root.destroy)

    # дополнительные команды (не требовались для этапа 1, но добавлены для демонстрации)
    def cmd_date(self, args):
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.write(now)

    def cmd_echo(self, args):
        # echo печатает аргументы, сохраняя пробелы
        self.write(" ".join(args))

    def cmd_cal(self, args):
        # простая реализация — показать календарь текущего месяца (используя calendar)
        import calendar
        now = datetime.datetime.now()
        cal_text = calendar.month(now.year, now.month)
        for line in cal_text.splitlines():
            self.write(line)

    # ===== история команд =====
    def history_up(self, event=None):
        if not self.history:
            return "break"
        if self.hist_index is None:
            self.hist_index = len(self.history) - 1
        else:
            self.hist_index = max(0, self.hist_index - 1)
        self.input_var.set(self.history[self.hist_index])
        return "break"

    def history_down(self, event=None):
        if not self.history or self.hist_index is None:
            return "break"
        self.hist_index = min(len(self.history) - 1, self.hist_index + 1)
        self.input_var.set(self.history[self.hist_index])
        return "break"

def main():
    root = tk.Tk()
    app = MiniShellGUI(root)
    root.geometry("800x500")
    root.mainloop()

if __name__ == "__main__":
    main()
