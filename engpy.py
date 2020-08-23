
DIGITS = '0123456789'

T_INT = 'T_INT'
T_FLOAT = 'FLOAT'
T_ADD = 'ADD'
T_MINUS = 'MINUS'
T_MULTIPLIED = 'MULTIPLIED'
T_DIVIDED = 'DIVIDED'
T_LPAREN = 'LPAREN'
T_RPAREN = 'RPAREN'
T_EOF = 'EOF'


class Error:
	def __init__(self, pos_start, pos_end, name, details):
		self.pos_start = pos_start
		self.pos_end = pos_end
		self.name = name
		self.details = details

	def asString(self):
		result = f'''{self.name}: {self.details}
File {self.pos_start.fn}, line {self.pos_start.ln + 1}'''
		return result


class IllegalCharError(Error):
	def __init__(self, pos_start, pos_end, details):
		super().__init__(pos_start, pos_end, 'Illegal character', details)


class InvalidSyntaxError(Error):
	def __init__(self, pos_start, pos_end, details):
		super().__init__(pos_start, pos_end, 'Invalid syntax', details)


class RunTimeError(Error):
	def __init__(self, pos_start, pos_end, details):
		super().__init__(pos_start, pos_end, 'Runtime error', details)


class RunTimeResult:
	def __init__(self):
		self.value = None
		self.error = None

	def register(self, res):
		if res.error: self.error = res.error
		return res.value

	def success(self, value):
		self.value = value
		return self

	def failure(self, error):
		self.error = error
		return self


class Token:
	def __init__(self, type_, value=None, pos_start=None, pos_end=None):
		self.type = type_
		self.value = value

		if pos_start:
			self.pos_start = pos_start.copy()
			self.pos_end = pos_start.copy()
			self.pos_end.advance()

		if pos_end:
			self.pos_end = pos_end.copy()

	def __repr__(self):
		if self.value: return f'{self.type}:{self.value}'
		return f'{self.type}'


class Position:
	def __init__(self, index, line_number, column, file_name, file_text):
		self.idx = index
		self.ln = line_number
		self.col = column
		self.fn = file_name
		self.ft = file_text

	def advance(self, current_char=None):
		self.idx += 1
		self.col += 1

		if current_char == '\n':
			self.ln += 1
			self.col = 0

		return self
	
	def copy(self):
		return Position(self.idx, self.ln, self.col, self.fn, self.ft)


class Lexer:
	def __init__(self, file_name, text):
		self.fn = file_name
		self.text = text
		self.pos = Position(-1, 0, -1, self.fn, text)
		self.current_char = None
		self.advance()

	def advance(self):
		self.pos.advance(self.current_char)
		self.current_char = self.text[self.pos.idx] if self.pos.idx < len(self.text) else None

	def makeTokens(self):
		tokens = []
		while self.current_char != None:
			if self.current_char in ' \t':
				self.advance()
			elif self.current_char in DIGITS:
				tokens.append(self.makeNumber())
			elif self.current_char in 'AMD':
				token = self.makeBinOp()
				if token == 'Error':
					pos_start = self.pos.copy()
					char = self.current_char
					self.advance()
					return [], IllegalCharError(pos_start, self.pos, "'" + char + "'")
				else:
					tokens.append(token)
					self.advance()
			elif self.current_char == '+':
				tokens.append(Token(T_ADD, pos_start=self.pos))
				self.advance()
			elif self.current_char == '-':
				tokens.append(Token(T_MINUS, pos_start=self.pos))
				self.advance()
			elif self.current_char == '*':
				tokens.append(Token(T_MULTIPLIED, pos_start=self.pos))
				self.advance()
			elif self.current_char == '/':
				tokens.append(Token(T_DIVIDED, pos_start=self.pos))
				self.advance()
			elif self.current_char == '(':
				tokens.append(Token(T_LPAREN, pos_start=self.pos))
				self.advance()
			elif self.current_char == ')':
				tokens.append(Token(T_RPAREN, pos_start=self.pos))
				self.advance()
			else:
				pos_start = self.pos.copy()
				char = self.current_char
				self.advance()
				return [], IllegalCharError(pos_start, self.pos, "'" + char + "'")

		tokens.append(Token(T_EOF, pos_start=self.pos))
		return tokens, None

	def makeNumber(self):
		num = ''
		decimal = 0
		pos_start = self.pos.copy()
		while self.current_char != None and self.current_char in DIGITS + '.':
			if self.current_char == '.':
				if decimal == 1: break
				decimal += 1
				num += '.'
			else:
				num += self.current_char
			self.advance()
		return Token(T_INT, int(num), pos_start, self.pos) if decimal == 0 else Token(T_FLOAT, float(num), pos_start, self.pos)

	def makeBinOp(self):
		op = ''
		pos_start = self.pos.copy()
		while self.current_char != None and self.current_char in 'ADEILMNPSTUV':
			op += self.current_char
			self.advance()
		if op == 'ADD': return Token(T_ADD, pos_start=pos_start, pos_end=self.pos)
		elif op == 'MINUS': return Token(T_MINUS, pos_start=pos_start, pos_end=self.pos)
		elif op == 'MULTIPLIED': return Token(T_MULTIPLIED, pos_start=pos_start, pos_end=self.pos)
		elif op == 'DIVIDED': return Token(T_DIVIDED, pos_start=pos_start, pos_end=self.pos)
		else: return 'Error'


