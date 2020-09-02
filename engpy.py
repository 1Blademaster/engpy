import string

################
# CONSTANTS
################

DIGITS = '0123456789'
VARCHARS = string.ascii_letters + '_'
STRINGCHARS = string.printable + '£'

T_INT = 'INT'
T_FLOAT = 'FLOAT'
T_STRING = 'STRING'

T_ADD = 'ADD'
T_MINUS = 'MINUS'
T_MULTIPLIED = 'MULTIPLIED'
T_DIVIDED = 'DIVIDED'

T_LPAREN = 'LPAREN'
T_RPAREN = 'RPAREN'
T_LSBRACK = 'LSBRACK'
T_RSBRACK = 'RSBRACK'
T_LESSTHAN = 'LESSTHAN'
T_MORETHAN = 'MORETHAN'
T_LESSEQUALS = 'LESSEQUALS'
T_MOREEQUALS = 'MOREEQUALS'
T_SAMEAS = 'SAMEAS'
T_NOTSAMEAS = 'NOTSAMEAS'

T_VAR = 'VAR'
T_EQUALS = 'EQUALS'
T_OUTPUT = 'OUTPUT'
T_LENGTH = 'LENGTH'
T_JOIN = 'JOIN'
T_IF = 'IF'
T_ELSEIF = 'ELSEIF'
T_ELSE = 'ELSE'

T_EOF = 'EOF'

VARS_SAVED = {}

################
# ERROR CLASSES
################

class Error:
	def __init__(self, pos_start, pos_end, name, details):
		self.pos_start = pos_start
		self.pos_end = pos_end
		self.name = name
		self.details = details

	def asString(self, noArrows=False):
		if noArrows: result = f'''{self.name}: {self.details}\nFile {self.pos_start.fn}, line {self.pos_start.ln + 1}'''
		else: result = f'''{self.showArrows()}\n{self.name}: {self.details}\nFile {self.pos_start.fn}, line {self.pos_start.ln + 1}'''
		return result

	def showArrows(self):
		arrows = '        '
		arrows += ' ' * (self.pos_start.col)
		arrows += '^'
		if self.pos_start == self.pos_end:
			return arrows
		else:
			difference = self.pos_end.col - self.pos_start.col
			arrows += '^' * (difference - 1)
			return arrows


class IllegalCharError(Error):
	def __init__(self, pos_start, pos_end, details):
		super().__init__(pos_start, pos_end, 'Illegal character', details)


class InvalidSyntaxError(Error):
	def __init__(self, pos_start, pos_end, details):
		super().__init__(pos_start, pos_end, 'Syntax error', details)


class RunTimeError(Error):
	def __init__(self, pos_start, pos_end, details):
		super().__init__(pos_start, pos_end, 'Runtime error', details)

################
# BASIC CLASSES
################

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
		if self.value: 
			if self.type == T_STRING:
				return f'{self.type}:"{self.value}"'
			return f'{self.type}:{self.value}'
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

	def __repr__(self):
		return f'idx:{self.idx}, ln:{self.ln}, col:{self.col}'

################
# LEXER
################

