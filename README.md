# The project

Virtual computer is a long project during wich I built a very simple yet functional computer and a programing language from the grownd up. This project is my implementation following the design of the computer described in the course Nand To Tetris, see their website for reference  <http://www.nand2tetris.org/>.
It consist of two part in the first one the hardware is implemented virtually. In the second part, an assembler, stack virtual machine, and compiler is implemented in order to create a programming language that can use the hardware built in the previous part. I will describe the 2 sections in detail.


## Hardware. 
Use an HDL Hadware Description Language to implement different chips, using only two elementary gates: Nand and flipflop. The Increased complexity increase gradualy to culminate in the implementation of a CPU, an a ROM and RAM memory units. The computer consist of this CPU and these two memory units, the ROM is design taccept a program, only one program can run at the time, like in an old nintendo cardtridge. The RAM is the main memory and is directly mapped to a keyboard and a screen.
Below the architecture of the cpu
Below the set of machine instructions available.
Note that the only data type accepted is integer and only operations are addition and substraction. More functionalities are implemented by the standard library of the programming language in the second part.

Below a description of the computer architecture.

![](./media/archi.png)

## Software. 
Java C# like programming language with a two tier compiler.
Implementation of a Standard Library/OS to provide functionalities.

## Example of Pong game.
You can test the program by compiling it with the Compiler.py script `python Compiler.py Pong`
It creates some file.vm of all classes. Continue with the VMtranslator then assembler.
The best way to test the program is to use the VMEmulator. This directory can then be loaded in the VMEmulator (to download from http://www.nand2tetris.org/software.php) to run the program.

## References
