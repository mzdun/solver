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
               ["core",
                "core/includes",
                "3rd/curl/lib",
                "3rd/curl/include",
                "3rd/curl/include/curl",
                "3rd/libexpat/inc",
                "3rd/libzlib/inc"], kDynamicLibrary, predef)
test = Project("test", [], ["core"], ["core/includes"], kApplication, predef)

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
