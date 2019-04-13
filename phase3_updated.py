import random
import sys

sys.path.insert(0, "../..")

quad=[]
l1=[]
vcount=1
lcount=1

scope_level = -1

if sys.version_info[0] >= 3:
    raw_input = input

reserved = {
    'public' : 'PUBLIC',
    'static': 'STATIC',
    'void': 'VOID',
    'main' : 'MAIN',
    'class' : 'CLASS',
    'String' : 'STRING',
    'args' : 'ARGS',
    'int' : 'INT',
    'float' : 'FLOAT',
    'boolean' : 'BOOLEAN',
    'false' : 'FALSE',
    'true' : 'TRUE',
    'if' : 'IF',
    'else' : 'ELSE',
    'private' : 'PRIVATE',
    'protected' : 'PROTECTED',
    'do' : 'DO',
    'while' : 'WHILE',
}

tokens = (
    'NAME', 'NUMBER', 'FLOATNUMBER', 'REL_EQ', 'REL_NEQ', 'REL_GTEQ', 'REL_LTEQ','MINEQ','PLUSEQ','DIVEQ','MULEQ',
    'LBRACE', 'RBRACE', 'LBRACKET', 'RBRACKET'
) + tuple(reserved.values());

literals = ['=', '+', '-', '*', '/', '(', ')', '<', '>', '!','{','}',';', ':']

# Tokens
# t_multicomment = r'/\*.*\n.*\*/'
t_REL_EQ = r'=='
t_REL_GTEQ = r'>='
t_REL_LTEQ = r'<='
t_REL_NEQ = r'!='
t_MINEQ = r'-='
t_PLUSEQ = r'\+='
t_DIVEQ = r'/='
t_MULEQ = r'\*='
# t_comment = r'//.*'

t_ignore = " \t"
def t_comment_ignore(t):
    r"//.*|/\*+[^*]*\*+(?:[^/*][^*]*\*+)*/"


def t_NAME(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value,'NAME')
    print(t)
    return t

def t_FLOATNUMBER(t):
    r'[0-9]*[.][0-9]+'
    # print(t.value)
    t.value = float(t.value)
    # print("In floatnumber", t.value)
    return t

def t_NUMBER(t):
    r'\d+'

    t.value = int(t.value)
    return t


# def t_FLOATNUMBER(t):


def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")
    # print(t.lexer.lineno)

def t_LBRACE(t):
    r'{'
    # print(t)
    global scope_level
    scope_level += 1
    # print(t, scope_level)
    return t

def t_RBRACE(t):
    r'}'
    # global scope_level
    # scope_level -= 1
    # print("Reduced here", t)
    return t

def t_LBRACKET(t):
    r'\['
    return t

def t_RBRACKET(t):
    r'\]'
    return t

def t_error(t):
    print("Illegal character '%s'"  %t.value)
    t.lexer.skip(1)

# Build the lexer
import ply.lex as lex
lexer = lex.lex()

# lexer.input(s)

# Parsing rules

precedence = (
    ('left','='),
    ('left','REL_EQ','REL_NEQ'),
    ('left', '<','>','REL_GTEQ', 'REL_LTEQ'),
    ('left', '+', '-'),
    ('left', '*', '/'),
    ('right', 'UMINUS','!'),
)

# dictionary of names
symbol_table = dict()
names = {}
start = 'start'

def p_start(p):
    ''' start : PUBLIC CLASS NAME LBRACE statements main_body RBRACE
              | CLASS NAME LBRACE statements main_body RBRACE'''

def p_main_body(p):
    ''' main_body : PUBLIC STATIC VOID MAIN '(' STRING ARGS ')' LBRACE body RBRACE 
                  | body '''

def p_body(p):
    ''' body : statements '''

def p_statements(p):
    ''' statements : statements statement 
                   | '''

def p_blockstatemet(p):
    ''' block_statement : LBRACE statements RBRACE '''
    global scope_level
    scope_level-=1

def p_statement_do_while(p):
    ''' statement : DO block_statement WHILE '(' expression ')' ';' '''    
#    ll
#    vcount
# num_called = 0;

