from com import ChatServer, ChatClient, AESCipher
from pygo import Go, Human

class PlayerChat(Human):
	def __init__(self,name,chat):
		self.chat = chat
		super(PlayerChat,self).__init__(name)

	def decide(self,board,color):
		coords = raw_input()
		self.chat.sendall(coords)
		if coords == 'pass': return None
		if coords == 'exit': raise ExitException()
		i,j = self._parse_coords(coords)
		i=int(i)
		j=int(j)
		return (i,j)

class OpponentChat(Human):
	def __init__(self,name,chat):
		self.chat = chat
		self.iterator = chat.iter_received()
		super(OpponentChat,self).__init__(name)

	def decide(self,board,color):
		coords = self.iterator.next().split(': ')[-1]
		if coords == 'pass': return None
		if coords == 'exit': raise ExitException()
		i,j = self._parse_coords(coords)
		i=int(i)
		j=int(j)
		return (i,j)

class Communicator(object):
	def __init__(self):
		self.commands_lookup = {
			'!chat':'start_chat',
			'!go':'start_go',
			'!help':'show_help'
		}

	def show_help(self):
		print 'Communicator help'
		print 'List of available commands:'
		print self.commands_lookup

	def start_go(self):
		ip_addr = raw_input('What IP (or type listen)?: ')
		name = raw_input('Name:')
		aes_cipher = AESCipher(raw_input('key: '))
		chat = None
		if ip_addr.lower() == 'listen':
			chat = ChatServer(name,aes_cipher)
		else:
			chat = ChatClient(name,aes_cipher)
			chat.host = ip_addr
		player = PlayerChat(name,chat)
		opponent = OpponentChat('Opponent',chat)
		chat.start()
		if ip_addr.lower() == 'listen': go = Go(9,player1=player,player2=opponent)
		else: go = Go(9,player1=opponent,player2=player)

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