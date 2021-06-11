# *****************************Вспомогательные функции**********************
isa = isinstance
Symbol = str


def read(s):
    """
        Читает lisp подобное выражение из строки и лексемазирует его 
    """
    return read_from(tokenize(s))


def tokenize(s):
    """
         Ковертирует строку в питон список токенов
    """
    return s.replace('(', ' ( ').replace(')', ' ) ').replace('>', ' > ').replace('-', ' - ').split()


def read_from(tokens):
    """
         Читает выражение,создает 'атомы' - float или строки
    """
    try:
        if len(tokens) == 0:
            raise SyntaxError('unexpected EOF while reading')
        token = tokens.pop(0)
        if token == '(' :
            L = []
            while tokens[0] != ')' :
                L.append(read_from(tokens))
            tokens.pop(0)    
            return L
        elif token == '>' :
            L = []
            while tokens[0] != '-'  :
                L.append(read_from(tokens))
            tokens.pop(0)    
            return L    
        elif token == '$' :
            L = ['$']
            while tokens[0] != '!' :
                L.append(read_from(tokens))
            tokens.pop(0)    
            return L        
        elif token == ')':
            raise SyntaxError('unexpected )')
        else:
            return atom(token)
    except Exception:
        return L
        pass

def atom(token):
    """
       Числа становятся числами float , остальное символами,строками 
    """
    try:
        return float(token)
    except ValueError:
        try:
            return float(token)
        except ValueError:
            return Symbol(token)





