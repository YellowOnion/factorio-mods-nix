#!/usr/bin/env python

import json
import re
import requests
import sys
import os
from packaging import version

mods_api = "https://mods.factorio.com"

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def fetch_mod_json(arg):
    return requests.get(mods_api + "/api/mods{0}".format(arg)).json()


deps_r = re.compile('(?P<type>[~!?])?\s?(?P<name>\w[^<=>]+\w)')

def matchOrNone(x):
    m = deps_r.match(x)
    if m:
        return m.groupdict()
    return None

def _toDeps(ds, c):
    return [ eprint(x) or '{}'.format(toName(x["name"])) for x in
             (matchOrNone(x) for x in ds)
             if x and (x["name"] != "base" and x["name"] != "Any MOD") and c(x)]

def toDeps(ds):
    return _toDeps(ds, lambda x: x["type"] is None or x["type"] == "~")

def toOpDeps(ds):
    return _toDeps(ds, lambda x: x["type"] == "?")

def toName(n):
    return '"{}"'.format(n)
    # we don't need the code below due to using quotes within nix now.
    if n[0].isdigit() or n[0] == "-":
        n = "n" + n
    n = n.replace(" ", "SPC")
    return '"{}"'.format(n)

def load_json_cached(name, version):
    meta = "mods/{}.meta".format(name)
    local_file = "mods/{}.json".format(name)
    if os.path.exists(meta) and open(meta).read() == version and os.path.exists(local_file):
        return json.load(open(local_file))
    else:
        j = fetch_mod_json("/{}/full".format(name))
        json.dump(j, open(local_file, "w"))
        open(meta, "w").write(version)
        return j

if os.path.exists("mods.json"):
    mods = json.load(open("mods.json"))
else:
    mods = fetch_mod_json("?page_size=max")
    json.dump(mods, open("mods.json", "w"))

nmods = len(mods["results"])

sparseModsList = sys.argv[1:]


modsToParse = {}
if sparseModsList != []:
    for mod in sparseModsList:
        modsToParse |= {mod: False}


eprint("getting info for {0} mods".format(nmods))

print("{"                                                      +
      "factorioMod \n"                                                     +
      ", fix \n" +
      ", filterMissing \n" +
      "}: \n"                                                                   +
      " fix (self: {"
       )

BANNED = ["ABSELTN"
          "ABwirefix"]
# while modsToParse == {} or not all(modsToParse.values):
for (i, result) in enumerate(sorted(list(mods["results"]), key=lambda a: a["name"])):
 #       if notnot result["name"] in modsToParse.keys and
 #           continue
 #       else:
        tries = 0
        if result["name"] in BANNED:
            eprint(result["name"] + ": BANNED!")
            break;
        while tries < 5:
            tries += 1
            try:
                full = load_json_cached(result["name"], result["latest_release"]["sha1"])

                name = toName(full["name"])
                percent = float(i * 100) / float(nmods)
                eprint("{0:02.3f}% {1} / {2}".format(percent, i, nmods))
                eprint(name)
                latest_release = max(full["releases"], key = lambda a: version.parse(a["version"]))
                if version.parse(latest_release["info_json"]["factorio_version"]) < version.parse("1.1"):
                    continue
                url = mods_api + latest_release["download_url"]
                file_name = latest_release["file_name"]
                sha1 = latest_release["sha1"]
                deps = toDeps(latest_release["info_json"]["dependencies"])
                deps = " ".join(deps)
                optionalDeps = " ".join(toOpDeps(latest_release["info_json"]["dependencies"]))
                out =  { "name" : name,
                        "version": latest_release["version"],
                        "url" : url,
                        "file_name" : file_name,
                        "deps" : deps,
                        "optionalDeps" : optionalDeps,
                        "sha1": sha1
                        }
                print( \
                    ("{name} = factorioMod {{\n"                    +
                    "  pname = {name}; \n"
                    "  url = \"{url}\";  \n"                    +
                    "  file_name = \"{file_name}\"; \n"              +
                    "  sha1 = \"{sha1}\"; \n"                   +
                    "  version = \"{version}\"; \n"             +
                    "  deps = filterMissing self [ {deps} ];\n"                    +
                    "  optionalDeps = filterMissing self [ {optionalDeps} ];\n"    +
                    " }}; \n").format(**out))
                tries = 99999

            except Exception as err:
                eprint("Failed on mod: {0}, trying again".format(name), err)

print("})")
