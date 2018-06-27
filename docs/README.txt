-------------------------
* Mini-shop Job Scheduler *

INPUT A file specifying available dates of helpers.
 File format specification: 
-File name format : year-month.csv (e.g. 2018-01.csv)
-File in CSV format
 Header   时间戳记,联系方式,Helper名字,"可以值班的时间（多选，请选择所有你可以值班的时间，选项中连续天数至少为两天, 一个月中至少有两个星期里面有连续的时间”  #helper的名字是强制需要的，以大写拼音输入，e.g. FENG QIAN  #“时间戳记”, “联系方式”, “Helper名字” 中不能出现“,”
 “可以的值班时间” example (包括特殊情况1)   7.1(Sat);7.2(Sun);7.3(Mon);7.4(Tue);7.7(Fri);7.8(Sat);7.9(Sun);7.10(Mon);7.11(Tue);7.12(Wed);7.13(Thu)
-File example  时间戳,联系方式,Helper名字,"可以值班的时间（多选，请选择所有你可以值班的时间，选项中连续天数至少为两天, 一个月中至少有两个星期里面有连续的时间）”  2017/06/14 1:34:49 下午 GMT+8,,SU RUI,7.1(Sat);7.2(Sun);7.3(Mon);7.4(Tue)  2017/06/14 1:51:00 下午 GMT+8,,CHEN XIN,7.3(Mon);7.4(Tue);7.5(Wed)
-同一个helper的多条记录  所有的记录按时间戳排序(早的记录在前面，晚的记录在后面)，如果同一个helper有多条记录被检测到，后面的记录将会覆盖前面的记录.
-特殊情况  1. Helper在这个月每天都有空。对应“可以的值班时间”显示为“All”.  2. Helper的名字没有填写，程序发出警告，并略过此条记录。使用者可更改数据后重新运行程序. 
OUTPUT
-output files
 available_days.csv   A matrix M in CSV format.  M(i, j) =1 means helper i is available in date indicated by column j, otherwise not available.
 available_helper_each_day.csv   Count the number of helpers available in each day.
 schedule.csv   The schedule recommended by the program.
-warnings will be given in following circumstances.
 A record without “name”.
 All helpers are unavailable in some days.

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