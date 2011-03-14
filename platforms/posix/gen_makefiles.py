import sys
sys.path.append("../solver")
from os import path
from IniReader import *
from xml.dom import minidom
import uuid
from files import FileList

root = "../../"

predef = Macros()
predef.add_macro("UNIX", "", Location("<command-line>", 0))
predef.add_macro("EXTERNAL_OPENSSL", "", Location("<command-line>", 0))

core = FileList()
core.read(predef, "%splatforms/core.files" % root)
test = FileList()
test.read(predef, "%splatforms/test.files" % root)

def print_compile(files, flist):
    for k in flist:
        f = files.sec.items[k]
        print "%s.obj: %s" % (path.splitext(f.name)[0], f.name)
        print "\t$(CC) $(C_FLAGS) $< $@"
        print

print_compile(core, core.cfiles)
print_compile(core, core.cppfiles)

print_compile(test, test.cfiles)
print_compile(test, test.cppfiles)
