import ply.lex as lex
import tokrules  # your lexer file

# Build the lexer
lexer = lex.lex(module=tokrules)

# Test input snippet
data = """
multmatrix([[1, 0, 0, 21.575],
            [0, 1, 0, 16.25],
            [0, 0, 1, 0],
            [0, 0, 0, 1]]) {
    sphere($fn = 20, $fa = 12, $fs = 2, r = 0.01);
}
"""

lexer.input(data)

# Tokenize and print
while True:
    tok = lexer.token()
    if not tok:
        break
    print(tok)

