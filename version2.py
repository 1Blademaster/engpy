# Negative numbers have been implemented
# Using parenthesises have been implemented
# Floating point numbers have been implemented
# Precedence has been implemented
# Using variables in expressions has been implemented
# QUIT keyword to end program has been implemented
# An output token has been made to output information to the user
# An Interpreter class has been made to read from multiline strings/files

# Error handling is not yet implemented, e.g. 0 / 0 will not work
# If-else statements have not yet been implemented
# Loops (while/for) have not yet been implemented



from sly import Lexer, Parser

class BasicLexer(Lexer):
    tokens = {QUIT, NAME, NUMBER, PLUS, MULTIPLIED, MINUS, DIVIDED, ASSIGN, LPAREN, RPAREN, UMINUS, OUTPUT}
    ignore = ' \t'

    # Tokens

    literals = {'(', ')', '[', ']'}
    
    NUMBER = r'[+-]?([0-9]+([.][0-9]*)?|[.][0-9]+)'

    @_(r'[+-]?([0-9]+([.][0-9]*)?|[.][0-9]+)')
    def NUMBER(self, t):
        t.value = float(t.value)
        if (t.value).is_integer():
            t.value = int(t.value)
        return t

    # Special symbols
    PLUS = r'(add)'
    MINUS = r'(minus)'
    MULTIPLIED = r'(multiplied)'
    DIVIDED = r'(divided)'
    ASSIGN = r'(equals)'
    UMINUS = r'\-'

    QUIT = r'(QUIT)'
    OUTPUT = r'(output)'

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

    precedence = (
        ('left', 'PLUS', 'MINUS'),
        ('left', 'MULTIPLIED', 'DIVIDED'),
        ('right', 'UMINUS'),
    )

    def __init__(self):
        self.names = {}

    @_('OUTPUT "[" expr "]"') # Note: return a tuple where the first item is an indication
                              # on wether to print out the second item, e.g.
                              # (1, 'output should be printed)
                              # (0, 'output should not be printed)
                              # and this will be decided in the __main__ section
    def expr(self, p):
        return p.expr, 1

    @_('quitProgram')
    def expr(self, p):
        exit()

    @_('NAME ASSIGN expr')
    def expr(self, p):
        self.names[p.NAME] = p.expr
        return self.names[p.NAME]

    @_('expr PLUS term',
       'expr MINUS term')
    def expr(self, p):
        if p[1] == 'add':
            return p.expr + p.term
        return p.expr - p.term

    @_('term')
    def expr(self, p):
        return p.term

    @_('term MULTIPLIED factor',
       'term DIVIDED factor')
    def term(self, p):
        if p[1] == 'multiplied':
            return p.term * p.factor
        return p.term / p.factor

    @_('factor')
    def term(self, p):
        return p.factor

    @_('"(" expr ")"')
    def factor(self, p):
        return p.expr

    @_('UMINUS factor')
    def factor(self, p):
        return -p.factor

    @_('NUMBER')
    def factor(self, p):
        return p.NUMBER

    @_('NAME')
    def factor(self, p):
        try:
            return self.names[p.NAME]
        except LookupError:
            print(f'Undefined name {p.NAME!r}')
            return

    @_('QUIT')
    def quitProgram(self, p):
        return



class Interpreter():
    def __init__(self, lexer, parser):
        self.lexer = lexer
        self.parser = parser

    def output(self, inputData):
        try:
            for line in inputData.splitlines():
                result = self.parser.parse(self.lexer.tokenize(line))
                if type(result) == tuple:
                    return result[0]
        except EOFError as e:
            print(e)



if __name__ == '__main__':
    lexer = BasicLexer()
    parser = BasicParser()

    # test = '''
    # x equals 5
    # output[x add 5]'''

    # for t in lexer.tokenize(test):
    #     print(t)

    while True:
        try:
            text = input('engpy > ')
            result = parser.parse(lexer.tokenize(text))
            if type(result) == tuple:
                print(result[0])
        except EOFError:
            break