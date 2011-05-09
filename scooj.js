
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
scooj._global         = getGlobalObject(this)
scooj._classes        = {}
scooj._currentClass   = {}

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
    
    func.signature = module.id + "." + funcName + "()"
    
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
    // as result of the exported getClass() function
    if (typeof(module.exports.getClass) != "function") {
        func.signature = module.id + "()"
        module.exports.getClass = function getClass() {
            return func
        }
    }
    
    return func
})

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
addExport(function defMethod(module, options, func) {
    if ((func == null) && (typeof(options) == "function")) {
        func    = options
        options = {}
    }
    return addMethod(module, func, false, false, false, options)
})

addExport(function defStaticMethod(module, options, func) {
    if ((func == null) && (typeof(options) == "function")) {
        func    = options
        options = {}
    }
    return addMethod(module, func, true,  false, false, options)
})

addExport(function defGetter(module, func)                {return addMethod(module, func, false, true,  false, {})})
addExport(function defSetter(module, func)                {return addMethod(module, func, false, false, true,  {})})
addExport(function defStaticGetter(module, func)          {return addMethod(module, func, true,  true,  false, {})})
addExport(function defStaticSetter(module, func)          {return addMethod(module, func, true,  false, true,  {})})

//----------------------------------------------------------------------------
addExport(function bindMethods(object) {

    var ctor = object && object.constructor
    if (!ctor) return
    
    var methods = ctor._scooj && ctor._scooj.methods
    if (!methods) return
    
    for (var methodName in methods) {
        var method = methods[methodName]
        
        object[methodName] =  method.bind(object)
    }
})

//----------------------------------------------------------------------------
addExport(function defSuper(module) {
    var klass = ensureClassCurrentlyDefined(module)

    return getSuperMethod(klass)
})

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
        "defSuper"
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
function addMethod(module, func, isStatic, isGetter, isSetter, options) {
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
    func._scooj.isMethod    = true
    func._scooj.isStatic    = isStatic
    func._scooj.isGetter    = isGetter
    func._scooj.isSetter    = isSetter
    func._scooj.isBound     = options.bind

    func.signature   = module.id + "." + funcName + "()"
    func.displayName = func._scooj.signature
    
    methodContainer[funcName] = func
    
    if (isStatic) {
    	if (isGetter)
    		klass.__defineGetter__(funcName, func)
    	else if (isSetter)
    		klass.__defineSetter__(funcName, func)
    	else 
    		if (options.bind) {
    		    klass[funcName] = func.bind(klass)
    		}
    		else {
        		klass[funcName] = func
    		}
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
function ensureClassCurrentlyDefined(module) {
    if (!scooj._currentClass[module.id]) throw new Error("no class currently defined")
    
    return scooj._currentClass[module.id]
}

//----------------------------------------------------------------------------
function addExport(func) {
    var funcName = ensureNamedFunction(func)
    
    exports[funcName] = func
}

//----------------------------------------------------------------------------
function getGlobalObject(theGlobal) {
    // running in a browser?
    if (typeof window != "undefined") {
        theGlobal = window
    }

    // running in node.js?
    else if (typeof global != "undefined") {
        theGlobal = global
    }

    return theGlobal
}

//----------------------------------------------------------------------------
// https://developer.mozilla.org/en/JavaScript/Reference/Global_Objects/Function/bind
//----------------------------------------------------------------------------
if ( !Function.prototype.bind ) {

  Function.prototype.bind = function( obj ) {
    var slice = [].slice,
        args = slice.call(arguments, 1), 
        self = this, 
        nop = function () {}, 
        bound = function () {
          return self.apply( this instanceof nop ? this : ( obj || {} ), 
                              args.concat( slice.call(arguments) ) );    
        };

    nop.prototype = self.prototype;

    bound.prototype = new nop();

    return bound;
  };
}