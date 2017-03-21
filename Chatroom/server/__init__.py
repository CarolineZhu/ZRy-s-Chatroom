import socket, select
from message import *
from server.memory import *
from message import *
from struct import pack, unpack


def broadcast_data(sock, message):
    for _sock in connection_list:
        if _sock != server_socket and _sock != sock:
            try:
                _sock.send(message)

            except:
                _sock.close()
                connection_list.remove(_sock)


def broadcast_login(message):
    for _sock in connection_list:
        if _sock != server_socket:
            try:
                _sock.send(message)

            except:
                _sock.close()
                connection_list.remove(_sock)


# def online_users_pkg(msgtype):
#     type = pack('L', msgtype)
#     message = ''
#     for k,v in online_user.items():
#         id = pack('L', k)
#         name = v['username']
#         message += id + '\n' + name + '\n'
#     return type + message


connection_list = []
recv_buffer = 4096
port = 5000

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(('0.0.0.0', port))
server_socket.listen(10)

connection_list.append(server_socket)
print 'Chat server started on port ' + str(port)


while 1:
    read_sockets, write_sockets, error_sockets = select.select(connection_list, [], [])
    for sock in read_sockets:
        if sock == server_socket:
            sockfd, addr = server_socket.accept()
            username = sockfd.recv(recv_buffer)
            # pack online_user()
            # online_users_message = online_users_pkg(3)
            # sockfd.send(online_users_message)
            pprint(memory.online_user)
            memory.client_id_i += 1
            memory.online_user[memory.client_id_i] = {'username': username, 'socket': sockfd}
            memory.socket_mappings[sockfd] = memory.client_id_i

            pprint(memory.online_user)
            connection_list.append(sockfd)
            print 'Client (%s, %s) connected.' % addr
            login_message = log_pkg(memory.client_id_i,
                      memory.online_user[memory.client_id_i]['username'],
                      0)

            broadcast_login(login_message)
            for k, v in online_user.items():
                message = log_pkg(k, v['username'], 0)
                # print 'message = ' + message
                sockfd.send(message)
            # enterInform = '\r' + '(%s: %s) entered room.\n' % addr
            # enterMsg = pack('L', 1) + pack('L', 0) + memory.font_size + enterInform.encode()
            # broadcast_data(sockfd, enterMsg)
            # broadcast_data(sockfd, '\r' + '(%s: %s) entered room.\n' % addr)
            # memory.online_user.append()
            print 'Login finished.'
        else:
            try:
                msg_length, = unpack('L', sock.recv(8))
                data = sock.recv(msg_length)
            except:
                data = ""

            if data:
                dest_id = s_getDest(data)
                pprint(['a__',dest_id])
                src_id = memory.socket_mappings[sock]
                if dest_id == 0:
                    message = s2cpackage(data, src_id + 1000, 1)[0]
                    broadcast_data(sock, message)
                else:
                    # memory.online_user[]
                    message = s2cpackage(data, src_id, 1)[0]
                    memory.online_user[dest_id]['socket'].send(message)
                    # send messages to given user.
                    # pass
            else:
                # broadcast_data(sock, '\r' + 'Client (%s, %s) is offline.\n' % addr)
                print 'Client (%s, %s) is offline.' % addr
                message = log_pkg(memory.socket_mappings[sock],
                                  memory.online_user[memory.socket_mappings[sock]]['username'],
                                  2)
                broadcast_data(sock, message)
                #delete the corresponding item in memory.online_user.
                del memory.online_user[memory.socket_mappings[sock]]
                del memory.socket_mappings[sock]
                sock.close()
                connection_list.remove(sock)
                continue

server_socket.close()
