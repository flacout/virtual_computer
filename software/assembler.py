import sys

class Assembler:
    def __init__(self):
        self.file_name = sys.argv[1]
        self.ifile = open(self.file_name, 'r')
        ofile_name = self.file_name.split('.')[0] + '.hack'
        self.ofile = open(ofile_name, 'w')

        # keep track of the instruction line in ROM
        self.instruction_nb = 0
        # keep track of address for variable in RAM, starting at 16.
        self.available_address = 16

        self.symbols ={'SP':0, 'LCL':1, 'ARG':2, 'THIS':3, 'THAT':4,
                       'R0':0, 'R1':1, 'R2':2, 'R3':3, 'R4':4, 'R5':5,
                       'R6':6, 'R7':7, 'R8':8, 'R9':9, 'R10':10,
                       'R11':11, 'R12':12, 'R13':13, 'R14':14, 'R15':15,
                       'SCREEN':16384, 'KBD':24576}
        self.computations = {'0':'0101010', '1':'0111111', '-1':'0111010', 
                             'D':'0001100', 'A':'0110000', '!D':'0001101',
                             '!A':'0110001', '-D':'0001111', '-A':'0110011',
                             'D+1':'0011111', 'A+1':'0110111', 'D-1':'0001110',
                             'A-1':'0110010', 'D+A':'0000010', 'D-A':'0010011',
                             'A-D':'0000111', 'D&A':'0000000', 'D|A':'0010101',
                             'M':'1110000', '!M':'1110001', '-M':'1110011',
                             'M+1':'1110111', 'M-1':'1110010', 'D+M':'1000010',
                             'M+D':'1000010',
                             'D-M':'1010011', 'M-D':'1000111', 'D&M':'1000000',
                             'D|M':'1010101'}
        self.destinations = {'null':'000', 'M':'001', 'D':'010', 'MD':'011',
                             'A':'100', 'AM':'101', 'AD':'110', 'AMD':'111'}
        self.jumps = {'null':'000', 'JGT':'001', 'JEQ':'010', 'JGE':'011',
                      'JLT':'100', 'JNE':'101', 'JLE':'110', 'JMP':'111'}


    # enter all the labels (goto variable) is the symbols table.
    def firstPass(self):
        for line in self.ifile:
            line = line.strip()
            # get rid of all comments
            if line.startswith('//') or line=='': continue
            line = self.removeComment(line)

            # enter label in table
            if line.startswith('('):
                label = line[1:-1]
                self.symbols[label] = self.instruction_nb
                continue

            # if normal instruction go to the next one.
            self.instruction_nb += 1
        print(self.symbols)


    def secondPass(self):
        self.ifile.seek(0)
        for line in self.ifile:
            line = line.strip()
            # get rid of all comments
            if line.startswith('//'): continue
            line = self.removeComment(line)

            if ('@' in line) : self.writeAInstruction(line)
            elif ('=' in line) or (';' in line) : self.writeCInstruction(line)



    def removeComment(self, line):
        words = line.split('//')
        return words[0].strip()

    def writeAInstruction(self, line):
        number = line[1:]
        if number.isdigit():
            instruction = format(int(number), '016b')
        else:
            if (number in self.symbols): 
                instruction = format(self.symbols[number], '016b')
            else:
                self.symbols[number] = self.available_address
                instruction = format(self.available_address, '016b')
                self.available_address += 1
        #print(instruction)
        self.ofile.write(instruction+'\n')

    def writeCInstruction(self, line):
        instruction = '111'
        line = line.split('=')
        if len(line) == 2 : dest = self.destinations[line[0].strip()]
        else : dest = '000'
        line = line[-1].split(';')
        if len(line) ==2: jump = self.jumps[line[1].strip()]
        else: jump = '000'
        comp = self.computations[line[0].strip()]
        instruction = instruction+comp+dest+jump
        self.ofile.write(instruction+'\n')



    def close(self):
        self.ifile.close()
        self.ofile.close()



ass = Assembler()
ass.firstPass()
ass.secondPass()
ass.close()