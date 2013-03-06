import platform

def ant_bin():
	if platform.system() == 'Windows':
		return 'ant.bat'
	else:
		return 'ant'

def write_to_file(file, content):
	fhandle = open(file,'w')
	fhandle.write(content)
	fhandle.close()

def run_ant(self, args):
	cmd_args = [ant_bin()].extend(args)
	prjFolder = self.window.folders()[0]
	self.window.run_command('exec',{'cmd': cmd_args, 'working_dir':prjFolder})
