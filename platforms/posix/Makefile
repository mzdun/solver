all: Makefile.gen
	make -f Makefile.gen all

clean: Makefile.gen
	make -f Makefile.gen clean

Makefile.gen: ../core.files ../test.files gen_makefiles.py
	python gen_makefiles.py
