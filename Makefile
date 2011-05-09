#-------------------------------------------------------------------------------
# Copyright (c) 2010 Patrick Mueller
# Licensed under the MIT license: 
# http://www.opensource.org/licenses/mit-license.php
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
all: help

#-------------------------------------------------------------------------------
test:
	@rm -rf tmp
	@mkdir tmp
	
	Markdown.pl < README.md > README.html
	
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
	
	@NODE_PATH=. node tmp/run-tests.js

#-------------------------------------------------------------------------------
test-modjewel:
	make test
	cp scooj.js tmp
	${MODJEWEL}/module2transportd.py --out tmp --htmlFile run-tests.html --htmlMain "require('run-tests')" tmp
	cp ${MODJEWEL}/modjewel-require.js tmp
	@echo
	@echo To run modjewel tests, open HTML file tmp/run-tests.html and check the console

#-------------------------------------------------------------------------------
get-prereqs:
	-rm -rf node_modules
	mkdir node_modules
	cd node_modules; npm install directive

#-------------------------------------------------------------------------------
clean:
	rm -rf tmp

#-------------------------------------------------------------------------------
# see: https://gist.github.com/240922
#-------------------------------------------------------------------------------
watch:
	run-when-changed "make test" *

#-------------------------------------------------------------------------------
help:
	@echo make targets available:
	@echo \  test
	@echo \  test-modjewel \(set MODJEWEL environment variable first\)
	@echo \  clean
	@echo \  watch
