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
a CommonJS module system for a browser, look at 
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
your functions will no longer be anonymous.

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

The file [Animals.js](./test-cases/scooj/Animals.js) contains a translation of the
[OO CoffeeScript example](http://jashkenas.github.com/coffee-script/#classes).

In scooj's defense:

* you wouldn't normally be defining more than one class in a file
* you wouldn't be using super so much
* you likely would never have to reference your own class directly, and
  thus not need the assignment of the **defClass()** invocation.

The file [RunTests.js](./test-cases/scooj/RunTests.js) is more the flavor I write
in.

scoopc.py - scooj compiler
===============================================================================

If you use the scooj module functions in your code, you may not be terribly
happy with the verbosity of the resultant code.  It's better than doing
the equivalent 'by hand', but it's still ... wordy.

scoopc is designed to fix that.  It's a "compiler" which takes files consisting
of JavaScript code prefixed with "directive lines", and generates new 
JavaScript files.  The "directive lines" are lines in the file which are used
to declare methods, classes, etc.  See the file 
[Animals.scoop](./test-cases/scoop/Animals.scoop) for an example of a
.scoop file.

Generally, directives are used to define functions.  You specify the
function/method/property name and optional parameter list in the
directive, and the body of the function following the directive.  The
outer-most braces required by JavaScript for function definitions are not
needed for the function bodies when using scoop.

One important feature of scoopc is that the resulting JavaScript file will
have the same line structure as the original scoop file.  If you have syntax
errors in your JavaScript file, you won't have to guess at what line number
the problem is back in the scoop file - it'll be the same line.

scoop directives:
-------------------------------------------------------------------------------

**class _className_**<br>
**class _className_ \(_parameter list_\)**<br>
**class _className_ < _superclassName_**<br>
**class _className_ \(_parameter list_\) < _superclassName_**<br>

The class directive defines a new class.  It can optionally define a parameter 
list for the constructor, and a superclass.

The JavaScript code following this directive becomes 
the body of the constructor function for the class.

**static method _methodName_**<br>
**static method _methodName_ \(_parameter list_\)**<br>

The static method directive defines a new static method on the previously
defined class.
It can optionally define a parameter list for the method.

The JavaScript code following this directive becomes 
the body of the static method.

**static getter _propertyName_**<br>

The static getter directive defines a property getter for the previously
defined class.

The JavaScript code following this directive becomes 
the body of the getter function for the property.

Note that this directive generates code that makes use of the 
ECMAScript 5 property accessor APIs.

**static setter _propertyName_ \(_parameter list_\)**<br>

The static setter directive defines a property setter for the previously
defined class.

The JavaScript code following this directive becomes 
the body of the setter function for the property.

Note that this directive generates code that makes use of the 
ECMAScript 5 property accessor APIs.

**method**<br>
**method \(_parameter list_\)**<br>

The method directive defines an instance method for the previously defined
class.
It can optionally define a parameter list for the method.

The JavaScript code following this directive becomes 
the body of the method.

**getter _propertyName_**<br>

The getter directive defines a property getter for instances of the previously
defined class.

The JavaScript code following this directive becomes 
the body of the getter function for the property.

Note that this directive generates code that makes use of the 
ECMAScript 5 property accessor APIs.


**setter _propertyName_ \(_parameter list_\)**<br>

The setter directive defines a property setter for instances of the previously
defined class.

The JavaScript code following this directive becomes 
the body of the setter function for the property.

Note that this directive generates code that makes use of the 
ECMAScript 5 property accessor APIs.

**static**<br>

The JavaScript code following this directive is left
unadorned in the resulting JavaScript file. It's similar to
Java's static initializer blocks.

**function**<br>
**function \(_parameter list_\)**<br>

The function directive defines a function defined globally within the
module's scope.
It can optionally define a parameter list for the function.

The JavaScript code following this directive becomes 
the body of the function.

**require _moduleName_**<br>
**require _moduleName_ as _variableName_**<br>

The require directive is used to generate a require() function within the
module.  The specified module is assigned to a variable name which
is the _basename_ of the moduleName.  Optionally, you may specify the
variable name which gets used by using the _as_ form.

The JavaScript code following this directive not otherwise processed.


Copyright / License
===============================================================================

Copyright (c) 2010 Patrick Mueller

Licensed under the 
[MIT license](http://www.opensource.org/licenses/mit-license.php)
