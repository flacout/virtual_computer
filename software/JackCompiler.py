import sys
import os


######################################################################################
# SYNTAX ANALYSER
# tokenize jack files, and parse them
######################################################################################

class JackAnalyzer:
    def __init__(self):
        self.input = sys.argv[1]

    # operate a single file or entire folder
    def operateInput(self):
        if self.input.endswith('.jack'):
            # tokenize
            tokenizer = Tokenizer()
            file = open(self.input, 'r')
            tokens = tokenizer.tokenize(file)
            file.close()

            # parse
            parser = CompilationEngine(tokens, self.input)
            parser.compileClass()

        else:
            #ofile_name = self.input+ '/' + self.input.split('/')[-1] + '.asm'
            for file in os.listdir(self.input):
                if file.endswith('.jack'):
                    # tokenize
                    tokenizer = Tokenizer()
                    fileOpen = open(self.input+'/'+file, 'r')
                    tokens = tokenizer.tokenize(fileOpen)
                    fileOpen.close()
                    #self.outputTokens(tokens, file)

                    # parse
                    parser = CompilationEngine(tokens, self.input+'/'+file)
                    parser.compileClass()


    def outputTokens(self, tokens, file):
        ofile = open(self.input+'/'+file.split('.')[0]+ 'TT.xml', 'w')
        ofile.write('<tokens>\n')
        for t in tokens:
            ofile.write('<' + t[1] + '>')
            if t[0] == '<': ofile.write('&lt;')
            elif t[0] == '>': ofile.write('&gt;')
            elif t[0] == '"': ofile.write('&quot;')
            elif t[0] == '&': ofile.write('&amp;')
            else: ofile.write(t[0])
            ofile.write('</' + t[1] + '>\n')
        ofile.write('</tokens>')
        ofile.close()




#######################################################################################
# TOKENIZER
# split a file into atomic tokens 
# return a list of them with their type
#######################################################################################

class Tokenizer:
    def __init__(self):
        self.tokens = []
        self.symbols = {'{', '}', '(', ')', '[', ']', '.', ',', ';', '+',
                        '-', '*', '/', '&', '|', '<', '>', '=', '~' }
        self.keywords = {'class', 'constructor', 'function', 'method', 
                         'field', 'static', 'var', 'int', 'char', 'boolean', 
                         'void', 'true', 'false', 'null', 'this', 'let', 'do', 
                         'if','else', 'while', 'return'}

    def tokenize(self, ifile):
        multiComments = False
        for line in ifile:
            line = line.strip()
            # get rid of all comments
            if line.startswith('//') or line=='': 
                continue
            elif line.startswith('/*') :
                multiComments = True
                if line.endswith('*/'):
                    multiComments = False
                continue
            elif line.endswith('*/') :
                multiComments = False
                continue
            elif multiComments == True :
                continue

            line = self.removeComment(line)
            self.atomize(line)
        return self.tokens


    def atomize(self, line):
        word = ''
        string_flag = False

        for c in line:
            if string_flag == True and c!='"':
                word += c
            elif c == '"':
                if string_flag == True:
                    self.add(word)
                    string_flag = False
                    word = ''
                else:
                    string_flag = True
                    word +=c
            elif c in self.symbols:
                self.add(word)
                self.tokens.append( (c, 'symbol') )
                word = ''
            elif c==' ':
                self.add(word)
                word = ''
            else:
                word += c
        self.add(word)


    def add(self, word):
        if word in self.keywords:
            self.tokens.append( (word, 'keyword') )
        elif word in self.symbols:
            self.tokens.append((word, 'symbol'))
        elif word.startswith('"'):
            self.tokens.append( (word.strip('"'), 'stringConstant') )
        elif word.isdigit():
            self.tokens.append( (word, 'integerConstant') )
        elif word == '': return
        else :
            self.tokens.append( (word, 'identifier') )


    def removeComment(self, line):
        words = line.split('//')
        return words[0].strip()


######################################################################################
# SYMBOL TABLE
# handle variables of the program
######################################################################################

