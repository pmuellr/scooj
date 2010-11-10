//-----------------------------------------------------------------------------
// Copyright (c) 2010 Patrick Mueller
// Licensed under the MIT license: 
// http://www.opensource.org/licenses/mit-license.php
//-----------------------------------------------------------------------------

//----------------------------------------------------------------------------
defClass(module, function Point2(properties) {
    if (!properties) return
    
    for (var key in properties) {
        this[key] = properties[key]
    }
})

//----------------------------------------------------------------------------
defMethod(function add(aPoint) {
    var result = new this.constructor(this)
    
    result.x += aPoint.x
    result.y += aPoint.y
    
    return result
})

//----------------------------------------------------------------------------
defMethod(function toString() {
    var result = this.constructor.name + "{ "

    result += "x:" + this.x + "; "
    result += "y:" + this.y + "; "
    
    result += "}"
    
    return result
})
