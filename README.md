scooj - Simple Classical OO for JavaScript
===============================================================================

Despite the ongoing hate for the "pseudo-classical" object oriented
class definition style in JavaScript from all the kewl kids, one of my
thoughts is that JavaScript actual needs some order brought to it, for
today's JavaScript mega-programs.  Because there is no order, and
programs become as maintainable as BASICA programs of yore. CommonJS
modules help some - they can help you keep your large chunks of code
better organized.  But I yearn for classic OO.  This is an experiment.

scooj is designed to run in a CommonJS module system.  If you need
one for a browser, look at 
[modjewel](https://github.com/pmuellr/modjewel). 

scooj is a JavaScript library that let's you define "classes" that have
instance methods and static methods.  Classes can have superclasses, and
a real super method invocation is available, though it's still kinda clunky.

See the included tests for some basic use cases.

Usage
-------------------------------------------------------------------------------

        var scooj = require("scooj") // or wherever you load it from

To keep your code a little cleaner, you can install the most useful functions
in scooj as global functions.  This works at least with node.js and modjewel.

Installing the scooj functions as globals is done by:

        scooj.installGlobals()
    
I suppose that's evil, but if you're working in a closed system, it makes life
easier.

Functions defined
-------------------------------------------------------------------------------

Note that all the functions passed to scooj functions should be named; this
is how the features are actually named, and it makes debugging nice because
you're functions will no longer be anonymous.

**scooj.defClass(module, [superclass,] constructorFunction)**

Defines a new class.  If subclassing an existing class, specify that
class as the second parameter.  The constructorFunction will be the
constructor for the class.  The module parameter is the current CommonJS
module.

All functions executed after this function is executed will be added to this
class.

**scooj.defStaticMethod(methodFunction)**

Define a static method on the current class.

**scooj.defMethod(methodFunction)**

Define an instance method on the current class.

**scooj.defSuper()**

Returns a function which performs super invocation.  The super
function should be invoked with the following parameters:

* the receiver (should be `this`) 
* the method name to be invoked 
* any parameters to be passed to the method

To make a super call on a constructor, pass null as the method name.

Example
-------------------------------------------------------------------------------

The file [animals.js](./test/animals.js) contains a translation of the
[OO CoffeeScript example](http://jashkenas.github.com/coffee-script/#classes).

In scooj's defense:

* you wouldn't normally be defining more than one class in a file
* you wouldn't be using super so much
* you likely would never have to reference your own class directly, and
  thus not need the assignment of the **defClass()** invocation.

The file [PointTests.js](./test/sample/PointTests.js) is more the flavor I write
in.

Copyright / License
-------------------------------------------------------------------------------

Copyright (c) 2010 Patrick Mueller

Licensed under the 
[MIT license](http://www.opensource.org/licenses/mit-license.php)
