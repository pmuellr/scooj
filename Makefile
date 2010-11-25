#===============================================================================
# nothing to do for a normal build
#===============================================================================
all: help

#===============================================================================
# run tests
#===============================================================================
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

#===============================================================================
# remove crap
#===============================================================================
clean:
	rm -rf tmp

#===============================================================================
# see: https://gist.github.com/240922
#===============================================================================
watch:
	run-when-changed "make test" *

#===============================================================================
# print some help
#===============================================================================
help:
	@echo make targets available:
	@echo \  test
	@echo \  clean
	@echo \  watch
