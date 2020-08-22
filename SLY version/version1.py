# Simple mathamatical operations (+, -, *, /) are implemented
# Scope for paranthesised operations is implemented, although not finished
# Storing variables is implemented as numbers or the result of an expression
# Illegal character checking is implemented

# Using variables in expressions is not yet implemented
# Error handling is not yet implemented, e.g. 0 / 0 will not work
# Negative numbers are not yet implemented
# Floats are not yet implemented
# An exit keyword is not yet implemented



from sly import Lexer, Parser

class BasicLexer(Lexer):
    tokens = { NAME, NUMBER, PLUS, TIMES, MINUS, DIVIDE, ASSIGN, LPAREN, RPAREN }
    ignore = ' \t'

    # Tokens
    
    NUMBER = r'\d+'

    @_(r'\d+')
    def NUMBER(self, t):
        t.value = int(t.value)
        return t

    # Special symbols
    PLUS = r'(add)'
    MINUS = r'(minus)'
    TIMES = r'(multiplied)'
    DIVIDE = r'(divided)'
    ASSIGN = r'(equals)'
    LPAREN = r'\('
    RPAREN = r'\)'

    NAME = r'[a-zA-Z_][a-zA-Z0-9_]*'

    # Ignored pattern
    ignore_newline = r'\n+'

    # Extra action for newlines
    def ignore_newline(self, t):
        self.lineno += t.value.count('\n')

    def error(self, t):
        print("Illegal character '%s'" % t.value[0])
        self.index += 1

class BasicParser(Parser):
    tokens = BasicLexer.tokens

    def __init__(self):
        self.names = {}
    
    @_('NAME ASSIGN expr')
    def expr(self, p):
        self.names[p.NAME] = p.expr
        return p.expr

    @_('expr PLUS term')
    def expr(self, p):
        return p.expr + p.term

    @_('expr MINUS term')
    def expr(self, p):
        return p.expr - p.term

    @_('term')
    def expr(self, p):
        return p.term

    @_('term TIMES factor')
    def term(self, p):
        return p.term * p.factor

    @_('term DIVIDE factor')
    def term(self, p):
        return p.term / p.factor

    @_('factor')
    def term(self, p):
        return p.factor

    @_('NUMBER')
    def factor(self, p):
        return p.NUMBER

    @_('NAME')
    def expr(self, p):
        try:
            return self.names[p.NAME]
        except LookupError:
            print(f'Undefined name {p.NAME!r}')
            return 0

if __name__ == '__main__':
    lexer = BasicLexer()
    parser = BasicParser()

#     test = '''
# 5 add 5
# x equals 5 add 5
#     '''

#     for t in lexer.tokenize(test):
#         print(t)

    while True:
        try:
            text = input('engpy > ')
            result = parser.parse(lexer.tokenize(text))
            print(result)
        except EOFError:
            break