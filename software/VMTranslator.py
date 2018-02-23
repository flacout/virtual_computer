import sys
import os


class VMTranslator:
    def __init__(self):
        self.input = sys.argv[1]
        ofile_name = ''
        self.ofile = None
        self.file_name = ''
        self.static_name = ''

        # keep track of labels number and names in assembly
        self.fuction_name = ''
        self.return_adress_nb = 0
        self.label_nb = 0
        self.symbols ={'local':'LCL', 'argument':'ARG', 'this':'THIS', 'that':'THAT',
                       'pointer':3, 'temp':5, 'static':self.static_name}

    # operate a single file or entire folder
    def operateInput(self):
        if self.input.endswith('.vm'): 
            ofile_name = self.input.split('.')[0] + '.asm'
            self.ofile = open(ofile_name, 'w')
            self.parse(self.input)

        else:
            ofile_name = self.input+ '/' + self.input.split('/')[-1] + '.asm'
            self.ofile = open(ofile_name, 'w')
            self.writeStartupCode()
            for file in os.listdir(self.input):
                if file.endswith('.vm'):
                    self.parse(self.input+'/'+file)


    # read a line and translate it in assembly
    def parse(self, filename):
        self.file_name = filename
        self.ifile = open(self.file_name, 'r')
        self.static_name = self.file_name.split('.')[0].split('/')[-1]

        for line in self.ifile:
            line = line.strip()
            # get rid of all comments
            if line.startswith('//') or line=='': continue
            line = self.removeComment(line)

            if line.startswith('push'): self.resolvePush(line)
            elif line.startswith('pop'): self.resolvePop(line)
            elif line.startswith('label'): self.resolveLabel(line)
            elif line.startswith('goto'): self.resolveGoto(line)
            elif line.startswith('if'): self.resolveIf(line)
            elif line.startswith('function'): self.resolveFunction(line)
            elif line.startswith('call'): self.resolveCall(line)
            elif line.startswith('return'): self.resolveReturn(line)
            else: self.resolveArithmetic(line)
        self.ifile.close()


    def removeComment(self, line):
        words = line.split('//')
        return words[0].strip()

    def close(self):
        self.ofile.close()

    # write bootstrap code and segment initialization
    # called only if the input is a directory.
    def writeStartupCode(self):
        instructions= ("//SP=256\n"
                      "@256\n"
                      "D=A\n"
                      "@SP\n"
                      "M=D\n"
                      "//call Sys.init 0\n"
                       "@INITIATION\n" 
                       "D=A\n"
                       "@SP\n"
                       "A=M\n"
                       "M=D\n"
                       "@SP\n"
                       "M=M+1\n"
                       "@LCL\n"
                       "D=M\n"
                       "@SP\n"
                       "A=M\n"
                       "M=D\n"
                       "@SP\n"
                       "M=M+1\n"
                       "@ARG\n"
                       "D=M\n"
                       "@SP\n"
                       "A=M\n"
                       "M=D\n"
                       "@SP\n"
                       "M=M+1\n"
                       "@THIS\n"
                       "D=M\n"
                       "@SP\n"
                       "A=M\n"
                       "M=D\n"
                       "@SP\n"
                       "M=M+1\n"
                       "@THAT\n"
                       "D=M\n"
                       "@SP\n"
                       "A=M\n"
                       "M=D\n"
                       "@SP\n"
                       "M=M+1\n"
                       "@SP\n"
                       "D=M\n"
                       "@5\n"
                       "D=D-A\n"
                       "@ARG\n"
                       "M=D\n"
                       "@SP\n"
                       "D=M\n"
                       "@LCL\n"
                       "M=D\n"
                      "@Sys.init\n"
                      "0;JMP\n"
                      "(INITIATION)\n")
        self.ofile.write(instructions)
        return

