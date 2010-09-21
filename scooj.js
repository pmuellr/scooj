//-----------------------------------------------------------------------------
// Copyright (c) 2010 Patrick Mueller
// Licensed under the MIT license: 
// http://www.opensource.org/licenses/mit-license.php
//-----------------------------------------------------------------------------

(function(){
    
if (this.scooj) return

this.scooj = {}

//----------------------------------------------------------------------------
// scooj properties
//----------------------------------------------------------------------------
scooj._global         = this
scooj._packages       = {}
scooj._classes        = {}
scooj._currentPackage = null
scooj._currentClass   = null

scooj.debug           = false

//----------------------------------------------------------------------------
// shortcut for defining scooj functions
//----------------------------------------------------------------------------
function defScooj(func) {
    ensureNamedFunction(func)
    
    scooj[func.name] = func
}

//----------------------------------------------------------------------------
// scooj.defPackage(string)
//----------------------------------------------------------------------------
defScooj(function defPackage(name) {
    scooj._currentPackage = name
})

//----------------------------------------------------------------------------
// scooj.defClass(function)
//----------------------------------------------------------------------------
defScooj(function defClass(superclass, func) {
    if (null == func) {
        func = superclass
        superclass = null
    }
    
    if (superclass) {
        // if (!superclass._scooj) throw new Error("superclass is not a defined class")
        // if (!superclass._scooj.isClass) throw new Error("superclass is not a defined class")
    }

    ensureNamedFunction(func)
    
    var fullClassName = getFullClassName(null, func.name)
    
    if (scooj._classes.hasOwnProperty(fullClassName)) {
        throw new Error("class is already defined: " + fullClassName)
    }
    
    func._scooj = {}
    func._scooj.isClass = true
    func._scooj.owningClass = func
    func._scooj.superclass = superclass
    func._scooj.subclasses = {}
    func._scooj.name = func.name
    func._scooj.packageName = scooj._currentPackage
    func._scooj.fullClassName = fullClassName
    func._scooj.methods = {}
    func._scooj.staticMethods = {}
    func._scooj.getters = {}
    func._scooj.setters = {}
    func._scooj.staticGetters = {}
    func._scooj.staticSetters = {}
    
    scooj._classes[fullClassName] = func
    
    scooj._currentClass = func
    
    if (superclass) {
        var T = function() {}
    
        T.prototype = superclass.prototype
        func.prototype = new T()
        func.prototype.constructor = func
        
        scooj.defStaticMethod(getSuperMethod(func))
    }

    defineGlobalFunction(func)
    
    return func
})

//----------------------------------------------------------------------------
// scooj.defMethod(function)
//----------------------------------------------------------------------------
defScooj(function defMethod(func) {
    addMethod(func, false, false, false)
})

//----------------------------------------------------------------------------
// scooj.defStaticMethod(function)
//----------------------------------------------------------------------------
defScooj(function defStaticMethod(func) {
    addMethod(func, true, false, false)
})

//----------------------------------------------------------------------------
// scooj.defGetter(function)
//----------------------------------------------------------------------------
defScooj(function defGetter(func) {
    addMethod(func, false, true, false)
})

//----------------------------------------------------------------------------
// scooj.defSetter(function)
//----------------------------------------------------------------------------
defScooj(function defSetter(func) {
    addMethod(func, false, false, true)
})

//----------------------------------------------------------------------------
// scooj.defStaticGetter(function)
//----------------------------------------------------------------------------
defScooj(function defStaticGetter(func) {
    addMethod(func, true, true, false)
})

//----------------------------------------------------------------------------
// scooj.defStaticSetter(function)
//----------------------------------------------------------------------------
defScooj(function defStaticSetter(func) {
    addMethod(func, true, false, true)
})

//----------------------------------------------------------------------------
// return a super invoker
//----------------------------------------------------------------------------
defScooj(function defSuper(args) {
    var klass = ensureClassCurrentlyDefined()

    return getSuperMethod(klass)
})
        

//----------------------------------------------------------------------------
// scooj.installGlobals()
//----------------------------------------------------------------------------
defScooj(function installGlobals() {
    var globalNames = [
        "defPackage",
        "defClass",
        "defSuperclass",
        "defMethod",
        "defStaticMethod",
        "defGetter",
        "defSetter",
        "defStaticGetter",
        "defStaticSetter",
        "defSuper"
    ]
    
    for (var i=0; i<globalNames.length; i++) {
        var name = globalNames[i]
        var func = scooj[name]
        
        scooj._global[name] = func
    }
})


//============================================================================
// utilities
//============================================================================

//----------------------------------------------------------------------------
// define a function globally
//----------------------------------------------------------------------------
function defineGlobalFunction(func) {
    var packageName = func._scooj.packageName
    
    if (null == packageName) {
        scooj._global[func.name] = func
        return
    }
    
    var lastContainer = scooj._global
    var pieces = packageName.split(".")
    for (var i=0; i<pieces.length; i++) {
        var piece = pieces[i]
        if (!lastContainer[piece]) lastContainer[piece] = {}
        lastContainer = lastContainer[piece]
    }
    
    lastContainer[func.name] = func
}

//----------------------------------------------------------------------------
// return a new $super method
//----------------------------------------------------------------------------
function getSuperMethod(owningClass) {
    var superclass = owningClass._scooj.superclass
    
    return function $super(thisp, methodName) {
        var superFunc = superclass.prototype[methodName]
        if (!superFunc) superFunc = superclass

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
    func._scooj.isMethod = true
    func._scooj.isStatic = isStatic
    func._scooj.isGetter = isGetter
    func._scooj.isSetter = isSetter
    
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
// return full class name
//----------------------------------------------------------------------------
function getFullClassName(packageName, className) {
    if (null == packageName) packageName = scooj._currentPackage
    
    if (null == packageName) return className
    
    return packageName + "." + className
}


//----------------------------------------------------------------------------
// debug logger
//----------------------------------------------------------------------------
function debugLog(message) {
    if (!scooj.debug) return
    console.log(message)
}

})()
