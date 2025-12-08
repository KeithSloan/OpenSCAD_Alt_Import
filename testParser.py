import ply.lex as lex
import ply.yacc as yacc
import tokrules  # your fixed lexer

# ----------------------------
# Build the lexer
# ----------------------------
lexer = lex.lex(module=tokrules, debug=True)

# ----------------------------
# Minimal parser rules
# ----------------------------

# Define a very basic block_list and multmatrix_action
# to match the snippet you gave

# We use a Python list to store the AST
def p_block_list_statement(p):
    'block_list : statement'
    p[0] = [p[1]]

def p_block_list_multiple(p):
    'block_list : block_list statement'
    p[0] = p[1] + [p[2]]

def p_statement_multmatrix(p):
    'statement : multmatrix_action'
    p[0] = p[1]

def p_statement_sphere(p):
    'statement : sphere_action'
    p[0] = p[1]

def p_multmatrix_action(p):
    'multmatrix_action : multmatrix LPAREN matrix RPAREN OBRACE block_list EBRACE'
    p[0] = ('multmatrix', p[3], p[6])

# Minimal sphere rule (dummy)
def p_sphere_action(p):
    'sphere_action : sphere LPAREN RPAREN SEMICOL'
    p[0] = ('sphere',)

# Minimal matrix rule
def p_matrix(p):
    'matrix : OSQUARE vector COMMA vector COMMA vector COMMA vector ESQUARE'
    p[0] = [p[2], p[4], p[6], p[8]]

# Minimal vector rule
def p_vector(p):
    'vector : OSQUARE NUMBER COMMA NUMBER COMMA NUMBER COMMA NUMBER ESQUARE'
    p[0] = [p[2], p[4], p[6], p[8]]

# Error rule
def p_error(p):
    if p:
        print("Syntax error at", p.value, "type", p.type)
    else:
        print("Syntax error at EOF")

# ------------------

