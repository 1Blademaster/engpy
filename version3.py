# Added Strings 
# Added variable class to store the type of variables as well as value etc

# Error handling is not yet implemented, e.g. 0 / 0 will not work
# If-else statements have not yet been implemented
# Loops (while/for) have not yet been implemented



from sly import Lexer, Parser

class BasicLexer(Lexer):
    tokens = {QUIT, VAR, NUMBER, ADD, MULTIPLIED, MINUS, DIVIDED, ASSIGN, UMINUS, LPAREN, RPAREN, LSBRAC, RSBRAC, OUTPUT, DQUOTE, STRING}
    ignore = ' \t'

    # literals = {'[', ']',}
    
    NUMBER = r'(?<!\S)[+-]?([0-9]+([.][0-9]*)?|[.][0-9]+)(?!\S)'

    @_(r'(?<!\S)[+-]?([0-9]+([.][0-9]*)?|[.][0-9]+)(?!\S)')
    def NUMBER(self, t):
        t.value = float(t.value)
        if (t.value).is_integer():
            t.value = int(t.value)
        return t

    ADD = r'(add)'
    MINUS = r'(minus)'
    MULTIPLIED = r'(multiplied)'
    DIVIDED = r'(divided)'
    ASSIGN = r'(equals)'
    UMINUS = r'\-'
    DQUOTE = r'\"'
    LPAREN = r'\('
    RPAREN = r'\)'
    LSBRAC = r'\['
    RSBRAC = r'\]'

    QUIT = r'(QUIT)'
    OUTPUT = r'(output)'
    
    VAR = r'(?<!\S)[a-zA-Z_][a-zA-Z0-9_]*(?!\S)'
    STRING = r'([^\[\][\n"]+)'

    ignore_newline = r'\n+'

    def ignore_newline(self, t):
        self.lineno += t.value.count('\n')

    def error(self, t):
        print("Illegal character '%s'" % t.value[0])
        self.index += 1

class BasicParser(Parser):
    tokens = BasicLexer.tokens

    precedence = (
        ('left', 'ADD', 'MINUS'),
        ('left', 'MULTIPLIED', 'DIVIDED'),
        # ('left', '(', ')'),
        ('right', 'UMINUS'),
    )

    def __init__(self):
        self.VARs = {}

    @_('OUTPUT LSBRAC expr RSBRAC',
       'OUTPUT LSBRAC string RSBRAC')
    def expr(self, p):
        return p[2], 1

    @_('quitProgram')
    def expr(self, p):
        exit()

    @_('VAR ASSIGN expr',
       'VAR ASSIGN string')
    def expr(self, p):
        var = p[2]
        if type(var) == int:
            varType = int
        elif type(var) == float:
            varType = float
        else:
            varType = str
        self.VARs[p.VAR] = variable(varType, var)
        return self.VARs[p.VAR].value

    @_('expr ADD term',
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

    @_('LPAREN expr RPAREN')
    def factor(self, p):
        return p.expr

    @_('UMINUS factor')
    def factor(self, p):
        return -p.factor

    @_('NUMBER')
    def factor(self, p):
        return p.NUMBER

    @_('VAR')
    def factor(self, p):
        try:
            return self.VARs[p.VAR].value
        except LookupError:
            print(f'Undefined VAR {p.VAR!r}')
            return

    @_('QUIT')
    def quitProgram(self, p):
        return

    @_('DQUOTE VAR DQUOTE',
       'DQUOTE STRING DQUOTE')
    def string(self, p):
        return p[1]



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



class variable():
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __repr__(self):
        return f'{self.value}'


if __name__ == '__main__':
    lexer = BasicLexer()
    parser = BasicParser()

    test = '''
    "hello"
    ( 5 add 5 )'''

    for t in lexer.tokenize(test):
        print(t)

    while True:
        try:
            text = input('engpy > ')
            result = parser.parse(lexer.tokenize(text))
            if type(result) == tuple:
                print(result[0])
        except EOFError:
            break