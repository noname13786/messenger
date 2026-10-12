import socket
import threading
import tkinter as tk
from tkinter import simpledialog, scrolledtext

HOST = '127.0.0.1'
PORT = 55555

class ChatClient:
    def __init__(self):
        # Запитуємо нікнейм перед відкриттям вікна чату
        root = tk.Tk()
        root.withdraw()
        self.nickname = simpledialog.askstring("Нікнейм", "Введіть ваше ім'я для чату:", parent=root)
        if not self.nickname:
            self.nickname = "Анонім"
        root.destroy()

        # Підключення до мережі
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client.connect((HOST, PORT))
        except:
            print("Не вдалося підключитися до сервера. Перевірте, чи запущений server.py")
            return

        # Налаштування візуального вікна чату
        self.win = tk.Tk()
        self.win.title(f"Месенджер — {self.nickname}")
        self.win.geometry("450x600")
        self.win.configure(bg="#f0f0f0")

        # Вікно з історією повідомлень (з прокруткою)
        self.chat_label = tk.Label(self.win, text="Кімната чату", font=("Arial", 14, "bold"), bg="#f0f0f0")
        self.chat_label.pack(pady=5)

        self.text_area = scrolledtext.ScrolledText(self.win, wrap=tk.WORD, font=("Arial", 11), bg="white")
        self.text_area.pack(padx=10, pady=5, fill="both", expand=True)
        self.text_area.config(state='disabled') # Забороняємо користувачу вручну стирати історію

        # Поле для введення тексту
        self.input_frame = tk.Frame(self.win, bg="#f0f0f0")
        self.input_frame.pack(padx=10, pady=10, fill="x")

        self.msg_entry = tk.Entry(self.input_frame, font=("Arial", 12), bd=2)
        self.msg_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.msg_entry.bind("<Return>", lambda event: self.write()) # Відправка по клавіші Enter

        self.send_button = tk.Button(self.input_frame, text="Надіслати", font=("Arial", 10, "bold"), bg="#4CAF50", fg="white", command=self.write)
        self.send_button.pack(side="right")

        # Запускаємо фоновий потік, який постійно чекає на нові повідомлення від сервера
        receive_thread = threading.Thread(target=self.receive)
        receive_thread.daemon = True
        receive_thread.start()

        self.win.mainloop()

    def write(self):
        message = f"{self.nickname}: {self.msg_entry.get()}"
        if self.msg_entry.get().strip() != "":
            self.client.send(message.encode('utf-8'))
            self.msg_entry.delete(0, tk.END)

    def receive(self):
        while True:
            try:
                message = self.client.recv(1024).decode('utf-8')
                if message == 'NICK':
                    self.client.send(self.nickname.encode('utf-8'))
                else:
                    self.text_area.config(state='normal')
                    self.text_area.insert(tk.END, message + '\n')
                    self.text_area.yview(tk.END) # Автоматична прокрутка вниз до нового повідомлення
                    self.text_area.config(state='disabled')
            except:
                print("Сталася помилка з'єднання!")
                self.client.close()
                break

client = ChatClient()
