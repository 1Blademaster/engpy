import engpy as ep
 

if __name__ == '__main__':
	while True:
		inputText = input('engpy > ')
		result, error = ep.run('<shell>', inputText, debug=False)

		if error:
			print(error.asString())
		else:
			if result is not None:
				print(result)