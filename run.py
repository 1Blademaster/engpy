import sys

from engpy import run, Error

def runFromShell(debug=False):
	while True:
		input_text = input('engpy > ')
		if not input_text:
			continue
		result, error = run('<shell>', input_text + '\n', debug=debug)

		if error:
			if isinstance(error, Error):
				print(error.asString())
			else:
				print(error)
		else:
			if result is not None:
				print(result)
 
def runFromFile(file_name, debug=False):
	result, error = run(file_name, open(file_name, 'r').read().strip(), debug=debug)
	if error:
		if isinstance(error, Error):
			print(error.asString(noArrows=True))
		else:
			print(error)
	else:
		if result is not None:
			print(result)



if __name__ == '__main__':
	# try:
		if len(sys.argv) > 1:
			if sys.argv[1] == 'shell':
				if len(sys.argv) > 2:
					if sys.argv[2] == '-d':
						runFromShell(debug=True)
				else:
					runFromShell()
			else:
				if len(sys.argv) > 2:
					if sys.argv[2] == '-d':
						runFromFile(sys.argv[1], debug=True)
				else:
					runFromFile(sys.argv[1])
		else:
			runFromShell()
	# except Exception as e:
	# 	print(e)
	# 	print('Something went wrong, quitting.')