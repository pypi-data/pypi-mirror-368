import subprocess

class ProcessResult():
	def __init__(self, pres):
		self.out = pres.stdout.decode('utf-8')
		self.err = pres.stderr.decode('utf-8')

def run_process(args):
	result = subprocess.run(
	    args, 
	    stdout=subprocess.PIPE, 
	    stderr=subprocess.PIPE)
	return ProcessResult(result)