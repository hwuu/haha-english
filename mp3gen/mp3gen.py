# -*- coding: utf-8 -*-

import os
import yaml
import hashlib

#

input_dir = "origin"
tmp_dir = "_tmp"

cmdseq = []
parts = []

#

with open(os.path.join(input_dir, "spec.yaml"), "r", encoding="utf-8") as f_in:
    spec = yaml.load(f_in, Loader=yaml.SafeLoader)

#

for x in spec["sequence"]:
    if "fileName" in x:
        file_path = os.path.join(input_dir, x["fileName"])
        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".m4a":
            cmd_prefix = "ffmpeg -y -i \"%s\" -codec:v copy -codec:a libmp3lame -q:a 4" % file_path
            cmd_sig = hashlib.md5(cmd_prefix.encode('utf-8')).hexdigest()
            file_path = os.path.join(tmp_dir, cmd_sig + ".mp3")
            cmd = "%s \"%s\"" % (cmd_prefix, file_path)
            cmdseq.append({
                "cmd_sig": cmd_sig,
                "cmd": cmd,
                "excluded": True
            })
        begin = "" if "begin" not in x else " -ss %s" % x["begin"]
        end = "" if "end" not in x else " -to %s" % x["end"]
        cmd_prefix = "ffmpeg -y -i \"%s\"%s%s -acodec copy" % (file_path, begin, end)
        cmd_sig = hashlib.md5(cmd_prefix.encode('utf-8')).hexdigest()
        file_path = os.path.join(tmp_dir, cmd_sig + ".mp3")
        cmd = "%s \"%s\"" % (cmd_prefix, file_path)
        cmdseq.append({
            "cmd_sig": cmd_sig,
            "cmd": cmd
        })
        parts.append(file_path)
    elif "silenceInSeconds" in x:
        cmd_prefix = "ffmpeg -y -f lavfi -i anullsrc=channel_layout=5.1:sample_rate=48000 -t %d" % x["silenceInSeconds"]
        cmd_sig = hashlib.md5(cmd_prefix.encode('utf-8')).hexdigest()
        file_path = os.path.join(tmp_dir, cmd_sig + ".mp3")
        cmd = "%s \"%s\"" % (cmd_prefix, file_path)
        cmdseq.append({
            "cmd_sig": cmd_sig,
            "cmd": cmd
        })
        parts.append(file_path)

#

cmd_prefix = "ffmpeg -y -i \"concat:%s\" -codec:a libmp3lame -q:a 4" % "|".join(parts)
cmd_sig = hashlib.md5(cmd_prefix.encode('utf-8')).hexdigest()
file_path = spec["name"] + ".mp3"
cmd = "%s \"%s\"" % (cmd_prefix, file_path)
cmdseq.append({
    "cmd_sig": cmd_sig,
    "cmd": cmd
})

#

if not os.path.isdir(tmp_dir):
    os.mkdirs(tmp_dir)

for x in cmdseq:
    if not os.path.isfile(os.path.join(tmp_dir, x["cmd_sig"] + ".mp3")):
        print(x["cmd"])
        os.system(x["cmd"])

#
# (END)