def p_else_if_block(p):
    ''' else_if : ELSE IF '(' condition ')' block_statement else_if
                | ELSE IF '(' condition ')' statement else_if 
                | ELSE block_statement
                | ELSE statement
                | '''
    # print("HEREEEEEEE")
    # global num_called
    # num_called+=1
    global lcount
    global quad
 
    if(p[1]=='else' and p[2]=='if'):
 
        label=(str("L"+str(lcount)))
        lcount+=1

        q=["Label",None,None,label]
        quad.append(q)
    
    else:
        label=(str("L"+str(lcount)))
        lcount+=1

        q=["goto",None,None,str("L"+str(lcount))]
        quad.append(q)

        q=["Label",None,None,label]
        quad.append(q)        


def p_statement_if(p):
    ''' statement : IF '(' condition ')' block_statement else_if
                  | IF '(' condition ')' statement else_if '''
    print('p inside statement_if',list(p))
    global quad
    if (len(list(p))==7):
        print('quad length',len(quad))
        print('quad',quad)
        print('popping element',quad[len(quad)-3])
        quad.pop(len(quad)-3)
        print('quad',quad)
        pass
    # global scope_level
    # global num_called
    # scope_level -= num_called + 1
    # num_called = 0
    # print("Reduced at", p.lexer.lineno)
    
def p_condition(p):
    '''condition : expression '''
    global l1
    global quad

    q=["ifFalse", l1[0], "goto", str("L"+str(lcount))]
    print('q inside statement_if',q)
    quad.append(q)
    l1.pop()

def p_statement_declare(p):
    ''' statement : INT NAME ';'
                  | FLOAT NAME ';'
                  | BOOLEAN NAME ';' 
                  | INT LBRACKET RBRACKET NAME ';'
                  | FLOAT LBRACKET RBRACKET NAME ';'
                  | INT NAME LBRACKET RBRACKET ';'
                  | FLOAT NAME LBRACKET RBRACKET ';' '''


    #print("In p_statement_declare", p.slice)
    global scope_level
    if((p[2] == '[' and p[3] == ']') or (p[3] == '[' and p[4] == ']')):
        names[p[2]] = "{}"
    elif p[1] == "int" :
        names[p[2]] = 0
    elif p[1] == "float":
        names[p[2]] = 0.0
    elif p[1] == "boolean":
        names[p[2]] = "False"
    if scope_level == 0:
        scope = 'global'
    else:
        scope = 'scope'+str(scope_level)
    #print("caught",p.slice)
    if(p.slice[2].value=='['):
        token = [p.slice[4].type,p.slice[4].value, p.lexer.lineno - 1,p[1],scope,names[p[2]]]
#    elif(p.slice[3].value=='['):
#        token = [p.slice[4].type,p.slice[4].value, p.lexer.lineno - 1,p[1],scope,names[p[2]]]
    else:
        token = [p.slice[2].type, p.slice[2].value, p.lexer.lineno - 1,p[1],scope,names[p[2]]]
    #print(token)
    if(scope_level not in symbol_table.keys()):
        symbol_table[scope_level] = dict()
    if(token[5]=='{}' and p.slice[2].value=='['):
        symbol_table[scope_level][token[1]+"_"+str(p.lexer.lineno - 1)] = token
    else:
        symbol_table[scope_level][p[2]+"_"+str(p.lexer.lineno - 1)] = token

# def p_statement_assign(p):
#     '''statement : NAME "=" expression ';' '''
#     print("In p_statement_assign", p.slice)
#     print(p[2])

