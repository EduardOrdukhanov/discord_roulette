import discord
import json

config = None

with open('config.json') as data:
	config = json.load(data)

registered_guilds = set()

valid_commands = { '~chat' }

class Participant:
	def __init__(self, message):
		self.channel = message.channel
		self.guild = message.guild

chat_queue = []

active_chat = {}

class MyClient(discord.Client):
	async def on_ready(self):
		print('Logged on as {0}!'.format(self.user))

	async def on_message(self, message):
		if message.content[0] == '~':
			command = self.parse_command(message.content)
			if command is None:
				await self.send_msg(message.channel, 'You\'ve entered an invalid command')
			else:
				await command(message)
		elif message.content.split()[0] == 'send' and message.guild.id in active_chat:
			b = active_chat[message.guild.id]
			await self.send_msg(b.channel, message.content[5:])
	
	async def try_chat(self, message):	
		if(message.guild.id in active_chat):
			await self.send_msg(message.channel, 'You\'re already chatting...')
		elif [(x,y) for x, y in chat_queue if x == message.guild.id]:
			await self.send_msg(message.channel, 'You\'re already in the queue, please wait...')
		else:	
			a = Participant(message)
			print('new participant {0}'.format(a))
			b = None
			if not chat_queue:
				print('participant {0} is not currently in queue'.format(a))
				chat_queue.append((a.guild.id, a))
				print('appended to queue {0}'.format(chat_queue))
				await self.send_msg(message.channel, 'You\'ve been added to a queue, please wait...')
			else:
				_,b = chat_queue.pop()
				active_chat[a.guild.id] = b
				active_chat[b.guild.id] = a
				await self.send_msg(a.channel, 'Starting chat!')
				await self.send_msg(b.channel, 'Starting chat!')
							
	
	async def try_quit(self, message):
		guild_id = message.guild.id
		if [(x,y) for x, y in chat_queue if x == guild_id]:
			chat_queue.remove([(x,y) for x, y in chat_queue if x == guild_id][0])
			await self.send_msg(message.channel, "You've been removed from the queue...")
		elif guild_id in active_chat:
			peer = active_chat[guild_id]
			await self.send_msg(peer.channel, "Your peer has terminated this session...")
			del active_chat[peer.guild.id]
			del active_chat[guild_id]
			await self.send_msg(message.channel, "You've terminated the chat session...")
		else:
			await self.send_msg(message.channel, "You're not even in an active session...")			
	
	async def send_msg(self, channel, text):
		await channel.send(text)

	def parse_command(self, message):
		switcher = {
			'~chat': self.try_chat,
			'~quit': self.try_quit
		}
		return switcher.get(message)

client = MyClient()
client.run(config['token'])