#!/bin/python

import numpy as np
import csv
import argparse
import sys
from calendar import monthrange
from collections import Counter
import math
import random
import time
import copy

class bcolors:
  HEADER = '\033[95m'
  OKBLUE = '\033[94m'
  OKGREEN = '\033[92m'
  WARNING = '\033[91m' #93
  FAIL = '\033[91m'
  ENDC = '\033[0m'
  BOLD = '\033[1m'
  UNDERLINE = '\033[4m'

def getArguments():
  parser = argparse.ArgumentParser(description='Arguments decription')
  parser.add_argument('-i', '--input', help="raw input csv file", default="")
  parser.add_argument('--available_days', help="by specifying this file and no raw input csv file, program will use information in this file.", default='')
  parser.add_argument('--ideal_fitness', help="program stops when a schedule with fitness >= ideal_fitness is found. Default: 0.95", type=float, default=0.95)
  parser.add_argument('--max_iter', help="program stops after maximum number of iterations even if a ideal schedule is not found. Defualt:1000", type=int, default=1000)
 #parser.add_argument('-o', '--output_dir', help="output directory", default="")

  args = parser.parse_args()
  return args

def ParseTimeSlots(timeslots):
  if not timeslots:
    return [0]*31
  elif timeslots == "All":
    return [1]*31
  timeslot_list = timeslots.split(';')
  result=[0] * 31
  for slot in timeslot_list:
    eles = slot.split()
    Date = eles[0]
    eles = Date.split('.')
    Day = int(eles[1])
    result[Day-1] = 1
  return result

def ExtractAvailableTime(fileName):
  table = []
  with open(fileName, 'rU') as fin:
    reader = csv.reader(fin)
    next(reader)
    print reader
    for row in reader:
      if not row:
        continue
      contact=row[1].strip()
      name=row[2].strip().upper().replace('"', '').replace("'", "").replace(",",'')
      timeslots=row[3].strip()
      if not name:
        if not contact:
          print bcolors.WARNING, "Warning: a record without name and contact is detected! Removed to continue!", bcolors.ENDC
        else:
          print bcolors.WARNING, "Warning: a record without name is detected! Removed to continue!", bcolors.ENDC
      else:
        record = [name]
        record += ParseTimeSlots(timeslots)
        table.append(record)
  return table

def removeDuplicate(table):
  table = sorted(table, key=lambda x: x[0])
  end = len(table)-1
  x=0
  while x < end:
    if table[x][0] == table[x+1][0]:
      del table[x]
      end -= 1
    else:
      x += 1
  return table

def list_find(list, ele):
  for x in list:
    if x==ele:
      return True
  return False

#schedule is an array
class Schedule:
  def __init__(self, schedule, fitness):
    self.schedule = schedule
    self.fitness = fitness
  def __eq__(self, other):
    if isinstance(other, Schedule):
      if other.fitness == self.fitness:
        if other.schedule == self.schedule:
          return True
    return False

class Schedule_GA:
  def __init__(self, table, NumberOfDays):
    self.NumberOfDays = NumberOfDays
    self.helper_num = len(table)
    self.available_helpers = get_available_helpers(table, NumberOfDays)
    self.population_size = 30
  def initialize(self):
    self.population = []
    for x in range(0, self.population_size):
      schedule = [''] * self.NumberOfDays
      for day in range(0, self.NumberOfDays):
        schedule[day] = random.choice(self.available_helpers[day])
      schedule_obj = Schedule(schedule, fitness(schedule, self.helper_num))
      if not list_find(self.population, schedule_obj):
        self.population.append(schedule_obj)

