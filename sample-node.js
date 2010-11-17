
var scooj = require("./scooj")
scooj.installGlobals()

var TestRunner = require("./test/test/TestRunner")
var PointTests = require("./test/sample/PointTests")

var testRunner = new TestRunner()
testRunner.addTestSuite(PointTests)
var results = testRunner.run()
TestRunner.resultsToConsole(results)
