import random
import sys

sys.path.insert(0, "../..")

quad=[]
l1=[]
vcount=1
lcount=1
nextcount=1
comment_count = 0
scope_level = -1

stop_prop = False

# node_list = []
scope_dict = {i:1 for i in range(200)}

ifFalselabel = []

class Node:
    def __init__(self, type, children=None):
        self.type = type
        if(children):
            self.children=children
        else:
            self.children=[]

    def indent_tree(self, level=0):
        print('\t'*level + repr(self.type))
        for child in self.children:
            if(child is not None):
                child.indent_tree(level+1)

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
    global comment_count
    comment_count+=1

def t_NAME(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value,'NAME')
    # print(t)
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

def print_ast(root):
    print(root.type)
    for i in root.children:
        print_ast(i)

root = None
def p_start(p):
    ''' start : PUBLIC CLASS NAME LBRACE statements main_body RBRACE
              | CLASS NAME LBRACE statements main_body RBRACE'''
    # print("AST")
    global root
    root = Node('PROGRAM')
    if len(list(p))==7:
        root.children=[p[4][1],p[5][1]]
    else:
        root.children=[p[5][1],p[6][1]]
    
    # print_ast(root)
    # print(node_list)
    # for node in node_list:
    # 	print(node.type)

def p_main_body(p):
    ''' main_body : PUBLIC STATIC VOID MAIN '(' STRING ARGS ')' LBRACE body RBRACE 
                  | body '''
    if len(list(p))!=2:
        p[0]=p[10]
    else:
        p[0]=p[1]

def p_body(p):
    ''' body : statements '''
    p[0]=p[1]

def p_statements(p):
    ''' statements : statements statement 
                   | '''
    # print(p)
    if len(list(p))==3:
        right_child=p[2][1]
        if p[1][1] is not None:
            left_child=p[1][1]
            parent=Node("SEQ",[left_child,right_child])
        else:
            parent=Node("SEQ",[right_child])
        p[0]=(None,parent)

    else:
        p[0]=(None,None)


def p_blockstatement(p):
    ''' block_statement : LBRACE statements RBRACE '''
    global scope_level
    scope_level-=1
    p[0] = p[2]
    if(scope_level not in symbol_table.keys()):
        symbol_table[scope_level] = dict()

def p_statement_do_while(p):
    ''' statement : action2 DO block_statement WHILE '(' condition ')'  ';' '''    
#    ll
#    vcount
# num_called = 0;
    # global lcount
    global scope_dict
    lcount = scope_dict[scope_level]
    global quad
    label = chr(64+scope_level) + str(lcount)
    

    q=["goto",None,None,chr(64+scope_level) + str(lcount-1)]
    quad.append(q)
    q=["Label",None,None,label]
    quad.append(q)
    # lcount+=1
    scope_dict[scope_level]+=1
    p[0] = (None, Node(p[2], [p[3][1], Node(p[4]), p[6][1]]))

def p_else_if_block(p):
    ''' else_if : ELSE IF '(' condition ')' block_statement action1 else_if
                | ELSE IF '(' condition ')' statement action1 else_if
                | ELSE block_statement action2
                | ELSE statement action2
                | action4 '''
    # print("HEREEEEEEE")
    # global num_called
    # num_called+=1
    # print(len(p))
    # print("In else_if", p.slice)
    if(len(list(p)) in [9,8]):
    	if(p[8] is None):
    		p[0] = (None, Node("ELSEIF", [p[4][1], p[6][1]]))
    	else:
    		p[0] = (None, Node("ELSEIF", [p[4][1], p[6][1], p[8][1]]))
    elif(len(list(p))==4):
    	print("p list",list(p))
    	p[0] = (None, Node("ELSE", [p[2][1]]))
    elif(len(list(p))==0):
    	p[0] = (None, None)
    # print("Leaving else_if with", p[0])


def p_action2(p):
    ''' action2 :'''
    # global lcount
    global scope_dict
    global quad

    lcount = scope_dict[scope_level]
    label=chr(64+scope_level)+str(lcount)
    replace()
    scope_dict[scope_level]+=1

    q=["Label",None,None,label]
    # print('q inside action_else',q)
    quad.append(q)

