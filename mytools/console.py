import argparse
import os
import pdb

console_directory = "C:\\MyConsole"
shortcuts_directory = console_directory + "\\shortcuts"
commands_directory = console_directory + "\\commands"
console_volume = console_directory[0]
sys32 = "C:\\Windows\\System32"
file_directory = os.path.dirname(os.path.realpath(__file__))
file_volume = file_directory[0]

def setup():
	if not os.path.isdir(commands_directory):
		os.makedirs(commands_directory)
	if not os.path.isdir(shortcuts_directory):
		os.makedirs(shortcuts_directory)	

	a_text = '@echo off\n{console_vol}:\ncd "{shortcuts_dir}"\ncall %1.bat'.format(console_vol=console_volume,shortcuts_dir=shortcuts_directory)
	shortcut_text = '@echo off\nset var=%CD%\n{file_vol}:\ncd "{file_dir}"\npython console.py --shortcut %1 "%var%"\ncd "%var%"'.format(file_vol = file_volume, file_dir = file_directory)
	c_text = '@echo off\ncall {commands_dir}\\%1.bat'.format(commands_dir = commands_directory)
	command_text = '@echo off\nset var=%CD%\n{file_vol}:\ncd "{file_dir}"\npython console.py --command %1 %2\ncd "%var%"'.format(file_vol = file_volume,file_dir=file_directory)
	write_batch("a",a_text,sys32)
	write_batch("shortcut",shortcut_text,sys32)
	write_batch("c",c_text,sys32)
	write_batch("command",command_text,sys32)

def write_batch(title,text,folder):
	f = open(folder+"\\"+title+".bat",'w')
	f.write(text)
	f.close()

def create_shortcut(alias,folder):
	sh_text = '{volume}:\ncd "{dir}"'.format(volume = folder[0],dir=folder)
	write_batch(alias,sh_text,shortcuts_directory)

def create_command(alias,command):
	write_batch(alias,command,commands_directory)

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('-s','--setup',action='store_true')
	parser.add_argument('-sh','--shortcut',nargs=2)
	parser.add_argument('-c','--command',nargs=2)
	args = parser.parse_args()
	if args.setup:
		setup()
	if args.shortcut is not None:
		create_shortcut(args.shortcut[0],args.shortcut[1])
	if args.command is not None:
		create_command(args.command[0],args.command[1])