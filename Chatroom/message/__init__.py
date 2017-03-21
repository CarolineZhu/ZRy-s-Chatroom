import socket
from pprint import pprint

from struct import pack, unpack


#
# class messageType():
#     broadcast = 0


def c2spackage(dest_id, body, fontsize):
    # body = body.encode()
    dest = pack('L', dest_id)
    fontsize = pack('L', fontsize)
    message = dest + fontsize + body
    return pack('L', len(message)) + message

def log_pkg(user_id, user_name, msgtype):
    # print 'username = ' + user_name
    message = pack('L', msgtype) + pack('L', user_id) + user_name
    return pack('L', len(message)) + message


def s2cpackage(srcmessage, src_id, msgtype):
    msg_type = pack('L', msgtype)
    dest, = unpack('L', srcmessage[0:8])
    # fontsize = unpack('L', srcmessage[1])
    body = s_getBody(srcmessage)
    src = pack('L', src_id)
    message = msg_type + src + srcmessage[8:16] + body
    return pack('L', len(message)) + message, dest

def s_getDest(message):
    dest, = unpack('L', message[0:8])
    return dest

def s_getBody(message):
    # del message[0:16]
    body = message[16:]
    return body


def c_getBody(message):
    body = message[24:]
    return body


def c_getMsgType(message):
    msgtype, = unpack('L', message[0:8])
    return msgtype


def c_log_unpkg(message):
    src_id, = unpack('L', message[8:16])
    # print src_id
    # del message[0:16]
    src_name = message[16:]
    # print name + '----xs'
    # src_name = name.decode()
    # pprint(src_name)
    return src_id, src_name


def c_unpackage(message):
    # msgtype = unpack('L', message[0])
    pprint([message,len(message)])
    src_id, = unpack('L', message[8:16])
    fontsize, = unpack('L', message[16:24])
    body = c_getBody(message)
    return src_id, fontsize, body

