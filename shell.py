from engpy import run, Error
 

if __name__ == '__main__':
	while True:
		inputText = input('engpy > ')
		result, error = run('<shell>', inputText, debug=False)

		if error:
			if isinstance(error, Error):
				print(error.asString())
			else:
				print(error)
		else:
			if result is not None:
				print(result)