def p_action3(p):
    '''action3 :'''
    # print("in action3")
    global stop_prop
    print("In action")
    stop_prop = True

def p_action4(p):
    ''' action4 :'''
    # global lcount
    # global quad

    # label=(str("L"+str(lcount)))
    global quad
    lcount = scope_dict[scope_level]
    print("In action4")
    print(scope_level, scope_dict[scope_level])
    for i in quad:
        if(i[3]=="next"+str(scope_level)):
            i[3]=chr(64+scope_level)+str(lcount-1)
    # lcount+=1

    # q=["Label",None,None,label]
    # print('q inside action_else',q)
    # quad.append(q)

def p_action5(p):
    '''action5 :'''
    print("ACTION 5")
    print(scope_level)

def p_statement_if(p):
    ''' statement : action3 IF '(' condition ')' block_statement action1 else_if action5
                  | action3 IF '(' condition ')' statement action1 else_if action5'''
    # print('p inside statement_if',list(p))
    global quad
    global stop_prop
    if (len(list(p))==8):
    	print('quad length',len(quad))
    	print('quad',quad)
    	print('popping element',quad[len(quad)-2])
    	quad.pop(len(quad)-3)
    	print('quad',quad)
    	# print(p[-1])
    	# if(p[-1][1] is None):
    	# 	p[0] = (None, Node("IF", [p[3][1], p[5][1]]))
    	# else:
    	# 	p[0] = (None, Node("IF", [p[3][1], p[5][1], p[-1][1]]))
    	pass
    else:
    	# print("plist in if",list(p))
    	# print(p[7][1].type, p[7][1].children)
    	if(p[8] is None):
    		p[0] = (None, Node("IF", [p[4][1], p[6][1]]))
    	else:
    		print("Right")
    		p[0] = (None, Node("IF", [p[4][1], p[6][1], p[8][1]]))

    stop_prop = False
    # global scope_level
    # global num_called
    # scope_level -= num_called + 1
    # num_called = 0
    # print("Reduced at", p.lexer.lineno)

def p_action1(p):
    ''' action1 :'''
    # print('p inside action_if',list(p))
    # global lcount
    global scope_dict
    global quad

    lcount = scope_dict[scope_level]
    label = chr(64+scope_level) + str(lcount)
    scope_dict[scope_level]+=1

    q=["goto",None,None,"next"+str(scope_level)]
    # print('goto inside action_if',q)
    quad.append(q)

    q=["Label",None,None,label]
    # print('label inside action_if',q)
    quad.append(q)        


def p_condition(p):
    '''condition : expression '''
    global l1
    global quad

    lcount = scope_dict[scope_level]
    label = chr(64 + scope_level) + str(lcount)
    q=["ifFalse", l1[0], "goto", label]
    # print('q inside statement_if',q)
    quad.append(q)
    l1.pop()
    p[0] = p[1]

def replace():
    # global lcount
    global quad
    lcount = scope_dict[scope_level]
    print("replace")
    for i in quad:
        if(i[3]=="next" + str(scope_level)):
            i[3]=chr(64+scope_level)+str(lcount)

def if_exists(name):
	if(scope_level not in symbol_table.keys()):
		return False

	for var in symbol_table[scope_level].keys():
		varname = var.split('_')[0]
		if(varname == name):
			return True
	return False

