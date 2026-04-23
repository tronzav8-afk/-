import sqlite3
import hashlib
import tkinter as tk
from tkinter import messagebox
import random
import os


if os.path.exists('users.db'):
    os.remove('users.db')
    print("Старая база данных удалена")


def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE users (
        id INTEGER PRIMARY KEY,
        username TEXT UNIQUE,
        password TEXT,
        email TEXT
    )''')
    c.execute('''CREATE TABLE notes (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        title TEXT,
        content TEXT
    )''')
    # Тестовый пользователь
    pwd = hashlib.sha256("123456".encode()).hexdigest()
    c.execute("INSERT INTO users (username, password, email) VALUES (?, ?, ?)", 
              ("test", pwd, "test@mail.com"))
    conn.commit()
    conn.close()
    print("База данных создана")

init_db()

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Auth System")
        self.root.geometry("500x500")
        self.root.configure(bg='#333')
        
        self.user_id = None
        self.show_login()
    
    def hash_pwd(self, pwd):
        return hashlib.sha256(pwd.encode()).hexdigest()
    
    def clear(self):
        for w in self.root.winfo_children():
            w.destroy()
    
    def show_login(self):
        self.clear()
        
        tk.Label(self.root, text="ВХОД", font=("Arial", 20, "bold"), bg='#333', fg='white').pack(pady=20)
        
        tk.Label(self.root, text="Логин:", bg='#333', fg='white').pack()
        self.login_user = tk.Entry(self.root, bg='white')
        self.login_user.pack(pady=5)
        
        tk.Label(self.root, text="Пароль:", bg='#333', fg='white').pack()
        self.login_pwd = tk.Entry(self.root, show="*", bg='white')
        self.login_pwd.pack(pady=5)
        
        tk.Button(self.root, text="Войти", command=self.login, bg='green', fg='white').pack(pady=10)
        tk.Button(self.root, text="Регистрация", command=self.show_register, bg='blue', fg='white').pack()
        
        tk.Label(self.root, text="\nТестовый вход: test / 123456", bg='#333', fg='yellow').pack()
    
    def login(self):
        user = self.login_user.get()
        pwd = self.login_pwd.get()
        
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        res = c.execute("SELECT id FROM users WHERE username=? AND password=?", 
                       (user, self.hash_pwd(pwd))).fetchone()
        conn.close()
        
        if res:
            self.user_id = res[0]
            self.show_menu()
        else:
            messagebox.showerror("Ошибка", "Неверный логин или пароль!")
    
    def show_register(self):
        self.clear()
        
        tk.Label(self.root, text="РЕГИСТРАЦИЯ", font=("Arial", 20, "bold"), bg='#333', fg='white').pack(pady=20)
        
        tk.Label(self.root, text="Логин:", bg='#333', fg='white').pack()
        reg_user = tk.Entry(self.root, bg='white')
        reg_user.pack(pady=5)
        
        tk.Label(self.root, text="Email:", bg='#333', fg='white').pack()
        reg_email = tk.Entry(self.root, bg='white')
        reg_email.pack(pady=5)
        
        tk.Label(self.root, text="Пароль:", bg='#333', fg='white').pack()
        reg_pwd = tk.Entry(self.root, show="*", bg='white')
        reg_pwd.pack(pady=5)
        
        tk.Label(self.root, text="Повторите пароль:", bg='#333', fg='white').pack()
        reg_pwd2 = tk.Entry(self.root, show="*", bg='white')
        reg_pwd2.pack(pady=5)
        
        def register():
            u = reg_user.get()
            e = reg_email.get()
            p = reg_pwd.get()
            p2 = reg_pwd2.get()
            
            if not u or not e or not p:
                messagebox.showerror("Ошибка", "Заполните все поля!")
                return
            if p != p2:
                messagebox.showerror("Ошибка", "Пароли не совпадают!")
                return
            if len(p) < 4:
                messagebox.showerror("Ошибка", "Пароль минимум 4 символа!")
                return
            
            try:
                conn = sqlite3.connect('users.db')
                conn.execute("INSERT INTO users (username, password, email) VALUES (?,?,?)",
                           (u, self.hash_pwd(p), e))
                conn.commit()
                conn.close()
                messagebox.showinfo("Успех", "Регистрация завершена!")
                self.show_login()
            except:
                messagebox.showerror("Ошибка", "Пользователь уже существует!")
        
        tk.Button(self.root, text="Зарегистрироваться", command=register, bg='green', fg='white').pack(pady=10)
        tk.Button(self.root, text="Назад", command=self.show_login, bg='gray', fg='white').pack()
    
    def show_menu(self):
        self.clear()
        
        tk.Label(self.root, text="ГЛАВНОЕ МЕНЮ", font=("Arial", 20, "bold"), bg='#333', fg='white').pack(pady=20)
        
        tk.Button(self.root, text="🎮 Игра", command=self.show_game, bg='purple', fg='white', width=20, pady=10).pack(pady=5)
        tk.Button(self.root, text="📝 Заметки", command=self.show_notes, bg='purple', fg='white', width=20, pady=10).pack(pady=5)
        tk.Button(self.root, text="🚪 Выход", command=self.logout, bg='red', fg='white', width=20, pady=10).pack(pady=20)
    
    def show_game(self):
        self.clear()
        
        self.secret = random.randint(1, 100)
        self.attempts = 0
        
        tk.Label(self.root, text="УГАДАЙ ЧИСЛО", font=("Arial", 20, "bold"), bg='#333', fg='white').pack(pady=20)
        tk.Label(self.root, text="Я загадал число от 1 до 100", bg='#333', fg='white').pack()
        
        self.status = tk.Label(self.root, text="", bg='#333', fg='yellow')
        self.status.pack(pady=10)
        
        self.entry = tk.Entry(self.root, bg='white')
        self.entry.pack(pady=5)
        
        def check():
            try:
                guess = int(self.entry.get())
                self.attempts += 1
                
                if guess == self.secret:
                    score = max(100 - (self.attempts - 1) * 10, 10)
                    self.status.config(text=f"ПОБЕДА! Число: {self.secret} | Счёт: {score}", fg='green')
                    self.entry.config(state='disabled')
                    tk.Button(self.root, text="Назад", command=self.show_menu, bg='gray', fg='white').pack(pady=10)
                elif guess < self.secret:
                    self.status.config(text=f"Больше! Попытка {self.attempts}", fg='orange')
                else:
                    self.status.config(text=f"Меньше! Попытка {self.attempts}", fg='orange')
                
                if self.attempts >= 10 and guess != self.secret:
                    self.status.config(text=f"Игра окончена! Число: {self.secret}", fg='red')
                    self.entry.config(state='disabled')
                    tk.Button(self.root, text="Назад", command=self.show_menu, bg='gray', fg='white').pack(pady=10)
                    
                self.entry.delete(0, tk.END)
            except:
                messagebox.showerror("Ошибка", "Введите число!")
        
        tk.Button(self.root, text="Проверить", command=check, bg='green', fg='white').pack(pady=5)
        tk.Button(self.root, text="Назад", command=self.show_menu, bg='gray', fg='white').pack(pady=10)
    
    def show_notes(self):
        self.clear()
        
        tk.Label(self.root, text="ЗАМЕТКИ", font=("Arial", 20, "bold"), bg='#333', fg='white').pack(pady=20)
        
        frame = tk.Frame(self.root, bg='#333')
        frame.pack(fill=tk.BOTH, expand=True, padx=20)
        
        def load_notes():
            for w in frame.winfo_children():
                w.destroy()
            
            conn = sqlite3.connect('users.db')
            notes = conn.execute("SELECT id, title, content FROM notes WHERE user_id=?", (self.user_id,)).fetchall()
            conn.close()
            
            if not notes:
                tk.Label(frame, text="Нет заметок", bg='#333', fg='white').pack()
            
            for nid, title, content in notes:
                f = tk.Frame(frame, bg='#555')
                f.pack(fill=tk.X, pady=2)
                tk.Label(f, text=f"📌 {title}", bg='#555', fg='white', width=30, anchor='w').pack(side=tk.LEFT)
                tk.Button(f, text="Удалить", command=lambda x=nid: delete_note(x), bg='red', fg='white').pack(side=tk.RIGHT)
        
        def add_note():
            win = tk.Toplevel(self.root)
            win.title("Новая заметка")
            win.geometry("400x400")
            win.configure(bg='#333')
            
            tk.Label(win, text="Заголовок:", bg='#333', fg='white').pack(pady=5)
            title = tk.Entry(win, bg='white')
            title.pack(pady=5)
            
            tk.Label(win, text="Содержание:", bg='#333', fg='white').pack(pady=5)
            content = tk.Text(win, bg='white', height=10)
            content.pack(pady=5, padx=20, fill=tk.BOTH, expand=True)
            
            def save():
                t = title.get()
                c = content.get("1.0", tk.END)
                if t:
                    conn = sqlite3.connect('users.db')
                    conn.execute("INSERT INTO notes (user_id, title, content) VALUES (?,?,?)", (self.user_id, t, c))
                    conn.commit()
                    conn.close()
                    win.destroy()
                    load_notes()
            
            tk.Button(win, text="Сохранить", command=save, bg='green', fg='white').pack(pady=10)
        
        def delete_note(nid):
            if messagebox.askyesno("Удалить", "Удалить заметку?"):
                conn = sqlite3.connect('users.db')
                conn.execute("DELETE FROM notes WHERE id=?", (nid,))
                conn.commit()
                conn.close()
                load_notes()
        
        tk.Button(self.root, text="+ Добавить заметку", command=add_note, bg='green', fg='white').pack(pady=10)
        load_notes()
        tk.Button(self.root, text="Назад", command=self.show_menu, bg='gray', fg='white').pack(pady=10)
    
    def logout(self):
        self.user_id = None
        self.show_login()


root = tk.Tk()
app = App(root)
root.mainloop()