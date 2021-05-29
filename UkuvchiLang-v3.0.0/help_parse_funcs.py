# *****************************Вспомогательные функции**********************
# import pdb
# pdb.set_trace()

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
    return s.replace('(',' ( ').replace(')',' ) ').split()
 
def read_from(tokens):
    """
        Читает выражение,создает 'атомы' - float или строки
    """    
    if len(tokens) == 0:
        raise SyntaxError('unexpected EOF while reading')
    token = tokens.pop(0)
    if '(' == token:
        L = []
        while tokens[0] != ')':
            L.append(read_from(tokens))
        tokens.pop(0) # pop off ')'
        return L
    elif ')' == token:
        raise SyntaxError('unexpected )')
    else:
        return atom(token)
 
def atom(token):
    """
       Числа становятся числами float , остальное символами,строками 
    """    
    try: return float(token)
    except ValueError:
        try: return float(token)
        except ValueError:
            return Symbol(token)


if __name__ == '__main__':
    c = None
    with open('src.txt', 'r') as f:
      s = "( (arif 8 + 3) (arif 9) )"
      c = read(s)
      print(c)
      # для ($ (arif 8.0 + 3.0))
      assert c==[['arif', 8.0, '+', 3.0]]


                

