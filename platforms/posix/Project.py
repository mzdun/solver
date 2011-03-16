import sys
sys.path.append("../solver")
from os import path
import uuid
from files import FileList

root = "../../"

kApplication = 0
kDynamicLibrary = 1

def arglist(prefix, l):
    if len(l) == 0: return ""
    return "%s%s" % (prefix, (" %s" % prefix).join(l))

class Project:
    def __init__(self, name, defs, libs, includes, bintype, predef):
        self.name = name
        self.files = FileList()
        self.out = name
        self.defs = defs
        self.libs = libs
        self.includes = includes + ["/opt/local/include"]
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
        print "%s_INCLUDES = %s" % (n, arglist("-I", self.includes))
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
