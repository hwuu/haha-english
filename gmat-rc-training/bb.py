#!/usr/bin/python
# -*- coding: utf-8 -*-

#
# Brain Booster
#
# Hao - micw.mm@gmail.com
# Created: 02/27/2017, modified: 03/03/2017
#

import os
import re
import sys
import flask
import datetime

#
##
#

_app = flask.Flask(__name__)
_elements = []

#
##
#

@_app.route('/')
def handle_root():
  return flask.render_template("index.html")

#
##
#

@_app.route('/get')
def handle_get_request():
  """ Handle a 'get' request.
  """
  global _elements
  #
  t = datetime.datetime.now()
  ts = t.strftime("%Y-%m-%d")
  filename_new = "./daily/%s.txt" % ts
  if not os.path.exists(filename_new):
    os.system("python ./bb_cli.py get %s" % filename_new)
  #
  f = None
  finished = False
  filename_finished = "./daily/%s_finished.txt" % ts
  #
  if os.path.exists(filename_finished):
    f = open(filename_finished, "r")
    finished = True
  else:
    f = open(filename_new, "r")
  #
  _elements = []
  current_element = {}
  for line in f:
    line = line.strip()
    if line == "" or line.startswith("#"):
      continue
    if line.startswith("I like it (y/N):"):
      action = 0
      action_string = re.findall(r":(.*)", line)[0].strip().lower()
      if action_string == "y":
        action = 1
      current_element["like"] = False if action == 0 else True
      _elements.append(current_element)
      current_element = {}
    current_element["text"] = line
  #
  return flask.jsonify({"finished": finished, "date": ts, "elements": _elements})

#
##
#

@_app.route('/log')
def handle_log_request():
  """ Handle a 'log' request.
  """
  global _elements
  #
  q = flask.request.args.get("checkedIds", "", type=str)
  checkedIds = set()
  for x in q.split(","):
    checkedIds.add(int(x))
  #
  t = datetime.datetime.now()
  ts = t.strftime("%Y-%m-%d")
  filename = "./daily/%s_finished.txt" % ts
  if os.path.exists(filename):
    return flask.jsonify({"status": 1}) # 1 means error.
  f = open(filename, "w+")
  f.write("#\n")
  f.write("# " + str(datetime.datetime.now()) + "\n")
  f.write("#\n")
  f.write("\n")
  for i in range(0, len(_elements)):
    _elements[i]["like"] = (i in checkedIds)
    f.write("#\n# %d.\n#\n\n%s\n\nI like it (y/N):%s\n\n" \
        % (i + 1, _elements[i]["text"], "y" if _elements[i]["like"] else ""))
  f.close()
  os.system("python ./bb_cli.py log %s" % filename)
  return flask.jsonify({"status": 0}) # 0 means successful.

#
##
#

if __name__ == '__main__':
  """ Start the web service.
  """
  _app.run(host='0.0.0.0', port=5000, threaded=True, debug=True)

#
##
###
##
#


