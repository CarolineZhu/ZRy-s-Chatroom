import client


# import socket, select, string, sys
#
#
# def prompt():
#     sys.stdout.write('<You> ')
#     sys.stdout.flush()
#
#
# if __name__ == '__main__':
#     recv_buffer = 4096
#     if (len(sys.argv) < 3):
#         print 'Usage: python Client.py hostname port.'
#         sys.exit()
#     host = sys.argv[1]
#     port = int(sys.argv[2])
#
#     s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     s.settimeout(2)
#
#     try:
#         s.connect((host, port))
#     except:
#         print 'Unable to connect.'
#         sys.exit()
#
#     print 'Connected successfully. Start sending messages.'
#     prompt()
#
#     while 1:
#         rlist = [sys.stdin, s]
#         read_list, write_list, error_list = select.select(rlist, [], [])
#         for sock in read_list:
#             if sock == s:
#                 data = sock.recv(recv_buffer)
#                 if not data:
#                     print '\nDisconnected from the server.'
#                     sys.exit()
#                 else:
#                     sys.stdout.write(data)
#                     prompt()
#             else:
#                 message = sys.stdin.readline()
#                 s.send(message)
#                 prompt()