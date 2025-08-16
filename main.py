import os
import base64 
from PIL import Image
import io 
from tkinter import filedialog
from customtkinter import*
import threading
from socket import*
class MainWindow(CTk):
    def __init__(self):
        super().__init__()
        self.geometry("500x400")
        self.username="Max"
        self.frame=CTkFrame(self,width=30,height=self.winfo_height())
        self.frame.pack_propagate(False)
        
        self.frame.place(x=0,y=0)
        self.is_show_menu=False
        self.menu_show_speed=-5

        self.label_theme=CTkOptionMenu(self.frame,values=['Темна','Світла'],command=self.change_theme)
        self.label_theme.pack(side='bottom',pady=20)
        self.theme=None

        self.btn=CTkButton(self,text='▶️',command=self.toggle_show_menu,width=30)
        self.btn.place(x=0,y=0)
        
        self.chat_text=CTkScrollableFrame(self)
        self.chat_text.place(x=0,y=0)

        self.open_img_button=CTkButton(self,text="⎗",width=50,height=40,command=self.open_image)
        self.open_img_button.place(x=0,y=0)

        self.message_input=CTkEntry(self,placeholder_text="Введіть повідомлення",height=40)
        self.message_input.place(x=0,y=0)
        self.send_button=CTkButton(self,text="▶️",width=50,height=40,command=self.send_message)
        self.send_button.place(x=0,y=0)

        self.label=None
        self.entry=None
        self.save_button=None
        
        try:
            self.sock=socket(AF_INET,SOCK_STREAM)
            self.sock.connect(('localhost',8080))
            hello=f"TEXT@{self.username}@[SYSTEM]{self.username} приєднався до чату \n"
            self.sock.send(hello.encode("utf-8"))
            threading.Thread(target=self.recv_message,daemon=True).start()
        except Exception as e:
            self.add_message(f"Не вдалося підключитися до сервера: {e}")


        self.adaptive_ui()

    def toggle_show_menu(self):
        if self.is_show_menu:
            self.is_show_menu=False
            self.menu_show_speed*=-1
            self.btn.configure(text='▶️')
            self.animate_menu()
        else:
            self.is_show_menu=True
            self.menu_show_speed*=-1
            self.btn.configure(text='▶️')
            self.animate_menu()

            self.label=CTkLabel(self.frame,text="Ваше ім'я")
            self.label.pack(pady=30)
            self.entry=CTkEntry(self.frame)
            self.entry.pack()
            self.save_button=CTkButton(self.frame,text="Зберегти",command=self.save_name)
            self.save_button.pack()
    def save_name(self):
        new_name=self.entry.get().strip()
        if new_name:
            self.username=new_name
            self.add_message(f"Ваш новий нiк:{self.username}")
    
    def animate_menu(self):
        self.frame.configure(width=self.frame.winfo_width()+self.menu_show_speed)
        if self.is_show_menu and self.frame.winfo_width() <200:
            self.after(10,self.animate_menu)
            
        elif not self.is_show_menu and self.frame.winfo_width()>=40:
                self.after(10,self.animate_menu)
                if self.label and self.entry:
                    self.label.destroy()
                    self.entry.destroy()
                if self.save_button:
                    self.save_button.destroy()

    
    
    def change_theme(self,value):
        if value=="Темна":
            set_appearance_mode("dark")
        else:
            set_appearance_mode("light")

    def adaptive_ui(self):
        self.frame.configure(height=self.winfo_height())

        self.chat_text.configure(width=self.winfo_width()-self.frame.winfo_width(),height=self.winfo_height()-70)
        self.chat_text.place(x=self.frame.winfo_width(),y=30)
        self.message_input.configure(width=self.winfo_width() - self.frame.winfo_width() - 110)
        self.message_input.place(x=self.frame.winfo_width(),y=self.send_button.winfo_y())
        self.send_button.place(x=self.winfo_width()-50,y=self.winfo_height()-40)

        self.open_img_button.place(x=self.winfo_width() - 105, y=self.send_button.winfo_y())
        self.after(50,self.adaptive_ui)


    def add_message(self,message,img=None):
        message_frame = CTkFrame(self.chat_text, fg_color='grey')
        message_frame.pack(pady=5, anchor='w')
        wrap_length = self.winfo_width() - self.frame.winfo_width() - 40

        if not img:
            CTkLabel(message_frame, text=message, wraplength=wrap_length,
                     text_color='white', justify='left').pack(padx=10, pady=5)
        else:
            CTkLabel(message_frame, text=message, wraplength=wrap_length,
                     text_color='white', image=img, compound='top',
                     justify='left').pack(padx=10, pady=5)

    def send_message(self):
        message=self.message_input.get()
        if message:
            self.add_message(f"{self.username}:{message}")
            data=f"TEXT@{self.username}@{message}\n"
            try:
                self.sock.sendall(data.encode())
            except:
                self.add_message("Помилка надсилання повідомлення!")
        self.message_input.delete(0,END)

    def recv_message(self):
        buffer="" 
        while True:
            try:
                chunk=self.sock.recv(4096)
                if not chunk:
                    break
                butter+=chunk.decode()
                while "\n" in buffer:
                    line,buffer=buffer.split("\n",1)
                    self.handle_line(line.strip())
            except:
                break
        self.sock.close()

    def handle_line(self,line):
        if not line:
            return
        parts=line.split("@",3)
        msg_type=parts[0]
        if msg_type=='TEXT' and len(parts)>=3:
            author=parts[1]
            message=parts[2]
            self.add_message(f"{author}:{message}")
        elif msg_type=='IMAGE' and len(parts)>=4:
            author=parts[1]
            filename=parts[2]
            b64_img=parts[3]
            try:
                img_data=base64.b64decode(b64_img)
                pil_img=Image.open(io.BytesIO(img_data))
                ctk_img=CTkImage(pil_img,size=(300,300))
                self.add_message(f"{author} надіслав зображення:{filename}",img=ctk_img)
            except Exception as e:
                self.add_message(f"Помилка відображення зображення:{e}")
        else:
            self.add_message(line)

    def open_image(self):
        file_name=filedialog.askopenfilename()
        if not file_name:
            return
        try:
            with open(file_name,"rb") as f:
                raw=f.read()
                b64_data=base64.b64encode(raw).decode()
                short_name=os.path.basename(file_name)
                data=f"Image@{self.username}@{short_name}@{b64_data}\n"
                self.sock.sendall(data.encode())
                self.add_message(" ",CTkImage(light_image=Image.open(file_name),size=(300,300)))
        except Exception as e:
            self.add_message(f"Не вдалося надіслати зображення {e}")

if __name__=="__main__":
    win=MainWindow()
    win.mainloop()