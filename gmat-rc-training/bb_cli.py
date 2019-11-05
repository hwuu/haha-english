# -*- coding: utf-8 -*-
#!/usr/bin/python

#
# Brain Booster
#
# Hao - micw.mm@gmail.com
# Created: 02/27/2017, modified: 03/03/2017
#

import os
import re
import sys
import math
import random
import argparse
import datetime
import operator
import jsonpickle

#
##
#

def parse_args():
  #
  parser = argparse.ArgumentParser()
  #
  # Add subparsers to parser
  #
  subparsers = parser.add_subparsers(
      dest="command", help="commands")
  #
  # 1. Add parsers to subparsers
  #
  parser_init = subparsers.add_parser(
      "init", help="Initialize database.")
  parser_add = subparsers.add_parser(
      "add", help="Add new elements.")
  parser_get = subparsers.add_parser(
      "get", help="Get today's top-k elements.")
  parser_log = subparsers.add_parser(
      "log", help="Log the viewing actions of elements.")
  parser_sim1 = subparsers.add_parser(
      "sim1", help="Run simulation 1.")
  parser_sim2 = subparsers.add_parser(
      "sim2", help="Run simulation 2.")
  #
  # Add arguments for parser_add
  #
  parser_add.add_argument(
      "filename", help="input filename")
  #
  # Add arguments for parser_get
  #
  parser_get.add_argument(
      "filename", help="output filename")
  parser_get.add_argument(
      "--number-of-elements", default=10, help="number of least-durable elements")
  parser_get.add_argument(
      "--score-threshold", default=0.1, help="all elements whose durability is below this threshold should be returned")
  #
  # Add arguments for parser_log
  #
  parser_log.add_argument(
      "filename", help="input filename")
  #
  # Done
  #
  return vars(parser.parse_args())

#
##
#

def init_database(args):
  """ Initialize database file with an empty dictionary of elements. Prompt error if the file exists.
  """
  if (os.path.exists("bb.json")):
    print "[ERROR] File exists. Please use another location."
  else:
    data = {}
    try:
      f = open("bb.json", "wb+")
      f.write(jsonpickle.encode(data))
      f.close()
      print "Database initialized."
    except:
      print "[ERROR] Saving data failed."

#
##
#

def add_new_elements(args):
  """ Add new elements from a file to the database. Each element that has a conflicting signature with an existing element will be ignored.
  """
  data = {}
  try:
    f = open("bb.json", "rb")
    data = jsonpickle.decode(f.read())
    f.close()
  except:
    print "[ERROR] Loading data failed."
    return
  k = 0
  n = 0
  for line in open(args["filename"], "r"):
    line = line.strip()
    if line == "" or line.startswith("#"):
      continue
    n += 1
    sig = f_signature(line)
    if sig in data:
      print "[WARNING] Signature confilict: '" + sig + "'. Element ignored."
      continue
    k += 1
    elem = {}
    elem["id"] = sig
    elem["text"] = line
    elem["log"] = []
    data[sig] = elem
  try:
    f = open("bb.json", "wb")
    f.write(jsonpickle.encode(data))
    f.close()
    print "%d of %d element(s) added." % (k, n)
  except:
    print "[ERROR] Saving data failed."

#
##
#

def get_top_elements(args):
  """ Get top elements and output to a file.
  """
  data = {}
  try:
    f = open("bb.json", "rb")
    data = jsonpickle.decode(f.read())
    f.close()
  except:
    print "[ERROR] Loading data failed."
    return
  P = pop(data)
  try:
    f = open(args["filename"], "w+")
    f.write("#\n")
    f.write("# " + str(datetime.datetime.now()) + "\n")
    f.write("#\n")
    f.write("\n")
    n = 0
    for sig in P:
      n += 1
      f.write("#\n# %d. %s (%d)\n#\n\n%s\n\nI like it (y/N):\n\n" \
          % (n, sig.encode('utf-8'), len(data[sig]["log"]), data[sig]["text"].encode('utf-8')))
    f.close()
    print "%d elements popped." % n
  except IOError, e:
    print e
    print "[ERROR] Saving top elements failed."

#
##
#

def log_processed_elements(args):
  """ Log processed elements into the database.
  """
  data = {}
  try:
    f = open("bb.json", "rb")
    data = jsonpickle.decode(f.read())
    f.close()
  except:
    print "[ERROR] Loading data failed."
    return
  k = 0
  n = 0
  current_element = {"sig": "", "log": {}}
  for line in open(args["filename"], "r"):
    line = line.strip()
    if line == "" or line.startswith("#"):
      continue
    if current_element["sig"] != "" and line.startswith("I like it (y/N):"):
      n += 1
      action = 0
      action_string = re.findall(r":(.*)", line)[0].strip().lower()
      if action_string == "y":
        action = 1
      current_element["log"]["datetime"] = datetime.datetime.now()
      current_element["log"]["action"] = action
      data[current_element["sig"]]["log"].append(current_element["log"])
      current_element = {"sig": "", "log": {}}
    else:
      sig = f_signature(line)
      if sig not in data:
        print "[WARNING] Signature not found: " + sig + "."
        continue
      k += 1
      current_element["sig"] = sig
  try:
    f = open("bb.json", "wb")
    f.write(jsonpickle.encode(data))
    f.close()
    print "%d of %d element(s) logged." % (k, n)
  except:
    print "[ERROR] Saving data failed."

