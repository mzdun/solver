import sys
sys.path.append("../solver")
from os import path
from IniReader import *
from xml.dom import minidom
import uuid
from files import FileList

root = "../../"
defs=["HAVE_CONFIG_H", "HAVE_EXPAT_CONFIG_H", "XML_STATIC", "XML_UNICODE_WCHAR_T", "CURL_STATICLIB", "CURL_NO_OLDIES"]
includes=["core/includes",
          "3rd/curl/include/curl",
          "3rd/curl/include",
          "3rd/curl/lib",
          "3rd/libexpat/inc",
          "3rd/libzlib/inc"]

predef = Macros()
predef.add_macro("UNIX", "", Location("<command-line>", 0))
predef.add_macro("EXTERNAL_OPENSSL", "", Location("<command-line>", 0))

core = FileList()
core.read(predef, "%splatforms/core.files" % root)
test = FileList()
test.read(predef, "%splatforms/test.files" % root)

def get_objects(files, tmp_dir, flist):
    out = []
    for k in flist:
        f = files.sec.items[k]
        out.append("$(%s)/%s.o" % (tmp_dir, path.split(path.splitext(f.name)[0])[1]))
    return out

def print_object(name, tmp_dir, files):
    print "%s= %s\n" % (name, """ \\
\t""".join(
    get_objects(files, tmp_dir, files.cfiles) +
    get_objects(files, tmp_dir, files.cppfiles))
                        )

def print_compile(files, tmp_dir, flist):
    for k in flist:
        f = files.sec.items[k]
        print "$(%s)/%s.o: %s%s Makefile.gen" % (tmp_dir, path.split(path.splitext(f.name)[0])[1], root, f.name)
        if path.splitext(f.name)[1] == ".c":
            print "\t@echo CC $<; $(COMPILE) -c -o $@ $<\n"
        else:
            print "\t@echo CC $<; $(COMPILE) -o $@ $<\n"

def arglist(prefix, l):
    if len(l) == 0: return ""
    return "%s%s" % (prefix, (" %s" % prefix).join(l))

print """DEFS = %s""" % arglist("-D", defs)
print """INCLUDES = %s""" % arglist("-I"+root, includes)
print """CFLAGS=-g0 -O2 -Wno-system-headers
CPPFLAGS=
CC=gcc
COMPILE = $(CC) $(INCLUDES) $(CFLAGS) $(DEFS) $(CPPFLAGS)
CCLD = $(CC)
LINK = $(LIBTOOL) --tag=CC --mode=link $(CCLD) $(CFLAGS) $(LDFLAGS) -o $@
RM=rm
RMDIR=rmdir

OUT_ROOT=%soutput
OUT=$(OUT_ROOT)/nix

TMP=./int
CORE_TMP=$(TMP)/core
TEST_TMP=$(TMP)/test
""" % root

print_object("CORE_OBJ", "CORE_TMP", core)
print_object("TEST_OBJ", "TEST_TMP", test)

print """all: $(OUT)/core.so $(OUT)/test

clean:
\t@if [ -e $(TMP) ]; then { echo 'RM $(TMP)'; $(RM) -r $(TMP); }; fi

$(OUT_ROOT):
\t@if ! [ -e $@ ]; then { echo 'mkdir $@'; mkdir $@; }; fi

$(OUT): $(OUT_ROOT)
\t@if ! [ -e $@ ]; then { echo 'mkdir $@'; mkdir $@; }; fi

$(TMP):
\t@if ! [ -e $@ ]; then { echo 'mkdir $@'; mkdir $@; }; fi

$(CORE_TMP): $(TMP)
\t@if ! [ -e $@ ]; then { echo 'mkdir $@'; mkdir $@; }; fi

$(TEST_TMP): $(TMP)
\t@if ! [ -e $@ ]; then { echo 'mkdir $@'; mkdir $@; }; fi

$(OUT)/core.so: $(CORE_TMP) $(CORE_OBJ) $(OUT)
\t$(LINK) $(SO_FLAGS) $< $@

$(OUT)/test: $(TEST_TMP) $(TEST_OBJ) $(OUT)
\t$(LINK) $(APP_FLAGS) $< $@

.c.o:
\t@echo CC $<
\t@$(COMPILE) -c -o $@ $<

.cpp.o:
\t@echo CC $<
\t@$(COMPILE) -o $@ $<
"""

print_compile(core, "CORE_TMP", core.cfiles)
print_compile(core, "CORE_TMP", core.cppfiles)

print_compile(test, "TEST_TMP", test.cfiles)
print_compile(test, "TEST_TMP", test.cppfiles)
