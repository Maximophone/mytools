from com import ChatServer, ChatClient, AESCipher

from pygo import Go, Human

class Communicator(object):
	def __init__(self):
		self.commands_lookup = {
			'!chat':'start_chat',
			'!help':'show_help'
		}

	def show_help(self):
		print 'Communicator help'
		print 'List of available commands:'
		print self.commands_lookup

	def start_chat(self):
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
		while True:
			text = raw_input('')
			chat.sendall(text)

	def start(self):
		while(True):
			command = raw_input('=>')
			try:
				getattr(self,self.commands_lookup.get(command,'show_help'))()
			except Exception as e:
				print 'Program %s got an exception and had to close. Exception:'%command
				print e


def run():
	c = Communicator()
	c.start()

if __name__ == '__main__':
	run()