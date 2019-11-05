# -*- coding: utf-8 -*-

import os
import sys
import yaml
import hashlib

#

spec_file_path = sys.argv[1]
input_dir = os.path.dirname(spec_file_path)
tmp_dir = "_tmp"

cmdseq = []
parts = []

#

with open(spec_file_path, "r", encoding="utf-8") as f_in:
    spec = yaml.load(f_in, Loader=yaml.SafeLoader)

#

for x in spec["sequence"]:
    print(x)
    cmd_prefix = ""
    if "fileName" in x:
        input_file_path = os.path.join(input_dir, x["fileName"])
        begin = "" if "begin" not in x else " -ss %s" % x["begin"]
        end = "" if "end" not in x else " -to %s" % x["end"]
        cmd_prefix = "ffmpeg -y -i \"%s\"%s%s" % (input_file_path, begin, end)
        ext = os.path.splitext(input_file_path)[1].lower()
        if ext == ".m4a":
            cmd_prefix += " -codec:v copy -codec:a libmp3lame -q:a 4"
        elif ext == ".mp3":
            cmd_prefix += " -acodec copy"
    elif "silenceInSeconds" in x:
        cmd_prefix = "ffmpeg -y -f lavfi -i anullsrc=channel_layout=5.1:sample_rate=48000 -t %d" % x["silenceInSeconds"]
    cmd_sig = hashlib.md5(cmd_prefix.encode('utf-8')).hexdigest()
    output_file_path = os.path.join(tmp_dir, cmd_sig + ".mp3")
    cmd = "%s \"%s\"" % (cmd_prefix, output_file_path)
    cmdseq.append({
        "cmd": cmd,
        "cmd_sig": cmd_sig,
        "output_file_path": output_file_path
    })

#

if not os.path.isdir(tmp_dir):
    os.mkdirs(tmp_dir)

for x in cmdseq:
    if not os.path.isfile(os.path.join(tmp_dir, x["cmd_sig"] + ".mp3")):
        print(x["cmd"])
        os.system(x["cmd"])

#

parts = []
for x in cmdseq:
    parts.append(x["output_file_path"])

print(parts)

cmd = "ffmpeg -y -i \"concat:%s\" -codec:a libmp3lame -q:a 4 %s" \
    % ("|".join(parts), spec["name"] + ".mp3")
print(cmd)
os.system(cmd)

#
# (END)

