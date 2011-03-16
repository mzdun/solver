import sys
sys.path.append("../solver")
from os import path
from IniReader import *
from xml.dom import minidom
import uuid
from files import FileList

root = "../../"

kApplication = 0
kDynamicLibrary = 1

predef = Macros()
predef.add_macro("POSIX", "", Location("<command-line>", 0))
predef.add_macro("EXTERNAL_OPENSSL", "", Location("<command-line>", 0))

def arglist(prefix, l):
    if len(l) == 0: return ""
    return "%s%s" % (prefix, (" %s" % prefix).join(l))

class Project:
    def __init__(self, name, defs, libs, includes, bintype):
        self.name = name
        self.files = FileList()
        self.out = name
        self.defs = defs
        self.libs = libs
        self.includes = includes
        self.bintype = bintype

        self.files.read(predef, "%splatforms/%s.files" % (root, name))

    def get_objects(self):
        out = []
        for k in self.files.cfiles + self.files.cppfiles:
            f = self.files.sec.items[k]
            out.append("$(%s_TMP)/%s.o" % (self.name.upper(), path.split(path.splitext(f.name)[0])[1]))
        return out

    def print_declaration(self):
        n = self.name.upper()
        print "%s_DEFS = %s" % (n, arglist("-D", self.defs))
        print "%s_INCLUDES = %s" % (n, arglist("-I"+root, self.includes))
        print "%s_C_COMPILE = $(C_COMPILE) $(%s_INCLUDES) $(%s_CFLAGS) $(%s_DEFS)" % (n, n, n, n)
        print "%s_CPP_COMPILE = $(CPP_COMPILE) $(%s_INCLUDES) $(%s_CFLAGS) $(%s_CPPFLAGS) $(%s_DEFS)" % (n, n, n, n, n)
        print "%s_TMP = $(TMP)/%s" % (n, self.name)
        print "%s_OBJ = %s\n" % (n, """ \\
\t""".join(self.get_objects()))

    def print_compile(self):
        n = self.name.upper()
        for k in self.files.cfiles + self.files.cppfiles:
            f = self.files.sec.items[k]
            print "$(%s_TMP)/%s.o: %s%s" % (self.name.upper(), path.split(path.splitext(f.name)[0])[1], root, f.name)
            if path.splitext(f.name)[1] == ".c":
                print "\t@echo CC $<; $(%s_C_COMPILE) -c -o $@ $<\n" % n
            else:
                print "\t@echo CC $<; $(%s_CPP_COMPILE) -c -o $@ $<\n" % n

    def print_link(self):
        n = self.name.upper()
        libs = arglist("-l", self.libs)
        if self.bintype == kApplication:
            print """$(OUT)/%s.exe: $(%s_TMP) $(%s_OBJ) $(OUT)\n\t$(LINK) %s $(%s_OBJ) -o $@\n""" % (self.out, n, n, libs, n)
        elif self.bintype == kDynamicLibrary:
            print """$(OUT)/%s.so: $(%s_TMP) $(%s_OBJ) $(OUT)\n\t$(LINK) -shared %s $(%s_OBJ) -o $@\n""" % (self.out, n, n, libs, n)

core = Project("core",
               ["HAVE_CONFIG_H", "HAVE_EXPAT_CONFIG_H", "XML_STATIC", "XML_UNICODE_WCHAR_T", "CURL_STATICLIB", "CURL_NO_OLDIES", "VOGEL_EXPORTS", "ZLIB", "L_ENDIAN"],
               #["c", "stdc++", "ssl", "crypto", "pthread"],
               ["c", "stdc++", "idn", "ldap", "crypto", "ssl", "ssh2", "dl", "pthread"],
               ["core",
                "core/includes",
                "3rd/curl/lib",
                "3rd/curl/include",
                "3rd/curl/include/curl",
                "3rd/libexpat/inc",
                "3rd/libzlib/inc"], kDynamicLibrary)
test = Project("test", [], ["core"], ["core/includes"], kApplication)

core.out = "bookshelf"

print """CFLAGS = -g0 -O2 -Wno-system-headers
CPPFLAGS =

CC = gcc
LIBTOOL = g++
LD_DIRS = -L/lib -L/usr/lib -L$(OUT)

C_COMPILE = $(CC) $(INCLUDES) $(CFLAGS) $(DEFS) -x c
CPP_COMPILE = $(CC) $(INCLUDES) $(CFLAGS) $(CPPFLAGS) $(DEFS) -x c++

CCLD = $(CC)
LINK = $(LIBTOOL) $(LD_DIRS) $(CFLAGS) $(LDFLAGS)
RM = rm
RMDIR = rmdir

OUT_ROOT = %soutput
OUT = $(OUT_ROOT)/posix

TMP = ./int

""" % root

core.print_declaration()
test.print_declaration()

print """all: $(OUT)/bookshelf.so $(OUT)/test.exe

clean:
\t@if [ -e $(TMP) ]; then { echo 'RM $(TMP)'; $(RM) -r $(TMP); }; fi
"""

for d in ["$(OUT_ROOT):", "$(OUT): $(OUT_ROOT)", "$(TMP):", "$(CORE_TMP): $(TMP)", "$(TEST_TMP): $(TMP)"]:
    print "%s\n\t@if ! [ -e $@ ]; then { echo 'mkdir $@'; mkdir $@; }; fi\n" % d

print "$(OUT)/test.exe: $(OUT)/bookshelf.so\n"

core.print_link()
test.print_link()

core.print_compile()
test.print_compile()
