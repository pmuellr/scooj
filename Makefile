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
# run tests
#===============================================================================
test-modjewel:
	make test
	cp scooj.js tmp
	${MODJEWEL}/module2transportd.py --out tmp --htmlFile run-tests.html --htmlMain "require('run-tests')" tmp
	cp ${MODJEWEL}/modjewel-require.js tmp
	@echo
	@echo To run modjewel tests, open HTML file tmp/run-tests.html and check the console

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