def p_statement_declare(p):
    ''' statement : INT NAME ';'
                  | FLOAT NAME ';'
                  | BOOLEAN NAME ';' 
                  | INT LBRACKET NUMBER RBRACKET NAME ';'
                  | FLOAT LBRACKET NUMBER RBRACKET NAME ';'
                  | INT NAME LBRACKET NUMBER RBRACKET ';'
                  | FLOAT NAME LBRACKET NUMBER RBRACKET ';'
                  | INT LBRACKET RBRACKET NAME ';'
                  | INT NAME LBRACKET RBRACKET ';'
                  | FLOAT NAME LBRACKET RBRACKET ';'
                  | FLOAT LBRACKET RBRACKET NAME ';' '''


    print("In p_statement_declare", p.slice)
    global scope_level
    if scope_level == 0:
        scope = 'global'
    else:
        scope = 'scope'+str(scope_level)

    if(p[2] == '[' and p[3] == ']'): 
        if(not(if_exists(p[4]))):
        	names[p[4]] = "{}"
        	token = [p.slice[4].type,p.slice[4].value, p.lexer.lineno - 1-comment_count,p[1],scope,names[p[4]]]
        else:
        	print("Redeclaration of variable",p[4])
        	p_error(p)
    elif(p[3] == '[' and p[4] == ']'):
        if(not(if_exists(p[2]))):
        	names[p[2]] = "{}"
        	token = [p.slice[2].type,p.slice[2].value, p.lexer.lineno - 1-comment_count,p[1],scope,names[p[2]]]
        else:
        	print("Redeclaration of variable",p[2])
        	p_error(p)
    elif(p[2] == '[' and p[4] == ']' ):
        if(not(if_exists(p[5]))):
        	names[p[5]] = "{}"
        	token = [p.slice[5].type,p.slice[5].value, p.lexer.lineno - 1-comment_count,p[1],scope,names[p[5]]]
        else:
        	print("Redeclaration of variable",p[5])
        	p_error(p)
    elif(p[3] == '[' and p[5] == ']'):
        if(not(if_exists(p[2]))):
        	names[p[2]] = "{}"
        	token = [p.slice[2].type,p.slice[2].value, p.lexer.lineno - 1-comment_count,p[1],scope,names[p[2]]]
        else:
        	print("Redeclaration of variable",p[2])
        	p_error(p)
    elif p[1] == "int" :
        if(not(if_exists(p[2]))):
        	names[p[2]] = 0
        	token = [p.slice[2].type,p.slice[2].value, p.lexer.lineno - 1-comment_count,p[1],scope,names[p[2]]]
        else:
        	print("Redeclaration of variable",p[2])
        	p_error(p)
    elif p[1] == "float":
        if(not(if_exists(p[2]))):
        	names[p[2]] = 0.0
        	token = [p.slice[2].type,p.slice[2].value, p.lexer.lineno - 1-comment_count,p[1],scope,names[p[2]]]
        else:
        	print("Redeclaration of variable",p[2])
        	p_error(p)
    elif p[1] == "boolean":
        names[p[2]] = "False"
    