#Every day has p to randomly mutate
#Every junction (a,b) has p1 for (a mutating to b) | (b mutating to a) with equal probability if the mutation is valid
  def mutate(self):
    ave_work_day = self.NumberOfDays/self.helper_num
    p = 0.2
    p1 = 0.3
    for x in range(0, min(len(self.population), self.population_size)):
      schedule = copy.deepcopy(self.population[x].schedule)
      for day in range(0, self.NumberOfDays):
        helper2days = Counter(schedule)
        if day < self.NumberOfDays-1 and schedule[day] != schedule[day+1]:
          if random.random() <= p:
            if random.random() < 0.5:
              schedule[day] = random.choice(self.available_helpers[day])
            else:
              schedule[day+1] = random.choice(self.available_helpers[day+1])
            continue
          if random.random()<=p1:
            if helper2days[schedule[day]] > ave_work_day+1:
              if helper2days[schedule[day+1]] <= ave_work_day and list_find(self.available_helpers[day], schedule[day+1]):
                schedule[day] = schedule[day+1]
              else:
                schedule[day] = random.choice(self.available_helpers[day])
            elif helper2days[schedule[day+1]] > ave_work_day+1:
              if helper2days[schedule[day]] <= ave_work_day and list_find(self.available_helpers[day+1], schedule[day]):
                schedule[day+1] = schedule[day]
              else:
                schedule[day+1] = random.choice(self.available_helpers[day+1])
            else:
              if random.random() <= p:
                if random.random() < 0.5:
                  schedule[day] = random.choice(self.available_helpers[day])
                else:
                  schedule[day+1] = random.choice(self.available_helpers[day+1])
      schedule_obj = Schedule(schedule, fitness(schedule, self.helper_num))
      if not list_find(self.population, schedule_obj):
        self.population.append(schedule_obj)
  def crossover(self):
    mid_point = self.NumberOfDays/2
    for x in range(0, min(len(self.population)-1, self.population_size-1)):
      for y in range(x+1, self.population_size):
        schedule = self.population[x].schedule[:mid_point]+self.population[y].schedule[mid_point:]
        schedule_obj = Schedule(schedule, fitness(schedule, self.helper_num))
        if not list_find(self.population, schedule_obj):
          self.population.append(schedule_obj)
        schedule = self.population[y].schedule[:mid_point]+self.population[x].schedule[mid_point:]
        schedule_obj = Schedule(schedule, fitness(schedule, self.helper_num))
        if not list_find(self.population, schedule_obj):
          self.population.append(schedule_obj)
  def crossover_inner(self):
    ave_work_day = self.NumberOfDays/self.helper_num
    for x in range(0, min(self.population_size, len(self.population))):
      schedule = copy.deepcopy(self.population[x].schedule)
      for day in range(1, self.NumberOfDays-1):
        helper2days = Counter(schedule)
        if schedule[day-1]!=schedule[day] and schedule[day]!=schedule[day+1]:
          if helper2days[schedule[day]] < ave_work_day:
            if list_find(self.available_helpers[day-1], schedule[day]):
              schedule[day-1] = schedule[day]
            elif list_find(self.available_helpers[day+1], schedule[day]):
              schedule[day+1] = schedule[day]
            elif random.random() < 0.1:
              schedule[day] == random.choice(self.available_helpers[day])
          else:
            if list_find(self.available_helpers[day], schedule[day-1]):
              schedule[day] = schedule[day-1]
            elif list_find(self.available_helpers[day], schedule[day+1]):
              schedule[day] = schedule[day+1]
            elif random.random() < 0.1:
              schedule[day] == random.choice(self.available_helpers[day])

      schedule_obj = Schedule(schedule, fitness(schedule, self.helper_num))
      if not list_find(self.population, schedule_obj):
        self.population.append(schedule_obj)
  def select(self):
    #print "select silenced."
    self.population.sort(key=lambda x: x.fitness, reverse=True)
    if len(self.population) > self.population_size:
      self.population = self.population[:self.population_size]
  def run(self, max_iter, ideal_fitness):
    self.initialize()
    while max_iter:
      max_iter -= 1
      self.mutate()
      self.crossover_inner()
      self.crossover()
      self.select()
      if self.population[0].fitness >= ideal_fitness:
        break

