#!/usr/bin/env python

#-------------------------------------------------------------------------------
# Copyright (c) 2010 Patrick Mueller
# 
# The MIT License - see: http://www.opensource.org/licenses/mit-license.php
#-------------------------------------------------------------------------------

import os
import re
import sys
import optparse

PROGRAM = os.path.basename(sys.argv[0])
VERSION = "0.4.0"

ExtensionScoop      = ".scoop"
ExtensionJavaScript = ".js"
ExtensionTransportD = ".transportd.%s" % ExtensionJavaScript

Options = None

#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
def main(): 
    global Options

    (options, iFileNames) = parseArgs()

    Options = options    
    
    for iFileName in iFileNames:
        if not os.path.exists(iFileName):
            error("file does not exist: '%s'" % iFileName)
            
    for iFileName in iFileNames:
        if os.path.isdir(iFileName):
            processDir(iFileName)
        else:
            processFile(iFileName)

#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
def processFile(iFileName, path=""):
    baseName = os.path.basename(iFileName)[:-6]
    oFileName = os.path.join(Options.dirName, path, baseName) + ".js"
    
    with open(iFileName) as iFile:
        contents = iFile.read()

    contents = compile(contents, iFileName, path, baseName)
    
    with open(oFileName, "w") as oFile:
        oFile.write(contents)
    
    log("generated module %s/%s in %s" % (path, baseName, oFileName))

#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
def compile(source, iFileName, path, baseName):
    lines = source.split("\n")
    
    directives = []
    
    patternDirective = re.compile(r"^[\w\$\._@]+")
    lineNo = 0
    for line in lines:
        lineNo += 1
        if patternDirective.match(line):
            directive = Directive.fromLine(line)
            if None == directive:
                error("%s:%d unknown directive found: '%s'" % (iFileName, lineNo, line))
            
            directives.append(directive)
            
    for directive in directives:
        directive.compile()
        
    lines = []
    for directive in directives:
        for comment in directive.comments:
            lines.append(comment)
            
        lines.append(directive.line)

        for body in directive.body:
            lines.append(body)

    return "\n".join(lines)        

#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
def processDir(iDirName, path=""):
    verbose("processDir:  %s path: %s" % (iDirName, path))

    for entry in os.listdir(iDirName):
        fullName = os.path.join(iDirName, entry)
        
        if os.path.isdir(fullName):
            if not entry.startswith("."):
                processDir(fullName, os.path.join(path, entry))
            continue
        
        if entry.endswith(ExtensionScoop):
            processFile(fullName, path)

#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
def parseArgs():
    usage        = "usage: %s [options] FILE FILE ..." % PROGRAM
    version      = "%s %s" % (PROGRAM,VERSION)
    description  = getHelp()
        
    parser = optparse.OptionParser(usage=usage, version=version, description=description)
    
    parser.add_option("-o", "--out", dest="dirName", metavar = "DIR", default=".",
        help="generate .js files in DIR (default: %default)"
    )
    
    parser.add_option("-t", "--transportD", dest="transportD", action="store_true", default=False,
        help="generate Transport/D compatible module files"
    )
    
    parser.add_option("-q", "--quiet", dest="quiet", action="store_true", default=False,
        help="be quiet"
    )
    
    parser.add_option("-v", "--verbose", dest="verbose", action="store_true", default=False,
        help="be noisy"
    )
    
    (options, args) = parser.parse_args()
    
    help = False
    if len(args) == 0:   help = True
    elif args[0] == "?": help = True
    
    if help:
        parser.print_help()
        sys.exit(0)
    
    return (options, args)
    
#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
def verbose(message):
    if not Options.verbose: return
    
    print "%s: %s" % (PROGRAM, message)

#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
def log(message):
    if Options.quiet: return
    
    print "%s: %s" % (PROGRAM, message)

#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
def error(message):
    print "%s: %s" % (PROGRAM, message)
    exit(1)

#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
def errorException(message):
    eType  = str(sys.exc_info()[0])
    eValue = str(sys.exc_info()[1])
    
    error("%s; exception: %s: %s" % (message, eType, eValue))

