from customtkinter import *
import base64
import io
import threading
from socket import socket, AF_INET, SOCK_STREAM


from tkinter import filedialog
from PIL import Image
class MainWindow(CTk):
    def __init__(self):
        super().__init__()
        self.geometry("400x300")
        self.label = None


        # --- бокова панель ---
        self.menu_frame = CTkFrame(self,width = 30,height = self.winfo_height())
        self.menu_frame.pack_propagate(False)
        self.menu_frame.place(x=0,y=0)

        self.is_show_menu = False
        self.speed_animate_menu = -5

        self.btn = CTkButton(self, text='▶️', width=30,command=self.toggle_show_menu)#тут недописав
        self.btn.place(x=0, y=0)

        # --- Область чата ---
        self.chat_field = CTkScrollableFrame(self)
        self.chat_field.place(x=0, y=0)

        self.massage_entry = CTkEntry(self,placeholder_text="Написати повідомлення,height = 40")
        self.massage_entry.place(x=0,y=0)

        self.send_button = CTkButton(self, text=">", width=50, height=40, command=self.send_message)#тут недописав
        self.send_button.place(x=0,y=0)
        self.send_button.place(x=0, y=0)
        self.addptive_ui()

        self.username = 'Max'
        try:
            self.sock = socket(AF_INET, SOCK_STREAM)
            self.sock.connect(("0.tcp.ngrok.io", 15255))
            hello = f"TEXT@{self.username}@[SYSTEM] {self.username} приєднався(лась) до чату!\n"
            self.sock.send(hello.encode('utf-8'))
            threading.Thread(target=self.recv_message, daemon=True).start()
        except Exception as e:
            self.add_message(f"Не вдалося підключитися до сервера: {e}")

    def addptive_ui(self):

        self.menu_frame.configure(height=self.winfo_height())
        self.chat_field.place(x= self.menu_frame.winfo_width())
        self.chat_field.configure(width=self.winfo_width()-self.menu_frame.winfo_width()-20,
                                  height=self.winfo_height()-40)
        self.send_button.place(x=self.winfo_width()-50, y=self.winfo_height()-40)
        self.massage_entry.place(x=self.menu_frame.winfo_width(),y= self.send_button.winfo_y())
        self.massage_entry.configure(
            width=self.winfo_width() - self.menu_frame.winfo_width() - self.send_button.winfo_width()
        )


        self.open_img_button = CTkButton(self, text='📂', width=50, height=40, command=self.open_image)
        self.open_img_button.place(x=0, y=0)
        self.open_img_button.place(x=self.winfo_width() - 105, y=self.send_button.winfo_y())
        self.after(50, self.addptive_ui)




    def toggle_show_menu(self):
            if self.is_show_menu:
                self.is_show_menu = False
                self.speed_animate_menu *= -1
                self.btn.configure(text='▶️')
                self.show_menu()
            else:
                self.is_show_menu = True
                self.speed_animate_menu *= -1
                self.btn.configure(text='◀️')
                self.show_menu()
                self.label = CTkLabel(self.menu_frame, text='Імʼя')
                self.label.pack(pady=30)
                self.entry = CTkEntry(self.menu_frame)
                self.entry.pack()
                self.save_btn = CTkButton(self.menu_frame, text = "Зберегти ім'я", command=self.save_name)
                self.save_btn.pack()


    def show_menu(self):
        current_width = self.menu_frame.winfo_width()
        new_width = current_width + self.speed_animate_menu
        self.menu_frame.configure(width=new_width)


        if (not new_width >= 200 and self.is_show_menu) or \
                (new_width >= 30 and not self.is_show_menu):
            self.after(10, self.show_menu)
        elif new_width < 30 and not self.is_show_menu:
            if self.label and self.entry:
                self.label.destroy()
                self.entry.destroy()
                self.save_btn.destroy()


    def send_message(self):
        message = self.massage_entry.get()
        if not message.strip():
            return

        try:
            self.sock.send(f"TEXT@{self.username}@{message}\n".encode())
            self.add_message(f"{self.username}: {message}")
            self.massage_entry.delete(0, 'end')
        except:
            self.add_message("Помилка: не вдалося відправити повідомлення")

    def recv_message(self):
        while True:
            try:
                message = self.sock.recv(4096).decode()
                if message:
                    self.add_message(message)
            except:
                break


    def save_name(self):
        new_name = self.entry.get().strip()
        if new_name:
            self.username = new_name
            self.add_message(f"Ваш новий нік: {self.username}")

    def add_message(self, text, img=None, is_self=False):
        # Для своїх повідомлень — інший фон
        bg_color = "#4CAF50" if is_self else "#2E2E2E"

        message_frame = CTkFrame(self.chat_field, fg_color=bg_color, corner_radius=15)
        message_frame.pack(pady=5, anchor='e' if is_self else 'w')

        wrapleng_size = self.winfo_width() - self.menu_frame.winfo_width() - 60

        if not img:
            CTkLabel(
                message_frame,
                text=text,
                wraplength=wrapleng_size,
                text_color="white",
                justify="left"
            ).pack(padx=10, pady=5)
        else:
            CTkLabel(
                message_frame,
                text=text,
                wraplength=wrapleng_size,
                text_color="white",
                image=img,
                compound="top",
                justify="left"
            ).pack(padx=10, pady=5)

    def handle_line(self, line):
        if not line:
            return

        parts = line.split("@", 3)
        msg_type = parts[0]
        if msg_type == "TEXT":
            if len(parts) >= 3:
                autor = parts[1]
                message = parts[2]
                self.add_message(f"{autor}: {message}")
        elif msg_type == "IMAGE":
            if len(parts) >= 4:
                autor = parts[1]
                filename = parts[2]
                img = parts[3]
                try:
                    img_data = base64.b64decode(img)
                    pil_img = Image.open(io.BytesIO(img_data))
                    ctk_tk = CTkImage(pil_img, size=(300, 300))
                    self.add_message(f"{autor}: Надіслав зображення {filename}", img=ctk_tk)

                except Exception as e:
                    self.add_message("Помилка відобрадення зображення")

    def open_image(self):
        file_name = filedialog.askopenfilename()
        if not file_name:
            return
        try:
            with open(file_name, 'rb') as f:
                raw = f.read()

            b64 = base64.b64encode(raw).decode()
            short_name = os.path.basename(file_name)
            data = f"IMAGE@{self.username}@{short_name}@{b64}\n"
            self.sock.send(data.encode())
            self.add_message(" ", CTkImage(light_image=Image.open(file_name), size=(300, 300)))

        except Exception as e:
            self.add_message("Не вдалося надіслати зображення")

win = MainWindow()
win.mainloop()