#     # print("caught",p.slice)
#     if(p.slice[2].value=='['):
#         token = [p.slice[4].type,p.slice[4].value, p.lexer.lineno - 1-comment_count,p[1],scope,names[p[3]]]
# #    elif(p.slice[3].value=='['):
# #        token = [p.slice[4].type,p.slice[4].value, p.lexer.lineno - 1,p[1],scope,names[p[2]]]
#     else:
#         token = [p.slice[2].type, p.slice[2].value, p.lexer.lineno - 1-comment_count,p[1],scope,names[p[2]]]
    #print(token)
    if(scope_level not in symbol_table.keys()):
        symbol_table[scope_level] = dict()
    if(token[5]=='{}' and p.slice[2].value=='['):
        symbol_table[scope_level][token[1]+"_"+str(p.lexer.lineno-comment_count - 1)] = token
    else:
        symbol_table[scope_level][p[2]+"_"+str(p.lexer.lineno-comment_count - 1)] = token

    if len(list(p))==4:
        # print("declared")
        left_child=Node(p[1])
        right_child=Node(p[2])
        parent=Node("DEC",[left_child,right_child])
        p[0]=(None,parent)
    elif(p[2] == '[' and p[3] == ']'):
    	left_child = Node(p[1])
    	right_child = Node(p[4])
    	parent = Node("ARRAYDEC", [left_child,right_child])
    	p[0] = (None, parent)
    elif(p[3] == '[' and p[4] == ']'):
    	left_child = Node(p[1])
    	right_child = Node(p[2])
    	parent = Node("ARRAYDEC", [left_child,right_child])
    	p[0] = (None, parent)
    elif(p[3] == '[' and p[5] == ']' ):
        print("In here")
        left_child = Node(p[1])
        right_child = Node(p[2])
        centre_child = Node(p[4])
        parent = Node("ARRAYDEC",[left_child,right_child,centre_child])
        p[0] = (None, parent)
    elif(p[2] == '[' and p[4] == ']'):
        left_child = Node(p[1])
        right_child = Node(p[3])
        centre_child = Node(p[5])
        parent = Node("ARRAYDEC",[left_child,right_child,centre_child])
        p[0] = (None, parent)


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
    # print("p[1] in init =", p[1])
    global l1
    if(p[2]=='='):
        l1.append(p[1])
        l1.append(p[3][0])
    elif(p[3]=='='):
        l1.append(p[2])
        if(not(isinstance(p[4], str))):
        	l1.append(p[4][0])
        else:
        	l1.append(p[4])

    # print("l1 in statement_init", l1)

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
        # print(symbol_table.keys)
        try:
            for s in symbol_table.keys():
                flag = 0
                print(s)
                # print(symbol_table[s].keys)
                for i in symbol_table[s].keys():
                    # print(len(i.split('_')[0]), len(p[1]))
                    if(i.split('_')[0]==p[1]):
                        print(s)
                        token = symbol_table[s][i].copy()
                        token[4] = scope
                        token[2] = p.lexer.lineno - 1 -comment_count
                        # print(key_p)
                        flag = 1
                        break
                print(p[1])
                if(flag):
                    break
                print(scope_level)

        except:
            print("Here")
            token = None
            pass

            # if(p[1] in symbol_table[s].keys()):
            #     token = symbol_table[s][key_p].copy()
            #     token[4] = scope
            #     token[2] = p.lexer.lineno - 1
            #     break
        if(not token):

            right_child = p[3][1]
            left_child = Node(p[1]+"_undefined")
            parent = Node(p[2], [left_child, right_child])
            p[0]=(None, parent)
            print("Token "+p[1]+" not found")

        else:
            key = p[1]+"_"+str(p.lexer.lineno-1-comment_count)
            print(symbol_table)
            symbol_table[scope_level][key] = token
            print(symbol_table)
            # print(type(p[3][0]))
            if (type(p[3][0]) == bool ):
                if(not(stop_prop)):
                    if(symbol_table[scope_level][key][3] == "boolean"):
                        names[p[1]] = p[3][0]
                        symbol_table[scope_level][key][5] = names[p[1]]
                    else:
                        print("Type error : assignment not supported")
            
            elif (type(p[3][0]) == int ) :
                print(l1)
                if(not(stop_prop)):
                    if(symbol_table[scope_level][key][3] == "int"):
                        names[p[1]] = p[3][0]
                        symbol_table[scope_level][key][5] = names[p[1]]
                    elif(symbol_table[scope_level][key][3] == "float"):
                        names[p[1]] = float(p[3][0])
                        symbol_table[scope_level][key][5] = names[p[1]]
                    else:
                        print("Herei")
                        print("Type error : assignment not supported")
            
            elif (type(p[3][0]) == float ) :
                if(not(stop_prop) and symbol_table[scope_level][key][3] == "float"):
                        names[p[1]] = p[3][0]
                        symbol_table[scope_level][key][5] = names[p[1]]
                else:
                    print("Type error : assignment not supported")
            
            right_child = p[3][1]
            left_child = Node(p[1])
            parent = Node(p[2], [left_child, right_child])
            p[0]=(None, parent)


    else:   
        # print("Printing p")
        # for i in p:
        #     print(i)
        if(if_exists(p[2])):
        	print("Redeclaration of variable", p[2])
        	p_error(p)

        key = p[2]+"_"+str(p.lexer.lineno-1-comment_count)
        symbol_table[scope_level][key] = [p.slice[2].type, p.slice[2].value, p.lexer.lineno - 1-comment_count,p[1],scope, 'placeholder']
        if(not(isinstance(p[4], str))):
        	names[p[2]] = p[4][0]
        else:
        	names[p[2]] = p[4]
        symbol_table[scope_level][key][5] = names[p[2]]
        symbol_table[scope_level][key][3] = p[1]


        name_child = Node(p[2])
        type_child = Node(p[1])
        # print("p.slice in else", p.slice)
        if(not(isinstance(p[4], str))):
            # print("Correct")
            parent = Node(p[3],[type_child,name_child,p[4][1]])
        else:
            # print("Incorrect")
            val_child=Node(p[4])
            parent=Node(p[3],[type_child,name_child,val_child])
        p[0] = (None, parent)

    global vcount
    #global l1
    q=[]

    if(p[2]=='='):
        # print('l1',l1)
        q.append("=")
        if(len(l1)==3):
            q.append(l1[0])
            q.append(None)
            q.append(l1[1])
        else:
            q.append(l1[1])
            q.append(None)
            q.append(l1[0])
        # print('q inside statement_init',q)
        quad.append(q)
        l1=[]

    elif(p[3]=='='):
        # print('l1',l1)
        q.append("=")
        q.append(l1[1])
        q.append(None)
        q.append(l1[0])
        # print('q inside statement_init',q)
        quad.append(q)
        l1=[]
    # print("Out of init", p[0])

