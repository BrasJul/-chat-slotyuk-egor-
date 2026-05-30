import base64
import io
import os
import threading
from socket import socket, AF_INET, SOCK_STREAM
from tkinter import filedialog

from customtkinter import *
from PIL import Image


set_appearance_mode("dark")
set_default_color_theme("blue")


COLOR_BG_DARK = "#1A1A1E"        
COLOR_SURFACE = "#252529"       
COLOR_CHAT_BG = "#131316"        
COLOR_MY_MSG = "#007AFF"         
COLOR_OTHER_MSG = "#2C2C30"      
COLOR_SYSTEM_MSG = "#3A3A3F"     
COLOR_TEXT_MAIN = "#FFFFFF"      
COLOR_TEXT_MUTED = "#8E8E93"    


class RegisterWindow(CTk):
    def __init__(self):
        super().__init__()
        self.username = None
        self.title('Вхід в ApexChat 🚀')
        self.geometry('360x440')
        self.resizable(False, False)
        self.configure(fg_color=COLOR_BG_DARK)
        

        main_frame = CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=30, pady=30)
        
        
        CTkLabel(main_frame, text='ApexChat 🚀✨', font=('Segoe UI', 28, 'bold'), text_color=COLOR_TEXT_MAIN).pack(pady=(10, 5))
        CTkLabel(main_frame, text='Авторизація у вашому просторі', font=('Segoe UI', 12), text_color=COLOR_TEXT_MUTED).pack(pady=(0, 25))
        
        self.name_entry = CTkEntry(main_frame, placeholder_text='Ваше імʼя', width=260, height=40, font=('Segoe UI', 13), fg_color=COLOR_SURFACE, border_width=1, border_color="#3A3A3F")
        self.name_entry.pack(pady=6)
        
       
        self.password_entry = CTkEntry(main_frame, placeholder_text='Пароль', show='*', width=260, height=40, font=('Segoe UI', 13), fg_color=COLOR_SURFACE, border_width=1, border_color="#3A3A3F")
        self.password_entry.pack(pady=6)
        
        
        self.confirm_password_entry = CTkEntry(main_frame, placeholder_text='Повторно пароль', show='*', width=260, height=40, font=('Segoe UI', 13), fg_color=COLOR_SURFACE, border_width=1, border_color="#3A3A3F")
        self.confirm_password_entry.pack(pady=6)
        
        
        self.error_label = CTkLabel(main_frame, text='', font=('Segoe UI', 11), text_color="#FF453A")
        self.error_label.pack(pady=2)
        
        
        self.submit_button = CTkButton(main_frame, text='Увійти', command=self.start_chat, width=260, height=42, font=('Segoe UI', 14, 'bold'), fg_color=COLOR_MY_MSG, hover_color="#0063CC")
        self.submit_button.pack(pady=(10, 0))

    def start_chat(self):
        self.username = self.name_entry.get().strip()
        password = self.password_entry.get().strip()
        confirm_password = self.confirm_password_entry.get().strip()
        
        if not self.username or not password or not confirm_password:
            self.error_label.configure(text="Заповніть усі поля!")
            return

        # Валідація збігу паролів
        if password != confirm_password:
            self.error_label.configure(text="Паролі не збігаються!")
            return

        self.error_label.configure(text="")

        try:
            
            host = "localhost"
            port = 12334
            
            self.sock = socket(AF_INET, SOCK_STREAM)
            self.sock.connect((host, port))
            
            
            hello = f"TEXT@{self.username}@[SYSTEM] {self.username} приєднався(лась) до чату!\n"
            self.sock.sendall(hello.encode('utf-8'))
            self.destroy()

            win = MainWindow(self.sock, self.username)
            win.mainloop()
        except Exception as e:
            self.error_label.configure(text="Сервер недоступний!")
            print(f"Помилка підключення до {host}:{port} -> {e}")


