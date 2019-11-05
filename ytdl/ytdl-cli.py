#
# Download youtube videos from a list of urls.
# Hao Wu, micw.mm@gmail.com
# Last modified: 08/22/2016
#
# Refs:
#   - Usage of youtube-dl: https://rg3.github.io/youtube-dl/
#   - Parse url: http://stackoverflow.com/questions/11600681/parse-query-part-from-url
#   - List all files in a certain type: http://stackoverflow.com/questions/3964681/find-all-files-in-directory-with-extension-txt-in-python
#   - Split file name into name and extension: http://stackoverflow.com/questions/541390/extracting-extension-from-filename-in-python
#   - Convert webm to mp4: http://askubuntu.com/questions/323944/convert-webm-to-other-formats
#

import os
import sys
import glob
import urlparse
import subprocess

#

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

#

def exec_cmd(cmd):
    """Execute a shell command and return its output.
    """
    p = subprocess.Popen( \
            cmd, \
            stdin=subprocess.PIPE, \
            stdout=subprocess.PIPE, \
            stderr=subprocess.PIPE, \
            shell=True)
    [output, error] = p.communicate()
    return output

#
# Enumerate all urls and download
#

fin = open("youtube.txt", "r")
k = 0
for line in fin:
  line = line.strip()
  if line == "":
    continue
  k += 1
  if line[0] == "#":
    continue
  for i in range(0, 5): # try at most 5 times on failure
    try:
      q = urlparse.parse_qs(urlparse.urlparse(line).query)
      arg_playlistitems = ""
      if "index" in q:
        arg_playlistitems = "--playlist-items %s" % ",".join(q["index"])
      #print
      #print q
      print bcolors.OKGREEN + "%d: %s" % (k, line) + bcolors.ENDC
      cmd_list = "youtube-dl -F %s \"%s\"" % (arg_playlistitems, line)
      print "  List All: " + cmd_list
      res_list = exec_cmd(cmd_list)
      best = False
      for line_res_list in res_list.split("\n"):
        fields = line_res_list.strip().split()
        if fields[-1] == "(best)":
          best = True
          cmd_download = "youtube-dl --max-filesize 100m -f %s %s \"%s\"" % (fields[0], arg_playlistitems, line)
          print "  Download: " + cmd_download
          os.system(cmd_download)
          break
      if best == False:
        print "  " + bcolors.WARNING + "No 'best' video available. Skipped." + bcolors.ENDC
      break
    except Exception,e:
        print "  " + bcolors.FAIL + "Failed." + bcolors.ENDC
        print e

#
# Convert webm files to mp4
#

for f in glob.glob("*.webm"):
  filename, fileext = os.path.splitext(f)
  cmd_convert = "ffmpeg -i '%s' -qscale 0 '%s.mp4'" % (f, filename)
  os.system(cmd_convert)

#
##
#

