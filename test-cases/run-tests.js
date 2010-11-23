
var scooj = require("../scooj")
scooj.installGlobals()

var TestRunner = require("./unit-test/TestRunner")

//---------------------------------------------------
var RunTests   = require("./scooj/RunTests")

var testRunner = new TestRunner()
testRunner.addTestSuite(RunTests)
var results = testRunner.run()
TestRunner.resultsToConsole("RunTests", results)

var animals = require("./scooj/Animals")

//---------------------------------------------------
var RunTests   = require("./scoop/RunTests")

var testRunner = new TestRunner()
testRunner.addTestSuite(RunTests)
var results = testRunner.run()
TestRunner.resultsToConsole("RunTests", results)

var animals = require("./scoop/Animals")

