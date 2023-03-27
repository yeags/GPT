import tkinter as tk
from tkinter import ttk
import openai
import os
import threading

class ChatApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('GPT Chat App')
        self.geometry('800x600')
        self.resizable(0, 0)
        self.root = tk.Frame(self, bg='white')
        self.root.grid(row=0, column=0, sticky='nsew')
        # self.iconbitmap('chatbot.ico')
        self.configure(bg='white')
        openai.api_key = os.environ.get('OPENAI_API_KEY')
        openai.Model.retrieve('gpt-4')

        # Create the chat window
        self.frm_chat = tk.Frame(self.root, bg='white')
        self.frm_chat.grid(row=0, column=0)
        self.chat_window = tk.Text(self.frm_chat, bd=1, bg='white', font='Arial', wrap='word')
        self.chat_window.grid(row=0, column=0, sticky='nsew', padx=(6,0), pady=5)

        # Bind scrollbar to chat window
        scrollbar = tk.Scrollbar(self.frm_chat, command=self.chat_window.yview)
        self.chat_window['yscrollcommand'] = scrollbar.set
        scrollbar.grid(row=0, column=1, sticky='nse', padx=0, pady=5)

        # Create the message input window
        self.frm_input = tk.Frame(self.root, bg='white')
        self.frm_input.grid(row=1, column=0, sticky='ew')
        self.frm_input.columnconfigure(1, weight=1)
        # Create the send button
        send_button = tk.Button(self.frm_input, text='Send', font='Arial', width=10,
                                bd=1, bg='white', activebackground='white', command=self.send)
        send_button.grid(row=0, column=0, padx=6, pady=5)
        # Create user input text field
        self.txt_send = tk.Entry(self.frm_input, bd=1, bg='white', font='Arial')
        self.txt_send.bind('<Return>', lambda event: self.send())
        self.txt_send.grid(row=0, column=1, sticky='nsew', padx=6, pady=5)
        self.txt_send.focus_set()
        # Create a busy animation to show when the bot is thinking
        self.busy = ttk.Progressbar(self.frm_input, orient='horizontal', length=100, mode='indeterminate')
        self.busy.grid(row=1, column=0, columnspan=2, sticky='ew', padx=6, pady=5)

    def send(self):
        self.msg = self.txt_send.get()
        self.txt_send.delete(0, 'end')
        self.chat_window.insert('end', 'User: ' + self.msg + '\n\n')
        self.busy.start()
        self.thread_send()
        self.thread_step_progress_bar()

    def send_msg(self):
        response = openai.ChatCompletion.create(model='gpt-4-0314', messages=[{'role': 'user', 'content': self.msg}], max_tokens=4000, temperature=0.2)
        self.chat_window.insert('end', 'GPT: ' + response['choices'][0]['message']['content'] + '\n\n')
        self.busy.stop()

    def thread_send(self):
        thread = threading.Thread(target=self.send_msg)
        thread.start()
    
    def thread_step_progress_bar(self):
        thread = threading.Thread(target=self.step_progress_bar)
        thread.start()

    def step_progress_bar(self):
        self.busy.step(1)
        self.busy.update()
        if self.busy['value'] < 100:
            self.after(10, self.step_progress_bar)

if __name__ == '__main__':
    app = ChatApp()
    app.mainloop()