###################################################################################
# Push functions
###################################################################################
    def resolvePush(self, line):
        commands = line.split()
        if (commands[1] == 'local') or (commands[1] == 'argument') or (
            commands[1] == 'this')  or (commands[1] == 'that'):
            self.writePushPointer(commands, line)
        elif (commands[1] == 'constant'):
            self.writeConstant(commands, line)
        else:
            self.writePushDirect(commands, line)


    def writePushPointer(self, commands, line):
        seg = commands[1]
        i = commands[2]
        instructions= ("//%s\n"
                      "@%s\n"
                      "D=A\n"
                      "@%s\n"
                      "A=D+M\n"
                      "D=M\n"
                      "@SP\n"
                      "A=M\n"
                      "M=D\n"
                      "@SP\n"
                      "M=M+1\n" %(line, i, self.symbols[seg]))
        #print(instructions)
        self.ofile.write(instructions)

    def writeConstant(self, commands, line):
        seg = commands[1]
        i = commands[2]
        instructions= ("//%s\n"
                      "@%s\n"
                      "D=A\n"
                      "@SP\n"
                      "A=M\n"
                      "M=D\n"
                      "@SP\n"
                      "M=M+1\n" %(line, i))
        #print(instructions)
        self.ofile.write(instructions)

    def writePushDirect(self, commands, line):
        seg = commands[1]
        i = commands[2]
        if seg=='pointer' or seg=='temp': address = str(self.symbols[seg]+int(i))
        else : address = str(self.static_name+'.'+i)
        instructions= ("//%s\n"
                      "@%s\n"
                      "D=M\n"
                      "@SP\n"
                      "A=M\n"
                      "M=D\n"
                      "@SP\n"
                      "M=M+1\n" %(line, address))
        #print(instructions)
        self.ofile.write(instructions)


###################################################################################
# Pop functions
###################################################################################
    def resolvePop(self, line):
        commands = line.split()
        if (commands[1] == 'local') or (commands[1] == 'argument') or (
            commands[1] == 'this')  or (commands[1] == 'that'):
            self.writePopPointer(commands, line)
        else:
            self.writePopDirect(commands, line)

    def writePopPointer(self, commands, line):
        seg = commands[1]
        i = commands[2]
        instructions= ("//%s\n"
                      "@%s\n"
                      "D=A\n"
                      "@%s\n"
                      "D=D+M\n"
                      "@R15\n"
                      "M=D\n"
                      "@SP\n"
                      "M=M-1\n"
                      "A=M\n"
                      "D=M\n"
                      "@R15\n"
                      "A=M\n"
                      "M=D\n" %(line, i, self.symbols[seg]))
        #print(instructions)
        self.ofile.write(instructions)

    def writePopDirect(self, commands, line):
        seg = commands[1]
        i = commands[2]
        if seg=='pointer' or seg=='temp': address = str(self.symbols[seg]+int(i))
        else : address = str(self.static_name+'.'+i)
        instructions= ("//%s\n"
                      "@SP\n"
                      "M=M-1\n"
                      "A=M\n"
                      "D=M\n"
                      "@%s\n"
                      "M=D\n" %(line, address))
        #print(instructions)
        self.ofile.write(instructions)

