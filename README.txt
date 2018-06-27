-------------------------
* Mini-shop Job Scheduler *
The problem we want to solve is defined as following.
We have many helpers working in a shop. Each month we need to have an arrangement specifying which helper will be on duty in each day.
So we collect available days information of each helper in that month. And this program uses these information to come up with an good arrangement.
#For more details including file format specification, we refer you to docs/README.txt.

HOW TO RUN
-Require Python(version 2.7 or after) with following modules (you can use pip to install python module)
numpy
csv
argparse
sys
calendar
collections
math
random
time
copy
We recommend you to run our program first to find out which modules are not installed.

-Run our program “./AutoScheduler.py” in the command line.
 A typical example:
	python ./AutoScheduler.py -i <datafile>
 There are more arguments which can be set to control the program.
 Run “python ./AutoScheduler.py -h” to see details of all the arguments.


ALGORITHM SPECIFIC
Genetic algorithm is applied with following details.
Each candidate solution S is represented as a vector, of which the length is the number of days in a month. Si=j represents that helper j will be on duty in i-th day of a month.
Fitness function:
Three factors are considered in the fitness function:
We want all helpers involved in the best case.
Number of working days for all helpers in the whole month should be similar.
The working days for each helper are better to be consecutive.
