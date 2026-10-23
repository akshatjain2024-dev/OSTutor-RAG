---
topic: Shell Programming
source: Lab manual - Experiment 2
---
# Shell Programming (bash)

A shell script is a text file containing commands that the shell runs in order. The first line, #!/bin/bash, is the shebang and tells the system which interpreter to use. Make the script executable with chmod +x script.sh and run it with ./script.sh, or run it directly with bash script.sh.

## Variables and input
Variables are assigned with no spaces around the equals sign, like name="OS", and used as $name. read var reads a value from the user. Special variables: $0 is the script name, $1 to $9 are command-line arguments, $# is the number of arguments, $@ is all arguments, $? is the exit status of the last command (0 means success) and $$ is the PID of the current shell.

## Arithmetic
Use $(( )) for integer arithmetic, for example sum=$((a + b)). The older expr command also works: expr $a + $b (spaces required). For decimals use bc, for example echo "scale=2; 10/3" | bc.

## Conditions
if [ $a -gt $b ]; then echo "a is bigger"; elif [ $a -eq $b ]; then echo "equal"; else echo "b is bigger"; fi
Numeric comparisons use -eq, -ne, -gt, -lt, -ge and -le. String comparisons use = and !=, -z checks for an empty string. File tests: -f (regular file exists), -d (directory exists), -r, -w and -x (permissions).

## Loops
for i in 1 2 3 4 5; do echo $i; done
while [ $i -le 10 ]; do i=$((i + 1)); done
until runs until the condition becomes true. break and continue work like in C.

## Case statement
case $choice in
  1) echo "Add";;
  2) echo "Subtract";;
  *) echo "Invalid";;
esac

## Functions
Define a function with name() { commands; } and call it by name. Arguments inside the function are $1, $2 and so on, and return gives an exit status.

## Common lab programs
Typical lab exercises: sum of digits of a number, checking whether a number is prime or a palindrome, factorial, Fibonacci series, finding the largest of three numbers, a simple calculator using case, and counting the lines, words and characters in a file using wc.
