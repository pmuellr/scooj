
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
scooj.version         = "1.1.0"
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
    
    var funcName = ensureNamedFunction(func)
    
    var fullClassName = module.id + "::" + funcName
    
    if (scooj._classes.hasOwnProperty(fullClassName)) {
        throw new Error("class is already defined: " + fullClassName)
    }
    
    func._scooj = {}
    func._scooj.isClass       = true
    func._scooj.owningClass   = func
    func._scooj.superclass    = superclass
    func._scooj.subclasses    = {}
    func._scooj.name          = funcName
    func._scooj.moduleId      = module.id
    func._scooj.fullClassName = fullClassName
    func._scooj.mixins        = []
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
    
    func.$super = getSuperMethod(func)

    // export the first class defined in a module
    if (typeof(module.exports) != "function") module.exports = func
    
    return func
})

//----------------------------------------------------------------------------
// class mixin - copy functions in mixinObject into prototype
//----------------------------------------------------------------------------
export(function useMixin(mixinObject) {
    var klass = ensureClassCurrentlyDefined()

    klass._scooj.mixins.push(mixinObject)
    
    var methodBag = mixinObject
    if (methodBag._scooj) {
        methodBag = methodBag._scooj.methods
    }
    
    for (var funcName in methodBag) {
        var func = methodBag[funcName]
        if (typeof func != "function") continue
        
        if (!func.name) {
            if (!func.displayName) {
                func.displayName = funcName
            }
        }
        
        var funcName2 = func.name || func.displayName
        if (funcName != funcName2) {
            throw new Error("function name doesn't match key it was stored under: " + valName)
        }
        
        this.defMethod(func)
    }
})

//----------------------------------------------------------------------------
// 
//----------------------------------------------------------------------------
export(function endClass() {
    scooj._currentClass = null
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
var globalsInstalled = false

export(function installGlobals() {
    var globalNames = [
        "defClass",
        "defMethod",
        "defStaticMethod",
        "defGetter",
        "defSetter",
        "defStaticGetter",
        "defStaticSetter",
        "defSuper",
        "endClass",
    ]

    if (globalsInstalled) return
    globalsInstalled = true
    
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
    var funcName = ensureNamedFunction(func)
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
    
    methodContainer[funcName] = func
    
    if (isStatic) {
    	if (isGetter)
    		klass.__defineGetter__(funcName, func)
    	else if (isSetter)
    		klass.__defineSetter__(funcName, func)
    	else 
    		klass[funcName] = func
    }
    
    else {
    	if (isGetter)
    		klass.prototype.__defineGetter__(funcName, func)
    	else if (isSetter)
    		klass.prototype.__defineSetter__(funcName, func)
    	else 
    		klass.prototype[funcName] = func
    }
    
    return func
}

//----------------------------------------------------------------------------
// ensure parameter is a named function
//----------------------------------------------------------------------------
function ensureNamedFunction(func) {
    if (typeof func != "function") throw new Error("expecting a function: " + func)
    
    if (!func.name) {
        if (!func.displayName) {
            throw new Error("function must not be anonymous: " + func)
        }
    }
    
    return func.name || func.displayName
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
    var funcName = ensureNamedFunction(func)
    
    exports[funcName] = func
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
