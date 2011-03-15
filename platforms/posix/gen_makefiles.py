import sys
sys.path.append("../solver")
from os import path
from IniReader import *
from xml.dom import minidom
import uuid
from files import FileList

root = "../../"
defs=["HAVE_CONFIG_H", "HAVE_EXPAT_CONFIG_H", "XML_STATIC", "XML_UNICODE_WCHAR_T", "CURL_STATICLIB", "CURL_NO_OLDIES"]
includes=["core",
          "core/includes",
          "3rd/curl/include/curl",
          "3rd/curl/include",
          "3rd/curl/lib",
          "3rd/libexpat/inc",
          "3rd/libzlib/inc"]

predef = Macros()
predef.add_macro("POSIX", "", Location("<command-line>", 0))
predef.add_macro("EXTERNAL_OPENSSL", "", Location("<command-line>", 0))

def arglist(prefix, l):
    if len(l) == 0: return ""
    return "%s%s" % (prefix, (" %s" % prefix).join(l))

class Project:
    def __init__(self, name):
        self.name = name
        self.files = FileList()
        self.out = name

        self.files.read(predef, "%splatforms/%s.files" % (root, name))

    def get_objects(self):
        out = []
        for k in self.files.cfiles + self.files.cppfiles:
            f = self.files.sec.items[k]
            out.append("$(%s_TMP)/%s.o" % (self.name.upper(), path.split(path.splitext(f.name)[0])[1]))
        return out

    def print_object(self):
        print "%s_TMP = $(TMP)/%s" % (self.name.upper(), self.name)
        print "%s_OBJ = %s\n" % (self.name.upper(), """ \\
\t""".join(self.get_objects())
                                )

    def print_compile(self):
        for k in self.files.cfiles + self.files.cppfiles:
            f = self.files.sec.items[k]
            print "$(%s_TMP)/%s.o: %s%s Makefile.gen" % (self.name.upper(), path.split(path.splitext(f.name)[0])[1], root, f.name)
            if path.splitext(f.name)[1] == ".c":
                print "\t@echo CC $<; $(COMPILE) -c -o $@ $<\n"
            else:
                print "\t@echo CC $<; $(COMPILE) -c -x c++ -o $@ $<\n"

core = Project("core")
test = Project("test")

print """DEFS = %s""" % arglist("-D", defs)
print """INCLUDES = %s""" % arglist("-I"+root, includes)
print """CFLAGS = -g0 -O2 -Wno-system-headers
CPPFLAGS =
CC = gcc
COMPILE = $(CC) $(INCLUDES) $(CFLAGS) $(DEFS) $(CPPFLAGS)
CCLD = $(CC)
LINK = $(LIBTOOL) --tag=CC --mode=link $(CCLD) $(CFLAGS) $(LDFLAGS) -o $@
RM = rm
RMDIR = rmdir

OUT_ROOT = %soutput
OUT = $(OUT_ROOT)/nix

TMP = ./int

""" % root

core.print_object()
test.print_object()

print """all: $(OUT)/core.so $(OUT)/test

clean:
\t@if [ -e $(TMP) ]; then { echo 'RM $(TMP)'; $(RM) -r $(TMP); }; fi
"""

for d in ["$(OUT_ROOT):", "$(OUT): $(OUT_ROOT)", "$(TMP):", "$(CORE_TMP): $(TMP)", "$(TEST_TMP): $(TMP)"]:
    print "%s\n\t@if ! [ -e $@ ]; then { echo 'mkdir $@'; mkdir $@; }; fi\n" % d

print """$(OUT)/core.so: $(CORE_TMP) $(CORE_OBJ) $(OUT)
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

core.print_compile()
test.print_compile()
