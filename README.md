-------------------------------------------------------------------------------
scooj - Simple Classical OO for JavaScript
===============================================================================

The "pseudo-classical" object oriented class definition style in JavaScript 
seems to be dismissed by all the kewl JavaScript folk, but one of my
thoughts is that JavaScript actual needs some order brought to it, for
today's JavaScript mega-programs.  Because there is no order, and
programs become as maintainable as BASICA programs of yore. CommonJS
modules help some - they can help you keep your large chunks of code
better organized.  But I yearn for classic OO.  This is an experiment.

**`scooj`** is designed to run in a CommonJS module system.  If you need
a CommonJS module system for a browser, look at 
[modjewel](https://github.com/pmuellr/modjewel). 

**`scooj`** is a JavaScript library that let's you define "classes" that have
instance methods and static methods.  Classes can have superclasses, and
a real super method invocation is available.

See the included tests for some basic use cases.

Beyond that description, you probably won't be using the **`scooj`** module
directly.  Instead, you'll author your classes in `.scoop` files, which you
compile into JavaScript source files with the `scoopc.py` compiler.


-------------------------------------------------------------------------------
scoopc.py - scooj compiler
===============================================================================

If you use the scooj module functions in your code, you may not be terribly
happy with the verbosity of the resultant code.  It's better than doing
the equivalent 'by hand', but it's still ... wordy.

scoopc is designed to fix that.  It's a "compiler" which takes files consisting
of JavaScript code prefixed with "directive lines", and generates new 
JavaScript files.  The "directive lines" are lines in the file which are used
to declare methods, classes, etc.  See the file 
[Animals.scoop](https://github.com/pmuellr/scooj/blob/master/test-cases/scoop/Animals.scoop) for an example of a
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

Enjoy brace-, bracket-, and comma-free class defining!

-------------------------------------------------------------------------------
scoop directive - `class`
-------------------------------------------------------------------------------

<pre>
<b>class</b> <i>className</i>
<b>class</b> <i>className</i> (<i>parameter list</i>)
<b>class</b> <i>className</i> &lt; <i>superclassName</i>
<b>class</b> <i>className</i> (<i>parameter list</i>) < <i>superclassName</i>
</pre>

The `class` directive defines a new class.  It can optionally define a parameter 
list for the constructor, and a superclass.

The JavaScript code following this directive becomes 
the body of the constructor function for the class.

-------------------------------------------------------------------------------
scoop directive - `static method`
-------------------------------------------------------------------------------

<pre>
<b>static method</b> <i>methodName</i>
<b>static method</b> <i>methodName</i> (<i>parameter list</i>)
</pre>

The `static method` directive defines a new static method on the previously
defined class.
It can optionally define a parameter list for the method.

The JavaScript code following this directive becomes 
the body of the static method.

-------------------------------------------------------------------------------
scoop directive - `static getter`
-------------------------------------------------------------------------------

<pre>
<b>static getter</b> <i>propertyName</i>
</pre>

The `static getter` directive defines a property getter for the previously
defined class.

The JavaScript code following this directive becomes 
the body of the getter function for the property.

Note that this directive generates code that makes use of the 
ECMAScript 5 property accessor APIs.

-------------------------------------------------------------------------------
scoop directive - `static setter`
-------------------------------------------------------------------------------

<pre>
<b>static setter</b> <i>propertyName</i> (<i>parameter list</i>)
</pre>

The `static setter` directive defines a property setter for the previously
defined class.

The JavaScript code following this directive becomes 
the body of the setter function for the property.

Note that this directive generates code that makes use of the 
ECMAScript 5 property accessor APIs.

-------------------------------------------------------------------------------
scoop directive - `method`
-------------------------------------------------------------------------------

<pre>
<b>method</b>
<b>method</b> (<i>parameter list</i>)
</pre>

The `method` directive defines an instance method for the previously defined
class.
It can optionally define a parameter list for the method.

The JavaScript code following this directive becomes 
the body of the method.

-------------------------------------------------------------------------------
scoop directive - `getter`
-------------------------------------------------------------------------------

<pre>
<b>getter</b> <i>propertyName</i>
</pre>

The `getter` directive defines a property getter for instances of the previously
defined class.

The JavaScript code following this directive becomes 
the body of the getter function for the property.

Note that this directive generates code that makes use of the 
ECMAScript 5 property accessor APIs.


-------------------------------------------------------------------------------
scoop directive - `setter`
-------------------------------------------------------------------------------

<pre>
<b>setter</b> <i>propertyName</i> (<i>parameter list</i>)
</pre>

The `setter` directive defines a property setter for instances of the previously
defined class.

The JavaScript code following this directive becomes 
the body of the setter function for the property.

Note that this directive generates code that makes use of the 
ECMAScript 5 property accessor APIs.

-------------------------------------------------------------------------------
scoop directive - `init`
-------------------------------------------------------------------------------

<pre>
<b>init</b>
</pre>

The JavaScript code following this directive is left
unadorned in the resulting JavaScript file. It's similar to
Java's static initializer blocks.

-------------------------------------------------------------------------------
scoop directive - `function`
-------------------------------------------------------------------------------

<pre>
<b>function</b>
<b>function</b> (<i>parameter list</i>)
</pre>

The `function` directive defines a function defined globally within the
module's scope.
It can optionally define a parameter list for the function.

The JavaScript code following this directive becomes 
the body of the function.

-------------------------------------------------------------------------------
scoop directive - `require`
-------------------------------------------------------------------------------

<pre>
<b>require <i>moduleName</i></b><br>
<b>require <i>moduleName</i> as <i>variableName</i></b><br>
</pre>

The `require` directive is used to generate a `require()` function within the
module.  The specified module is assigned to a variable name which
is the _basename_ of the moduleName.  Optionally, you may specify the
variable name which gets used by using the _as_ form.

The JavaScript code following this directive not otherwise processed.

-------------------------------------------------------------------------------
scoop directive - `requireClass`
-------------------------------------------------------------------------------

<pre>
<b>requireClass <i>moduleName</i></b><br>
<b>requireClass <i>moduleName</i> as <i>variableName</i></b><br>
</pre>

Same as the `require` directive, but `getClass()` is called on the
object returned from the `require()` function, which is presumably
the first class defined in the scoop module.


-------------------------------------------------------------------------------
Running the `scoopc.py` compiler
===============================================================================

The command line for `scoopc.py` is as follows:

    scoopc.py [options] FILE FILE ...

`scoopc.py` converts `.scoop` files to `.js` files.  `FILE` can be a `.scoop` 
file or a directory
of `.scoop` files.  Each `.scoop` file is converted to a  root module, and each
directory of `.scoop` files is considered a root for it's contained `.scoop` files
(the directory name `FILE` is not part of the module name.
    
Options:
    --version          show program's version number and exit
    -h, --help         show this help message and exit
    -o DIR, --out=DIR  generate .js files in DIR (default: .)
    -q, --quiet        be quiet
    -v, --verbose      be noisy

-------------------------------------------------------------------------------
Copyright / License
===============================================================================

Copyright (c) 2010 Patrick Mueller

Licensed under the 
[MIT license](http://www.opensource.org/licenses/mit-license.php)