#maximum fitness 1
def fitness(schedule, helper_num):
  day_num = len(schedule)

  #number of helper involved
  helperInvolve = len(set(schedule))
  #number of breakpoints in schedule
  #breaks = {name : 0 for name in set(schedule)}
  #breaks[schedule[0]] += 1
  #for idx in range(0, day_num-1):
  #   if schedule[idx] != schedule[idx+1]:
  #     breaks[schedule[idx+1]] += 1
  breakpoints = 0
  for idx in range(0, day_num-1):
    if schedule[idx] != schedule[idx+1]:
      breakpoints += 1
  #days scheduled for each helper
  workDays = Counter(schedule)
  ave_work_day = 1.0*day_num/helper_num
  std_dev_work_day = 0.0
  for x in workDays.values():
    std_dev_work_day += (ave_work_day-x)*(ave_work_day-x)
  std_dev_work_day = math.sqrt(std_dev_work_day)

  extra_work_day_helper = day_num%helper_num
  #print extra_work_day_helper, " ", ave_work_day
  ex_std_dev = (helper_num-extra_work_day_helper)*((ave_work_day-day_num/helper_num)**2)+ extra_work_day_helper*((ave_work_day-day_num/helper_num)**2)
  #print ex_std_dev
  ex_std_dev = math.sqrt(ex_std_dev)
  #rint ",".join(schedule)
  #print 1.0*helperInvolve/helper_num, ":", 1.0*(helperInvolve-1)/breakpoints, ":", ex_std_dev/std_dev_work_day
  #if (1.0*helperInvolve/helper_num + 1.0*(helperInvolve-1)/breakpoints + ex_std_dev/std_dev_work_day)/3 > 0.93:
  #  print helperInvolve, " ", helper_num, " ", breakpoints, " ", ex_std_dev, ' ', std_dev_work_day
  #  print ",".join(schedule)
  #  print (1.0*helperInvolve/helper_num + 1.0*(helperInvolve-1)/breakpoints + ex_std_dev/std_dev_work_day)/3
  #  sys.exit()
  return (1.0*helperInvolve/helper_num + 1.0*(helperInvolve-1)/breakpoints + ex_std_dev/std_dev_work_day)/3

def get_available_helpers(table, NumberOfDays):
  helper_num = len(table)
  available_helpers = []
  for day in range(1, NumberOfDays+1):
    tmp = []
    for helper_idx in range(0, helper_num):
      if table[helper_idx][day]==1:
        tmp.append(table[helper_idx][0])
    if not len(tmp):
      tmp=['Idle']
    available_helpers.append(tmp)
  return available_helpers

def schedule_bruteFroce(table, NumberOfDays):
  helper_num = len(table)
  schedule = ['']*NumberOfDays
  schedule_searchPoint = [0] * NumberOfDays
  #initialize schedule
  for day in range(0, NumberOfDays):
    flag1=False
    for helper_idx in range(0, helper_num):
      if table[helper_idx][day+1] == 1:
        schedule[day] = table[helper_idx][0]
        schedule_searchPoint[day]=helper_idx
        flag1=True
        break
    if not flag1:
      schedule[day] = "Idle"
      schedule_searchPoint[day]=helper_num

  max_fitness = 0
  tmp_counter = 0
  while True:
    tmp_counter += 1
    fit = fitness(schedule, helper_num)
    if fit>max_fitness:
      max_fitness = fit
      best_schedule = schedule
      print max_fitness
      print ",".join(best_schedule)

    #get next schedule
    flag=False
    for day in range(NumberOfDays, 0, -1):
      for helper_idx in range(schedule_searchPoint[day-1]+1, helper_num):
        if table[helper_idx][day]==1:
          schedule[day-1] = table[helper_idx][0]
          schedule_searchPoint[day-1] = helper_idx
          flag = True
          break
      if flag:
        for idx in range(day+1, NumberOfDays+1):
          flag1=False
          for helper_idx in range(0, helper_num):
            if table[helper_idx][idx] == 1:
              schedule[idx-1] = table[helper_idx][0]
              schedule_searchPoint[idx-1]=helper_idx
              flag1=True
              break
          if not flag1:
            schedule[idx-1] = "Idle"
            schedule_searchPoint[idx-1]=helper_num
        break
    #if tmp_counter % 1000 == 0:
    #  print tmp_counter
    #  print ",".join([str(x) for x in schedule_searchPoint])
    if not flag:
      break
  print "Brute force: best schedule with fitness ", max_fitness, " is found."
  print tmp_counter
  return best_schedule