class Lexer:
	def __init__(self, file_name, text, pos=None):
		self.fn = file_name
		self.text = text + '\n'
		if pos:
			self.pos = pos
		else:
			self.pos = Position(-1, 0, -1, self.fn, text)
		self.current_char = None
		self.total_tokens = []
		self.advance()

	def advance(self):
		self.pos.advance(self.current_char)
		self.current_char = self.text[self.pos.idx] if self.pos.idx < len(self.text) else None

	def makeTokens(self, internalCall=False):
		tokens = []
		while self.current_char != None:
			if self.current_char in ' \t':
				self.advance()
			elif self.current_char in '\n':
				if tokens:
					tokens.append(Token(T_EOF, pos_start=self.pos))
					self.total_tokens.append(tokens)
				tokens = [] 
				self.advance()
			elif self.current_char == '"':
				pos_start = self.pos.copy()
				s = self.makeString()
				if s[0] == 'error':
					return [], InvalidSyntaxError(pos_start, self.pos, s[1])
				else:
					tokens.append(s[0])
			elif self.current_char in DIGITS:
				tokens.append(self.makeNumber())
			elif self.current_char in VARCHARS:
				tokens.append(self.makeKeywordToken())
			elif self.current_char == '-':
				tokens.append(Token(T_MINUS, pos_start=self.pos))
				self.advance()
			elif self.current_char == '(':
				tokens.append(Token(T_LPAREN, pos_start=self.pos))
				self.advance()
			elif self.current_char == ')':
				tokens.append(Token(T_RPAREN, pos_start=self.pos))
				self.advance()
			elif self.current_char == '[':
				tokens.append(Token(T_LSBRACK, pos_start=self.pos))
				res, error, pos = self.makeConditional()
				self.pos.ln = pos[1]
				self.pos.col = pos[2]
				if error: return [], error

				tokens.append(res)
				tokens.append(Token(T_RSBRACK, pos_start=self.pos))
			else:
				pos_start = self.pos.copy()
				char = self.current_char
				self.advance()
				return [], IllegalCharError(pos_start, self.pos, "'" + char + "'")

		if self.total_tokens:
			if self.total_tokens[-1][-1].type != T_EOF:
				self.total_tokens[-1].append(Token(T_EOF, pos_start=self.pos))
			return self.total_tokens, None
		else:
			return [], RunTimeError(self.pos, self.pos, 'No text found')

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

	def makeKeywordToken(self):
		kword = ''
		pos_start = self.pos.copy()
		while self.current_char != None and self.current_char in VARCHARS:
			kword += self.current_char
			self.advance()

		if kword == 'ADD': return Token(T_ADD, pos_start=pos_start, pos_end=self.pos)
		elif kword == 'MINUS': return Token(T_MINUS, pos_start=pos_start, pos_end=self.pos)
		elif kword == 'MULTIPLIED': return Token(T_MULTIPLIED, pos_start=pos_start, pos_end=self.pos)
		elif kword == 'DIVIDED': return Token(T_DIVIDED, pos_start=pos_start, pos_end=self.pos)
		elif kword == 'EQUALS': return Token(T_EQUALS, pos_start=pos_start, pos_end=self.pos)
		elif kword == 'LENGTH': return Token(T_LENGTH, pos_start=pos_start, pos_end=self.pos)
		elif kword == 'JOIN': return Token(T_JOIN, pos_start=pos_start, pos_end=self.pos)
		elif kword == 'OUTPUT': return Token(T_OUTPUT, pos_start=pos_start, pos_end=self.pos)
		elif kword == 'LESSTHAN': return Token(T_LESSTHAN, pos_start=pos_start, pos_end=self.pos)
		elif kword == 'MORETHAN': return Token(T_MORETHAN, pos_start=pos_start, pos_end=self.pos)
		elif kword == 'LESSEQUALS': return Token(T_LESSEQUALS, pos_start=pos_start, pos_end=self.pos)
		elif kword == 'MOREEQUALS': return Token(T_MOREEQUALS, pos_start=pos_start, pos_end=self.pos)
		elif kword == 'SAMEAS': return Token(T_SAMEAS, pos_start=pos_start, pos_end=self.pos)
		elif kword == 'NOTSAMEAS': return Token(T_NOTSAMEAS, pos_start=pos_start, pos_end=self.pos)
		elif kword == 'IF': return Token(T_IF, pos_start=pos_start, pos_end=self.pos)
		elif kword == 'ELSEIF': return Token(T_ELSEIF, pos_start=pos_start, pos_end=self.pos)
		elif kword == 'ELSE': return Token(T_ELSE, pos_start=pos_start, pos_end=self.pos)
		else: return Token(T_VAR, value=kword, pos_start=pos_start, pos_end=self.pos)

	def makeString(self):
		string = ''
		quotes_num = 0
		pos_start = self.pos.copy()
		while self.current_char != None and self.current_char in STRINGCHARS:
			if self.current_char == '"':
				quotes_num += 1
				if quotes_num == 2:
					self.advance()
					break
			else:
				string += self.current_char
			self.advance()

		if quotes_num == 1:
			return 'error', 'Expected ' + '"'

		return Token(T_STRING, value=string, pos_start=pos_start, pos_end=self.pos), None

	def makeConditional(self):
		ln = self.pos.ln
		self.advance()
		text = ''
		while self.current_char != None:
			if self.current_char == '\t':
				self.advance()
			if self.current_char == ']': 
				self.advance()
				break
			text += self.current_char
			self.advance()
	
		int_lexer = Lexer('<conditional>', text, pos=Position(-1, ln, -1, self.fn, text))
		res, error = int_lexer.makeTokens()
		if error: return [], error, (int_lexer.pos.idx, int_lexer.pos.ln, int_lexer.pos.col)
		
		return res, None, (int_lexer.pos.idx, int_lexer.pos.ln, int_lexer.pos.col)
		# Need new line after '['
		# Go line by line and lex each line into a list for everyline containing all the tokens for that line