class SymbolTable:
    def __init__(self):
        self.classTable = {}
        self.subroutineTable = {}
        self.indices = {'static':0, 'field':0, 'arg':0, 'var':0}

    def startSubroutine(self):
        self.subroutineTable = {}
        self.indices['arg']=0
        self.indices['var']=0

    def define(self, name, type, kind):
        if kind=='static' or kind=='field':
            self.classTable[name] = {'type':type, 'kind': kind, 
                                     'number':self.indices[kind]}
            self.indices[kind] +=1
        elif kind=='arg' or kind=='var':
            self.subroutineTable[name] = {'type':type, 'kind': kind, 
                                          'number':self.indices[kind]}
            self.indices[kind] +=1

    def varCount(self, kind):
        return self.indices[kind]

    def kindOf(self, name):
        if name in self.subroutineTable:
            return self.subroutineTable[name]['kind']
        elif name in self.classTable:
            return self.classTable[name]['kind']
        else:
            return None

    def typeOf(self, name):
        if name in self.subroutineTable:
            return self.subroutineTable[name]['type']
        elif name in self.classTable:
            return self.classTable[name]['type']
        else:
            return None

    def indexOf(self, name):
        if name in self.subroutineTable:
            return self.subroutineTable[name]['number']
        elif name in self.classTable:
            return self.classTable[name]['number']
        else:
            return None


######################################################################################
# VMWriter
# emits VM commands.
######################################################################################

class VMWriter:
    def __init__(self, file):
        self.ofile = open(file.split('.')[0] + '.vm', 'w')

    def writePush(self, segment, index):
        if segment == 'arg': segment='argument'
        elif segment == 'var': segment = 'local'
        elif segment == 'field': segment = 'this'
        self.ofile.write('push '+segment+' '+str(index)+'\n')

    def writePop(self, segment, index):
        if segment == 'arg': segment='argument'
        elif segment == 'var': segment = 'local'
        elif segment == 'field': segment = 'this'
        self.ofile.write('pop '+segment+' '+str(index)+'\n')

    def writeArithmetic(self, command):
        if command=='mult': 
            self.ofile.write("call Math.multiply 2\n")
        elif command=='div': 
            self.ofile.write("call Math.divide 2\n")
        else:
            self.ofile.write(command+'\n')

    def writeLabel(self, label):
        self.ofile.write('label '+label+'\n')

    def writeGoto(self, label):
        self.ofile.write('goto '+label+'\n')

    def writeIf(self, label):
        self.ofile.write('if-goto '+label+'\n')

    def writeCall(self, name, nArgs):
        self.ofile.write('call '+name+' '+str(nArgs)+'\n')

    def writeFunction(self, name, nLocals):
        self.ofile.write('function '+name+' '+str(nLocals)+'\n')

    def writeReturn(self):
        self.ofile.write('return'+'\n')

    def writeComment(self, comment):
        self.ofile.write(comment+'\n')

    def close(self):
        self.ofile.close()




######################################################################################
# COMPILATION ENGINE
# parse the grammar of jack file.
######################################################################################

class CompilationEngine:
    def __init__(self, tokens, file):
        self.ofile = open(file.split('.')[0] + '.xml', 'w')
        self.tokens = tokens
        self.iterator = 0
        self.statements = {'let':self.compileLetStatement, 
                           'if':self.compileIfStatement, 
                           'do': self.compileDoStatement, 
                           'while': self.compileWhileStatement, 
                           'return': self.compileReturnStatement}
        self.operators = {'+':'add', '-':'neg', '*':'mult', 
                          '/':'div', '&':'and', '|':'or', 
                        '<':'lt', '>':'gt', '=':'eq', '~':'not'}
        self.className = ''
        self.functionName = ''
        self.subroutineType = ''
        self.nLocals = 0
        self.labelNb = 0
        self.nArgs = 0

        # members useful for the symbol table.
        self.symbol_table = SymbolTable()
        self.name=''
        self.type=''
        self.kind=''

        self.VMWriter = VMWriter(file)

    def writeAndAdvence(self):
        self.ofile.write('<'+self.tokens[self.iterator][1]+'>'+
                    self.tokens[self.iterator][0]+
                '</'+self.tokens[self.iterator][1]+'>' + '\n')
        self.iterator += 1

    def write(self):
        self.ofile.write('<'+self.tokens[self.iterator][1]+'>'+
                    self.tokens[self.iterator][0]+
                '</'+self.tokens[self.iterator][1]+'>' + '\n')

    def writeIdentifierAndAdvence(self, dec, cat=''):
        kind = self.symbol_table.kindOf(self.tokens[self.iterator][0])
        index = self.symbol_table.indexOf(self.tokens[self.iterator][0])
        if kind!=None:
            self.ofile.write('<'+kind+'_'+str(index)+'_'+dec+'>'+
                             self.tokens[self.iterator][0]+
                            '<'+kind+'_'+str(index)+'_'+dec+'>' + '\n')
        else:
            self.ofile.write('<'+cat+'_'+dec+'>'+
                             self.tokens[self.iterator][0]+
                            '<'+cat+'_'+dec+'>' + '\n')

        self.iterator += 1



