import ply.lex as lex


tokens = ('NAME', 'OR', 'CLINI', 'LPAREN', 'RPAREN', 'LBRACKET', 'RBRACKET', 'GROUP', 'TIMES', 'EMPTY')
t_NAME = r'.'
t_EMPTY = r'\$|\#'

last_bracket = ''
last_paren = ''


def t_LBRACKET(t):
    r'\['
    global last_bracket, last_paren
    if last_paren == 'LPAREN' or last_bracket == 'LBRACKET':
        t.type = 'NAME'
        return t
    last_bracket = t.type
    return t


def t_RBRACKET(t):
    r'\]'
    global last_bracket, last_paren
    if last_paren == 'LPAREN':
        t.type = 'NAME'
        return t
    last_bracket = t.type
    return t


def t_OR(t):
    r'\|'
    global last_bracket
    if last_bracket == 'LBRACKET' or last_paren == "LPAREN":
        t.type = 'NAME'
    return t


def t_CLINI(t):
    r'\*|\\.\.\.'
    global last_bracket, last_paren
    if last_bracket == 'LBRACKET' or last_paren == 'LPAREN':
        t.type = 'NAME'
    return t


def t_LPAREN(t):
    r'\('
    global last_bracket, last_paren
    if last_bracket == 'LBRACKET' or last_paren == 'LPAREN':
        t.type = 'NAME'
        return t
    last_paren = t.type
    return t


def t_RPAREN(t):
    r'\)'
    global last_bracket, last_paren
    if last_bracket == 'LBRACKET':
        t.type = 'NAME'
        return t
    last_paren = t.type
    return t


def t_GROUP(t):
    r'\\([1-9][0-9]*)'
    global last_bracket, last_paren
    if last_bracket == 'LBRACKET' or last_paren == 'LPAREN':
        t.type = 'NAME'
    return t


def t_TIMES(t):
    r'\{[1-9][0-9]*}'
    global last_bracket, last_paren
    if last_bracket == 'LBRACKET' or last_paren == 'LPAREN':
        t.type = 'NAME'
    return t


t_ignore = ' \r\t\n'


def t_error(t):
    print("Illegal character '%s'", t.value[0])
    t.lexer.skip(1)

lexer = lex.lex()


if __name__ == "__main__":
    data = '[$]'
    lexer.input(data)

    while True:
        tok = lexer.token()
        if not tok:
            break
        print(tok)