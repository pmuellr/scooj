
//-----------------------------------------------------------------------------
// Copyright (c) 2010 Patrick Mueller
// Licensed under the MIT license: 
// http://www.opensource.org/licenses/mit-license.php
//-----------------------------------------------------------------------------

require("scooj").installGlobals()

//-------------------------------------------------------------------
defClass(module, function TestSuite() {
})

//-------------------------------------------------------------------
defStaticMethod(module, function suiteSetUp() {})
defStaticMethod(module, function suiteTearDown() {})

//-------------------------------------------------------------------
defMethod(module, function setUp() {})
defMethod(module, function tearDown() {})

//-------------------------------------------------------------------
defMethod(module, function assertEqual(expected, actual, message) {
    if (expected == actual) return

    this.fail(message || expected + " != " + actual)
})  

//-------------------------------------------------------------------
defMethod(module, function assertStrictEqual(expected, actual, message) {
    if (expected === actual) return
    
    this.fail(message || expected + " !== " + actual)
})  

//-------------------------------------------------------------------
defMethod(module, function assertTrue(actual, message) {
    if (actual) return

    this.fail(message || actual + " is not truthy")
})  

//-------------------------------------------------------------------
defMethod(module, function assertFalse(actual, message) {
    if (actual == null) return
    
    this.fail(message || actual + " is not falsey")
})  

//-------------------------------------------------------------------
defMethod(module, function fail(message) {
    var ex = new Error(message || "failure")
    ex.isAssertionError = true
    throw ex
})  