################
# AST NODE CLASSES
################

class BasicNode:
	output = False


class numberNode(BasicNode):
	def __init__(self, token):
		self.type = 'numberNode'
		self.token = token
		self.pos_start = self.token.pos_start
		self.pos_end = self.token.pos_end
	
	def __repr__(self):
		return f'{self.token}'


class binOpNode(BasicNode):
	def __init__(self, left_node, op_token, right_node):
		self.type = 'binOpNode'
		self.left_node = left_node
		self.op_token = op_token
		self.right_node = right_node
		self.pos_start = left_node.pos_start
		self.pos_end = right_node.pos_end

	def __repr__(self):
		return f'({self.left_node}, {self.op_token}, {self.right_node})'


class unaryOpNode(BasicNode):
	def __init__(self, op_token, node):
		self.type = 'unaryOpNode'
		self.op_token = op_token
		self.node = node
		self.pos_start = self.op_token.pos_start
		self.pos_end = self.node.pos_end

	def __repr__(self):
		return f'({self.op_token}, {self.node})'


class varAssignNode(BasicNode):
	def __init__(self, varNode, node):
		self.type = 'varAssignNode'
		self.varNode = varNode
		self.node = node
		self.pos_start = self.varNode.pos_start
		self.pos_end = self.node.pos_end

	def __repr__(self):
		return f'({self.varNode}={self.node})'


class varNode(BasicNode):
	def __init__(self, node):
		self.type = 'varNode'
		self.node = node
		self.pos_start = self.node.pos_start
		self.pos_end = self.node.pos_end

	def __repr__(self):
		return f'({self.node})'


class stringNode(BasicNode):
	def __init__(self, token):
		self.type = 'stringNode'
		self.token = token
		self.pos_start = self.token.pos_start
		self.pos_end = self.token.pos_end
	
	def __repr__(self):
		return f'{self.token}'


class stringLengthNode(BasicNode):
	def __init__(self, token):
		self.type = 'stringLengthNode'
		self.token = token
		self.pos_start = self.token.pos_start
		self.pos_end = self.token.pos_end
	
	def __repr__(self):
		return f'Length({self.token})'

	
class stringOpNode(BasicNode):
	def __init__(self, left_node, op_token, right_node):
		self.type = 'stringOpNode'
		self.left_node = left_node
		self.op_token = op_token
		self.right_node = right_node
		self.pos_start = left_node.pos_start
		self.pos_end = right_node.pos_end

	def __repr__(self):
		return f'({self.left_node}, {self.op_token}, {self.right_node})'


class equalityNode(BasicNode):
	def __init__(self, left_node, op_token, right_node):
		self.type = 'equalityNode'
		self.left_node = left_node
		self.op_token = op_token
		self.right_node = right_node
		self.pos_start = left_node.pos_start
		self.pos_end = right_node.pos_end

	def __repr__(self):
		return f'({self.left_node}, {self.op_token}, {self.right_node})'


class conditionalNode(BasicNode):
	def __init__(self, if_node, elseif_nodes=None, else_node=None):
		self.type = 'conditionalNode'
		self.if_node = if_node
		if elseif_nodes:
			self.elseif_nodes = elseif_nodes
		if else_node:
			self.else_node = else_node


class ifNode(BasicNode):
	def __init__(self, if_node, if_comp_node, if_code_nodes):
		self.if_node = if_node
		self.if_comp_node = if_comp_node
		self.if_code_nodes = if_code_nodes


class elseifNode(BasicNode):
	def __init__(self, elseif_node, elseif_comp_node, elseif_code_nodes):
		self.elseif_node = elseif_node
		self.elseif_comp_node = elseif_comp_node
		self.elseif_code_nodes = elseif_code_nodes


class elseNode(BasicNode):
	def __init__(self, else_node, else_code_nodes):
		self.else_node = else_node
		self.else_code_nodes = else_code_nodes
		

################
# PARSER
################