def p_statement_expr(p):
    '''statement : expression ";" '''
    # print("In statement_expr", p[1])
    p[0] = p[1]


def p_expr_boolean(p):
    '''expression : TRUE
                  | FALSE '''
    p[0] = p[1]


def p_expression_binop(p):
    '''expression : expression '+' expression
                  | expression '-' expression
                  | expression '*' expression
                  | expression '/' expression'''
    global l1, root
    l1=[]
    l1.append(p[1])
    l1.append(p[3])
    # print(l1)

    if p[2] == '+':
        val = p[1][0] + p[3][0]
        newnode = Node('+',[p[1][1],p[3][1]])
        p[0] = (val, newnode)
    elif p[2] == '-':
        val = p[1][0] - p[3][0]
        newnode = Node('-',[p[1][1],p[3][1]])
        p[0] = (val, newnode)
    elif p[2] == '*':
        val = p[1][0] * p[3][0]
        newnode = Node('*',[p[1][1],p[3][1]])
        p[0] = (val, newnode)
    elif p[2] == '/':
        val = p[1][0] / p[3][0]
        newnode = Node('/',[p[1][1],p[3][1]])
        p[0] = (val, newnode)

    q=[]
    global quad
    global vcount
    #global l1


    res = str("t"+str(vcount))
    vcount+=1
    # print('l1',l1)
    arg2=l1.pop()
    arg1=l1.pop()
    l1.append(res)
    op=p[2]
    q.append(op)
    q.append(arg1[0])
    q.append(arg2[0])
    q.append(res)
    # print('q inside expression_binop',q)
    quad.append(q)
    #print(quad)


def p_statement_relational(p):
    '''expression : expression '>' expression
                 | expression '<' expression'''
    global l1
    l1.append(p[1][0])
    l1.append(p[3][0])
    # print(l1)
    # print("p[1]=",p[1])
    if p[2] == '>':
        val = (p[1][0] > p[3][0])
        newnode = Node('>', [p[1][1], p[3][1]])
    elif p[2] == '<':
        val = (p[1][0] < p[3][0])
        newnode = Node('<', [p[1][1], p[3][1]])
    p[0] = (val, newnode)

    q=[]        
    global quad
    global vcount
    #global l1

    res = str("t"+str(vcount))
    vcount+=1
    # print('l1',l1)
    arg2=l1.pop()
    arg1=l1.pop()
    l1.append(res)
    op=p[2]
    q.append(op)
    q.append(arg1)
    q.append(arg2)
    q.append(res)
    # print('q inside statement_relational',q)
    quad.append(q)
    #print(quad)


