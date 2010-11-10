//-----------------------------------------------------------------------------
// Copyright (c) 2010 Patrick Mueller
// Licensed under the MIT license: 
// http://www.opensource.org/licenses/mit-license.php
//-----------------------------------------------------------------------------

//-------------------------------------------------------------------
defClass(module, function TestRunner() {
    this.suites = []
})

//-------------------------------------------------------------------
defMethod(function addTestSuite(testSuiteClass) {
    this.suites.push(testSuiteClass)
})

//-------------------------------------------------------------------
defMethod(function run(results) {
    if (!results) results = {}
    if (!results.passes) results.passes = []
    if (!results.fails)  results.fails  = []
    if (!results.errors) results.errors = []
    
    for (var i=0; i<this.suites.length; i++) {
        this._runSuite(this.suites[i], results)
    }
    
    return results
})

//-------------------------------------------------------------------
defMethod(function _runSuite(suiteClass, results) {
    if (!this._runCatching(suiteClass, "suiteSetUp", results)) return    
    
    var tests = this._getTests(suiteClass)
  
    for (var i=0; i<tests.length; i++) {
        var suite = this._newSuite(suiteClass, results)
        if (!suite) return
        
        this._runTest(suite, tests[i], results)
    }
    
    if (!this._runCatching(suiteClass, "suiteTearDown", results)) return    
})

//-------------------------------------------------------------------
defMethod(function _newSuite(suiteClass, results) {
    try {
        return new suiteClass()
    }
    catch (e) {
        results.errors.push(suiteClass.name + ": error instantiating class: " + e)
        return
    }
})

//-------------------------------------------------------------------
defMethod(function _runCatching(suite, methodName, results) {
    var func
    
    if (!suite[methodName]) return true
    
    try {
        suite[methodName].call(suite)
        return true
    }
    catch (e) {
        results.errors.push(suite.constructor.name + ": error running " + methodName + ": " + e)
        return false
    }
})

//-------------------------------------------------------------------
defMethod(function _getTests(suiteClass) {
    var tests = []
    
    for (var propertyName in suiteClass.prototype) {
        if (typeof suiteClass.prototype[propertyName] != "function") continue
        if (!propertyName.match(/^test.*/)) continue
        
        tests.push(propertyName)
    }
    
    return tests
})

//-------------------------------------------------------------------
defMethod(function _runTest(suite, testName, results) {

    if (!this._runCatching(suite, "setUp", results)) return    
    
    var testTitle = suite.constructor.name + " : " + testName
    
    var passed = false
    try {
        suite[testName].call(suite)
        passed = true
    }
    catch (e) {
        if (e.isAssertionError) {
            results.fails.push(testTitle + " : assertion failed: " + e.message)
        }
        else {
            results.errors.push(testTitle + " : error: " + e)
        }
    }
    
    if (!this._runCatching(suite, "tearDown", results)) return    
    
    if (passed) results.passes.push(testTitle)
})

//-------------------------------------------------------------------
defStaticMethod(function resultsAsHTML(results) {

    function generateSection(html, title, type) {
        html.push("<div class='test-messages-section'>")
        html.push("<h2>" + title + "</h2>")
        html.push("<hr>")
        html.push("<ul class='test-messages test-" + type + "'>")

        for (var i=0; i<results[type].length; i++) {
            html.push("<li>" + results[type][i])
        }

        if (0 == results[type].length) {
            html.push("<li class='test-message-none'>none")
        }

        html.push("</ul>")
        html.push("</div>")
    }
    
    var html = []
    
    generateSection(html, "Passing  tests", "passes")
    generateSection(html, "Failing  tests", "fails")
    generateSection(html, "Erroring tests", "errors")

    return html.join("\n")
})

//-------------------------------------------------------------------
defStaticMethod(function resultsToConsole(results) {

    function generateSection(title, type) {
        console.log(title)
        
        for (var i=0; i<results[type].length; i++) {
            console.log("    " + results[type][i])
        }

        if (0 == results[type].length) {
            console.log("    none")
        }
        
        console.log()
        
    }
    
    generateSection("Passing  tests", "passes")
    generateSection("Failing  tests", "fails")
    generateSection("Erroring tests", "errors")
})