#----------------------PROGRAM STRUCTURE-----------------------------------
    def compileClass(self):
        self.VMWriter.writeComment("// class")
        # class
        self.iterator +=1
        # className
        self.className = self.tokens[self.iterator][0]
        self.iterator +=1
        # {
        self.iterator +=1
        # classVarDec*
        while (self.tokens[self.iterator][0] == 'static' or
              self.tokens[self.iterator][0] == 'field'):
            self.compileClassVarDec()
        # subroutineDec*
        while (self.tokens[self.iterator][0] == 'constructor' or
               self.tokens[self.iterator][0] == 'function' or
               self.tokens[self.iterator][0] == 'method'):
            print(self.functionName)
            print(self.symbol_table.classTable)
            print(self.symbol_table.subroutineTable)
            self.symbol_table.startSubroutine()
            self.compileSubroutine()
        # }
        self.VMWriter.close()


    def compileClassVarDec(self):
        self.VMWriter.writeComment("// class menber declaration")
        # static|field
        self.kind = self.tokens[self.iterator][0]
        self.iterator +=1
        # type
        self.type = self.tokens[self.iterator][0]
        self.iterator +=1
        # varName (',' varName)*
        self.name = self.tokens[self.iterator][0]
        self.symbol_table.define(self.name, self.type, self.kind)
        self.iterator +=1
        while self.tokens[self.iterator][0] == ',':
            # ,
            self.iterator +=1
            # varName
            self.name = self.tokens[self.iterator][0]
            self.symbol_table.define(self.name, self.type, self.kind)
            self.iterator +=1
        # ;
        self.iterator +=1


    def compileSubroutine(self):
        self.VMWriter.writeComment("// subroutine declaration")
        # constructor|function|method
        self.subroutineType = self.tokens[self.iterator][0]
        self.iterator +=1
        # void|type
        self.iterator +=1
        # subroutineName
        self.functionName = self.className+'.'+self.tokens[self.iterator][0]
        self.iterator +=1
        # (
        self.iterator +=1
        # parameterList method
        self.compileParameterList()
        # )
        self.iterator +=1
        # subroutineBody method
        self.compileSubroutineBody()
        self.nLocals = 0

    def compileParameterList(self):
        self.VMWriter.writeComment("// parameter list")
        # (type varName (',' type varName)* )
        self.kind = 'arg'
        if self.subroutineType == 'method':
            self.symbol_table.define('this', self.className, self.kind)
        if self.tokens[self.iterator][0] != ')':
            # type
            self.type = self.tokens[self.iterator][0]
            self.iterator +=1
            # varName
            self.name = self.tokens[self.iterator][0]
            self.symbol_table.define(self.name, self.type, self.kind)
            self.iterator +=1
            while self.tokens[self.iterator][0] == ',':
                # ,
                self.iterator +=1
                # type
                self.type = self.tokens[self.iterator][0]
                self.iterator +=1
                # varName
                self.name = self.tokens[self.iterator][0]
                self.symbol_table.define(self.name, self.type, self.kind)
                self.iterator +=1

    def compileSubroutineBody(self):
        self.VMWriter.writeComment("// subroutine body")
        # {
        self.iterator +=1
        # varDec* method
        while self.tokens[self.iterator][0] == 'var':
            self.compileVarDec()
            
        self.VMWriter.writeFunction(self.functionName, self.nLocals)
        if self.subroutineType == 'method':
            self.VMWriter.writePush('arg', 0)
            self.VMWriter.writePop('pointer', 0)
        elif self.subroutineType == 'constructor':
            nbFields = self.symbol_table.varCount('field')
            self.VMWriter.writePush('constant', nbFields)
            self.VMWriter.writeComment('call Memory.alloc 1')
            self.VMWriter.writePop('pointer', 0)
        # statements method
        self.compileStatements()
        # }
        self.iterator +=1
        self.labelNb = 0

    def compileVarDec(self):
        self.VMWriter.writeComment("// var declaration")
        self.kind = 'var'
        # var
        self.iterator +=1
        # type
        self.type = self.tokens[self.iterator][0]
        self.iterator +=1
        # varName (',' varName)*
        self.name = self.tokens[self.iterator][0]
        self.symbol_table.define(self.name, self.type, self.kind)
        self.iterator +=1
        self.nLocals +=1
        while self.tokens[self.iterator][0] == ',':
            # ,
            self.iterator +=1
            # varName
            self.name = self.tokens[self.iterator][0]
            self.symbol_table.define(self.name, self.type, self.kind)
            self.iterator +=1
            self.nLocals +=1
        # ;
        self.iterator +=1



