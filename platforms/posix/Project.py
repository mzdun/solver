import sys
sys.path.append("../solver")
from os import path
import uuid
from files import FileList

root = "../../"

so_ext=".dylib"
app_ext=""

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
        self.depends = []

        self.files.read(predef, "%splatforms/%s.files" % (root, name))

    def depends_on(self, project):
        dep = project.get_link_dep()
        if dep != "": self.depends.append(dep)

    def get_link_dep(self):
        if self.bintype == kDynamicLibrary: return self.get_short_dest()
        return ""

    def get_objects(self):
        out = []
        for k in self.files.cfiles + self.files.cppfiles:
            f = self.files.sec.items[k]
            out.append("$(%s_TMP)/%s.o" % (self.name.upper(), path.split(path.splitext(f.name)[0])[1]))
        return out

    def get_dest(self):
        return "$(OUT)/"+self.get_short_dest()

    def get_short_dest(self):
        if self.bintype == kApplication:
            return "%s%s" % (self.out, app_ext)
        elif self.bintype == kDynamicLibrary:
            return "%s%s" % (self.out, so_ext)

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
            print "$(%s_TMP)/%s.o: %s%s #$(%s_TMP) Makefile.gen" % (self.name.upper(), path.split(path.splitext(f.name)[0])[1], root, f.name, self.name.upper())
            if path.splitext(f.name)[1] == ".c":
                print "\t@echo CC $<; $(%s_C_COMPILE) -c -o $@ $<\n" % n
            else:
                print "\t@echo CC $<; $(%s_CPP_COMPILE) -c -o $@ $<\n" % n

    def print_link(self):
        n = self.name.upper()
        libs = arglist("-l", self.libs)
        deps = arglist("", self.depends)
        if deps != "": deps = " " + deps
        deps2 = arglist("$(OUT)/", self.depends)
        if deps2 != "": deps2 = " " + deps2
        print "%s: $(%s_TMP) $(%s_OBJ) $(OUT)%s Makefile.gen" % (self.get_dest(), n, n, deps2)
        if self.bintype == kApplication:
            print "\t$(LINK) %s%s $(%s_OBJ) -o %s%s\n\tcp %s%s $@\n" % (libs, deps, n, self.out, app_ext, self.out, app_ext)
        elif self.bintype == kDynamicLibrary:
            print "\t$(LINK) -shared %s%s $(%s_OBJ) -o %s%s\n\tcp %s%s $@\n" % (libs, deps, n, self.out, so_ext, self.out, so_ext)