class Parser:
	def __init__(self, tokens):
		self.tokens = tokens
		self.tok_idx = -1
		self.current_tok = ''
		self.output = False
		self.advance()

	def buildConditional(self):
		res = ParseResult()
		if_node = self.current_tok
		res.register(self.advance())
		if_comp_node = self.equalityOp()
		res.register(self.advance())
		if_code_tokens = self.current_tok
		if_code_nodes = []
		for toks in if_code_tokens:
			p = Parser(toks)
			node = p.parse()
			if node.error: node

			if_code_nodes.append(node.node)

		if_ast_node = ifNode(if_node, if_comp_node, if_code_nodes)
		conditional_ast_node = conditionalNode(if_ast_node)
		return res.success(conditional_ast_node)

	def advance(self):
		self.tok_idx += 1
		if self.tok_idx < len(self.tokens):
			self.current_tok = self.tokens[self.tok_idx]

		return self.current_tok

	def parse(self):
		if self.tok_idx == 0 and self.tokens[self.tok_idx].type == T_VAR and self.tokens[self.tok_idx + 1].type == T_EQUALS:
			res = self.varAssign()
		elif self.tokens[0].type == T_IF:
			res = self.buildConditional()
			if res.error: return ParseResult().failure(res.error)
			self.advance()
			if self.current_tok.type != T_RSBRACK:
				return ParseResult().failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end, 'Cannot find a closing ]'))
			self.advance()
		else:
			if self.tokens[0].type == T_OUTPUT:
				self.output = True
				if self.checkIfEqualsKwordInTokens():
					return ParseResult().failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end, 'Cannot output an assignment'))
				self.advance()
			
			if self.checkIfEqualityInTokens():
				res = self.equalityOp()
			elif self.checkIfStringNotLengthInTokens():
				res = self.stringOp()
			else:
				res = self.expr()

			if not res.error and self.current_tok.type != T_EOF:
				return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end, 'Invalid syntax'))

		self.outputCopy = self.output
		self.output = False
		return res

	def checkIfEqualsKwordInTokens(self):
		equals_found = False
		for tok in self.tokens[self.tok_idx:]:
			if tok.type == T_EQUALS:
				equals_found = True

		return equals_found

	def checkIfStringInTokens(self):
		string_found = False
		for tok in self.tokens[self.tok_idx:]:
			if tok.type == T_STRING:
				string_found = True

		return string_found

	def checkIfStringNotLengthInTokens(self):
		string_found = False
		for tok in self.tokens[self.tok_idx:]:
			if tok.type == T_STRING:
				string_found = True

		if not string_found:
			return False
		for tok in self.tokens:
			if tok.type == T_LENGTH:
				return False
		return True

	def checkIfEqualityInTokens(self):
		equality_found = False
		for tok in self.tokens[self.tok_idx:]:
			if tok.type in [T_LESSTHAN, T_MORETHAN, T_LESSEQUALS, T_MOREEQUALS, T_SAMEAS, T_NOTSAMEAS]:
				equality_found = True

		return equality_found

	def factor(self):
		res = ParseResult()
		tok = self.current_tok
		if tok.type == T_VAR:
			res.register(self.advance())
			n = varNode(tok)
			n.output = self.output
			return res.success(n)
		elif tok.type == T_STRING:
			res.register(self.advance())
			n = stringNode(tok)
			n.output = self.output
			return res.success(n)
		elif tok.type == T_LENGTH:
			res.register(self.advance())
			string = res.register(self.stringOp())
			if res.error: return res

			n = stringLengthNode(string)
			n.output = self.output
			return res.success(n)
		elif tok.type in [T_ADD, T_MINUS]:
			res.register(self.advance())
			factor = res.register(self.factor())
			if res.error: return res

			n = unaryOpNode(tok, factor)
			n.output = self.output
			return res.success(n)
		elif tok.type in [T_INT, T_FLOAT]:
			res.register(self.advance())
			n = numberNode(tok)
			n.output = self.output
			return res.success(n)
		elif tok.type == T_LPAREN:
			res.register(self.advance())
			if self.checkIfStringInTokens():
				expr = res.register(self.stringOp())
			else:
				expr = res.register(self.expr())
			if res.error: return res
			
			if self.current_tok.type == T_RPAREN:
				res.register(self.advance())
				return res.success(expr)
			else:
				return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end, "Expected ')'"))

		return res.failure(InvalidSyntaxError(tok.pos_start, tok.pos_end, 'Invalid syntax in expression'))

	def term(self):
		return self.binOp(self.factor, [T_MULTIPLIED, T_DIVIDED])

	def expr(self):
		if self.checkIfEqualityInTokens():
			return self.equalityOp()
		return self.binOp(self.term, [T_ADD, T_MINUS])

	def varAssign(self):
		res = ParseResult()
		var = self.current_tok
		res.register(self.advance())
		if self.current_tok.type != T_EQUALS:
			return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end, "Expected EQUALS"))
		else:
			res.register(self.advance())
			if self.checkIfStringNotLengthInTokens():
				var_val = res.register(self.stringOp())
			else:
				var_val = res.register(self.expr())

		if res.error: return res

		return res.success(varAssignNode(var, var_val))

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
		
		left.output = self.output
		return res.success(left)

	def stringOp(self):
		res = ParseResult()
		left = res.register(self.factor())
		if res.error: return res

		while self.current_tok.type in [T_JOIN, T_MULTIPLIED]:
			op_tok = self.current_tok
			res.register(self.advance())
			right = res.register(self.factor())
			if res.error: return res

			left = stringOpNode(left, op_tok, right)

		left.output = self.output
		return res.success(left)

	def equalityOp(self):
		res = ParseResult()
		left = res.register(self.factor())
		if res.error: return res

		while self.current_tok.type in [T_LESSTHAN, T_MORETHAN, T_LESSEQUALS, T_MOREEQUALS, T_SAMEAS, T_NOTSAMEAS]:
			op_tok = self.current_tok
			res.register(self.advance())
			right = res.register(self.factor())
			if res.error: return res

			left = equalityNode(left, op_tok, right)

		left.output = self.output
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