def p_statement_init(p):
    '''statement : NAME "=" expression ';'
                 | INT NAME "=" expression ';'
                 | FLOAT NAME "=" expression ';'
                 | BOOLEAN NAME "=" TRUE ';'
                 | BOOLEAN NAME "=" FALSE ';'
                 | '''
    global l1
    if(p[2]=='='):
        l1.append(p[1])
        l1.append(p[3])
    elif(p[3]=='='):
        l1.append(p[2])
        l1.append(p[4])
    print(l1)
        
    global scope_level
    # print("STATEMENT")
    # print(symbol_table, scope_level)
    # print("In p_statement_init", p.slice)
    # print(p[2])
    if scope_level == 0:
        scope = 'global'
    else:
        scope = 'scope'+str(scope_level)
    if(scope_level not in symbol_table.keys()):
            symbol_table[scope_level] = dict()
    if(p[2] == '='):
        #print('caught')
        #print(symbol_table)
        # token = [p.slice[2].type, p.slice[2].value, p.lexer.lineno,p[1],scope, 'placeholder']
        token = None
        for s in range(scope_level, -1, -1):
            flag = 0
            for i in symbol_table[s].keys():
                # print(len(i.split('_')[0]), len(p[1]))
                if(i.split('_')[0]==p[1]):
                    token = symbol_table[s][i].copy()
                    token[4] = scope
                    token[2] = p.lexer.lineno - 1
                    # print(key_p)
                    flag = 1
                    break
            if(flag):
                break
                
            # if(p[1] in symbol_table[s].keys()):
            #     token = symbol_table[s][key_p].copy()
            #     token[4] = scope
            #     token[2] = p.lexer.lineno - 1
            #     break
        if(not token):
            print("Token "+p[1]+" not found")
        
        key = p[1]+"_"+str(p.lexer.lineno-1)
        symbol_table[scope_level][key] = token
        if (type(p[3]) == bool ):
            if symbol_table[scope_level][key][3] == "boolean":
                names[p[1]] = p[3]
                symbol_table[scope_level][key][5] = names[p[1]]
            else:
                print("Type error : assignment not supported")
        elif (type(p[3]) == int ) :
            if symbol_table[scope_level][key][3] == "int":
                names[p[1]] = p[3]
                symbol_table[scope_level][key][5] = names[p[1]]
            elif symbol_table[scope_level][key][3] == "float":
                # print("Here")
                names[p[1]] = float(p[3])
                symbol_table[scope_level][key][5] = names[p[1]]
            else:
                print("Type error : assignment not supported")
        elif ( type(p[3]) == float ) :
            if symbol_table[scope_level][key][3] == "float":
                names[p[1]] = p[3]
                symbol_table[scope_level][key][5] = names[p[1]]
            else:
                print("Type error : assignment not supported")
    else:   
        # print("Printing p")
        # for i in p:
        #     print(i)
        key = p[2]+"_"+str(p.lexer.lineno-1)
        symbol_table[scope_level][key] = [p.slice[2].type, p.slice[2].value, p.lexer.lineno - 1,p[1],scope, 'placeholder']
        names[p[2]] = p[4]
        symbol_table[scope_level][key][5] = names[p[2]]
        symbol_table[scope_level][key][3] = p[1]
        
    global vcount
    #global l1

    q=[]

    print('l1',l1)
    q.append("=")
    q.append(l1[1])
    q.append(None)
    q.append(l1[0])
    print('q inside statement_init',q)
    quad.append(q)
    l1=[]

    
def p_statement_expr(p):
    '''statement : expression ";" '''
    print(p[1])

def p_expr_boolean(p):
    '''expression : TRUE
                  | FALSE '''
    p[0] = p[1]

def p_expression_binop(p):
    '''expression : expression '+' expression
                  | expression '-' expression
                  | expression '*' expression
                  | expression '/' expression'''
    global l1
    l1.append(p[1])
    l1.append(p[3])
    print(l1)
    
    if p[2] == '+':
        p[0] = p[1] + p[3]
    elif p[2] == '-':
        p[0] = p[1] - p[3]
    elif p[2] == '*':
        p[0] = p[1] * p[3]
    elif p[2] == '/':
        p[0] = p[1] / p[3]

    q=[]
    global quad
    global vcount
    #global l1
    
    
    res = str("t"+str(vcount))
    vcount+=1
    print('l1',l1)
    arg2=l1.pop()
    arg1=l1.pop()
    l1.append(res)
    op=p[2]
    q.append(op)
    q.append(arg1)
    q.append(arg2)
    q.append(res)
    print('q inside expression_binop',q)
    quad.append(q)
    #print(quad)


def p_statement_relational(p):
    '''expression : expression '>' expression
                 | expression '<' expression'''
    global l1
    l1.append(p[1])
    l1.append(p[3])
    print(l1)
    
    if p[2] == '>':
        p[0] = (p[1] > p[3])
    elif p[2] == '<':
        p[0] = (p[1] < p[3])
        
    q=[]        
    global quad
    global vcount
    #global l1

    res = str("t"+str(vcount))
    vcount+=1
    print('l1',l1)
    arg2=l1.pop()
    arg1=l1.pop()
    l1.append(res)
    op=p[2]
    q.append(op)
    q.append(arg1)
    q.append(arg2)
    q.append(res)
    print('q inside statement_relational',q)
    quad.append(q)
    #print(quad)


