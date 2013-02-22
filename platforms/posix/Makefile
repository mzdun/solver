all: Makefile.gen
	$(MAKE) -f Makefile.gen all

clean: Makefile.gen
	$(MAKE) -f Makefile.gen clean
	rm Makefile.gen

Makefile.gen: ../core.files ../test.files gen_makefiles.py Project.py
	python gen_makefiles.py 2>&1 >Makefile.gen