#----------------------STATEMENTS-----------------------------------
    def compileStatements(self):
        while self.tokens[self.iterator][0] in self.statements:
            self.statements[ self.tokens[self.iterator][0] ]()

    def compileLetStatement(self):
        self.VMWriter.writeComment("//let statements")
        # let
        self.iterator +=1
        # varName
        name = self.tokens[self.iterator][0]
        seg = self.symbol_table.kindOf(name)
        index = self.symbol_table.indexOf(name)
        self.iterator +=1

        # ('['expression']')?
        if self.tokens[self.iterator][0] == '[':
            self.VMWriter.writePush(seg, index)
            self.iterator +=1
            # exp1
            self.compileExpression()
            self.iterator +=1
            # ]
            self.VMWriter.writeArithmetic('add')
            # =
            self.iterator +=1
            # expression 2
            self.compileExpression()
            self.VMWriter.writePop('temp', 0)
            self.VMWriter.writePop('pointer', 1)
            self.VMWriter.writePush('temp', 0)
            self.VMWriter.writePop('that', 0)
            # ;
            self.iterator +=1
        
        else:
            # =
            self.iterator +=1
            # expression
            self.compileExpression()
            self.VMWriter.writePop(seg, index)
            # ;
            self.iterator +=1


    def compileIfStatement(self):
        L1 = 'L'+ str(self.labelNb)
        self.labelNb +=1
        L2 = 'L'+ str(self.labelNb)
        self.labelNb +=1

        self.VMWriter.writeComment("//if statements")
        # if
        self.iterator +=1
        # (
        self.iterator +=1
        # expression
        self.compileExpression()
        self.VMWriter.writeArithmetic('not')
        self.VMWriter.writeIf(L1)
        # )
        self.iterator +=1
        # {
        self.iterator +=1
        # statements
        self.compileStatements()
        self.VMWriter.writeGoto(L2)
        # }
        self.iterator +=1
        # if else {statements }
        self.VMWriter.writeLabel(L1)
        if self.tokens[self.iterator][0] == 'else':
            # else
            self.iterator +=1
            # {
            self.iterator +=1
            # statements
            self.compileStatements()
            # }
            self.iterator +=1
        self.VMWriter.writeLabel(L2)


    def compileWhileStatement(self):
        L1 = 'L'+ str(self.labelNb)
        self.labelNb +=1
        L2 = 'L'+ str(self.labelNb)
        self.labelNb +=1

        self.VMWriter.writeComment("//while statements")
        self.VMWriter.writeLabel(L1)
        # while
        self.iterator +=1
        # (
        self.iterator +=1
        # expression
        self.compileExpression()
        # )
        self.iterator +=1
        self.VMWriter.writeArithmetic('not')
        self.VMWriter.writeIf(L2)
        # {
        self.iterator +=1
        # statements
        self.compileStatements()
        self.VMWriter.writeGoto(L1)
        # }
        self.VMWriter.writeLabel(L2)
        self.iterator +=1

    def compileDoStatement(self):
        self.nArgs = 0
        self.VMWriter.writeComment("//do statements")
        # do
        self.iterator +=1
        # subroutineCall
        self.iterator += 1
        if self.tokens[self.iterator][0] == '(':
            self.iterator -= 1
            # subroutineName
            callFunction = self.tokens[self.iterator][0]
            callFunction = self.className + '.' + callFunction
            self.iterator +=1
            # (
            self.iterator +=1
            # expressionList
            self.VMWriter.writePush('pointer', 0)
            self.nArgs +=1
            self.compileExpressionList()
            # )
            self.iterator +=1
            self.VMWriter.writeCall(callFunction, self.nArgs)
        else:
            self.iterator -= 1
            # class|varName
            kind = self.symbol_table.kindOf(self.tokens[self.iterator][0])
            otype = self.symbol_table.typeOf(self.tokens[self.iterator][0])
            index = self.symbol_table.indexOf(self.tokens[self.iterator][0])
            if kind == None:  # class
                callFunction = self.tokens[self.iterator][0]
                self.iterator +=1
                # .
                self.iterator +=1
                # subroutineName
                callFunction = callFunction+'.'+self.tokens[self.iterator][0]
                self.iterator +=1
                # (
                self.iterator +=1
                # expressionList
                self.compileExpressionList()
                # )
                self.iterator +=1
                self.VMWriter.writeCall(callFunction, self.nArgs)
            else: # varName
                self.iterator +=1
                # .
                self.iterator +=1
                # subroutineName
                method = otype+'.'+self.tokens[self.iterator][0]
                self.iterator +=1
                # (
                self.iterator +=1
                # expressionList
                self.VMWriter.writePush(kind, index)
                self.nArgs +=1
                self.compileExpressionList()
                # )
                self.iterator +=1
                self.VMWriter.writeCall(method, self.nArgs)

        # ;
        self.iterator +=1
        # do statement is only void
        self.VMWriter.writePop('temp', 0)
        self.nArgs = 0

    def compileReturnStatement(self):
        self.VMWriter.writeComment("//return statements")
        if self.subroutineType == 'constructor':
            self.VMWriter.writePush('pointer', 0)
            self.VMWriter.writeReturn()
            # return
            self.iterator +=1
            # this
            self.iterator +=1
            # ;
            self.iterator +=1
            return
        # return
        self.iterator +=1
        # expression?
        if self.tokens[self.iterator][0] != ';':
            self.compileExpression()
            self.VMWriter.writeReturn()
        else:
            # function is void
            self.VMWriter.writePush('constant', 0)
            self.VMWriter.writeReturn()
        # ;
        self.iterator +=1


