import sys
sys.path.append("../solver")
from os import path
from IniReader import *
from Project import *

predef = Macros()
predef.add_macro("POSIX", "", Location("<command-line>", 0))
predef.add_macro("USE_POSIX", "", Location("<command-line>", 0))
predef.add_macro("EXTERNAL_OPENSSL", "", Location("<command-line>", 0))

core = Project("core",
               ["HAVE_CONFIG_H", "HAVE_EXPAT_CONFIG_H", "XML_STATIC", "XML_UNICODE_WCHAR_T", "CURL_STATICLIB", "CURL_NO_OLDIES", "VOGEL_EXPORTS", "USE_POSIX", "ZLIB", "L_ENDIAN"],
               ["c", "stdc++", "idn", "ldap", "crypto", "ssl", "ssh2", "dl", "pthread"],
               [root+"core",
                root+"core/includes",
                root+"3rd/curl/lib",
                root+"3rd/curl/include",
                root+"3rd/curl/include/curl",
                root+"3rd/libexpat/inc",
                root+"3rd/libzlib/inc"], kDynamicLibrary, predef)
test = Project("test", [], [], [root+"core/includes"], kApplication, predef)

core.out = "bookshelf"
test.out = "bookshelf"

test.depends_on(core)

print """CFLAGS = -g0 -O2 -Wno-system-headers
CPPFLAGS =

CC = gcc
LIBTOOL = g++
LD_DIRS = -L/usr/lib -L/opt/local/lib -L$(OUT)

C_COMPILE = gcc $(INCLUDES) $(CFLAGS) $(DEFS) -x c
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

print """all: %s %s

clean:
\t@if [ -e $(TMP) ]; then { echo 'RM $(TMP)'; $(RM) -r $(TMP); }; fi
""" % (core.get_dest(), test.get_dest())

for d in ["$(OUT_ROOT):", "$(OUT): $(OUT_ROOT)", "$(TMP):", "$(CORE_TMP): $(TMP)", "$(TEST_TMP): $(TMP)"]:
    print "%s\n\t@if ! [ -e $@ ]; then { echo 'mkdir $@'; mkdir $@; }; fi\n" % d

print "$(OUT)/test.exe: $(OUT)/bookshelf.so\n"

core.print_link()
test.print_link()

core.print_compile()
test.print_compile()