#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
def getHelp():
    return """
Converts .scoop files to .js files.  FILE can be a .scoop file or
a directory of .scoop files.  Each .scoop file is converted to a 
root module, and each directory of .scoop files is considered a
root for it's contained .scoop files (the directory name FILE is
not part of the module name.
    """.strip()

#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
class Directive:
    
    classes = []

    #---------------------------------------------------------------------------
    @staticmethod
    def fromLine(line):
        for cls in Directive.classes:
            if cls.match(line):
                return cls(line)
                
        return None
    
    #---------------------------------------------------------------------------
    def __init__(self, line):
        self.line     = line
        self.comments = []
        self.body     = []

    #---------------------------------------------------------------------------
    def compile(self):
        raise Exception("subclass responsibility")

    #---------------------------------------------------------------------------
    def comments(self, value=None):
        if None == value: return self.comments
        
        self.comments = value

    #---------------------------------------------------------------------------
    def body(self, value=None):
        if None == value: return self.body
        
        self.body = value

#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
class DirectiveClass(Directive):
    matchPattern = re.compile("^class\s+(.*?)\s*(<<\s*(.*?))?")

    #---------------------------------------------------------------------------
    @staticmethod
    def match(line):
        return DirectiveClass.matchPattern.match(line)
    
    #---------------------------------------------------------------------------
    def __init__(self, line):
        Directive.__init__(self, line)

    #---------------------------------------------------------------------------
    def compile(self):
        self.line = "console.log('compilation of \"" + self.line + "\"')"
        
#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
class DirectiveStaticMethod(Directive):
    matchPattern = re.compile("^static\s+method\s+(.*?)\s*(\((.*?)\))?")

    #---------------------------------------------------------------------------
    @staticmethod
    def match(line):
        return DirectiveStaticMethod.matchPattern.match(line)
    
    #---------------------------------------------------------------------------
    def __init__(self, line):
        Directive.__init__(self, line)

    #---------------------------------------------------------------------------
    def compile(self):
        self.line = "console.log('compilation of \"" + self.line + "\"')"
        
#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
class DirectiveMethod(Directive):
    matchPattern = re.compile("^method\s+(.*?)\s*(\((.*?)\))?")

    #---------------------------------------------------------------------------
    @staticmethod
    def match(line):
        return DirectiveMethod.matchPattern.match(line)
    
    #---------------------------------------------------------------------------
    def __init__(self, line):
        Directive.__init__(self, line)

    #---------------------------------------------------------------------------
    def compile(self):
        self.line = "console.log('compilation of \"" + self.line + "\"')"
        
#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
class DirectiveFunction(Directive):
    matchPattern = re.compile("^function\s+(.*?)\s*(\((.*?)\))?")

    #---------------------------------------------------------------------------
    @staticmethod
    def match(line):
        return DirectiveFunction.matchPattern.match(line)
    
    #---------------------------------------------------------------------------
    def __init__(self, line):
        Directive.__init__(self, line)

    #---------------------------------------------------------------------------
    def compile(self):
        self.line = "console.log('compilation of \"" + self.line + "\"')"
        
#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
class DirectiveStatic(Directive):
    matchPattern = re.compile("^static\s*")

    #---------------------------------------------------------------------------
    @staticmethod
    def match(line):
        return DirectiveStatic.matchPattern.match(line)
    
    #---------------------------------------------------------------------------
    def __init__(self, line):
        Directive.__init__(self, line)

    #---------------------------------------------------------------------------
    def compile(self):
        self.line = "console.log('compilation of \"" + self.line + "\"')"
        
#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
class DirectiveRequire(Directive):
    matchPattern = re.compile("^require\s+(.*?)(\s+as\s+(.*))?")

    #---------------------------------------------------------------------------
    @staticmethod
    def match(line):
        return DirectiveRequire.matchPattern.match(line)
    
    #---------------------------------------------------------------------------
    def __init__(self, line):
        Directive.__init__(self, line)

    #---------------------------------------------------------------------------
    def compile(self):
        self.line = "console.log('compilation of \"" + self.line + "\"')"
        
#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
Directive.classes.extend([
    DirectiveClass,
    DirectiveStaticMethod,
    DirectiveMethod,
    DirectiveFunction,
    DirectiveStatic,
    DirectiveRequire,
])

#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
if __name__ == '__main__':
    main()

