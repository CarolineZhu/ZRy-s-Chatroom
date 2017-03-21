import socket, select, string, sys

import _tkinter
from Tkinter import *
import tkSimpleDialog, tkMessageBox
import datetime, time
from client.memory import *
import thread

from message import *


class ChatForm:
    def socket_thread(self):
        recv_buffer = 4096
        host = '127.0.0.1'
        port = 5000

        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.s.settimeout(2)

        try:
            self.s.connect((host, port))
            self.s.send(memory.current_user['username'])
        except:
            tkMessageBox.showerror('Unable to connect', 'Unable to connect')
            root.destroy()

        # print 'Connected successfully. Start sending messages.'
        self.text.tag_config("tag" + str(memory.tag_i), foreground="red", font=15)
        self.text.insert(END, 'Welcome ' + memory.current_user['username'] + ' to the room.' + '\n',
                         "tag" + str(memory.tag_i))
        memory.tag_i += 1

        while 1:
            receive = self.s.recv(8)
            if not receive:
                # print '\nDisconnected from the server.'
                root.destroy()
                sys.exit()
            else:
                msg_length, = unpack('L', receive)
                # print msg_length
                data = self.s.recv(msg_length)
                msgtype = c_getMsgType(data)
                # print msgtype
                if msgtype == 0:
                    # print '-------'
                    src_id, src_name = c_log_unpkg(data)
                    # print 'src_id = ' + str(src_id)
                    # print 'src_name = ' + src_name
                    memory.online_user[src_id] = {"username": src_name}
                    memory.user_list[src_id] = {"username": src_name}
                    if current_user.has_key('user_id') == True:
                        self.online_users.insert(END, src_name)
                        # self.text.insert(END, src_name + ' entered chatroom.\n')
                        chat_history[src_id] = []

                        # message[]
                        # self.s.send(message)
                    else:
                        current_user["user_id"] = src_id

                    self.refresh_user_list()
                if msgtype == 1:
                    src_id, font_size, body = c_unpackage(data)
                    select_id = self.get_selected_user()
                    # current user's message
                    # group chat
                    if src_id > 1000:
                        src_id -= 1000
                        if select_id == 0:
                            self.text.tag_config("tag" + str(memory.tag_i), foreground='blue')
                            self.text.insert(END, online_user[src_id]['username'] + ':' + '\n',
                                             "tag" + str(memory.tag_i))
                            memory.tag_i += 1
                            self.text.tag_config("tag" + str(memory.tag_i), font=(None, font_size))
                            self.text.insert(END, body + '\n', "tag" + str(memory.tag_i))
                            memory.tag_i += 1
                        self.create_chat_history(0, src_id, data)
                    else:
                        if select_id == src_id:
                            self.text.tag_config("tag" + str(memory.tag_i), foreground='blue')
                            self.text.insert(END, online_user[src_id]['username'] + ':' + '\n',
                                             "tag" + str(memory.tag_i))
                            memory.tag_i += 1
                            self.text.tag_config("tag" + str(memory.tag_i), font=(None, font_size))
                            self.text.insert(END, body + '\n', "tag" + str(memory.tag_i))
                            memory.tag_i += 1
                            # other user's message

                            # new_message_inform()
                        self.create_chat_history(src_id, src_id, data)

                if msgtype == 2:
                    src_id, src_name = c_log_unpkg(data)
                    del memory.online_user[src_id]
                    # self.online_users.delete(src_name, src_name)
                    self.remove_chat_history(src_id)
                    self.text.insert(END, src_name + ' is offline.\n')
                    self.refresh_user_list()
                    # self.text.insert(END, data)
                    # sys.stdout.write(data)

    def fontsizeGet(self):
        memory.font_size = tkSimpleDialog.askinteger("Enter font size", 'Font size', initialvalue=memory.font_size)

    def entryGet(self):
        body = self.input.get()
        if len(body) == 0:
            return
        # print body
        self.text.tag_config("tag" + str(memory.tag_i), foreground="green")
        self.text.insert(END, 'Me:' + '\n',
                         "tag" + str(memory.tag_i))
        # text.tag_delete("tag" + str(memory.tag_i))
        memory.tag_i += 1
        self.text.tag_config("tag" + str(memory.tag_i), font=(None, memory.font_size))
        self.text.insert(END, body + '\n', "tag" + str(memory.tag_i))
        memory.tag_i += 1

        # listbox select_get
        dest_id = self.get_selected_user()
        font_size = memory.font_size
        if body:
            message = c2spackage(dest_id, body, font_size)
        else:
            message = body

        self.s.send(message)
        # print 'current_user:'
        # pprint(current_user)
        self.create_chat_history(dest_id, current_user['user_id'], message)
        self.input.delete(0, END)

    # def online_user_list_increment(self, user_id):
    #     self.online_users.insert(END, memory.online_user[user_id]['user_id'])
    #     return
    #
    # def online_user_list_decrement(self, user_id):
    #     self.online_users.delete(memory.online_user[user_id]['username'], memory.online_user[user_id]['username'])
    #     return
    #
    # def online_user_new_message(self, user_id):
    #     self.online_users.delete(memory.online_user[user_id]['username'], memory.online_user[user_id]['username'])
    #     return


    def refresh_user_list(self):
        # returns 0 for "Group" or user_id
        selected_user_id = self.get_selected_user()

        self.online_users.delete(0, END)
        self.online_users.insert(0, 'GROUP')

        for (k, v) in online_user.items():
            if k != current_user['user_id']:
                self.online_users.insert(END, v['username'])  # + " (" + str(value['id']) + ")")
            if k == selected_user_id:
                self.online_users.select_set(END)

        if len(self.online_users.curselection()) == 0:
            self.online_users.select_set(0)

        return

    def get_selected_user(self):
        if len(self.online_users.curselection()) == 0:
            # print '======='
            return 0
        index = self.online_users.curselection()[0]
        # return group chat
        if index == 0:
            return 0
        else:
            username = self.online_users.get(index)
        try:
            # ???
            id = list(filter(lambda i: online_user[i]['username'] == username, online_user))[0]
            return id
        except IndexError:
            # print '----------'
            return 0

    def create_chat_history(self, user_id, src_id, message):
        if user_id not in chat_history:
            chat_history[user_id] = []
        chat_history[user_id].append({'src_id': src_id, 'message': message})

    def remove_chat_history(self, user_id):
        del (chat_history[user_id])

    def show_chat_history(self, user_id):
        self.text.delete(1.0, END)
        # if user_id == 0:
        # chat
        for item in chat_history[user_id]:
            # I sent to others.
            pprint([item['src_id'], user_id, item])

            if user_id == 0:
                is_me = item['src_id'] == current_user['user_id']
                sender_id, font_size, body = c_unpackage(item['message'])

                self.text.tag_config("tag" + str(memory.tag_i), foreground="green" if is_me else "blue")
                self.text.insert(END, ("Me" if is_me else user_list[item['src_id']]['username']) + ':' + '\n',
                                 "tag" + str(memory.tag_i))
                memory.tag_i += 1

                self.text.tag_config("tag" + str(memory.tag_i), font=(None, font_size))
                self.text.insert(END, body + '\n', "tag" + str(memory.tag_i))
                memory.tag_i += 1

            else:

                if item['src_id'] != user_id:
                    sender_id, font_size, body = c_unpackage(item['message'])

                    self.text.tag_config("tag" + str(memory.tag_i), foreground="green")
                    self.text.insert(END, 'Me:' + '\n',
                                     "tag" + str(memory.tag_i))
                    memory.tag_i += 1

                    self.text.tag_config("tag" + str(memory.tag_i), font=(None, font_size))
                    self.text.insert(END, body + '\n', "tag" + str(memory.tag_i))
                    memory.tag_i += 1

                # others sent to me.
                else:
                    sender_id, font_size, body = c_unpackage(item['message'])

                    self.text.tag_config("tag" + str(memory.tag_i), foreground="blue")
                    self.text.insert(END, online_user[user_id]['username'] + ':\n', "tag" + str(memory.tag_i))
                    memory.tag_i += 1

                    self.text.tag_config("tag" + str(memory.tag_i), font=(None, font_size))
                    self.text.insert(END, body + '\n', "tag" + str(memory.tag_i))
                    memory.tag_i += 1

    def switch_user(self, _):
        # print 'enter switch_user function.'
        id = self.get_selected_user()
        self.show_chat_history(id)
        # new_message_inform_remove()

    def __init__(self, root):

        self.root = root
        self.root.withdraw()
        memory.current_user["username"] = tkSimpleDialog.askstring("Log in", 'Your Name')
        if memory.current_user["username"]== None:
            exit()
        self.root.deiconify()

        self.root.title("Chatroom -- " + memory.current_user['username'])

        self.online_users = Listbox(root, exportselection=False)
        self.online_users.pack(fill=Y, expand=0, side=LEFT)
        self.online_users.bind('<<ListboxSelect>>', self.switch_user)
        # print 'Bind'
        for k, v in memory.online_user.items():
            self.online_users.insert(END, v['username'])

        self.chat_box = Frame(root)
        self.chat_box.pack(fill=BOTH, expand=1, side=RIGHT)

        self.text = Text(self.chat_box)
        self.text.pack(fill=BOTH, expand=1)
        self.text.bind("<Key>", lambda e: "break")

        self.input = Entry(self.chat_box)
        self.input.pack(fill=X, expand=0)

        self.buttonFrame = Frame(self.chat_box)
        self.buttonFrame.pack(fill=X, expand=0)

        self.sendBtn = Button(self.buttonFrame, text="Send", command=self.entryGet)
        self.sendBtn.pack(side=RIGHT)

        self.fontsizeBtn = Button(self.buttonFrame, text="Font Size", command=self.fontsizeGet)
        self.fontsizeBtn.pack(side=LEFT)

        thread.start_new_thread(self.socket_thread, ())
        root.mainloop()

        try:
            root.destroy()
        except TclError:
            pass


root = Tk()
# root.title("Chatroom")
root.minsize(200, 400)
ChatForm(root)