###################################################################################
# Arithmetic functions
###################################################################################
    def resolveArithmetic(self, line):
        if (line == 'add'): self.writeAdd(line)
        elif (line == 'sub'): self.writeSub(line)
        elif (line == 'neg'): self.writeNeg(line)
        elif (line == 'eq'): self.writeEq(line)
        elif (line == 'gt'): self.writeGt(line)
        elif (line == 'lt'): self.writeLt(line)
        elif (line == 'and'): self.writeAnd(line)
        elif (line == 'or'): self.writeOr(line)
        elif (line == 'not'): self.writeNot(line)

    def writeAdd(self, line):
        instructions= ("//%s\n"
                      "@SP\n"
                      "A=M\n"
                      "A=A-1\n"
                      "D=M\n"
                      "A=A-1\n"
                      "M=M+D\n"
                      "@SP\n" 
                      "M=M-1\n" %(line))
        #print(instructions)
        self.ofile.write(instructions)

    def writeSub(self, line):
        instructions= ("//%s\n"
                      "@SP\n"
                      "A=M\n"
                      "A=A-1\n"
                      "D=M\n"
                      "A=A-1\n"
                      "M=M-D\n"
                      "@SP\n" 
                      "M=M-1\n" %(line))
        #print(instructions)
        self.ofile.write(instructions)

    def writeNeg(self, line):
        instructions= ("//%s\n"
                      "@SP\n"
                      "A=M\n"
                      "A=A-1\n"
                      "M=-M\n" %(line))
        #print(instructions)
        self.ofile.write(instructions)

    def writeEq(self, line):
        instructions= ("//%s\n"
                      "@SP\n"
                      "M=M-1\n"
                      "A=M\n"
                      "D=M\n"
                      "@SP\n"
                      "M=M-1\n"
                      "A=M\n"
                      "D=M-D\n"
                      "@LABEL%d\n"
                      "D;JEQ\n"
                      "@SP\n"
                      "A=M\n"
                      "M=0\n"
                      "@LABEL%d\n"
                      "0;JMP\n"
                      "(LABEL%d)\n"
                      "@SP\n"
                      "A=M\n"
                      "M=-1\n"
                      "(LABEL%d)\n"
                      "@SP\n"
                      "M=M+1\n" %(line, self.label_nb, self.label_nb+1, 
                                  self.label_nb, self.label_nb+1))
        #print(instructions)
        self.ofile.write(instructions)
        self.label_nb +=2

    def writeGt(self, line):
        instructions= ("//%s\n"
                      "@SP\n"
                      "M=M-1\n"
                      "A=M\n"
                      "D=M\n"
                      "@SP\n"
                      "M=M-1\n"
                      "A=M\n"
                      "D=M-D\n"
                      "@LABEL%d\n"
                      "D;JGT\n"
                      "@SP\n"
                      "A=M\n"
                      "M=0\n"
                      "@LABEL%d\n"
                      "0;JMP\n"
                      "(LABEL%d)\n"
                      "@SP\n"
                      "A=M\n"
                      "M=-1\n"
                      "(LABEL%d)\n"
                      "@SP\n"
                      "M=M+1\n" %(line, self.label_nb, self.label_nb+1, 
                                  self.label_nb, self.label_nb+1))
        #print(instructions)
        self.ofile.write(instructions)
        self.label_nb +=2

    def writeLt(self, line):
        instructions= ("//%s\n"
                      "@SP\n"
                      "M=M-1\n"
                      "A=M\n"
                      "D=M\n"
                      "@SP\n"
                      "M=M-1\n"
                      "A=M\n"
                      "D=M-D\n"
                      "@LABEL%d\n"
                      "D;JLT\n"
                      "@SP\n"
                      "A=M\n"
                      "M=0\n"
                      "@LABEL%d\n"
                      "0;JMP\n"
                      "(LABEL%d)\n"
                      "@SP\n"
                      "A=M\n"
                      "M=-1\n"
                      "(LABEL%d)\n"
                      "@SP\n"
                      "M=M+1\n" %(line, self.label_nb, self.label_nb+1, 
                                  self.label_nb, self.label_nb+1))
        #print(instructions)
        self.ofile.write(instructions)
        self.label_nb +=2


    def writeAnd(self, line):
        instructions= ("//%s\n"
                      "@SP\n"
                      "A=M\n"
                      "A=A-1\n"
                      "D=M\n"
                      "A=A-1\n"
                      "M=D&M\n"
                      "@SP\n" 
                      "M=M-1\n" %(line))
        #print(instructions)
        self.ofile.write(instructions)

    def writeOr(self, line):
        instructions= ("//%s\n"
                      "@SP\n"
                      "A=M\n"
                      "A=A-1\n"
                      "D=M\n"
                      "A=A-1\n"
                      "M=D|M\n"
                      "@SP\n" 
                      "M=M-1\n" %(line))
        #print(instructions)
        self.ofile.write(instructions)

    def writeNot(self, line):
        instructions= ("//%s\n"
                      "@SP\n"
                      "A=M\n"
                      "A=A-1\n"
                      "M=!M\n" %(line))
        #print(instructions)
        self.ofile.write(instructions)


###################################################################################
#Branching functions
###################################################################################

    def resolveLabel(self, line):
        commands = line.split()
        label = self.fuction_name +'$'+commands[-1]
        instructions= ("//%s\n"
                       "(%s)\n" %(line, label))
        self.ofile.write(instructions)


    def resolveGoto(self, line):
        commands = line.split()
        label = self.fuction_name +'$'+commands[-1]
        instructions= ("//%s\n"
                       "@%s\n" 
                       "0;JMP\n" %(line, label))
        self.ofile.write(instructions)


    def resolveIf(self, line):
        commands = line.split()
        label = self.fuction_name +'$'+commands[-1]
        instructions= ("//%s\n"
                       "@SP\n"
                       "M=M-1\n"
                       "A=M\n"
                       "D=M\n"
                       "@%s\n"
                       "D;JNE\n" %(line, label))
        self.ofile.write(instructions)

