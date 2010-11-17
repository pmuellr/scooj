
//-----------------------------------------------------------------------------
// Copyright (c) 2010 Patrick Mueller
// Licensed under the MIT license: 
// http://www.opensource.org/licenses/mit-license.php
//-----------------------------------------------------------------------------

//----------------------------------------------------------------------------
// make sure running in CommonJS
//----------------------------------------------------------------------------
if (typeof exports == "undefined") {
    throw new Error("exports undefined; not running in a CommonJS environment?")
}

//----------------------------------------------------------------------------
// hidden globals
//----------------------------------------------------------------------------
var scooj = {}

scooj._global         = getGlobalObject()
scooj._classes        = {}
scooj._currentClass   = null

//----------------------------------------------------------------------------
// 
//----------------------------------------------------------------------------
export(function defClass(module, superclass, func) {
    if (null == module) {
        throw new Error("must pass a module as the first parameter")
    }
    
    if (null == module.id) {
        throw new Error("module parameter has no id")
    }
    
    if (null == func) {
        func = superclass
        superclass = null
    }
    
    ensureNamedFunction(func)
    
    var fullClassName = module.id + "::" + func.name
    
    if (scooj._classes.hasOwnProperty(fullClassName)) {
        throw new Error("class is already defined: " + fullClassName)
    }
    
    func._scooj = {}
    func._scooj.isClass       = true
    func._scooj.owningClass   = func
    func._scooj.superclass    = superclass
    func._scooj.subclasses    = {}
    func._scooj.name          = func.name
    func._scooj.moduleId      = module.id
    func._scooj.fullClassName = fullClassName
    func._scooj.methods       = {}
    func._scooj.staticMethods = {}
    func._scooj.getters       = {}
    func._scooj.setters       = {}
    func._scooj.staticGetters = {}
    func._scooj.staticSetters = {}
    
    scooj._classes[fullClassName] = func
    
    scooj._currentClass = func
    
    if (superclass) {
        var T = function() {}
    
        T.prototype = superclass.prototype
        func.prototype = new T()
        func.prototype.constructor = func
    }

    module.exports = func
    
    return func
})

//----------------------------------------------------------------------------
// method/accessor definers
//----------------------------------------------------------------------------
export(function defMethod(func)       {return addMethod(func, false, false, false)})
export(function defStaticMethod(func) {return addMethod(func, true,  false, false)})
export(function defGetter(func)       {return addMethod(func, false, true,  false)})
export(function defSetter(func)       {return addMethod(func, false, false, true)})
export(function defStaticGetter(func) {return addMethod(func, true,  true,  false)})
export(function defStaticSetter(func) {return addMethod(func, true,  false, true)})

//----------------------------------------------------------------------------
// return a super invoker
//----------------------------------------------------------------------------
export(function defSuper() {
    var klass = ensureClassCurrentlyDefined()

    return getSuperMethod(klass)
})

//----------------------------------------------------------------------------
// install scooj functions as globals
//----------------------------------------------------------------------------
export(function installGlobals() {
    var globalNames = [
        "defClass",
        "defMethod",
        "defStaticMethod",
        "defGetter",
        "defSetter",
        "defStaticGetter",
        "defStaticSetter",
        "defSuper"
    ]
    
    if (!scooj._global) {
        throw new Error("unable to determine global object")
    }

    for (var i=0; i<globalNames.length; i++) {
        var name = globalNames[i]
        var func = module.exports[name]
        
        scooj._global[name] = func
    }
})


//============================================================================
// utilities
//============================================================================

//----------------------------------------------------------------------------
// return a new $super method
//----------------------------------------------------------------------------
function getSuperMethod(owningClass) {
    var superclass = owningClass._scooj.superclass

    return function $super(thisp, methodName) {
        var superFunc
        if (methodName == null) {
            superFunc = superclass
        }
        else {
            superFunc = superclass.prototype[methodName]
        }

        return superFunc.apply(thisp, Array.prototype.splice.call(arguments, 2))
    }
}

//----------------------------------------------------------------------------
// add a method to a class
//----------------------------------------------------------------------------
function addMethod(func, isStatic, isGetter, isSetter) {
    ensureNamedFunction(func)
    var klass = ensureClassCurrentlyDefined()
    
    var methodContainer
    if (isGetter) {
    	if (isStatic) 
    		methodContainer = klass._scooj.staticGetters
    	else
    		methodContainer = klass._scooj.getters
    }
    
    else if (isSetter) {
    	if (isStatic) 
    		methodContainer = klass._scooj.staticSetters
    	else
    		methodContainer = klass._scooj.setters
    }
    
    else {
    	if (isStatic) 
    		methodContainer = klass._scooj.staticMethods
    	else
    		methodContainer = klass._scooj.methods
    }
    
    if (methodContainer.hasOwnProperty(func.name)) {
        throw new Error("method is already defined in class: " + klass.name + "." + func.name)
    }
    
    func._scooj = {}
    func._scooj.owningClass = klass
    func._scooj.isMethod    = true
    func._scooj.isStatic    = isStatic
    func._scooj.isGetter    = isGetter
    func._scooj.isSetter    = isSetter
    
    methodContainer[func.name] = func
    
    if (isStatic) {
    	if (isGetter)
    		klass.__defineGetter__(func.name, func)
    	else if (isSetter)
    		klass.__defineSetter__(func.name, func)
    	else 
    		klass[func.name] = func
    }
    
    else {
    	if (isGetter)
    		klass.prototype.__defineGetter__(func.name, func)
    	else if (isSetter)
    		klass.prototype.__defineSetter__(func.name, func)
    	else 
    		klass.prototype[func.name] = func
    }
    
    return func
}

//----------------------------------------------------------------------------
// ensure no methods
//----------------------------------------------------------------------------
function ensureNoMethods() {
    var klass = ensureClassCurrentlyDefined()
    
    for (var name in klass.methods) {
        if (!klass.methods.hasOwnProperty(name)) continue
        
        throw new Error("class already has methods defined: " + klass.name)
    }
}


//----------------------------------------------------------------------------
// ensure parameter is a named function
//----------------------------------------------------------------------------
function ensureNamedFunction(func) {
    if (typeof func != "function") throw new Error("expecting a function: " + func)
    if (!func.name) throw new Error("function must not be anonymous: " + func)
    
    return func.name
}

//----------------------------------------------------------------------------
// ensure a class is currently defined
//----------------------------------------------------------------------------
function ensureClassCurrentlyDefined() {
    if (!scooj._currentClass) throw new Error("no class currently defined")
    
    return scooj._currentClass
}

//----------------------------------------------------------------------------
// export a function
//----------------------------------------------------------------------------
function export(func) {
    ensureNamedFunction(func)
    
    exports[func.name] = func
}

//----------------------------------------------------------------------------
// 
//----------------------------------------------------------------------------
function getName(o) {
    if (!o) return "null"
    o = o.name
    if (!o) return "null"
    return o
}

//----------------------------------------------------------------------------
// get the "global" object
//----------------------------------------------------------------------------
function getGlobalObject() {
    var globalObject = null

    // running in a browser?
    if (typeof window != "undefined") {
        globalObject = window
    }

    // running in node.js?
    else if (typeof global != "undefined") {
        globalObject = global
    }

    return globalObject
}