################
# TYPE CLASSES
################

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


class String:
	def __init__(self, value):
		self.value = str(value)
		self.setPos()

	def setPos(self, pos_start=None, pos_end=None):
		self.pos_start = pos_start
		self.pos_end = pos_end
		return self

	def joinedTo(self, other):
		if isinstance(other, String):
			return String(self.value + other.value), None
		return None, RunTimeError(self.pos_start, other.pos_end, 'You can only join strings together')
	
	def multipliedTo(self, other):
		if isinstance(other, Number):
			return String(self.value * other.value), None

	def lengthOf(self):
		return Number(len(self.value)), None

	def __repr__(self):
		return f'{self.value}'


class Boolean:
	def __init__(self, value):
		self.value = bool(value)
		self.setPos()

	def setPos(self, pos_start=None, pos_end=None):
		self.pos_start = pos_start
		self.pos_end = pos_end
		return self

	def __repr__(self):
		return self.value


class Comparision:
	def __init__(self, left_node, op_token, right_node):
		self.left = left_node
		self.op_tok = op_token
		self.right = right_node

	def checkNodeCompatibility(self):
		if type(self.left) != type(self.right):
			return False
		else:
			return True

	def compare(self):
		op = self.op_tok.type
		left = self.left.value
		right = self.right.value

		if not self.checkNodeCompatibility():
			return None, RunTimeError(self.left.pos_start, self.right.pos_end, f'Cannot compare {type(self.left).__name__} and {type(self.right).__name__}')

		if type(left) == str and type(right) == str:
			left = len(left)
			right = len(right)
		
		if op == T_LESSTHAN:
			return Boolean(left < right), None
		elif op == T_MORETHAN:
			return Boolean(left > right), None
		elif op == T_LESSEQUALS:
			return Boolean(left <= right), None
		elif op == T_MOREEQUALS:
			return Boolean(left >= right), None
		elif op == T_SAMEAS:
			return Boolean(self.left.value == self.right.value), None
		elif op == T_NOTSAMEAS:
			return Boolean(self.left.value != self.right.value), None
		else:
			return None, RunTimeError(self.op_tok.pos_start, self.op_tok.pos_end, 'Unknown comparision operator')

################
# INTERPRETER
################

