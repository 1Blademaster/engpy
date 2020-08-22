import engpy as ep
 

if __name__ == '__main__':
	while True:
		inputText = input('engpy > ')
		result, error = ep.run('<shell>', inputText)

		if error: print(error.asString())
		else: print(result)