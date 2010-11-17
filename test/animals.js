#!/usr/bin/env node
//-----------------------------------------------------------------------------
// Copyright (c) 2010 Patrick Mueller
// Licensed under the MIT license: 
// http://www.opensource.org/licenses/mit-license.php
//-----------------------------------------------------------------------------

//-----------------------------------------------------------------------------
// the CoffeeScript example: http://jashkenas.github.com/coffee-script/
//-----------------------------------------------------------------------------

require("../scooj").installGlobals()

var Animal = defClass(module, function Animal(name) {
    this.name = name
})

    defMethod(function move(meters){
        console.log(this.name + " moved " + meters + "m.")
    })

var Snake = defClass(module, Animal, function Snake(name) {
    $superSnake(this, null, name)
})

    var $superSnake = defSuper()

    defMethod(function move(meters){
        console.log("Slithering...")
        $superSnake(this, "move", 5)
    })

var Horse = defClass(module, Animal, function Horse(name) {
    $superHorse(this, null, name)
})

    var $superHorse = defSuper()

    defMethod(function move(meters){
        console.log("Galloping...")
        $superSnake(this, "move", 45)
    })

var sam = new Snake("Sammy the Python")
var tom = new Horse("Tommy the Palomino")

sam.move()
tom.move()