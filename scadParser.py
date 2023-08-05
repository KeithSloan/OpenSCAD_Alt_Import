def parseFile(scadFile):

    lexer = lex.lex(debug=False)
    lexer.filename = scadFile
    parser = yacc.yacc(debug=False)

    from pathlib import Path
    with Path(scadFile).open() as f:
        for i in  parser.parse(f.read(), lexer=lexer):
            print(f"Type : {i.getType()](i)}

