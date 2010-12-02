
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
scooj._currentClass   = {}

//----------------------------------------------------------------------------
// 
//----------------------------------------------------------------------------
addExport(function defClass(module, superclass, func) {
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
    
    scooj._currentClass[module.id] = func
    
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
addExport(function useMixin(module, mixinObject) {
    var klass = ensureClassCurrentlyDefined(module)

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
        
        this.defMethod(module, func)
    }
})

//----------------------------------------------------------------------------
// 
//----------------------------------------------------------------------------
addExport(function endClass() {
    console.log("scooj.endClass() is deprecated")
})

//----------------------------------------------------------------------------
// method/accessor definers
//----------------------------------------------------------------------------
addExport(function defMethod(module, func)       {return addMethod(module, func, false, false, false)})
addExport(function defStaticMethod(module, func) {return addMethod(module, func, true,  false, false)})
addExport(function defGetter(module, func)       {return addMethod(module, func, false, true,  false)})
addExport(function defSetter(module, func)       {return addMethod(module, func, false, false, true)})
addExport(function defStaticGetter(module, func) {return addMethod(module, func, true,  true,  false)})
addExport(function defStaticSetter(module, func) {return addMethod(module, func, true,  false, true)})

//----------------------------------------------------------------------------
// return a super invoker
//----------------------------------------------------------------------------
addExport(function defSuper(module) {
    var klass = ensureClassCurrentlyDefined(module)

    return getSuperMethod(klass)
})

//----------------------------------------------------------------------------
// install scooj functions as globals
//----------------------------------------------------------------------------
var globalsInstalled = false

addExport(function installGlobals() {
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
function addMethod(module, func, isStatic, isGetter, isSetter) {
    var funcName = ensureNamedFunction(func)
    var klass = ensureClassCurrentlyDefined(module)
    
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
    func._scooj.signature   = module.id + "." + funcName + "()"
    func._scooj.displayName = func._scooj.signature
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
function ensureClassCurrentlyDefined(module) {
    if (!scooj._currentClass[module.id]) throw new Error("no class currently defined")
    
    return scooj._currentClass[module.id]
}

//----------------------------------------------------------------------------
// export a function
//----------------------------------------------------------------------------
function addExport(func) {
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
