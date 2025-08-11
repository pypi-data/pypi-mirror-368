Hi! LetrBinr is programming language. 

rules of the language LetrBinr:
    there are 2 data types in this language - ltr (string or symbol) and bin (number).
    you can`t write capital letters excluding words True and False.

    there are seven math operators:  +, -, %, ^ (in Python: **), /, *, //
    and an assign operator: =

    there are six logic operators: & (and), || (or), bg (>), ls (<), cmpeq (==), !cmpeq (!=).
    and two boolean variables - True and False.
    you can`t use logic operators on not variables. 
    for example, you can`t write: a !cmpeq bin 01010 ; 
    or: bin 01001 cmpeq bin 0101 ;
    you can only compare the variables: a cmpeq b ;, b bg c ;, kwa !cmpeq meow ;

    initializing variable - {variable name} eq {data type} {binary number} ;
    for example: a eq bin 0101 ;

    creating a function - its {function name} lb {arguments} rb ;
    for example: its frog lb kwa rb ;

    calling a function: do {function name} lb {arguments} rb ;
    for example: do frog lb kwa rb ;
    before calling a function, you should initialize the arguments as variables.
    for example: kwa eq ltr 01 ;
                do frog lb kwa rb ;

    to start for loop, write: for {letter or word} bin {decimal number} ;
    for example: for i bin 0101 ;

    to start infinity while loop, write: for inf ;

    to create if statement, write: true lb {condition} rb ;
    for example: true lb a !cmpeq b & b cmpeq c rb ;

    you can also take the symbols from the string. 
    For example:
        a eq bin 01010 ; (a = 10)
        b eq a lb 0 rb ;
        say b ; (writes 1 - symbol with index 0 from a)

    to create an input, write: talk lb (something for input) rb ;
    for example: talk lb bin 01010 bin 01010 ltr 011 bin 011 ltr 01110 rb ;

    to create print, write: say (something to print) ;
    for example: say ltr 00000111 ltr 00000100 ltr 00001011 ltr 00001011 ltr 00001110 spc ltr 00010110 ltr 00001110 ltr 00010001 ltr 00001011 ltr 00000011 ; 
    this line is saying "hello world"

    to convert the variable to another data type:
        if the variable is string:
            write "bin var {variable name}"
        if the variable is number:
            write "ltr var {variable name}"
        for example: 
            bin var a
            ltr var a
        note that when you are initializing the variable, the interpreter saves variable as string (ltr)

    to add space, write "spc", to add enter ("\n"), write "ntr", to add tab, write "tab".

    in the end of every line write ";".

    after if statement, for loop or while loop in the start of new line write "tab". 
    this command will add 4 spaces (required indentation) to the line.     

    to initialize the variable with value = "" (empty string):
        write "{variable name} eq ltr ;"
            for example:
                a eq ltr ; 
        in LetrBinRAND you need to write:
            {variable name} {word for eq} {word for ltr} 11010 {word for ;}
            for example:
                a + / 11010 &

rules of the language LetrBinRAND:
    the rules are the same as in LetrBinr but the keywords and operators are random.
    and you can`t initialize functions and variables with word names, only with one letter names 
    you have the function lexer in class LetrBinRAND. call this function and print the result.
    the result is the key (dict with keywords) for your code.
    example of the key:
    {'True': 'int', "//": "//", 'do': 'True', '!cmpeq': '==', '&': ';', 'ls': ')', '/': 'str', 'bin': '(', ';': '%', 'spc': 'input', 
    '||': 'print', 'var': 'var', 'False': '!=', 'eq': ' ', 'its': '    ', 'bg': 'for', 'ntr': '<', 'tab': 'if', '+': '=', 
    '-': '-', '*': 'or', 'true': "float('inf')", 'rb': 'def', 'for': 'False', 'say': '>', 'lb': '+', 'cmpeq': 'and', 
    'ltr': '\n', 'inf': 'call', 'end': '**', '^': 'break', '%': '/', 'talk': '*', 'a': 'a', 'b': 'b', 'c': 'c', 'd': 'd', 
    'e': 'e', 'f': 'f', 'g': 'g', 'h': 'h', 'i': 'i', 'j': 'j', 'k': 'k', 'l': 'l', 'm': 'm', 'n': 'n', 'o': 'o', 'p': 'p', 
    'q': 'q', 'r': 'r', 's': 's', 't': 't', 'u': 'u', 'v': 'v', 'w': 'w', 'x': 'x', 'y': 'y', 'z': 'z'}
    after receiving the key, erase the calling of function lexer and enter:
        {name of the class}.python = {key}
        for example: 
            l = LetrBinRAND()
            l.python = {'True': 'int', "//": "//", 'do': 'True', '!cmpeq': '==', '&': ';', 'ls': ')', '/': 'str', 'bin': '(', ';': '%', 'spc': 'input', '||': 'print', 'var': 'var', 'False': '!=', 'eq': ' ', 'its': '    ', 'bg': 'for', 'ntr': '<', 'tab': 'if', '+': '=', '-': '-', '*': 'or', 'true': "float('inf')", 'rb': 'def', 'for': 'False', 'say': '>', 'lb': '+', 'cmpeq': 'and', 
            'ltr': '\n', 'inf': 'call', 'end': '**', '^': 'break', '%': '/', 'talk': '*', 'a': 'a', 'b': 'b', 'c': 'c', 'd': 'd', 
            'e': 'e', 'f': 'f', 'g': 'g', 'h': 'h', 'i': 'i', 'j': 'j', 'k': 'k', 'l': 'l', 'm': 'm', 'n': 'n', 'o': 'o', 'p': 'p', 
            'q': 'q', 'r': 'r', 's': 's', 't': 't', 'u': 'u', 'v': 'v', 'w': 'w', 'x': 'x', 'y': 'y', 'z': 'z'}
        the rules are the same but the words and operators are different - take them from the key (l.python)

writing code:
    to start writing the code, call the function "code".

    line numbering starts from 1.

    if you made a mistake and you want to fix the line, write "fix {line number} {new code}".
    for example: fix 1 a eq bin 0101 ;
    
    if you want to run the code, enter "run code".

    if you want to end the coding, enter "end coding".

    if you want to watch the code in Python in the interpreter, enter "interpreter".

how to start LetrBinr:
    from letrbinr import LetrBinr
    
    lb = LetrBinr()
    if your IDE supports ANSI colors:
        lb.ANSI_color_code()
    else:
        lb.blackwhite_code()

how to start LetrBinRAND:
    from letrbinr import LetrBinRAND

    l = LetrBinRAND()
    l.lexer() # after calling, save the dict in l.python and erase this line
    l.python = {your key(dict from l.lexer)}
    if your IDE supports ANSI colors:
        l.ANSI_color_code()
    else:
        l.blackwhite_code()

Thank you so much for your interest in letrbinr!