class numberNode:
	def __init__(self, token):
		self.token = token
		self.pos_start = self.token.pos_start
		self.pos_end = self.token.pos_end
	
	def __repr__(self):
		return f'{self.token}'


class binOpNode:
	def __init__(self, left_node, op_token, right_node):
		self.left_node = left_node
		self.op_token = op_token
		self.right_node = right_node
		self.pos_start = left_node.pos_start
		self.pos_end = right_node.pos_end

	def __repr__(self):
		return f'({self.left_node}, {self.op_token}, {self.right_node})'


class unaryOpNode:
	def __init__(self, op_token, node):
		self.op_token = op_token
		self.node = node
		self.pos_start = self.op_token.pos_start
		self.pos_end = self.node.pos_end

	def __repr__(self):
		return f'({self.op_tok}, {self.node})'


class Parser:
	def __init__(self, tokens):
		self.tokens = tokens
		self.tok_idx = -1
		self.current_tok = ''
		self.advance()

	def advance(self):
		self.tok_idx += 1
		if self.tok_idx < len(self.tokens):
			self.current_tok = self.tokens[self.tok_idx]
		return self.current_tok

	def parse(self):
		res = self.expr()
		if not res.error and self.current_tok.type != T_EOF:
			return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end, 'Expected ADD, MINUS, MULTIPLIED or DIVIDED'))
		return res

	def factor(self):
		res = ParseResult()
		tok = self.current_tok
		if tok.type in [T_ADD, T_MINUS]:
			res.register(self.advance())
			factor = res.register(self.factor())
			if res.error: return res
			return res.success(unaryOpNode(tok, factor))
		elif tok.type in [T_INT, T_FLOAT]:
			res.register(self.advance())
			return res.success(numberNode(tok))
		elif tok.type == T_LPAREN:
			res.register(self.advance())
			expr = res.register(self.expr())
			if res.error: return res
			if self.current_tok.type == T_RPAREN:
				res.register(self.advance())
				return res.success(expr)
			else:
				return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end, "Expected ')'"))

		return res.failure(InvalidSyntaxError(tok.pos_start, tok.pos_end, 'Expected INT or FLOAT'))

	def term(self):
		return self.binOp(self.factor, [T_MULTIPLIED, T_DIVIDED])

	def expr(self):
		return self.binOp(self.term, [T_ADD, T_MINUS])

	def binOp(self, func, ops):
		res = ParseResult()
		left = res.register(func())
		if res.error: return res

		while self.current_tok.type in ops:
			op_tok = self.current_tok
			res.register(self.advance())
			right = res.register(func())
			if res.error: return res

			left = binOpNode(left, op_tok, right)
		return res.success(left)


class ParseResult:
	def __init__(self):
		self.error = None
		self.node = None

	def register(self, res):
		if isinstance(res, ParseResult):
			if res.error: self.error = res.error
			return res.node
		return res

	def success(self, node):
		self.node = node
		return self

	def failure(self, error):
		self.error = error
		return self


class Number:
	def __init__(self, value):
		self.value = value
		self.setPos()

	def setPos(self, pos_start=None, pos_end=None):
		self.pos_start = pos_start
		self.pos_end = pos_end
		return self

	def addedTo(self, other):
		if isinstance(other, Number):
			return Number(self.value + other.value), None

	def minusTo(self, other):
		if isinstance(other, Number):
			return Number(self.value - other.value), None

	def multipliedTo(self, other):
		if isinstance(other, Number):
			return Number(self.value * other.value), None

	def dividedTo(self, other):
		if isinstance(other, Number):
			if other.value == 0:
				return None, RunTimeError(other.pos_start, other.pos_end, 'Division by zero')
			return Number(self.value / other.value), None

	def __repr__(self):
		return f'{self.value}'



class Interpreter:
	def visit(self, node):
		method_name = f'visit_{type(node).__name__}'
		method = getattr(self, method_name, self.noVisitMethod)
		return method(node)
		
	def noVisitMethod(self, node):
		raise Exception(f'No visit_{type(node).__name__} method defined')

	def visit_numberNode(self, node):
		return RunTimeResult().success(Number(node.token.value).setPos(node.pos_start, node.pos_end))

	def visit_binOpNode(self, node):
		res = RunTimeResult()
		left = res.register(self.visit(node.left_node))
		right = res.register(self.visit(node.right_node))
		if res.error: return res

		if node.op_token.type == T_ADD:
			result, error = left.addedTo(right)
		if node.op_token.type == T_MINUS:
			result, error = left.minusTo(right)
		if node.op_token.type == T_MULTIPLIED:
			result, error = left.multipliedTo(right)
		if node.op_token.type == T_DIVIDED:
			result, error = left.dividedTo(right)

		if error:
			return res.failure(error)

		return res.success(result.setPos(node.pos_start, node.pos_end))

	def visit_unaryOpNode(self, node):
		res = RunTimeResult()
		number = res.register(self.visit(node.node))
		if res.error: return res

		error = None
		if node.op_token.type == T_MINUS:
			number, error = number.multipliedTo(Number(-1))

		if error:
			return res.failure(error)

		return res.success(number.setPos(node.pos_start, node.pos_end))






def run(file_name, text):
	lexer = Lexer(file_name, text)
	tokens, error = lexer.makeTokens()
	if error: return None, error

	parser = Parser(tokens)
	ast = parser.parse()
	if ast.error: return None, ast.error

	interpreter = Interpreter()
	result = interpreter.visit(ast.node)

	return result.value, result.error