random.seed(time.time())
args = getArguments()

if args.input:
  idx = args.input.rfind('.')
  output_prefix = args.input[:idx+1]
  table = ExtractAvailableTime(args.input)
  table = removeDuplicate(table)
elif args.available_days:
  idx = args.available_days.rfind('.')
  idx = args.available_days.rfind('.', 0, idx-1)
  output_prefix = args.available_days[:idx+1]
  with open(args.available_days, 'rb') as f:
    reader = csv.reader(f)
    table = list(reader)
    del table[0]
    for row in table:
      for col in range(1, len(row)):
        row[col] = int(row[col])
else:
  print bcolors.WARNING, "Error: either input or available_days should be specified!", bcolors.ENDC
  sys.exit(0)

idx=output_prefix.rfind('/')
Date = output_prefix[idx+1:]
idx=Date.rfind('.')
if idx != -1:
  Date=Date[:idx]
idx=Date.find("-")
year=int(Date[:idx])
month=int(Date[idx+1:])
NumberOfDays = monthrange(year, month)[1]

if args.input:
  for idx in range(0, len(table)):
    table[idx] = table[idx][:(NumberOfDays+2)]

  print bcolors.OKBLUE, "Logging available days of each helper into '"+output_prefix+"available_days.txt'....", bcolors.ENDC
  with open(output_prefix + "available_days.csv", 'w') as fout:
    fout.write(","+",".join(map(str, [x for x in range(1, NumberOfDays+1)]))+"\n")
    for row in table:
      fout.write(",".join(map(str, row))+"\n")

helper_num = len(table)
ave_work_day = 1.0*NumberOfDays/helper_num
extra_work_day_helper = NumberOfDays%helper_num

#sort the helper in ascending order of total available days
for idx in range(0, len(table)):
  total = sum(table[idx][1:])
  table[idx].append(total)
table = sorted(table, key=lambda x: x[-1])

#Number of helpers available in each day
Date2freeHepler=[[x,0] for x in range(1, NumberOfDays+1)]
for row in table:
  for day in range(1, NumberOfDays+1):
    if row[day]==1:
      Date2freeHepler[day-1][1] += 1
Date2freeHepler = sorted(Date2freeHepler, key=lambda x: x[-1])

print bcolors.OKBLUE, "Logging available helpers each day into '"+output_prefix+"available_helper_each_day.txt'....", bcolors.ENDC
with open(output_prefix + "available_helper_each_day.csv", 'w') as fout:
  fout.write("Day,NumberOfAvailableHelper\n")
  for row in Date2freeHepler:
    fout.write(str(row[0])+","+ str(row[1])+"\n")

solution_tmp = [""] * (NumberOfDays+1)
#print bcolors.WARNING, bcolors.ENDC
if(Date2freeHepler[0][1]==0):
  str_tmp = ""
  for row in Date2freeHepler:
    if row[1]==0:
      str_tmp = str_tmp + " " + str(row[0])
      solution_tmp[row[0]] ='Idle'
  print bcolors.WARNING, "No helper available in"+str_tmp+"!", bcolors.ENDC

#schedule = schedule_bruteFroce(table, NumberOfDays)
scheduler = Schedule_GA(table, NumberOfDays)
scheduler.run(args.max_iter, args.ideal_fitness)

print "Top 5 schedules founded by program:"
for x in range(0, min(5, len(scheduler.population))):
  print "*****",x+1,"*****"
  schedule = scheduler.population[x].schedule
  print "fitness",scheduler.population[x].fitness
  print ",".join(scheduler.population[x].schedule)

with open(output_prefix+"schedule.csv", 'w') as fout:
  fout.write("Day,Helper\n")
  for day in range(0, NumberOfDays):
    fout.write(str(day+1)+","+schedule[day]+"\n")

sys.exit(0)
#start a brute force search
