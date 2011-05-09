#!/usr/bin/env node

directive = require("directive")

VERSION = "1.1.0"

//--------------------------------------------------------------------
function compile(source, fileName) {
    var dr = new directive.DirectiveReader(source, fileName)

    var handler = {
        processDirective: handle_processDirective,
        fileBegin:        handle_fileBegin,
        fileEnd:          handle_fileEnd,
        contents:         []
    }
    
    dr.process(handler)
    
    process.stdout.write(handler.contents.join("\n"))
}

//--------------------------------------------------------------------
function compileForNode(module, fileName) {
    var fs     = require("fs")
    var source = fs.readFileSync(filename, "utf8")
    var js     = compile(source, fileName)
    
    return module._compile(js, fileName)
}

//--------------------------------------------------------------------
function handle_processDirective(info) {
    var h = this
    var d = info.directive
    
    d.comments.forEach(function(line) {
        h.contents.push(line)
    })

    h.contents.push(d.name + " " + d.args)
    
    d.body.forEach(function(line) {
        h.contents.push(line)
    })
}

//--------------------------------------------------------------------
function handle_fileBegin(info) {
    log("starting: " + info.fileName)
}

//--------------------------------------------------------------------
function handle_fileEnd(info) {
    log("finished: " + info.fileName)
    if (info.error) {
        log("error: " + info.error)
    }
    
    var source = this.contents.join("\n")
    
}

//--------------------------------------------------------------------
function log(message) {
    process.stderr.write(PROGRAM + ": " + message + "\n")
}

//--------------------------------------------------------------------
function error(message) {
    log(message)
    process.exit(1)
}

//--------------------------------------------------------------------
// exports
//--------------------------------------------------------------------
exports.compile = compile
exports.version = VERSION

//--------------------------------------------------------------------
// install scoop compiler for node
//--------------------------------------------------------------------
if (require.extensions) {
    require.extensions[".scoop"] = compileForNode
}