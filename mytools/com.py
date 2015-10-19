from socket import *
import threading
import select
import time
import sys,traceback
import base64
from Crypto.Cipher import AES
from Crypto import Random
import hashlib

HOST = ''
PORT = 1776

BS = 16
pad = lambda s: s + (BS-len(s)%BS)*chr(BS - len(s)%BS)
unpad = lambda s: s[:-ord(s[len(s)-1:])]

class AESCipher:
	def __init__(self,key):
		self.key=hashlib.sha256(key.encode()).digest()

	def encrypt(self,raw):
		raw = pad(raw)
		iv = Random.new().read(AES.block_size)
		cipher = AES.new(self.key,AES.MODE_CBC, iv)
		return base64.b64encode(iv+cipher.encrypt(raw))

	def decrypt(self,enc):
		enc = base64.b64decode(enc)
		iv = enc[:16]
		cipher = AES.new(self.key,AES.MODE_CBC,iv)
		return unpad(cipher.decrypt(enc[16:]))

class Chat(threading.Thread):
	def __init__(self,name,cipher):
		threading.Thread.__init__(self)
		self.running = 1
		self.name = name
		self.cipher = cipher
		self.sock = socket(AF_INET,SOCK_STREAM)
		self.received = []
		self.sent = []

	def iter_received(self):
		served = 0
		while True:
			while len(self.received) == served: time.sleep(1)
			yield self.received[served]
			served += 1


	def sendall(self,text):
		self.sent.append((text,self._sendall(self.cipher.encrypt(self.name+': '+text))))

	def receive(self,text):
		decrypted = self.cipher.decrypt(text)
		self.received.append(decrypted)
		self._receive(decrypted)

	def _receive(self,text):
		print text


class ChatServer(Chat):
	def __init__(self,name,cipher):
		super(ChatServer,self).__init__(name,cipher)
		self.conn = None
		self.addr = None
		

	def _sendall(self,text):
		try:
			if self.conn:
				self.conn.sendall(text)
				return True
			else:
				print 'No connection available'
				return False
		except Exception as e:
			print "Encoutered exception when sending message. Exception:"
			print e
			return False

	def run(self):
		# s = socket(AF_INET,SOCK_STREAM)
		self.sock.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
		self.sock.bind((HOST,PORT))
		self.sock.listen(1)
		self.conn, self.addr = self.sock.accept()
		while self.running:
			inputready, outputready, exceptready = select.select([self.conn],[self.conn],[])
			for input_item in inputready:
				data = self.conn.recv(1024)
				if data:
					self.receive(data)
				else:
					break
			time.sleep(0)

	def kill(self):
		self.running = 0

class ChatClient(Chat):
	def __init__(self,name,cipher):
		super(ChatClient,self).__init__(name,cipher)
		self.host = None

	def _sendall(self,text):
		try:
			self.sock.sendall(text)
			return True
		except Exception as e:
			print "Encoutered exception when sending message. Exception:"
			print e
			return False

	def run(self):
		# self.sock = socket(AF_INET,SOCK_STREAM)
		self.sock.connect((self.host,PORT))

		while self.running:
			inputready, outputready, exceptready = select.select([self.sock],[self.sock],[])
			for input_item in inputready:
				data = self.sock.recv(1024)
				if data:
					self.receive(data)
				else:
					break
			time.sleep(0)

	def kill(self):
		self.running = 0

# class text_input(threading.Thread):
# 	def __init__(self,cipher,chat_server,chat_client):
# 		threading.Thread.__init__(self)
# 		self.running = 1
# 		self.chat_server = chat_server
# 		self.chat_client = chat_client
# 		self.cipher = cipher
# 	def run(self):
# 		while self.running:
# 			text = raw_input('>')
# 			try:
# 				self.chat_client.sock.sendall(self.cipher.encrypt(text))
# 			except:
# 				#traceback.print_exc(file=sys.stdout)
# 				Exception
# 			try:
# 				self.chat_server.conn.sendall(self.cipher.encrypt(text))
# 			except:
# 				#traceback.print_exc(file=sys.stdout)
# 				Exception
# 			time.sleep(0)
# 	def kill(self):
# 		self.running = 0

def run():
	ip_addr = raw_input('What IP (or type listen)?: ')
	name = raw_input('Name:')
	aes_cipher = AESCipher(raw_input('key: '))
	chat = None
	if ip_addr.lower() == 'listen':
		chat = ChatServer(name,aes_cipher)
	else:
		chat = ChatClient(name,aes_cipher)
		chat.host = ip_addr
	chat.start()
	# if ip_addr.lower() == 'listen':
	# 	cs.start()
	# else:
	# 	cc.host = ip_addr
	# 	cc.start()
	# ti = text_input(aes_cipher,cs,cc)
	# ti.start()
	while True:
		text = raw_input('>')
		chat.sendall(text)

if __name__ == "__main__":
	run()