class MainWindow(CTk):
    def __init__(self, sock, username):
        super().__init__()
        self.sock = sock
        self.username = username

        self.geometry('650x500')
        self.minsize(500, 400)
        
        self.title("ApexChat 🚀 Messenger")
        self.configure(fg_color=COLOR_BG_DARK)

        
        self.top_bar = CTkFrame(self, height=50, fg_color=COLOR_SURFACE, corner_radius=0)
        self.top_bar.pack(fill="x", side="top")
        self.top_bar.pack_propagate(False)
        
        self.menu_btn = CTkButton(self.top_bar, text='≡', command=self.toggle_show_menu, width=40, height=40, font=('Segoe UI', 20), fg_color="transparent", hover_color="#3A3A3F", text_color=COLOR_TEXT_MAIN)
        self.menu_btn.place(x=5, y=5)
        
        
        self.title_label = CTkLabel(self.top_bar, text="ApexChat 🚀 • Загальний простір", font=('Segoe UI', 15, 'bold'), text_color=COLOR_TEXT_MAIN)
        self.title_label.place(x=55, y=12)

        
        self.menu_frame = CTkFrame(self, width=0, fg_color=COLOR_SURFACE, corner_radius=0)
        self.menu_frame.pack_propagate(False)
        self.menu_frame.place(x=0, y=50)
        
        self.is_show_menu = False
        self.speed_animate_menu = 20
        self.max_menu_width = 240

        self.label = None
        self.entry = None
        self.save_button = None

        
        self.bottom_bar = CTkFrame(self, height=60, fg_color=COLOR_SURFACE, corner_radius=0)
        self.bottom_bar.pack(fill="x", side="bottom")
        self.bottom_bar.pack_propagate(False)

        self.open_img_button = CTkButton(self.bottom_bar, text='📎', width=40, height=40, font=('Segoe UI', 18), fg_color="transparent", hover_color="#3A3A3F", command=self.open_image)
        self.open_img_button.place(x=10, y=10)

        self.message_entry = CTkEntry(self.bottom_bar, placeholder_text='Напишіть повідомлення...', height=40, font=('Segoe UI', 13), fg_color=COLOR_BG_DARK, border_width=0)
        self.message_entry.place(x=60, y=10)
        self.message_entry.bind("<Return>", lambda e: self.send_message())
        
        self.send_button = CTkButton(self.bottom_bar, text='➔', width=40, height=40, font=('Segoe UI', 16, 'bold'), fg_color=COLOR_MY_MSG, hover_color="#0063CC", command=self.send_message)
        self.send_button.place(x=590, y=10)

        
        self.chat_field = CTkScrollableFrame(self, fg_color=COLOR_CHAT_BG, corner_radius=0)
        self.chat_field.place(x=0, y=50)

        self.after(100, self.adaptive_ui)
        threading.Thread(target=self.recv_message, daemon=True).start()

    def toggle_show_menu(self):
        if self.is_show_menu:
            self.is_show_menu = False
            self.speed_animate_menu = -25
            self.menu_btn.configure(text='≡')
            self.show_menu()
        else:
            self.is_show_menu = True
            self.speed_animate_menu = 25
            self.menu_btn.configure(text='✕')
            
            self.label = CTkLabel(self.menu_frame, text='Мій профіль', font=('Segoe UI', 16, 'bold'), text_color=COLOR_TEXT_MAIN)
            self.label.pack(pady=(30, 20), padx=20, anchor="w")
            
            self.entry = CTkEntry(self.menu_frame, placeholder_text="Змінити нік...", width=200, height=35, fg_color=COLOR_BG_DARK, border_width=1, border_color="#3A3A3F")
            self.entry.insert(0, self.username)
            self.entry.pack(pady=5, padx=20)
            
            self.save_button = CTkButton(self.menu_frame, text="Зберегти", font=('Segoe UI', 12, 'bold'), fg_color=COLOR_MY_MSG, hover_color="#0063CC", height=32, command=self.save_name)
            self.save_button.pack(pady=15, padx=20, fill="x")
            
            self.show_menu()

    def show_menu(self):
        current_width = self.menu_frame.winfo_width()
        new_width = current_width + self.speed_animate_menu
        
        if self.is_show_menu and new_width <= self.max_menu_width:
            self.menu_frame.configure(width=new_width)
            self.after(10, self.show_menu)
        elif not self.is_show_menu and new_width >= 0:
            self.menu_frame.configure(width=new_width)
            self.after(10, self.show_menu)
        else:
            if not self.is_show_menu:
                self.menu_frame.configure(width=0)
                if self.label: self.label.destroy()
                if self.entry: self.entry.destroy()
                if self.save_button: self.save_button.destroy()

    def save_name(self):
        new_name = self.entry.get().strip()
        if new_name:
            self.username = new_name
            self.add_message("Система", f"Ви змінили нікнейм на: {self.username}", is_system=True)

    def adaptive_ui(self):
        if not self.winfo_exists():
            return
            
        menu_w = self.menu_frame.winfo_width()
        win_w = self.winfo_width()
        win_h = self.winfo_height()

        self.menu_frame.configure(height=win_h - 110)
        
        self.chat_field.place(x=menu_w, y=50)
        self.chat_field.configure(width=win_w - menu_w - 15, height=win_h - 110)
        
        self.send_button.place(x=win_w - 50, y=10)
        self.message_entry.configure(width=max(50, win_w - 120))

        self.after(50, self.adaptive_ui)

    def add_message(self, author, text, img=None, is_system=False):
        is_me = (author == "Ви" or author == self.username)
        
