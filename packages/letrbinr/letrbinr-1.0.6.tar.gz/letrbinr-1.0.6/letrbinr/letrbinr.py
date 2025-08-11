import random

class LetrBinr():
    def __init__(self):
        self.letters = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", 
                    "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", " "]
        self.math_list = ["+", "-", "^", "%", "/", "*", "//"]
        self.logic_list = ["&", ">", "||", "cmpeq", "<", "!cmpeq"]
        self.python = {}
        self.place = {}
        self.variables = {}
        self.functions = {}
        self.exec = {}
    def unbin(self, binary):
        if type(binary) != list:
            binary = list(binary)
        binary.reverse()
        number = 0
        for i in range(len(binary)):
            try:
                number += int(binary[i])*2**i
            except ValueError:
                break
        return number
    def lexer(self):
        python = {"+": "+",
                "-": "-",
                "/": "/",
                "*": "*",
                "^": "^",
                "%": "%",
                "//": "//",
                "0": "0",
                "1": "1",
                "2": "2",
                "3": "3",
                "4": "4",
                "5": "5",
                "6": "6",
                "7": "7",
                "8": "8",
                "9": "9",
                "lb": "(",
                "rb": ")",
                "!cmpeq": "!=",
                "cmpeq": "==",
                "bg": ">",
                "ls": "<",
                "eq": "=",
                "end": "break",
                "True": "True",
                "False": "False",
                "&": "and",
                "||": "or",
                ":": ":",
                "inf": "float('inf')",
                "spc": " ",
                "say": "print",
                ";": ";",
                "ntr": "\n",
                "tab": "\t",
                "for": "for",
                "'": "'"}
        for i in range(len(self.letters)):
            python.update({self.letters[i]: self.letters[i]})
        return python
    def parser(self, line):
        self.python = self.lexer()
        line = line.split()
        correct = []
        name = 0
        var = 0
        value = []
        if_st = False
        say = False
        math = False
        fl = False
        talking = False
        math_var = False
        range_char = 0
        for i in range(len(line) - 1):
            if line[i] == "bin" and line[i + 1] != "lb" and line[i + 1] != "var" and "eq" not in line and fl == False and say == False and talking == False:
                correct.append(str(self.unbin(line[i + 1])))
            if line[i] == "ltr" and line[i + 1] != "lb" and line[i + 1] != "var" and "eq" not in line and fl == False and say == False and talking == False:
                correct.append(self.letters[self.unbin(line[i + 1])])
            if ((line[i + 1] in self.math_list and line[i] in self.variables) or math == True) and math_var == False:
                math = True
                if line[i] != ";":
                    if line[i] in self.variables:
                        correct.append(f"int({line[i]})")
                    elif line[i] == "lb":
                        correct.append("(")
                    elif line[i] == "rb":
                        correct.append(")")
                    else:
                        correct.append(self.python[line[i]])
            if line[i] == "true" and line[i + 1] == "lb" or if_st == True and math == False and say == False:
                if_st = True
                if line[i + 1] == "lb" and line[i] == "true":
                    correct.append("if (")
                    i += 2 
                    while line[i] != "rb":
                        for key, value3 in self.variables.items():
                            if key == line[i]:
                                correct.append(f" {line[i]} ")
                        if line[i] not in self.variables:
                            for key, value1 in self.python.items():
                                if key == line[i]:
                                    correct.append(f" {self.python[line[i]]} ")
                        i += 1
                    if line[i] == "rb":
                        correct.append("):")
            if (line[i + 1][0] == "0" or line[i + 1][0] == "1") and line[i] == "lb" and line[i - 1] != "eq":
                if line[i - 1] == "ltr":
                    correct.append(self.letters[self.unbin(line[i + 1])])
                if line[i - 1] == "bin":
                    correct.append(str(self.unbin(line[i + 1])))
            if line[i] == "for" or fl == True:
                fl = True
                range_char = line[i]
                i += 1
                if len(line) > 2:
                    if line[i] == "bin":
                        i += 1
                        correct.append(f"for {range_char} in range({self.unbin(line[i])}):")
                if line[i] == "inf":
                    correct.append(f"while True:")
            if line[i] == "say" and line[i + 1] != "var" or say == True:
                say = True
                if line[i] == "say":
                    correct.append("print(f'")
                    if line[i + 1] == "lb":
                        i += 1
                    while line[i] != ";":
                        if line[i] == "bin":
                            correct.append(str(self.unbin(line[i + 1])))
                        if line[i] == "ltr":
                            correct.append(self.letters[(self.unbin(line[i + 1]))])
                        if line[i] in self.variables:
                            lb = "{"
                            rb = "}"
                            correct.append(f"{lb}{line[i]}{rb}")
                        if line[i] == "spc":
                            correct.append(" ")
                        if line[i] == "ntr":
                            correct.append("\n")
                        if line[i] == "tab":
                            correct.append(" "*4)
                        i += 1
                    if line[i] == ";":
                        correct.append("')")
            if line[i] == "talk" or talking == True:
                talking = True
                correct.append("input('")
                if line[i + 1] == "lb":
                    i += 2
                    while line[i] != "rb":
                        if line[i] == "bin" and line[i + 1] != "lb":
                            correct.append((self.unbin(line[i + 1])))
                            i += 1
                        elif line[i] == "ltr" and line[i + 1] != "lb":
                            correct.append(self.letters[self.unbin(line[i + 1])])
                            i += 1
                        elif line[i] in self.variables:
                            correct.append(self.variables[line[i]])
                            i += 1
                        elif line[i] == "spc":
                            correct.append(" ")
                            i += 1
                        elif line[i] == "tab":
                            correct.append("\t")
                            i += 1
                        elif line[i] == "ntr":
                            correct.append("\n")
                            i += 1
                        else:
                            i += 1
                            continue
                    if line[i] == "rb":
                        correct.append("')")
                        break
            if line[i][0] in self.letters and fl == False and talking == False and say == False and if_st == False:
                name = line[i]
                if line[i + 1] == "eq":
                    correct.append(f"{name} = ")
                    var = i + 2
                    values = []
                    for where in range(var, len(line) - 1):
                        if line[where] != ";":
                            if line[where] == "bin" and (line[where + 1][0] == "0" or line[where + 1][0] == "1"):
                                correct.append(str(self.unbin(line[where + 1])))
                                value.append(str(self.unbin(line[where + 1])))
                            if line[where] == "ltr" and (line[where + 1][0] == "0" or line[where + 1][0] == "1"):
                                correct.append("'")
                                correct.append(self.letters[self.unbin(line[where + 1])])
                                correct.append("'")
                            if line[where] == "True" or line[where] == "False":
                                correct.append(line[where])
                                value.append(line[where])
                            if line[where] == "ltr" and (line[where + 1][0] != "0" and line[where + 1][0] != "1"):
                                correct.append("''")
                                value.append('')
                                break
                            if line[where] == "talk":
                                talking == True
                                break
                            if line[where] in self.variables:
                                if line[where + 1] == "lb":
                                    correct.append(f"str({line[where]})")
                                    correct.append("[")
                                    value.append(line[where])
                                    value.append("[")
                                    while line[where] != "rb":
                                        where += 1
                                        if line[where + 1][0] == "0" or line[where + 1][0] == "1":
                                            correct.append(str(self.unbin(line[where + 1])))
                                            value.append(str(self.unbin(line[where + 1])))
                                        elif line[where + 1] in self.variables:
                                            correct.append(line[where + 1])
                                            value.append(line[where + 1])
                                        else:
                                            continue
                                    correct.append("]")
                                    value.append("]")
                                    break
                                elif type(self.variables[line[where]]) != str:
                                    correct.append(f"int({line[where]})")
                                    value.append(str(self.variables[line[where]]))
                                    math_var = True
                                elif type(self.variables[line[where]]) == str:
                                    correct.append(f"str({line[where]})")
                                    value.append(str(self.variables[line[where]]))
                                    math_var = True
                                else:
                                    correct.append(f"{self.variables[line[where]]}")
                                    value.append(self.variables[line[where]])
                            if line[where] in self.math_list:
                                correct.append(line[where])
                                value.append(" ")
                                value.append(line[where])
                                value.append(" ")
                                math_var = True
                        if len(values) > 0:
                            value = values
                            value.append(")")
                    self.variables.update({name: "".join(value)})
            if line[i] == "its":
                func_name = 0
                args = []
                i += 1
                correct.append(f"def {line[i]}")
                func_name = line[i]
                if line[i + 1] == "lb":
                    correct.append("(")
                    i += 2
                    while line[i] != "rb":
                        correct.append(line[i])
                        args.append(line[i])
                        if line[i + 1] != "rb":
                            correct.append(", ")
                            args.append(", ")
                        i += 1 
                if line[i] == "rb":
                    correct.append("):")
                self.functions.update({func_name: args})
            if line[i] == "do":
                func_name = line[i + 1]
                i += 1
                if line[i + 1] == "lb":
                    correct.append(func_name)
                    correct.append("(")
                    if line[i] == "'":
                        correct.append("'")
                    for arg in range(len(self.functions[func_name])):
                        if self.functions[func_name][arg] != ", ":
                            correct.append(self.functions[func_name][arg])
                        else:
                            correct.append(", ")
                    correct.append(")")
            if line[i] == "say" and line[i + 1] == "var":
                correct.append("print(self.variables)")
            for key, value2 in self.variables.items():
                if line[i - 1] == "bin" and line[i] == "var" and line[i + 1] == key:
                    self.variables.update({key: eval(value2)})
                    correct.append(f"{key} = int({key})")
                    break
                if line[i - 1] == "ltr" and line[i] == "var" and line[i + 1] == key:
                    value2 = str(value2)
                    self.variables.update({key: value2})
                    correct.append(f"{key} = str({key})")
            if line[i] == "end":
                correct.append("break")
            if line[i] == "spc":
                correct.append(" ")
            if line[i] == "ntr":
                correct.append("\n")
            if line[i] == "tab":
                correct.append(" "*4)
        correct.append("\n")
        correct = "".join(correct)
        return correct
    def ANSI_color_code(self):
        codespace = []
        pycode = []
        start = "a"
        fixpy = ""
        GREEN = "\033[32m"
        YELLOW = "\033[33m"
        BLUE = "\033[34m"
        PURPLE = "\033[35m"
        RESET = "\033[0m"
        lines = []
        while True:
            try:
                line = input(f'{"".join(codespace)}\n')
                start = line
                line = line.split()
                if line == "":
                    codespace.append("\n")
                    correct = ""
                if len(line) > 1:
                    if line[0] == "fix":
                        start = ""
                        codespace[int(line[1]) - 1] = ""
                        pycode[int(line[1]) - 1] = ""
                        for j in range(2, len(line)):
                            if (line[j][0] != "0" and line[j][0] != "1" and (line[j] in self.letters or line[j] == "lb" or line[j] == "rb")) or line[j] == "var" or line[j] in self.variables: 
                                fixpy += line[j]
                                fixpy += " "
                                line[j] = f"{GREEN}{line[j]}{RESET}"
                            elif line[j][0] != "0" and line[j][0] != "1" and line[j] in self.functions or line[j] in self.math_list or line[j] == "bin" or line[j] == "ltr" or line[j] == "say" or line[j] == "talk":
                                fixpy += line[j]
                                fixpy += " "
                                line[j] = f"{YELLOW}{line[j]}{RESET}"
                            elif line[j][0] != "0" and line[j][0] != "1" and (line[j] in self.logic_list or line[j] == "eq"):
                                fixpy += line[j]
                                fixpy += " "
                                line[j] = f"{BLUE}{line[j]}{RESET}"
                            elif line[j][0] == "0" or line[j][0] == "1" or line[j] == "true" or line[j] == "its" or line[j] == "do" or line[j] == "for":
                                fixpy += line[j]
                                fixpy += " "
                                line[j] = f"{PURPLE}{line[j]}{RESET}"
                            else:
                                fixpy += line[j]
                                fixpy += " "
                                line[j] = line[j]
                        for k in range(2, len(line)):
                            start += line[k]
                            start += " "
                        codespace[int(line[1]) - 1] = f"{start}\n"
                        pycode[int(line[1]) - 1] = f"{self.parser(fixpy)}\n"
                        fixpy = ""
                    if line[0] == "end" and line[1] == "coding":
                        print("your code:\n", "".join(lines))
                        break
                    if line[0] == "interpreter" and line[1] == ";":
                        print("".join(pycode))
                    if line[0] == "run" and line[1] == "code":
                        try:
                            exec("".join(pycode))
                        except Exception as e:
                            print(f"ERROR!!! ERROR!!! ERROR!!! ERROR!!! ERROR!!!\n Python interpreter, class LetrBinr: {e}")
                            print("line:", pycode.index(correct) + 1)
                            print(codespace[pycode.index(correct)])
                    if (line[0] != "run" or line[1] != "code") and line[0] != "" and line[0] != "fix" and (line[0] != "end" or line[1] != "coding") and (line[0] != "interpreter" or line[1] != ";"):
                        line = start
                        correct = self.parser(line)
                        pycode.append(correct)
                        lines.append(f"{line}\n")
                        line = line.split()
                        for i in range(len(line)):
                            if (line[i][0] != "0" and line[i][0] != "1" and (line[i] in self.letters or line[i] == "lb" or line[i] == "rb")) or line[i] == "var" or line[i] in self.variables: 
                                line[i] = f"{GREEN}{line[i]}{RESET}"
                            elif line[i][0] != "0" and line[i][0] != "1" and line[i] in self.functions or line[i] in self.math_list or line[i] == "bin" or line[i] == "ltr" or line[i] == "say" or line[i] == "talk":
                                line[i] = f"{YELLOW}{line[i]}{RESET}"
                            elif line[i][0] != "0" and line[i][0] != "1" and (line[i] in self.logic_list or line[i] == "eq"):
                                line[i] = f"{BLUE}{line[i]}{RESET}"
                            elif line[i][0] == "0" or line[i][0] == "1" or line[i] == "true" or line[i] == "its" or line[i] == "do" or line[i] == "for":
                                line[i] = f"{PURPLE}{line[i]}{RESET}"
                            else:
                                line[i] = line[i]
                        start = ""
                        for row in line:
                            start += row
                            start += " "
                        codespace.append(f"{start}\n")
            except Exception as e:
                continue
    def blackwhite_code(self):
        codespace = []
        pycode = []
        start = "a"
        fixpy = ""
        while True:
            try:
                line = input(f'{"".join(codespace)}\n')
                start = line
                line = line.split()
                if line == "":
                    codespace.append("\n")
                    correct = ""
                if len(line) > 1:
                    if line[0] == "fix":
                        codespace[int(line[1]) - 1] = ""
                        pycode[int(line[1]) - 1] = ""
                        for j in range(2, len(line)):
                            codespace[int(line[1]) - 1] += f" {line[j]}"
                            fixpy += f" {line[j]}"
                        pycode[int(line[1]) - 1] = f"{self.parser(fixpy)}"
                        fixpy = ""
                    if line[0] == "interpreter" and line[1] == ";":
                        print("".join(pycode))
                    if line[0] == "end" and line[1] == "coding":
                        print("your code:", codespace)
                        break
                    if line[0] == "run" and line[1] == "code":
                        try:
                            exec("".join(pycode))
                        except Exception as e:
                            print(f"ERROR! {e}")
                    if (line[0] != "run" or line[1] != "code") and line[0] != "" and line[0] != "fix" and (line[0] != "end" or line[1] != "coding") and (line[0] != "interpreter" or line[1] != ";"):
                        line = start
                        correct = self.parser(line)
                        pycode.append(correct)
                        codespace.append(f"{line}\n")
            except Exception as e:
                continue
