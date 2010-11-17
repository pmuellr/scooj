
//-----------------------------------------------------------------------------
// Copyright (c) 2010 Patrick Mueller
// Licensed under the MIT license: 
// http://www.opensource.org/licenses/mit-license.php
//-----------------------------------------------------------------------------

//-------------------------------------------------------------------
defClass(module, function TestSuite() {
})

//-------------------------------------------------------------------
defStaticMethod(function suiteSetUp() {})
defStaticMethod(function suiteTearDown() {})

//-------------------------------------------------------------------
defMethod(function setUp() {})
defMethod(function tearDown() {})

//-------------------------------------------------------------------
defMethod(function assertEqual(expected, actual, message) {
    if (expected == actual) return

    this.fail(message || expected + " != " + actual)
})  

//-------------------------------------------------------------------
defMethod(function assertStrictEqual(expected, actual, message) {
    if (expected === actual) return
    
    this.fail(message || expected + " !== " + actual)
})  

//-------------------------------------------------------------------
defMethod(function assertTrue(actual, message) {
    if (actual) return

    this.fail(message || actual + " is not truthy")
})  

//-------------------------------------------------------------------
defMethod(function assertFalse(actual, message) {
    if (actual == null) return
    
    this.fail(message || actual + " is not falsey")
})  

//-------------------------------------------------------------------
defMethod(function fail(message) {
    var ex = new Error(message || "failure")
    ex.isAssertionError = true
    throw ex
})  