###################################################################################
#Functions handling
###################################################################################

    def resolveFunction(self, line):
        commands = line.split()
        label = commands[-2]
        self.fuction_name = label
        instructions= ("//%s\n"
                      "(%s)\n"
                      "@%s\n"
                      "D=A\n"
                      "@R15\n"
                      "M=D\n"
                      "(LABEL%d)\n"
                      "@R15\n"
                      "M=M-1\n"
                      "D=M\n"
                      "@LABEL%d\n"
                      "D;JLT\n"
                      "@LCL\n"
                      "A=D+M\n"
                      "M=0\n"
                      "@SP\n"
                      "M=M+1\n"
                      "@LABEL%d\n"
                      "0;JMP\n"
                      "(LABEL%d)\n" %(line, label, commands[-1], 
                                      self.label_nb, self.label_nb+1, 
                                      self.label_nb, self.label_nb+1))
        self.ofile.write(instructions)
        self.label_nb +=2


    def resolveCall(self, line):
        commands = line.split()
        n = commands[-1]
        f = commands[-2]
        return_address = self.fuction_name + "$ret." + str(self.return_adress_nb)
        self.return_adress_nb +=1
        instructions= ("//%s\n"
                       "@%s\n" 
                       "D=A\n"
                       "@SP\n"
                       "A=M\n"
                       "M=D\n"
                       "@SP\n"
                       "M=M+1\n"
                       "@LCL\n"
                       "D=M\n"
                       "@SP\n"
                       "A=M\n"
                       "M=D\n"
                       "@SP\n"
                       "M=M+1\n"
                       "@ARG\n"
                       "D=M\n"
                       "@SP\n"
                       "A=M\n"
                       "M=D\n"
                       "@SP\n"
                       "M=M+1\n"
                       "@THIS\n"
                       "D=M\n"
                       "@SP\n"
                       "A=M\n"
                       "M=D\n"
                       "@SP\n"
                       "M=M+1\n"
                       "@THAT\n"
                       "D=M\n"
                       "@SP\n"
                       "A=M\n"
                       "M=D\n"
                       "@SP\n"
                       "M=M+1\n"
                       "@SP\n"
                       "D=M\n"
                       "@%s\n"
                       "D=D-A\n"
                       "@5\n"
                       "D=D-A\n"
                       "@ARG\n"
                       "M=D\n"
                       "@SP\n"
                       "D=M\n"
                       "@LCL\n"
                       "M=D\n"
                       "@%s\n"
                       "0;JMP\n"
                       "(%s)\n" %(line, return_address, str(n), f, return_address))
        self.ofile.write(instructions)


    def resolveReturn(self, line):
        instructions= ("//%s\n"
                       "@LCL\n"
                       "D=M\n"
                       "@R15\n"
                       "M=D\n"
                       "D=M\n"
                       "@5\n"
                       "D=D-A\n"
                       "A=D\n"
                       "D=M\n"
                       "@R14\n"
                       "M=D\n"
                       "@SP\n"
                       "M=M-1\n"
                       "A=M\n"
                       "D=M\n"
                       "@ARG\n"
                       "A=M\n"
                       "M=D\n"
                       "@ARG\n"
                       "D=M\n"
                       "D=D+1\n"
                       "@SP\n"
                       "M=D\n"
                       "@R15\n"
                       "M=M-1\n"
                       "A=M\n"
                       "D=M\n"
                       "@THAT\n"
                       "M=D\n"
                       "@R15\n"
                       "M=M-1\n"
                       "A=M\n"
                       "D=M\n"
                       "@THIS\n"
                       "M=D\n"
                       "@R15\n"
                       "M=M-1\n"
                       "A=M\n"
                       "D=M\n"
                       "@ARG\n"
                       "M=D\n"
                        "@R15\n"
                       "M=M-1\n"
                       "A=M\n"
                       "D=M\n"
                       "@LCL\n"
                       "M=D\n"
                       "@R14\n"
                       "A=M\n"
                       "0;JMP\n" %(line))
        self.ofile.write(instructions)



translator = VMTranslator()
translator.operateInput()
translator.close()