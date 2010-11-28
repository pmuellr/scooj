
//-----------------------------------------------------------------------------
// Copyright (c) 2010 Patrick Mueller
// Licensed under the MIT license: 
// http://www.opensource.org/licenses/mit-license.php
//-----------------------------------------------------------------------------

//-----------------------------------------------------------------------------
// the CoffeeScript example: http://jashkenas.github.com/coffee-script/
//-----------------------------------------------------------------------------

require("scooj").installGlobals()

//-----------------------------------------------------------------------------
var Animal = defClass(module, function Animal(name) {
    this.name = name
})

    defStaticMethod(function report(message) {
        if (!Animal.reports) Animal.reports = []
        Animal.reports.push(message)
    })
    
    defStaticMethod(function getReports() {
        if (!Animal.reports) Animal.reports = []
        return Animal.reports
    })
    
    defMethod(function move(meters){
        Animal.report(this.name + " moved " + meters + "m.")
    })


//-----------------------------------------------------------------------------
var Snake = defClass(module, Animal, function Snake(name) {
    $superSnake(this, null, name)
})

    var $superSnake = defSuper()

    defMethod(function move(meters){
        Animal.report("Slithering...")
        $superSnake(this, "move", 5)
    })

//-----------------------------------------------------------------------------
var Horse = defClass(module, Animal, function Horse(name) {
    $superHorse(this, null, name)
})

    var $superHorse = defSuper()

    defMethod(function move(meters){
        Animal.report("Galloping...")
        $superSnake(this, "move", 45)
    })

//-----------------------------------------------------------------------------
var sam = new Snake("Sammy the Python")
var tom = new Horse("Tommy the Palomino")

sam.move()
tom.move()

//-----------------------------------------------------------------------------
function assertEqual(x,y) {
    if (x != y) throw new Exception(x + " != " + y)
    return true
}

//-----------------------------------------------------------------------------
var messages = Animal.getReports()

assertEqual(4, messages.length)
assertEqual(messages[0], "Slithering...")
assertEqual(messages[1], "Sammy the Python moved 5m.")
assertEqual(messages[2], "Galloping...")
assertEqual(messages[3], "Tommy the Palomino moved 45m.")

console.log("module: " + module.id + ": all tests pass")