class LetrBinRAND():
    def __init__(self):
        self.letters = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", 
                    "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", '']
        self.math_list = ["+", "-", "^", "%", "/", "*", "//"]
        self.logic_list = ["&", ">", "||", "cmpeq", "<", "!cmpeq"]
        self.what = ["for", "&", "||", "lb", "ls", "rb", "ltr", "bg", "bin", "its", "do", "!cmpeq", "cmpeq", 
                     "end", "+", "-", "^", "%", "spc", "*", "/", "tab", "ntr", ";", "eq", "true", "True", "False",
                     "say", "inf", "talk", "var", "//"]
        self.why = ["for", "and", "or", "(", "<", ")", "str", ">", "int", "def", "call", "!=", "==",
                    "break", "+", "-", "**", "%", " ", "*", "/", "    ", "\n", ";", "=", "if", "True", "False", 
                    "print", "float('inf')", "input", "var", "//"]
        self.python = {}
        self.place = {}
        self.variables = {}
        self.functions = {}
        self.exec = {}
    def unbin(self, binary):
        if type(binary) != list:
            binary = list(binary)
        binary.reverse()
        number = 0
        for i in range(len(binary)):
            try:
                number += int(binary[i])*2**i
            except ValueError:
                break
        return number
    def lexer(self):
        random.shuffle(self.what)
        random.shuffle(self.why)
        pairs = list(zip(self.what, self.why))
        random.shuffle(pairs)
        self.python = dict(pairs)
        for i in range(len(self.letters)):
            self.python.update({self.letters[i]: self.letters[i]})
        return self.python
    def parser(self, line):
        line = line.split()
        correct = []
        name = 0
        var = 0
        value = []
        if_st = False
        say = False
        math = False
        fl = False
        talking = False
        math_var = False
        range_char = 0 
        for i in range(len(line) - 1):
            if line[i + 1][0] != "0" and line[i + 1][0] != "1" and line[i][0] != "0" and line[i][0] != "1" and self.python[line[i]] == "int" and self.python[line[i + 1]] != "(" and fl == False and say == False and talking == False:
                for key, value in self.python.items():
                    for ln in range(len(line)):
                        if self.python[line[ln]] != "=" and ln == len(line) - 1:
                            correct.append(str(self.unbin(self.python[line[i + 1]])))
            if line[i][0] != "0" and line[i][0] != "1" and line[i + 1][0] != "0" and line[i + 1][0] != "1" and self.python[line[i]] == "str" and self.python[line[i + 1]] != "(" and fl == False and say == False and talking == False:
                for key, value in self.python.items():
                    for ln in range(len(line)):
                        if self.python[line[ln]] != "=" and ln == len(line) - 1:
                            correct.append(str(self.unbin(self.python[line[i + 1]])))
            if line[i + 1][0] != "0" and line[i + 1][0] != "1" and line[i][0] != "0" and line[i][0] != "1" and ((self.python[line[i + 1]] in self.math_list and self.python[line[i]] in self.variables) or math == True) and math_var == False:
                math = True
                if self.python[line[i]] != ";":
                    if line[i] in self.variables:
                        correct.append(f"int({line[i]})")
                    else:
                        correct.append(self.python[line[i]])
            if line[i][0] != "0" and line[i][0] != "1" and line[i + 1][0] != "0" and line[i + 1][0] != "1" and self.python[line[i]] == "if" and self.python[line[i + 1]] == "(" or if_st == True and math == False and say == False:
                if_st = True
                if line[i][0] != "0" and line[i][0] != "1" and self.python[line[i + 1]] == "(" and self.python[line[i]] == "if":
                    correct.append("if (")
                    i += 2
                    while self.python[line[i]] != ")":
                        if line[i] in self.variables:
                            correct.append(f" {line[i]} ")
                        if line[i] not in self.variables:
                            for key, value1 in self.python.items():
                                if key == line[i]:
                                    correct.append(f" {self.python[line[i]]} ")
                        i += 1
                    if self.python[line[i]] == ")":
                        correct.append("):")
            if (line[i + 1][0] == "0" or line[i + 1][0] == "1") and self.python[line[i]] == "(" and self.python[line[i - 1]] != "=":
                if self.python[line[i - 1]] == "str":
                    correct.append(self.letters[self.unbin(line[i + 1])])
                if self.python[line[i - 1]] == "int":
                    correct.append(str(self.unbin(line[i + 1])))
            if line[i][0] != "0" and line[i][0] != "1" and self.python[line[i]] == "for" or fl == True:
                fl = True
                range_char = line[i]
                i += 1
                if len(line) > 2:
                    if line[i][0] != "0" and line[i][0] != "1" and self.python[line[i]] == "int":
                        i += 1
                        correct.append(f"for {range_char} in range({self.unbin(line[i])}):")
                if line[i][0] != "0" and line[i][0] != "1" and self.python[line[i]] == "float('inf')":
                    correct.append(f"while True:")
            if line[i][0] != "0" and line[i][0] != "1" and self.python[line[i]] == "print" and self.python[line[i + 1]] != "var" or say == True:
                say = True
                if self.python[line[i]] == "print":
                    correct.append("print(f'")
                    if self.python[line[i + 1]] == "(":
                        i += 1
                    while self.python[line[i]] != ";":
                        if self.python[line[i]] == "int":
                            correct.append(str(self.unbin(line[i + 1])))
                        if self.python[line[i]] == "str":
                            correct.append(self.letters[(self.unbin(line[i + 1]))])
                        if self.python[line[i]] in self.variables:
                            lb = "{"
                            rb = "}"
                            correct.append(f"{lb}{self.python[line[i]]}{rb}")
                        if self.python[line[i]] == " ":
                            correct.append(" ")
                        if self.python[line[i]] == "\n":
                            correct.append("\n")
                        if self.python[line[i]] == "    ":
                            correct.append(" "*4)
                        i += 1
                    if self.python[line[i]] == ";":
                        correct.append("')")
            if line[i][0] != "0" and line[i][0] != "1" and self.python[line[i]] == "input" or talking == True:
                talking = True
                if line[i][0] != "0" and line[i][0] != "1" and line[i + 1][0] != "0" and line[i + 1][0] != "1" and self.python[line[i + 1]] == "(":
                    correct.append("input('")
                    i += 2
                    if line[i][0] != "0" and line[i][0] != "1":
                        while True:
                            if line[i][0] != "0" and line[i][0] != "1" and self.python[line[i]] == ";":
                                correct.append("')")
                                break
                            elif line[i][0] != "0" and line[i][0] != "1" and self.python[line[i]] == "int":
                                correct.append(str(self.unbin(line[i + 1])))
                                i += 1
                            elif line[i][0] != "0" and line[i][0] != "1" and self.python[line[i]] == "str":
                                correct.append(self.letters[self.unbin(line[i + 1])])
                                i += 1
                            elif line[i][0] != "0" and line[i][0] != "1" and self.python[line[i]] == " ":
                                correct.append(" ")
                                i += 1
                            elif line[i][0] != "0" and line[i][0] != "1" and self.python[line[i]] == "    ":
                                correct.append("\t")
                                i += 1
                            elif line[i][0] != "0" and line[i][0] != "1" and self.python[line[i]] == "\n":
                                correct.append("\n")
                                i += 1
                            else:
                                i += 1
                                continue
            if line[i][0] != "0" and line[i][0] != "1" and self.python[line[i]][0] in self.letters and fl == False and talking == False and say == False and if_st == False:
                name = line[i]
                if line[i + 1][0] != "0" and line[i + 1][0] != "1" and self.python[line[i + 1]] == "=":
                    correct.append(f"{name} = ")
                    var = i + 2
                    values = []
                    for where in range(var, len(line) - 1):
                        if line[where][0] != "0" and line[where][0] != "1" and self.python[line[where]] != ";":
                            if self.python[line[where]] == "int" and (line[where + 1][0] == "0" or line[where + 1][0] == "1"):
                                correct.append(str(self.unbin(line[where + 1])))
                                value.append(str(self.unbin(line[where + 1])))
                            if self.python[line[where]] == "str" and (line[where + 1][0] == "0" or line[where + 1][0] == "1"):
                                correct.append("'")
                                correct.append(self.letters[self.unbin(line[where + 1])])
                                correct.append("'")
                            if self.python[line[where]] == "True" or self.python[line[where]] == "False":
                                correct.append(self.python[line[where]])
                                value.append(self.python[line[where]])
                            if self.python[line[where]] == "input":
                                talking == True
                                break
                            if line[where] in self.variables:
                                if self.python[line[where + 1]] == "(":
                                    correct.append(f"str({line[where]})")
                                    correct.append("[")
                                    value.append(line[where])
                                    value.append("[")
                                    while self.python[line[where]] != ")":
                                        where += 1
                                        if line[where + 1][0] == "0" or line[where + 1][0] == "1":
                                            correct.append(str(self.unbin(line[where + 1])))
                                            value.append(str(self.unbin(line[where + 1])))
                                        elif line[where + 1] in self.variables:
                                            correct.append(line[where + 1])
                                            value.append(line[where + 1])
                                        else:
                                            continue
                                    correct.append("]")
                                    value.append("]")
                                    break
                                elif self.variables[line[where][0]] not in self.letters:
                                    correct.append(f"int({line[where]})")
                                    value.append(self.variables[line[where]])
                                    math_var = True
                                else:
                                    correct.append(f"{line[where]}")
                                    value.append(self.variables[line[where]])
                            if self.python[line[where]] in self.math_list:
                                correct.append(self.python[line[where]])
                                value.append(self.python[line[where]])
                                math_var = True
                        if len(values) > 0:
                            value = values
                            value.append(")")
                    self.variables.update({name: "".join(value)})
            if line[i][0] != "0" and line[i][0] != "1" and self.python[line[i]] == "def":
                func_name = 0
                args = []
                i += 1
                correct.append(f"def {self.python[line[i]]}")
                func_name = self.python[line[i]]
                if self.python[line[i + 1]] == "(":
                    correct.append("(")
                    i += 2
                    while self.python[line[i]] != ")":
                        correct.append(line[i])
                        args.append(line[i])
                        if self.python[line[i + 1]] != ")":
                            correct.append(", ")
                            args.append(", ")
                        i += 1 
                if self.python[line[i]] == ")":
                    correct.append("):")
                self.functions.update({func_name: args})
            if line[i][0] != "0" and line[i][0] != "1" and self.python[line[i]] == "call":
                func_name = line[i + 1]
                i += 1
                if self.python[line[i + 1]] == "(":
                    correct.append(func_name)
                    correct.append("(")
                    for arg in range(len(self.functions[func_name])):
                        if self.functions[func_name][arg] != ",":
                            correct.append(self.variables[self.functions[func_name][arg]])
                        else:
                            correct.append(",")
                    correct.append(")")
            if line[i][0] != "0" and line[i][0] != "1" and self.python[line[i]] == "print" and self.python[line[i + 1]] == "var":
                correct.append("print(self.variables)")
            if line[i] in self.variables:
                if line[i - 1][0] != "0" and line[i - 1][0] != "1" and line[i][0] != "0" and line[i][0] != "1" and line[i + 1][0] != "0" and line[i + 1][0] != "1":
                    if self.python[line[i - 1]] == "int" and self.python[line[i]] == "var" and self.python[line[i + 1]] == key:
                        value2 = int(eval(value2))
                        self.variables.update({key: value2})
                    if self.python[line[i - 1]] == "str" and self.python[line[i]] == "var" and self.python[line[i + 1]] == key:
                        value2 = str(eval(value2))
                        self.variables.update({key: value2})
            if line[i][0] != "0" and line[i][0] != "1":
                if self.python[line[i]] == "break":
                    correct.append("break")
                if self.python[line[i]] == " ":
                    correct.append(" ")
                if self.python[line[i]] == "\n":
                    correct.append("\n")
                if self.python[line[i]] == "    ":
                    correct.append(" "*4)
        correct.append("\n")
        correct = "".join(correct)
        return correct
    def ANSI_color_code(self):
        
        codespace = []
        pycode = []
        start = "a"
        fixpy = "u"
        GREEN = "\033[32m"
        YELLOW = "\033[33m"
        BLUE = "\033[34m"
        PURPLE = "\033[35m"
        RESET = "\033[0m"
        while True:
            try:
                line = input(f'{"".join(codespace)}\n')
                start = line
                line = line.split()
                if line == "":
                    codespace.append("\n")
                    correct = ""
                if len(line) > 1:
                    if line[0] == "fix":
                        start = ""
                        fixpy = ""
                        codespace[int(line[1]) - 1] = ""
                        pycode[int(line[1]) - 1] = ""
                        for j in range(2, len(line)):
                            if (line[j][0] != "0" and line[j][0] != "1" and (line[j] in self.letters or self.python[line[j]] == "(" or self.python[line[j]] == ")" or self.python[line[j]] == "var" or line[j] in self.variables)): 
                                fixpy += line[j]
                                fixpy += " "
                                line[j] = f"{GREEN}{line[j]}{RESET}"
                            elif line[j][0] != "0" and line[j][0] != "1" and (line[j] in self.functions or self.python[line[j]] in self.math_list or self.python[line[j]] == "int" or self.python[line[j]] == "str" or self.python[line[j]] == "print" or self.python[line[j]] == "input"):
                                fixpy += line[j]
                                fixpy += " "
                                line[j] = f"{YELLOW}{line[j]}{RESET}"
                            elif line[j][0] != "0" and line[j][0] != "1" and (self.python[line[j]] in self.logic_list or self.python[line[j]] == "="):
                                fixpy += line[j]
                                fixpy += " "
                                line[j] = f"{BLUE}{line[j]}{RESET}"
                            elif line[j][0] == "0" or line[j][0] == "1" or self.python[line[j]] == "if" or self.python[line[j]] == "def" or self.python[line[j]] == "call" or self.python[line[j]] == "for":
                                fixpy += line[j]
                                fixpy += " "
                                line[j] = f"{PURPLE}{line[j]}{RESET}"
                            else:
                                fixpy += line[j]
                                fixpy += " "
                                line[j] = line[j]
                        for k in range(2, len(line)):
                            start += line[k]
                            start += " "
                        codespace[int(line[1]) - 1] = f"{start}\n"
                        pycode[int(line[1]) - 1] = f"{self.parser(fixpy)}\n"
                    if line[0] == "end" and line[1] == "coding":
                        print("your code:", codespace)
                        break
                    if line[0] == "interpreter":
                        print("".join(pycode))
                    if line[0] == "run" and line[1] == "code":
                        try:
                            exec("".join(pycode))
                        except Exception as e:
                            print(f"ERROR!!! ERROR!!! ERROR!!! ERROR!!! ERROR!!!\n Python interpreter, class LetrBinRAND: {e}")
                            print("line:", pycode.index(correct) + 1)
                            print(codespace[pycode.index(correct)])
                    if (line[0] != "run" or line[1] != "code") and line[0] != "" and line[0] != "fix" and (line[0] != "end" or line[1] != "coding") and line[0] != "interpreter":
                        line = start
                        correct = self.parser(line)
                        pycode.append(correct)
                        line = line.split()
                        for i in range(len(line)):
                            if line[i][0] != "0" and line[i][0] != "1" and (line[i] in self.letters or self.python[line[i]] == "(" or self.python[line[i]] == ")" or self.python[line[i]] == "var" or line[i] in self.variables): 
                                line[i] = f"{GREEN}{line[i]}{RESET}"
                            elif line[i][0] != "0" and line[i][0] != "1" and (line[i] in self.functions or self.python[line[i]] in self.math_list or self.python[line[i]] == "int" or self.python[line[i]] == "str" or self.python[line[i]] == "print" or self.python[line[i]] == "input"):
                                line[i] = f"{YELLOW}{line[i]}{RESET}"
                            elif line[i][0] != "0" and line[i][0] != "1" and (self.python[line[i]] in self.logic_list or self.python[line[i]] == "="):
                                line[i] = f"{BLUE}{line[i]}{RESET}"
                            elif line[i][0] == "0" or line[i][0] == "1" or self.python[line[i]] == "if" or self.python[line[i]] == "def" or self.python[line[i]] == "call" or self.python[line[i]] == "for":
                                line[i] = f"{PURPLE}{line[i]}{RESET}"
                            else:
                                line[i] = line[i]
                        start = ""
                        for row in line:
                            start += row
                            start += " "
                        codespace.append(f"{start}\n")
            except Exception as e:
                continue
    def blackwhite_code(self):
        codespace = []
        pycode = []
        start = "a"
        fixpy = ""
        while True:
            try:
                line = input(f'{"".join(codespace)}\n')
                start = line
                line = line.split()
                if line == "":
                    codespace.append("\n")
                    correct = ""
                if len(line) > 1:
                    if line[0] == "fix":
                        codespace[int(line[1]) - 1] = ""
                        pycode[int(line[1]) - 1] = ""
                        for j in range(2, len(line)):
                            codespace[int(line[1]) - 1] += f" {line[j]}"
                            fixpy += f" {line[j]}"
                        pycode[int(line[1]) - 1] = f"{self.parser(fixpy)}"
                        fixpy = ""
                    if line[0] == "end" and line[1] == "coding":
                        print("your code:", codespace)
                        break
                    if line[0] == "interpreter":
                        print("".join(pycode))
                    if line[0] == "run" and line[1] == "code":
                        try:
                            exec("".join(pycode))
                        except Exception as e:
                            print("ERROR!!! ERROR!!! ERROR!!! ERROR!!! ERROR!!!")
                            print("line:", pycode.index(correct) + 1)
                            print(codespace[pycode.index(correct)])
                    if (line[0] != "run" or line[1] != "code") and line[0] != "" and line[0] != "fix" and (line[0] != "end" or line[1] != "coding") and line[0] != "interpreter":
                        line = start
                        correct = self.parser(line)
                        pycode.append(correct)
                        codespace.append(f"{line}\n")
            except Exception as e:
                continue