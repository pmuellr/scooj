all:
	@echo not much to do

test:
	@rm -rf tmp
	@mkdir tmp
	
	@echo
	@echo ----------------------------------
	@echo Building tests
	@echo ----------------------------------
	cp -R test-cases/* tmp
	./scoopc.py --out tmp test-cases
	
	@echo
	@echo ----------------------------------
	@echo Running tests
	@echo ----------------------------------
	@node tmp/run-tests.js

clean:
	rm -rf tmp

help:
	@echo make targets available:
	@echo \  all
	@echo \  test
	@echo \  clean
