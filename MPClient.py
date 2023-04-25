import socket
import sys
import json
import _thread
from threading import Thread
from _thread import interrupt_main
from json.decoder import JSONDecodeError

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

ip = None
port = 0
joined = False
registered = False

def recv_cmd():
  cont = True
  s = " "
  while cont:
    data, addr = sock.recvfrom(2048)
    if not data:
      sys.exit(0)
    data = data.decode("utf-8")
    msg_rec = json.loads(data)
    if msg_rec["command"] == "all":
      print(f"{msg_rec['message']}")
    elif msg_rec["command"] == "msg":
      print(f"[From {msg_rec['handle']}]: {msg_rec['message']}")
    elif msg_rec["command"] == "smsg":
      print(f"[To {msg_rec['handle']}]: {msg_rec['message']}")
    elif msg_rec["command"] == "leave":
      print("Connection closed. Thank you!")
    else:
      print(msg_rec['message'])


def checkHasSlash(cmd):
  if cmd[0] == '/':
    cmd = cmd[1:]
    return True
  return False

def verifyCommand(cmd, num_args):
  args = cmd.split()
  
  if args[0] == '/msg' or args[0] == '/all':
    if len(args[1:]) >= num_args:
      return True
  
  else:
    if len(args[1:]) == num_args:
      return True
  
  print("Error: Command parameters do not match or is not allowed.")
  return False


# verifies if arguments are valid parameters for the command
def paramCheck(cmd, num_args):
  args = cmd.split()
  if args[0] == '/join':
    if isinstance(args[2], int):
      return True
    else:
      print("Error: Command parameters do not match or is not allowed")
      return False
  elif args[0] == '/register' or args[0] == '/all':
    if isinstance(args[1], str):
      return True
    else:
      print("Error: Command parameters do not match or is not allowed")
      return False
  elif args[0] == 'msg':
    if isinstance(args[1:], str):
      return True
    else:
      print("Error: Command parameters do not match or is not allowed")
      return False


# returns command
def parsedCommand(cmd):
  cmd = cmd.split()
  return cmd[0]


# returns args
def parsedArgs(cmd):
  args = cmd.split()
  return args[1:]


def help_cmd():
  print("/join <server_ip_add> <port>")
  print("/leave")
  print("/register <handle>")
  print("/all <message>")
  print("/msg <handle> <message>")


try:
  while True:
    userInput = input()
    if parsedCommand(userInput) == '/join':
      if not joined:
        if verifyCommand(userInput, 2):
          # set ip and port number
          ip = parsedArgs(userInput)[0]
          port = int(parsedArgs(userInput)[1])

          msgCmd = '{"command":"join"}'
          
          if ip != "127.0.0.1" or port != 12345:
            print("Invalid Connection")
            
          else:
            sock.sendto(bytes(msgCmd, "utf-8"), (ip, port))
            data, addr = sock.recvfrom(2048)
            print(data.decode("utf-8"))
            joined = True
      else:
        print("User has already joined the chat server.")

    elif parsedCommand(userInput) == '/leave':
      if joined:
        if verifyCommand(userInput, 0):
          msgCmd = '{"command":"leave"}'

          sock.sendto(bytes(msgCmd, "utf-8"), (ip, port))
          data, addr = sock.recvfrom(2048)
          response = json.loads(data.decode())

          print(response['message'])
      else:
        print("User has not yet registered in the chat server.")

    elif parsedCommand(userInput) == '/?':
      if verifyCommand(userInput, 0):
        help_cmd()

    elif parsedCommand(userInput) == '/register':
      if joined and not registered:
        if verifyCommand(userInput, 1):
          handle = parsedArgs(userInput)[0]
          msgCmd = '{"command":"register", "handle":"%s"}' % handle

          sock.sendto(bytes(msgCmd, "utf-8"), (ip, port))
          data, addr = sock.recvfrom(2048)
          response = json.loads(data.decode())

          print(response['message'])
          if response['command'] == "success":
            registered=True
            Thread(target=recv_cmd).start()
      else:
        if registered:
          print("User has already registered")
        else:
          print("User has not yet joined in the chat server.")

    elif parsedCommand(userInput) == '/msg':
      if joined and registered:
        if verifyCommand(userInput, 2):
        # get handle of current user
          recevingHandle = parsedArgs(userInput)[0]
          messageList = parsedArgs(userInput)[1:]
          message = " "
          message = message.join(messageList)
          msgCmd = '{"command":"msg", "handle":"%s", "message":"%s"}' % (recevingHandle, message)
          sock.sendto(bytes(msgCmd, "utf-8"), (ip, port))
      else:
        print("User has not yet registered in the chat server.")
        
    elif parsedCommand(userInput) == '/all':
      if joined and registered:
        if verifyCommand(userInput, 1):
          messageList = parsedArgs(userInput)[0:]
          message = " "
          message = message.join(messageList)
          request = '{"command": "all", "message": "%s"}' % message
          sock.sendto(bytes(request, "utf-8"), (ip, port))
      else:
        print("User has not yet registered in the chat server.")

    else:
      print("Error: Command not found.")
except (JSONDecodeError, KeyboardInterrupt):
  sys.exit(0)