def p_relop(p):
    '''expression : expression REL_EQ expression
              | expression REL_NEQ expression
                      | expression REL_GTEQ expression
              | expression REL_LTEQ expression'''
    global l1
    l1.append(p[1][0])
    l1.append(p[3][0])
    # print(l1)

    if p[2] == "==" :
        p[0] = ((p[1][0] == p[3][0]), Node("==", [p[1][1], p[3][1]]))
    elif p[2] == "!=" :
        p[0] = ((p[1][0] != p[3][0]), Node("!=", [p[1][1], p[3][1]]))
    elif p[2] == "<=" : 
        p[0] = ((p[1][0] <= p[3][0]), Node("<=", [p[1][1], p[3][1]]))
    elif p[2][0] == ">=" :
        p[0] = ((p[1][0] >= p[3][0]), Node(">=", [p[1][1], p[3][1]]))



    q=[]
    global quad
    global vcount
    #global l1

    res = str("t"+str(vcount))
    vcount+=1
    # print('l1',l1)
    arg2=l1.pop()
    arg1=l1.pop()
    l1.append(res)
    op=p[2]
    q.append(op)
    q.append(arg1)
    q.append(arg2)
    q.append(res)
    # print('q inside relop',q)
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
    # print(l1)
    print(type(p.lexer.lineno))
    token = None
    try:
        for s in symbol_table.keys():
            flag = 0
            for i in symbol_table[s].keys():
                        # print(len(i.split('_')[0]), len(p[1]))
                if(i.split('_')[0]==p[1]):
                    print(symbol_table[s][i])
                    token = symbol_table[s][i].copy()
                    token[4] = "scope" + "_" + str(scope_level)
                    token[2] = p.lexer.lineno - 1-comment_count
                    print(token)
                        # print(key_p)
                    flag = 1
                    break
            if(flag):
                break
    except:
        token = None
        pass

    print(token)
    if scope_level == 0:
        scope = 'global'
    else:
        scope = 'scope'+str(scope_level)
    if(scope_level not in symbol_table.keys()):
            symbol_table[scope_level] = dict()
    if(token!=None):
        left_child = Node(p[1])
        key = p[1]+"_"+str(p.lexer.lineno-1-comment_count)
        symbol_table[scope_level][key] = token 
    # print("In p_operation_equals", p.slice)
    
        if p[2] == '+=':
            names[p[1]] = names[p[1]] + p[3][0]
            # symbol_table[scope_level][string][3] = 
            symbol_table[scope_level][key][5] = names[p[1]]
            p[0] = (None, Node("+=", [left_child, p[3][1]]))
        elif p[2] == '-=':
            names[p[1]] = names[p[1]] - p[3][0]
            symbol_table[scope_level][key][5] = names[p[1]]
            p[0] = (None, Node("-=", [left_child, p[3][1]]))
        elif p[2] == '/=':
            names[p[1]] = names[p[1]] / p[3][0]
            symbol_table[scope_level][key][5] = names[p[1]]
            p[0] = (None, Node("/=", [left_child, p[3][1]]))
        elif p[2] == '*=':
            names[p[1]] = names[p[1]] * p[3][0]
            symbol_table[scope_level][key][5] = names[p[1]]
            p[0] = (None, Node("*=", [left_child, p[3][1]]))
    else:
        print("Variable not defined in the block")
    q=[]
    global quad
    global vcount
    #global l1

    res = str("t"+str(vcount))
    vcount+=1
    # print('l1',l1)
    arg2=l1.pop()
    arg1=l1.pop()
    l1.append(res)
    op=p[2]
    q.append(op)
    q.append(arg1)
    q.append(arg2[0])
    q.append(res)
    # print('q inside operational_equals',q)
    quad.append(q)
    q=[]
    q.append("=")
    q.append(res)
    q.append(None)
    q.append(p[1])
    quad.append(q)
    #print(quad)

def p_expression_not(p):
    '''expression : '!' expression'''
    p[0] = p[2]
    p[0][0] = not (p[2][0])

def p_expression_uminus(p):
    '''expression : '-' expression %prec UMINUS'''
    global l1
    l1.appned(p[2][0])
    # print(l1)

    p[0][0] = -p[2][0]


def p_expression_group(p):
    '''expression : '(' expression ')' '''
    global l1
    l1.append(p[2][0])
    # print(l1)

    p[0] = p[2]


def p_expression_number(p):
    '''expression : FLOATNUMBER
                  | NUMBER'''
#    global l1
#    l1.append(p[1])
#    print(l1)

    p[0] = (p[1], Node(p[1]))


def p_expression_name(p):
    '''expression : NAME'''
#    global l1
#    l1.append(p[1])
#    print(l1)
    # print("In expression_name")
    try:
        p[0] = (names[p[1]], Node(p[1]))
    except LookupError:
        print("Undefined name '%s'" % p[1])
        p[0] = (0, Node(p[1]+"_undefined"))
    # print("Exiting with", p[0])

def p_error(p):
    if p:
        print("Syntax error at",(p.lexer.lineno-1))
    else:
        print("Syntax error at EOF")
    sys.exit() 

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
print("\nSYMBOL TABLE")
print(symbol_table)
print("\nAST")
root.indent_tree()
print("\n")
print_quad()
