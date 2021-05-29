import tokenize
from tokenize import NUMBER, STRING, NAME, OP, ENDMARKER


class Node:
    def __init__(self, kind, value=None, op1=None, op2=None, op3=None):
        self.kind = kind
        self.value = value
        self.op1 = op1
        self.op2 = op2
        self.op3 = op3


class Tokenizer:
    def __init__(self, tokengen):
        """Call with tokenize.generate_tokens(...)."""
        self.tokengen = tokengen
        self.tokens = []
        self.pos = 0

    def mark(self):
        return self.pos

    def reset(self, pos):
        self.pos = pos

    def get_token(self):
        token = self.peek_token()
        self.pos += 1
        return token

    def peek_token(self):
        if self.pos == len(self.tokens):
            self.tokens.append(next(self.tokengen))
        return self.tokens[self.pos]


class ParserBase:
    def __init__(self, tokenizer):
        self.tokenizer = tokenizer

    def mark(self):
        return self.tokenizer.mark()

    def reset(self, pos):
        self.tokenizer.reset(pos)

    def expect(self, arg):
        token = self.tokenizer.peek_token()
        if token.type == arg or token.string == arg:
            return self.tokenizer.get_token()
        return None

    def term(self):
        token = self.tokenizer.peek_token()
        if token.type == NUMBER or token.type == NAME:
            return self.tokenizer.get_token()
        return None


class Parser(ParserBase):
    ADD, CONST = range(2)

    def __init__(self, tokenizer):
        super().__init__(tokenizer)

    def expr(self):
        t = self.term()
        if t:
            pos = self.mark()
            n1 = Node(self.CONST, value=int(t.string))
            op = self.expect('+')
            if op:
                t = self.term()
                if t:
                    n2 = Node(self.CONST, value=int(t.string))
                return Node(self.ADD, op1=n1, op2=n2)
            self.reset(pos)

        return None
    def program(self):
        while True:
            token=self.tokenizer.get_token()
            if token.type==ENDMARKER:
                break
            
            print(token)
            # self.expr()


Istop = 0
Ipush = 1
Iadd = 2


class Compiler:
    b_c = []
    pc = 0

    def gen(self, command):
        self.b_c.append(command)
        self.pc += 1

    def compile(self, node):
        if node.kind == Parser.CONST:
            self.gen(Ipush)
            self.gen(node.value)
        elif node.kind == Parser.ADD:
            self.compile(node.op1)
            self.compile(node.op2)
            self.gen(Iadd)

    def get_bc(self):
        self.b_c.append(Istop)
        return self.b_c


class Vm:
    def __init__(self):
        self.vm_instructions = [("Istop", 0),
                                ("Ipush", 1), ("Iadd", 0)]

    def print_instruction(self, b_c, pc):
        op = b_c[pc]

        n_args = self.vm_instructions[op][1]
        inst_name = self.vm_instructions[op][0]

        if n_args == 0:
            print("{0} {1}".format(pc, inst_name))
        elif n_args == 1:
              print("{0} {1} {2}".format(pc, inst_name, b_c[pc + 1]))
        elif n_args == 2:
                print("{0} {1} {2} {3}".format(pc, inst_name,
                      b_c[pc + 1],
                      b_c[pc + 2]))

    def run(self, b_c, trace=True):
        stack=[]
        pc=0
        vm_is_running=True
        while vm_is_running:
            if trace:
                self.print_instruction(b_c, pc)
            op=b_c[pc]
            if op==Istop:
                break
            elif op==Ipush:
                pc+=1
                arg=b_c[pc]
                stack.append(arg)
            elif op==Iadd:
              b=stack.pop()
              a=stack.pop()
              stack.append(a+b)        
            pc+=1 
        print('stack:',stack)        
                                                        


SRC = 'src.txt'


def main():
    tree = None
    with tokenize.open(SRC) as f:
        tokens = tokenize.generate_tokens(f.readline)
        tokenizer = Tokenizer(tokens)
        parser = Parser(tokenizer)
        tree = parser.program()
    compiler = Compiler()
    vm=Vm()
    print(tree)
    compiler.compile(tree)
    b_c = compiler.get_bc()
    print(b_c)
    vm.run(b_c)


main()