class Interpreter:
	def __init__(self, debug=False):
		self.debug = debug

	def visit(self, node):
		method_name = f'visit_{type(node).__name__}'
		method = getattr(self, method_name, self.noVisitMethod)
		result = method(node)

		return result
		
	def noVisitMethod(self, node):
		raise Exception(f'No visit_{type(node).__name__} method defined')

	def visit_numberNode(self, node):
		return RunTimeResult().success(Number(node.token.value).setPos(node.pos_start, node.pos_end)), node.output

	def visit_binOpNode(self, node, addToVarsSaved=False):
		res = RunTimeResult()
		left = res.register(self.visit(node.left_node))
		right = res.register(self.visit(node.right_node))
		op_tok_type = node.op_token.type

		if res.error: return res, None

		if type(left) == Boolean or type(right) == Boolean:
			return res.failure(RunTimeError(node.pos_start, node.pos_end, 'Cannot perform binary operations on Boolean values')), None

		if op_tok_type == T_ADD:
			result, error = left.addedTo(right)
		if op_tok_type == T_MINUS:
			result, error = left.minusTo(right)
		if op_tok_type == T_MULTIPLIED:
			result, error = left.multipliedTo(right)
		if op_tok_type == T_DIVIDED:
			result, error = left.dividedTo(right)

		# right is Number object
		# result is Number object

		if error:
			return res.failure(error), None

		return res.success(result.setPos(node.pos_start, node.pos_end)), node.output

	def visit_unaryOpNode(self, node):
		res = RunTimeResult()
		number = res.register(self.visit(node.node))
		if res.error: return res, None

		error = None
		if node.op_token.type == T_MINUS:
			number, error = number.multipliedTo(Number(-1))

		if error:
			return res.failure(error), None

		return res.success(number.setPos(node.pos_start, node.pos_end)), node.output

	def visit_varAssignNode(self, node):
		res = RunTimeResult()
		number = res.register(self.visit(node.node))
		if res.error: return res, None

		expr = node.node

		val = res.register(self.visit(expr))
		VARS_SAVED[node.varNode.value] = val
		return res.success(val), node.output

	def visit_varNode(self, node):
		res = RunTimeResult()
		if node.node.value in VARS_SAVED:
			result = VARS_SAVED[node.node.value]
			return res.success(result.setPos(node.pos_start, node.pos_end)), node.output
		else:
			return res.failure(RunTimeError(node.pos_start, node.pos_end, f'No variable with name {node.node.value} defined')), None

	def visit_stringNode(self, node):
		return RunTimeResult().success(String(node.token.value).setPos(node.pos_start, node.pos_end)), node.output

	def visit_stringLengthNode(self, node):
		res = RunTimeResult()
		string = res.register(self.visit(node.token))
		if res.error: return res, None

		result, error = string.lengthOf()
		if error:
			return res.failure(error), None
		return res.success(result), node.output

	def visit_stringOpNode(self, node):
		res = RunTimeResult()
		left = res.register(self.visit(node.left_node))
		right = res.register(self.visit(node.right_node))
		op_tok_type = node.op_token.type

		if res.error: return res, None

		if op_tok_type == T_JOIN:
			result, error = left.joinedTo(right)
		if op_tok_type == T_MULTIPLIED:
			if isinstance(left, Number):
				result, error = right.multipliedTo(left)
			else:
				result, error = left.multipliedTo(right)

		if error:
			return res.failure(error), None

		return res.success(result.setPos(node.pos_start, node.pos_end)), node.output

	def visit_equalityNode(self, node):
		res = RunTimeResult()
		left = res.register(self.visit(node.left_node))
		right = res.register(self.visit(node.right_node))
		op_tok = node.op_token
		
		if res.error: return res, None
		
		comp = Comparision(left, op_tok, right)
		result, error = comp.compare()

		if error:
			return res.failure(error), None

		return res.success(result.setPos(node.pos_start, node.pos_end)), node.output

	def visit_conditionalNode(self, node):
		res = RunTimeResult()
		comparision_val, output = self.visit(node.if_node.if_comp_node.node)
		if comparision_val.error: return comparision_val, None

		comparision_val = comparision_val.value.value

		if comparision_val:
			for line in node.if_node.if_code_nodes:
				result, output = self.visit(line)
				if result.error: return result, None

				if output or self.debug:
					print(result.value)

		return None, None



class RunTimeResult:
	def __init__(self):
		self.value = None
		self.error = None

	def register(self, res):
		if type(res) == tuple:
			if res[0].error: self.error = res[0].error
			return res[0].value
		if res.error: self.error = res.error
		return res.value

	def success(self, value):
		self.value = value
		return self

	def failure(self, error):
		self.error = error
		return self

################
# FUNCTIONS
################

def run(file_name, text, debug=False):
	lexer = Lexer(file_name, text)
	tokens, error = lexer.makeTokens()
	if error: return None, error

	if debug:
		print('TOKENS:')
		print(tokens, '\n')

	
	for tok in tokens:
		parser = Parser(tok)
		ast = parser.parse()
		if ast.error: return None, ast.error

		if debug:
			print('\nAST:')
			print(ast.node.type)

		interpreter = Interpreter(debug=debug)
		result, output = interpreter.visit(ast.node)
		#print(result.value, result.error)
		
		if result == None and output == None:
			continue

		res = result.value
		error = result.error

		if error:
			if isinstance(error, Error):
				if file_name != '<shell>':
					print(error.asString(noArrows=True))
				else:
					print(error.asString())
			else:
				print(error)
			return None, None
		else:
			if output or debug:
				if res is not None:
					print(res)
	
	return None, None