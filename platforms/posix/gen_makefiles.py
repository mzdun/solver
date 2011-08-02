import sys
sys.path.append("../solver")
from os import path
from IniReader import *
from Project import *

predef = Macros()
predef.add_macro("POSIX", "", Location("<command-line>", 0))
predef.add_macro("USE_POSIX", "", Location("<command-line>", 0))
predef.add_macro("EXTERNAL_OPENSSL", "", Location("<command-line>", 0))
#predef.add_macro("EXTERNAL_EXPAT", "", Location("<command-line>", 0))
predef.add_macro("EXTERNAL_CURL", "", Location("<command-line>", 0))

_3rd = Project("3rdparty",
               ["HAVE_CONFIG_H", "VOGEL_EXPORTS", "USE_POSIX", "ZLIB", "L_ENDIAN", "HAVE_MEMMOVE"],
               ["c", "stdc++", "dl", "pthread"],
               [root+"3rd/libexpat/inc",
                root+"3rd/libzlib/inc"], kStaticLibrary, predef)

core = Project("core",
               ["HAVE_CONFIG_H", "VOGEL_EXPORTS", "USE_POSIX", "ZLIB", "L_ENDIAN"],
               ["c", "stdc++", "curl", "crypto", "ssl", "dl", "pthread"],
               [root+"core",
                root+"core/includes",
                root+"3rd/libzlib/inc"], kDynamicLibrary, predef)
test = Project("test", [], [], [root+"core/includes"], kApplication, predef)

core.out = "bookshelf"
test.out = "bookshelf"

core.depends_on(_3rd)
#test.depends_on(_3rd)
test.depends_on(core)

print """CFLAGS = -g3 -Wno-system-headers
CPPFLAGS =
CORE_CFLAGS= -fvisibility=hidden

CC = gcc
LIBTOOL = g++
LD_DIRS = -L/opt/local/lib -L$(OUT) -L/usr/lib

LD_LIBRARY_PATH=.

C_COMPILE = gcc $(INCLUDES) $(CFLAGS) $(DEFS) -x c
CPP_COMPILE = $(CC) $(INCLUDES) $(CFLAGS) $(CPPFLAGS) $(DEFS) -x c++

CCLD = $(CC)
LINK = $(LIBTOOL) $(LD_DIRS) $(CFLAGS) $(LDFLAGS)
RM = rm
RMDIR = rmdir

AR_FLAGS = rcs

OUT_ROOT = %soutput
OUT_ = $(OUT_ROOT)/posix
OUT = $(OUT_)/release

TMP = ./int

""" % root

_3rd.print_declaration()
core.print_declaration()
test.print_declaration()

print """CORE_OBJ += $(A3RDPARTY_OBJ)

all: %s %s %s

clean:
\t@if [ -e $(TMP) ]; then { echo 'RM $(TMP)'; $(RM) -r $(TMP); }; fi
""" % (_3rd.get_dest(), core.get_dest(), test.get_dest())

for d in ["$(OUT_ROOT):", "$(OUT): $(OUT_)", "$(OUT_): $(OUT_ROOT)", "$(TMP):", "$(A3RDPARTY_TMP): $(TMP)", "$(CORE_TMP): $(TMP)", "$(TEST_TMP): $(TMP)"]:
    print "%s\n\t@if ! [ -e $@ ]; then { echo 'mkdir $@'; mkdir $@; }; fi\n" % d

_3rd.print_link()
core.print_link()
test.print_link()

_3rd.print_compile()
core.print_compile()
test.print_compile()
