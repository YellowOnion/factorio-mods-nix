#!/usr/bin/env python

import json
import re
import requests
import sys
import os

mods_api = "https://mods.factorio.com"

VERSION = "1.1"

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

def toDeps(ds):
    return [ eprint(x) or toName(x["name"]) for x in
             (matchOrNone(x) for x in ds)
             if x and x["name"] != "base" and (x["type"] is None or x["type"] == "~")]

def toOpDeps(ds):
    return [ eprint(x) or toName(x["name"]) for x in
             (matchOrNone(x) for x in ds)
             if x and x["type"] == "?"]

def toName(n):
    if n[0].isdigit():
        n = "n" + n
    return n.replace(" ", "-")

if os.path.exists("mods.json"):
    mods = json.load(open("mods.json"))
else:
    mods = fetch_mod_json("?page_size=max&version=" + VERSION)
    json.dump(mods, open("mods.json", "w"))

nmods = len(mods["results"])

sparseModsList = sys.argv[1:]


modsToParse = {}
if sparseModsList != []:
    for mod in sparseModsList:
        modsToParse |= {mod: False}


eprint("getting info for {0} mods".format(nmods))

print("{ lib, fetchurl \n"                                                      +
      ", factorio-utils \n"                                                     +
      ", allRecommendedMods ? true \n"                                          +
      ", allOptionalMods ? false \n"                                            +
      ", username ? \"\" , token ? \"\" \n"                                     +
      "}: \n"                                                                   +
      "with lib; \n"                                                            +
      "let \n"                                                                  +
      "  fetchurl2 = args: lib.overrideDerivation (fetchurl (args // { curlOptsList = [  \n"              +
      "    \"--get\" \n"                                                          +
      "    \"--data-urlencode\" \"username@username\" \n"                           +
      "    \"--data-urlencode\" \"token@token\"  \n"                             +
      "];}))  \n"                                                               +
       """  (_: { preHook =
                if username != "" && token != "" then ''
                    echo -n "${username}" >username
                    echo -n "${token}"    >token
                '' else "exit 1"
                ;});
      """ +
      "  modDrv = factorio-utils.modDrv { inherit allRecommendedMods allOptionalMods; };\n " +
      "in \n"                                                                   +
      " rec {"
       )

# while modsToParse == {} or not all(modsToParse.values):
for (i, result) in enumerate(mods["results"]):
 #       if notnot result["name"] in modsToParse.keys and
 #           continue
 #       else:
        tries = 0
        while tries < 5:
            tries += 1
            try:
                full = fetch_mod_json( "/" + result["name"] + "/full")
                name = toName(full["name"])
                percent = float(i * 100) / float(nmods)
                eprint("{0:02.3f}% {1} / {2}".format(percent, i, nmods))
                eprint(name)
                latest_release = list(filter(lambda a: a["info_json"]["factorio_version"] == VERSION ,full["releases"]))[-1]
                url = mods_api + latest_release["download_url"]
                file_name = latest_release["file_name"]
                deps = toDeps(latest_release["info_json"]["dependencies"])
                deps = " ".join(deps)
                optionalDeps = " ".join(toOpDeps(latest_release["info_json"]["dependencies"]))
                sha1 = latest_release["sha1"]
                out =  { "name" : name,
                        "title": full["title"],
                        "version": latest_release["version"],
                        "url" : url,
                        "file_name" : file_name,
                        "deps" : deps,
                        "optionalDeps" : optionalDeps,
                        "sha1": sha1
                        }
                print( \
                    ("  {name} = modDrv {{\n"                           +
                        "    name = \"{title}\"; \n"                    +
                        "    src = fetchurl2 {{\n"                      +
                        "      url = \"{url}\";  \n"                    +
                        "      name = \"{file_name}\"; \n"              +
                        "      sha1 = \"{sha1}\"; \n"                   +
                        "    }};\n"                                     +
                        "    deps = [ {deps} ];\n"                      +
                        "    optionalDeps = [ {optionalDeps} ];\n"      +
                        "    recommendedDeps = []; \n"                  +
                        " }}; \n").format(**out))
                tries = 99999

            except Exception as err:
                eprint("Failed on mod: {0}, trying again".format(name), err)

print("}")