#
##
#

def sim1():
  """ Simulation 1: In which day an element will be popped.
  """
  t_logged = 0
  n_logged = 0
  t = 0
  while n_logged < 10:
    t += 1
    if n_logged == 0:
      t_logged = t
      n_logged += 1
      #print "%2d: Day %d" % (n_logged, t_logged)
      print "%d\t%f" % (t, f_score(0, n_logged))
      continue
    score = f_score(t - t_logged, n_logged)
    if score <= 3:
      t_logged = t
      n_logged += 1
      #print "%2d: Day %d" % (n_logged, t_logged)
    print "%d\t%f" % (t, f_score(t - t_logged, n_logged))

#
##
#

def sim2():
  """ Simulation 2.
  """
  N = 200 # Total number of elements to remember.
  K = 10  # Maximum number of processable elements per day.
  L_min = 1   # Minimum number of new elements per day.
  L_max = 3   # Maximum number of new elements per day.
  C = 2   # Critical level of element score.
  F = 0.1 # Daily forgetting ratio.
  #
  # Init data.
  #
  data = {}
  for i in range(0, N):
    element = {}
    sig = "%d" % (i + 1)
    element["id"] = sig
    element["log"] = []
    data[sig] = element
  #
  # Start the simulation
  #
  t = datetime.datetime.now()
  while True:
    t += datetime.timedelta(days=1)
    #
    # Get the signatures of top elements
    #
    P = pop(data, K, L_min, L_max, C, t)
    #
    # Log these elements on the same day
    #
    for sig in P:
      log_item = {}
      log_item["datetime"] = t
      log_item["action"] = 1 if random.uniform(0, 1) < F else 0
      data[sig]["log"].append(log_item)
    #
    # Print today's workload
    #
    print "\nDay %d: %d elements processed" \
        % ((t - datetime.datetime.now()).days, len(P))
    #
    # Print statistics
    #
    min_log_length = 10000
    min_log_age = 10000
    min_score = 10000
    max_log_length = 0
    max_log_age = 0
    max_score = 0
    sum_log_length = 0
    sum_log_age = 0
    sum_score = 0
    n = 0
    for sig, element in data.iteritems():
      log_length = len(element["log"])
      if log_length == 0:
        continue
      n += 1
      log_age = (t - element["log"][-1]["datetime"]).days
      score = f_score(log_age, log_length)
      if min_log_length > log_length:
        min_log_length = log_length
      if min_log_age > log_age:
        min_log_age = log_age
      if min_score > score:
        min_score = score
      if max_log_length < log_length:
        max_log_length = log_length
      if max_log_age < log_age:
        max_log_age = log_age
      if max_score < score:
        max_score = score
      sum_log_length += log_length
      sum_log_age += log_age
      sum_score += score
    if n > 0:
      """
      print "%d\t%d\t%f" % ( \
          (t - datetime.datetime.now()).days,
          n,
          sum_score / 30
      )
      """
      print "  # of touched elements:", n
      print "  log len: min = %3d, max = %3d, avg = %3.2f" \
          % (min_log_length, max_log_length, float(sum_log_length) / n)
      print "  log age: min = %3d, max = %3d, avg = %3.2f" \
          % (min_log_age, max_log_age, float(sum_log_age) / n)
      print "  score  : min = %3.2f, max = %3.2f, avg = %3.2f" \
          % (min_score, max_score, sum_score / n)
    #
    # If every element has a score larger than 10, then exit.
    #
    if n == N and min_score >= 30:
      break
  """
  x = 1
  n = 100
  print f_clarity(x, n)
  print f_stability(x, n)
  print f_durability(n)
  print f_score(x, n)
  """

#
##
#

