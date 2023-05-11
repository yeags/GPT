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
        self.frm_chat = tk.Frame(self.root, bg='white')
        self.frm_input = tk.Frame(self.root, bg='white')
        self.frm_command_bar = tk.Frame(self.root, bg='white')
        self.root.grid(row=0, column=0, sticky='nsew')
        self.frm_chat.grid(row=0, column=0)
        self.frm_input.grid(row=1, column=0, sticky='ew')
        self.frm_input.columnconfigure(1, weight=1)
        self.frm_command_bar.grid(row=2, column=0, sticky='ew')
        # self.iconbitmap('chatbot.ico')
        self.configure(bg='white')
        openai.api_key = os.environ.get('OPENAI_API_KEY')
        self.conversation = []

        # Create the chat window
        self.chat_window = tk.Text(self.frm_chat, bd=1, bg='white', font='Arial', wrap='word')
        self.chat_window.grid(row=0, column=0, sticky='nsew', padx=(6,0), pady=5)

        # Bind scrollbar to chat window
        scrollbar = tk.Scrollbar(self.frm_chat, command=self.chat_window.yview)
        self.chat_window['yscrollcommand'] = scrollbar.set
        scrollbar.grid(row=0, column=1, sticky='nse', padx=0, pady=5)

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
        # Create new chat button
        btn_new_chat = tk.Button(self.frm_command_bar, text='New Chat', font='Arial', width=10, bg='white', command=self.reset_chat)
        btn_new_chat.grid(row=2, column=0, padx=6, pady=5)
        # Create a save chat button
        btn_save_chat = tk.Button(self.frm_command_bar, text='Save Chat', font='Arial', width=10, bg='white', command=self.save_chat)
        btn_save_chat.grid(row=2, column=1, padx=6, pady=5)

    def save_chat(self):
        with open('chat.txt', 'w', encoding='utf-8') as f:
            for message in self.conversation:
                f.write(message['role'] + ': ' + message['content'] + '\n\n')
        self.chat_window.insert('end', 'Chat saved to chat.txt\n\n')

    def send(self):
        user_input = self.txt_send.get()
        self.conversation.append({'role': 'user', 'content': user_input})
        self.txt_send.delete(0, 'end')
        self.chat_window.insert('end', 'User: ' + user_input + '\n\n')
        self.busy.start()
        self.thread_send()
        self.thread_step_progress_bar()

    def send_msg(self):
        response = openai.ChatCompletion.create(model='gpt-4',
                                                messages=self.conversation,
                                                temperature=0.2)
        self.conversation.append({'role': 'assistant', 'content': response['choices'][0]['message']['content']})
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
    
    def reset_chat(self):
        self.chat_window.delete('1.0', 'end')
        self.conversation = []
        self.txt_send.focus_set()

if __name__ == '__main__':
    app = ChatApp()
    app.mainloop()