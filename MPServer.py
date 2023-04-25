import socket
import sys
import json


class User:

  def __init__(self, handle, addr):
    self.handle = handle
    self.addr = addr

  def info(self):  # checks info of connected client
    return f"Handle: {self.handle} Address: {self.addr}"


def getUserByAddr(addr, users):
  for u in users:
    if u.addr == addr:
      return u.handle


def getAddr(hdl, users):
  for u in users:
    if u.handle == hdl:
      return u.addr


def isUserExists(hdl, users):
  for u in users:
    if u.handle == hdl:
      return True
  return False


def isUnique(hdl, users):
  for u in users:
    if u.handle == hdl:
      return False
  return True


def isValidIPOrPort(ip, port):
  if (ip == server_ip_add and port == server_port):
    return True
  return False


SUCCESS_CONNECTION = "Connection to the Message Board Server is successful!"
SUCCESS_DISCONNECTION = "Connection closed. Thank you!"

ERR_IP_OR_PORT = "Error: Connection to the Message Board Server has failed! Please check IP Address and Port Number."
ERR_HANDLE_NOT_FOUND = "Error: Handle or alias not found."
ERR_USER_ALREADY_EXISTS = "Error: Registration failed. Handle or alias already exists."

server_ip_add = '127.0.0.1'
server_port = 12345

userList = []

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print('Starting on IP %s port %d' % (server_ip_add, server_port))
sock.bind((server_ip_add, server_port))

while True:
  data, addr = sock.recvfrom(2048)
  msgIn = data.decode('utf-8')

  parsedMsg = json.loads(msgIn)

  if parsedMsg['command'] == 'join':
    
    print("New User Joined: ", addr)
    sock.sendto(bytes(SUCCESS_CONNECTION, 'utf-8'), addr)

  elif parsedMsg['command'] == 'leave':
    leavingUser = getUserByAddr(addr, userList)

    if isUserExists(leavingUser, userList):
      userList = [User for User in userList if User.handle != leavingUser]
      print("%s has left the server" % leavingUser)
      response = '{"command": "success", "message": "%s"}' % SUCCESS_DISCONNECTION
      sock.sendto(bytes(response, "utf-8"), addr)
    else:
      errorResponse = '{"command": "error", "message": "%s"}' % ERR_HANDLE_NOT_FOUND
      sock.sendto(bytes(errorResponse, "utf-8"), addr)

  elif parsedMsg['command'] == 'register':
    if isUnique(parsedMsg['handle'], userList):

      userList.append(User(parsedMsg['handle'], addr))

      response = '{"command": "success", "message": "Welcome %s"}' % parsedMsg[
        'handle']
      sock.sendto(bytes(response, "utf-8"), addr)
    else:
      errorResponse = '{"command":"error", "message": "%s"}' % ERR_USER_ALREADY_EXISTS
      sock.sendto(bytes(errorResponse, "utf-8"), addr)

  elif parsedMsg['command'] == 'msg':
    if isUserExists(parsedMsg['handle'], userList):
      receivingAddr = getAddr(parsedMsg['handle'], userList)
      receivingUser = getUserByAddr(addr, userList)

      # receiver message
      response1 = '{"command":"msg", "handle":"%s", "message":"%s"}' % (receivingUser, parsedMsg['message'])
      sock.sendto(bytes(response1, "utf-8"), receivingAddr)

      # sender message
      response2 = '{"command":"smsg", "handle":"%s", "message":"%s"}' % (parsedMsg['handle'], parsedMsg['message'])
      sock.sendto(bytes(response2, "utf-8"), addr)
    else:
      errorResponse = '{"command":"error", "message": "%s"}' % ERR_HANDLE_NOT_FOUND
      sock.sendto(bytes(errorResponse, "utf-8"), addr)

  elif parsedMsg['command'] == 'all':
    receivingUser = getUserByAddr(addr, userList)
    response = '{"command": "all", "message": "%s: %s"}' % (
      receivingUser, parsedMsg['message'])
    for u in userList:
      sock.sendto(bytes(response, "utf-8"), u.addr)