def pop(data, K=10, L_min=1, L_max=3, C=2, t=datetime.datetime.now()):
  """ Pop the signatures of the top elements in data.
      data:  Dictionary of all data.
      K:     Number of elements to be selected daily.
      L_min: Minimum number of new elements to be selected daily.
      L_max: Maximum number of new elements to be selected daily.
      C:     Critical level of element score.
      t:     Current date time.
  """
  assert 0 <= L_min and L_min <= L_max and L_max <= K
  #
  # Init result lists:
  #   - T_sel: List of signatures of selected touched elements sorted by score.
  #   - U_sel: List of signatures of selected untouched elements.
  #
  T_sel = []
  U_sel = []
  #
  # Calculate scores and populate T_all and U_all.
  #   - T_all: List of signatures of all touched elements sorted by score.
  #   - U_all: List of signatures of all untouched elements.
  #   - S:     Dictionary of (sig -> score).
  #
  T_all = []
  U_all = []
  S = {}
  for sig, element in data.iteritems():
    score = 0
    log_length = len(element["log"])
    if log_length == 0:
      U_all.append(sig)
    else:
      t0 = datetime.datetime(1970, 1, 1)
      d1 = (element["log"][-1]["datetime"] - t0).days
      d2 = (t - t0).days
      d = d2 - d1
      n = 0
      for x in element["log"]:
        if x["action"] == 0: # Marked 'N' for 'I like it'.
          n += 1
        elif x["action"] == 1: # Marked 'Y' for 'I like it'.
          n -= 0 # The more you like an element, the more probable it will be popped in the future.
      if n < 1:
        n = 1
      S[element["id"]] = f_score(d, n)
  T_all = sorted(S.keys(), key=operator.itemgetter(1))
  random.shuffle(U_all)
  #
  # Selection step 1/5: Put the signatures of L_min untouched elements into U_sel.
  #
  for sig in U_all:
    if len(U_sel) == L_min:
      break
    if sig not in U_sel:
      U_sel.append(sig)
      print "Step 1/5 - Added into U_sel:", sig
  #
  # Selection step 2/5: Get top touched elements and store thier signatures into T_sel.
  #
  for sig in T_all:
    if len(T_sel) + len(U_sel) == K or S[sig] > C:
      break
    if sig not in T_sel:
      T_sel.append(sig)
      print "Step 2/5 - Added into T_sel:", sig
  #
  # Selection step 3/5: If there are not enough elements selected so far, add untouched elements. (This case happens when almost all already-selected elements have been well remembered.)
  #
  for sig in U_all:
    if len(T_sel) + len(U_sel) == K or len(U_sel) == L_max:
      break
    if sig not in U_sel:
      U_sel.append(sig)
      print "Step 3/5 - Added into U_sel:", sig
  #
  # Selection step 4/5: If there are still not enough elements selected so far, add touched elements with less constrain. (This case happens when almost all exisiting elements have been processed and well remembered.)
  #
  for sig in T_all:
    if len(T_sel) + len(U_sel) == K:
      break
    if sig not in T_sel:
      T_sel.append(sig)
      print "Step 4/5 - Added into T_sel:", sig
  #
  # Selection step 5/5: If there are still not enough elements selected, add untouched elements with less constrain. (Cold start.)
  #
  for sig in U_all:
    if len(T_sel) + len(U_sel) == K:
      break
    if sig not in U_sel:
      U_sel.append(sig)
      print "Step 5/5 - Added into U_sel:", sig
  #
  # Done.
  #
  random.shuffle(T_sel)
  result = T_sel + U_sel
  return result

#
##
#

_stop_words = set("a,able,about,across,after,all,almost,also,am,among,an,and,any,are,as,at,be,because,been,but,by,can,cannot,could,dear,did,do,does,either,else,ever,every,for,from,get,got,had,has,have,he,her,hers,him,his,how,however,i,if,in,into,is,it,its,just,least,let,like,likely,may,me,might,most,must,my,neither,no,nor,not,of,off,often,on,only,or,other,our,own,rather,said,say,says,she,should,since,so,some,than,that,the,their,them,then,there,these,they,this,tis,to,too,twas,us,wants,was,we,were,what,when,where,which,while,who,whom,why,will,with,would,yet,you,your,unlike".split(","))

#
##
#

def f_signature(s):
  """ Get the signature of a string.
      Step 1. Remove heading and tailing spaces.
      Step 2. Convert all letters to lowercases.
      Step 3. Remove all stop words.
      Step 4. Remove all non-alphabic characters.
  """
  s = s.strip().lower()
  words = []
  for x in re.split("[^a-zA-Z]", s):
    if x != "" and len(x) > 1 and x not in _stop_words:
      words.append(x)
  sig = words[0]
  for i in range(1, min(3, len(words))):
    sig += words[i][0]
  if len(words) > 1:
    sig += str(len(words))
  return sig

#
##
#

def f_clarity(x, n):
  """ Clarity := e^(-x/n)
  """
  assert x >= 0 and n >= 1
  return math.exp(-1.0 * x / n)

#
##
#

def f_stability(x, n):
  """ Stability := diff(f_clarity(x, n)) = -e^(-x/n)/n
  """
  assert x >= 0 and n >= 1
  return -math.exp(-1.0 * x / n) / n

#
##
#

def f_durability(n):
  """ Durability := (max value of x s.t. f_clarity > 0.05) = -n * ln(0.05)
  """
  assert n >= 1
  return -1.0 * n * math.log(0.05)

#
##
#

def f_score(x, n):
  """ Score := max(0, durability - x)
  """
  assert x >= 0 and n >= 1
  return max(0, f_durability(n) - x)

#
##
#

if __name__ == "__main__":
  #
  args = parse_args()
  if args["command"] == "init":
    init_database(args)
  if args["command"] == "add":
    add_new_elements(args)
  elif args["command"] == "get":
    get_top_elements(args)
  elif args["command"] == "log":
    log_processed_elements(args)
  elif args["command"] == "sim1":
    sim1()
  elif args["command"] == "sim2":
    sim2()

#
##
###
##
#
#
##
###
##
#
#
##
###
##
#

