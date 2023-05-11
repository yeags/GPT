import tkinter as tk
from tkinter import ttk
import openai
import os
import threading
from pathlib import Path

class ChatApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('GPT Assistant')
        # self.geometry('800x600')
        # self.resizable(0, 0)
        self.root = tk.Frame(self, bg='white')
        self.frm_chat = tk.Frame(self.root, bg='white')
        self.frm_input = tk.Frame(self.root, bg='white')
        self.frm_command_bar = tk.Frame(self.root, bg='white')
        self.frm_saved_chats = tk.LabelFrame(self.root, text='Saved Chats', bg='white')
        self.frm_saved_chats.rowconfigure(0, weight=1)
        self.root.grid(row=0, column=0, sticky='nsew')
        self.frm_chat.grid(row=0, column=0)
        self.frm_input.grid(row=1, column=0, sticky='ew')
        self.frm_input.columnconfigure(1, weight=1)
        self.frm_command_bar.grid(row=2, column=0, sticky='ew')
        self.frm_saved_chats.grid(row=0, column=1, rowspan=2, sticky='nsew', padx=6, pady=5)
        # self.iconbitmap('chatbot.ico')
        self.configure(bg='white')
        openai.api_key = os.environ.get('OPENAI_API_KEY')
        self.conversation = []
        self.chat_folder = Path().cwd() / 'conversations'
        self.list_saved_chats()

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
    
    def list_saved_chats(self):
        saved_chats = [chat for chat in self.chat_folder.iterdir() if chat.is_file() and chat.suffix == '.txt']
        self.lbox_saved_chats = tk.Listbox(self.frm_saved_chats, bd=0, bg='white', font='Arial', width=30, height=20)
        # insert saved chats into listbox
        for chat in saved_chats:
            self.lbox_saved_chats.insert('end', chat.stem)
        # bind double click to load chat
        self.lbox_saved_chats.bind('<Double-Button-1>', lambda event: self.load_chat())
        # bind delete key to delete chat
        self.lbox_saved_chats.bind('<Delete>', lambda event: self.delete_chat())
        self.lbox_saved_chats.rowconfigure(0, weight=1)
        self.lbox_saved_chats.grid(row=0, column=0, sticky='nsew', padx=0, pady=(5, 0))

    def load_chat(self):
        self.reset_chat()
        selected_chat = self.lbox_saved_chats.get('active')
        with open(self.chat_folder / (selected_chat + '.txt'), 'r', encoding='utf-8') as f:
            for line in f:
                self.chat_window.insert('end', line)
        self.chat_window.insert('end', 'Loaded chat: ' + selected_chat + '\n\n')
    
    def delete_chat(self):
        selected_chat = self.lbox_saved_chats.get('active')
        os.remove(self.chat_folder / (selected_chat + '.txt'))
        self.lbox_saved_chats.delete('active')

    def save_chat(self):

        with open('chat.txt', 'w', encoding='utf-8') as f:
            for message in self.conversation:
                f.write(message['role'] + ': ' + message['content'] + '\n\n')
        self.chat_window.insert('end', 'Chat saved to chat.txt\n\n')

    def generate_chat_title(self):
        message = {'role': 'user', 'content': 'Generate a four word title for this conversation.  The title should be filename safe.'}
        self.thread_send(self.conversation+[message])

    def send(self):
        user_input = self.txt_send.get()
        self.conversation.append({'role': 'user', 'content': user_input})
        self.txt_send.delete(0, 'end')
        self.chat_window.insert('end', 'User: ' + user_input + '\n\n')
        self.busy.start()
        self.thread_send(self.conversation)
        self.thread_step_progress_bar()

    def send_msg(self, conversation):
        response = openai.ChatCompletion.create(model='gpt-4',
                                                messages=conversation,
                                                temperature=0.2)
        self.conversation.append({'role': 'assistant', 'content': response['choices'][0]['message']['content']})
        self.chat_window.insert('end', 'GPT: ' + response['choices'][0]['message']['content'] + '\n\n')
        self.busy.stop()

    def thread_send(self, conversation):
        thread = threading.Thread(target=self.send_msg, args=(conversation,))
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