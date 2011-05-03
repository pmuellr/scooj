
//-----------------------------------------------------------------------------
// Copyright (c) 2010 Patrick Mueller
// Licensed under the MIT license: 
// http://www.opensource.org/licenses/mit-license.php
//-----------------------------------------------------------------------------

require("scooj").installGlobals()

var Point3 = require("./Point3").getClass()

//----------------------------------------------------------------------------
defClass(module, Point3, function Point4(properties) {
    $super(this, null, properties)
})

//----------------------------------------------------------------------------
var $super = defSuper(module)

//----------------------------------------------------------------------------
defMethod(module, function add(aPoint) {
    var result = $super(this, "add", aPoint)
    
    if (aPoint.a) {
        result.a += aPoint.a
    }
    
    return result
})

//----------------------------------------------------------------------------
defMethod(module, function toString() {
    return $super(this, "toString")
})


