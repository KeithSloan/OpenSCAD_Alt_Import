import ply.lex as lex
import ply.yacc as yacc

from SCADparser.scad_ast import *
from SCADparser.scad_tokens import *
from SCADparser.scad_parser import *

def parseScadFile(scadFile):

    print(f"parseSCADFile {scadFile}")

    lexer = lex.lex(debug=False)
    lexer.filename = scadFile
    parser = yacc.yacc(debug=False)

    from pathlib import Path
    with Path(scadFile).open() as f:
        for i in  parser.parse(f.read(), lexer=lexer):
            print(f"Type : {i.getType()}")

