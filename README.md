scooj - Simple Classical OO for JavaScript
===============================================================================

Despite the ongoing hate for the "pseudo-classical" object oriented
class definition style in JavaScript from all the kewl kids, one of my
thoughts is that JavaScript actual needs some order brought to it, for
today's JavaScript mega-programs.  Because there is no order, and
programs become as maintainable as BASICA programs of yore. It's the
wild west.  Classical OO brings some order.  This is an experiment.

**`scooj`** is currently targeted to browser JavaScript, as compared to
CommonJS-y, module-y JavaScript.  When I finally implement or find a nice
small require() system for browser JavaScript, I'll write a version of
**`scooj`** which is module-friendly.

**`scooj`** is a JavaScript library that let's you define "classes" that have
instance methods and static methods.  Classes can have superclasses, and
a real super method invocation is available.

See the
[examples](http://pmuellr.github.com/scooj/test/scooj.sample/sample.html) 
for some basic use cases.

Usage
-------------------------------------------------------------------------------

Add a link to **`scooj.js`** to your HTML file.

**`scooj`** defines all of it's functions in the "**`scooj`**" global 
variable.  You can use the function **`scooj.installGlobals()`** to have
some of the functions defined globally as well.

Functions defined
-------------------------------------------------------------------------------

**`scooj.defPackage(packageName)`**

Defines a new package.  All classes added after this function is
executed will be added to this package.  The package defines the
global name the classes will be available in.

**`scooj.defClass([superclass,] constructorFunction)`**

Defines a new function.  If subclassing an existing class, specify that
class as the first parameter.  The constructorFunction will be the
constructor for the class.

All methods added after this function is executed will be added to this
class.

**`scooj.defStaticMethod(methodFunction)`**

Define a static method on the current class.

**`scooj.defMethod(methodFunction)`**

Define an instance method on the current class.

**`scooj.defSuper()`**

Returns a function which performs super invocation.  The super
function should be invoked with the following parameters:
the receiver (should be `this`), the method name to
be invoked, and then any parameters to be passed to the method.

**`scooj.installGlobals()`**

Makes all of the **`scooj.def*()`** functions available globally, instead
of just as properties of the **`scooj`** object.

Copyright / License
-------------------------------------------------------------------------------

Copyright (c) 2010 Patrick Mueller

Licensed under the 
[MIT license](http://www.opensource.org/licenses/mit-license.php)