#----------------------EXPRESSIONS-----------------------------------
    def compileExpression(self):
        self.VMWriter.writeComment("// expression")
        # term 
        self.compileTerm()
        # (op term)*
        while self.tokens[self.iterator][0] in self.operators:
            # op
            op = self.tokens[self.iterator][0]
            if op == '-' : op = 'sub'
            else: op = self.operators[op]
            self.iterator +=1
            # term
            self.compileTerm()
            self.VMWriter.writeArithmetic(op)


    def compileExpressionList(self):
        self.VMWriter.writeComment("// expression list")
        # (expression (, expression*))?
        if self.tokens[self.iterator][0] != ')':
            self.compileExpression()
            self.nArgs += 1
            while self.tokens[self.iterator][0] == ',':
                self.iterator +=1
                self.compileExpression()
                self.nArgs += 1


    def compileTerm(self):
        self.VMWriter.writeComment("// expression")
        # '('expression')' case
        if self.tokens[self.iterator][0] == '(':
            self.iterator +=1
            self.compileExpression()
            self.iterator +=1
            return

        # unaryOp term case
        elif (self.tokens[self.iterator][0] == '-' or
              self.tokens[self.iterator][0] == '~'):
            op = self.operators[self.tokens[self.iterator][0]]
            self.iterator +=1
            self.compileTerm()
            self.VMWriter.writeArithmetic(op)
            return

        self.iterator += 1
        # varName[expression] case
        if self.tokens[self.iterator][0] == '[':
            self.iterator -= 1
            # varName
            name = self.tokens[self.iterator][0]
            seg = self.symbol_table.kindOf(name)
            index = self.symbol_table.indexOf(name)
            self.VMWriter.writePush(seg, index)
            self.iterator +=1
            # [
            self.iterator +=1
            # expression
            self.compileExpression()
            # ]
            self.VMWriter.writeArithmetic('add')
            self.VMWriter.writePop('pointer', 1)
            self.VMWriter.writePush('that', 0)
            self.iterator +=1
            return

        # functioncall() case
        elif self.tokens[self.iterator][0] == '(':
            self.nArgs = 0
            self.iterator -= 1
            # subroutineName
            name = self.tokens[self.iterator][0]
            self.iterator +=1
            # (
            self.iterator +=1
            # expressionList
            self.VMWriter.writePush('pointer', 0)
            self.nArgs +=1
            self.compileExpressionList()
            # )
            self.iterator +=1
            self.VMWriter.writeCall(name, self.nArgs)
            self.nArgs = 0
            return

        # class.methodCall() case
        elif self.tokens[self.iterator][0] == '.':
            self.nArgs = 0
            self.iterator -= 1
            # class|varName
            kind = self.symbol_table.kindOf(self.tokens[self.iterator][0])
            otype = self.symbol_table.typeOf(self.tokens[self.iterator][0])
            index = self.symbol_table.indexOf(self.tokens[self.iterator][0])
            if kind == None:  # class
                name = self.tokens[self.iterator][0]
                self.iterator += 1
                # .
                self.iterator += 1
                # subroutineName
                name = name+'.'+self.tokens[self.iterator][0]
                self.iterator += 1
                # (
                self.iterator += 1
                # expressionList
                self.compileExpressionList()
                # )
                self.iterator += 1
                self.VMWriter.writeCall(name, self.nArgs)
                self.nArgs = 0
            else: # varName
                self.iterator +=1
                # .
                self.iterator +=1
                # subroutineName
                method = otype+'.'+self.tokens[self.iterator][0]
                self.iterator +=1
                # (
                self.iterator +=1
                # expressionList
                self.VMWriter.writePush(kind, index)
                self.nArgs +=1
                self.compileExpressionList()
                # )
                self.iterator +=1
                self.VMWriter.writeCall(method, self.nArgs)
            return
        
        # integerConstant, stringConstant, keywordConstant, varName case
        self.iterator -= 1
        if self.tokens[self.iterator][1]=='integerConstant':
            self.VMWriter.writePush('constant', self.tokens[self.iterator][0])
            self.iterator += 1
        elif self.tokens[self.iterator][0]=='true':
            self.VMWriter.writePush('constant', 1)
            self.VMWriter.writeArithmetic('neg')
            self.iterator += 1
        elif self.tokens[self.iterator][0]=='false' or self.tokens[self.iterator][0]=='null':
            self.VMWriter.writePush('constant', 0)
            self.iterator += 1
        elif self.tokens[self.iterator][0]=='this':
            self.VMWriter.writePush('pointer', 0)
            self.iterator += 1
        elif self.tokens[self.iterator][1]=='stringConstant':
            self.compileStringConstant(self.tokens[self.iterator][0])
        elif self.tokens[self.iterator][1]=='identifier':
            name = self.tokens[self.iterator][0]
            seg = self.symbol_table.kindOf(name)
            index = self.symbol_table.indexOf(name)
            self.VMWriter.writePush(seg, index)
            self.iterator += 1
        else: 
            self.iterator += 1


    def compileStringConstant(self, s):
        # this = String.length)
        self.VMWriter.writePush('constant', len(s))
        self.VMWriter.writeComment("call String.new 1\n")
        # this = "pointer to string"
        for c in s:
            self.VMWriter.writePush('constant', ord(c))
            self.VMWriter.writeComment("call String.appendChar 2\n")
        self.iterator += 1

if __name__ == '__main__':
    analyser = JackAnalyzer()
    analyser.operateInput()