def p_relop(p):
    '''expression : expression REL_EQ expression
              | expression REL_NEQ expression
                      | expression REL_GTEQ expression
              | expression REL_LTEQ expression'''
    global l1
    l1.append(p[1])
    l1.append(p[3])
    print(l1)
    
    if p[2] == "==" :
        p[0] = (p[1] == p[3])
    elif p[2] == "!=" : 
        p[0] = (p[1] != p[3])
    elif p[2] == "<=" : 
        p[0] = (p[1] <= p[3])
    elif p[2] == ">=" :
        p[0] = (p[1] >= p[3])

    q=[]
    global quad
    global vcount
    #global l1
    
    res = str("t"+str(vcount))
    vcount+=1
    print('l1',l1)
    arg2=l1.pop()
    arg1=l1.pop()
    l1.append(res)
    op=p[2]
    q.append(op)
    q.append(arg1)
    q.append(arg2)
    q.append(res)
    print('q inside relop',q)
    quad.append(q)
    #print(quad)

   
def p_operation_equals(p):
    '''statement : NAME MINEQ expression ";"
                 | NAME PLUSEQ expression ";"
                 | NAME DIVEQ expression ";"
                 | NAME MULEQ expression ";" '''
    global l1
    l1.append(p[1])
    l1.append(p[3])
    print(l1)
    
    print("In p_operation_equals", p.slice)
    if p[2] == '+=':
        names[p[1]] = names[p[1]] + p[3]
        symbol_table[scope_level][p[1]][5] = names[p[1]]
    elif p[2] == '-=':
        names[p[1]] = names[p[1]] - p[3]
        symbol_table[scope_level][p[1]][5] = names[p[1]]
    elif p[2] == '/=':
        names[p[1]] = names[p[1]] / p[3]
        symbol_table[scope_level][p[1]][5] = names[p[1]]
    elif p[2] == '*=':
        names[p[1]] = names[p[1]] * p[3]
        symbol_table[scope_level][p[1]][5] = names[p[1]]
        
    q=[]
    global quad
    global vcount
    #global l1

    res = str("t"+str(vcount))
    vcount+=1
    print('l1',l1)
    arg2=l1.pop()
    arg1=l1.pop()
    l1.append(res)
    op=p[2]
    q.append(op)
    q.append(arg1)
    q.append(arg2)
    q.append(res)
    print('q inside operational_equals',q)
    quad.append(q)
    #print(quad)

def p_expression_not(p):
    '''expression : '!' expression'''
    p[0] = not (p[2])

def p_expression_uminus(p):
    '''expression : '-' expression %prec UMINUS'''
    global l1
    l1.appned(p[2])
    print(l1)
    
    p[0] = -p[2]
    

def p_expression_group(p):
    '''expression : '(' expression ')' '''
    global l1
    l1.append(p[2])
    print(l1)
    
    p[0] = p[2]


def p_expression_number(p):
    '''expression : FLOATNUMBER
                  | NUMBER'''
#    global l1
#    l1.append(p[1])
#    print(l1)
    
    p[0] = p[1]


def p_expression_name(p):
    '''expression : NAME'''
#    global l1
#    l1.append(p[1])
#    print(l1)
    
    try:
        p[0] = names[p[1]]
    except LookupError:
        print("Undefined name '%s'" % p[1])
        p[0] = 0


def p_error(p):
    if p:
        print("Syntax error at '%s'" % p.lineno)
    else:
        print("Syntax error at EOF")

import ply.yacc as yacc
parser = yacc.yacc()

def print_quad():
	quad
	print("QUAD TABLE\n")
	for i in range(0, len(quad)):
	    print(i, "  ", quad[i])
#print_quad()

try:
    f = open(sys.argv[1],"r")
    s=f.read()
except:
    print("Please enter input filename as argument.")
    sys.exit(1)

parser = yacc.yacc()
parser.parse(s)
# print("Here")
print(symbol_table)
print("\n")
print_quad()
