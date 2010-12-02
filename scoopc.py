#!/usr/bin/env python

#-------------------------------------------------------------------------------
# Copyright (c) 2010 Patrick Mueller
# Licensed under the MIT license: 
# http://www.opensource.org/licenses/mit-license.php
#-------------------------------------------------------------------------------

import os
import re
import sys
import optparse

PROGRAM = os.path.basename(sys.argv[0])
VERSION = "1.1.0"

ExtensionScoop      = ".scoop"
ExtensionJavaScript = ".js"

Options = None

#-------------------------------------------------------------------------------
# main program
#-------------------------------------------------------------------------------
def main(): 
    global Options

    (options, iFileNames) = parseArgs()

    Options = options    
    
    # make sure files exist
    for iFileName in iFileNames:
        if not os.path.exists(iFileName):
            error("file does not exist: '%s'" % iFileName)
         
    # for each file/path, process it
    for iFileName in iFileNames:
        if os.path.isdir(iFileName):
            processDir(iFileName)
        else:
            processFile(iFileName)

#-------------------------------------------------------------------------------
# process a file
#-------------------------------------------------------------------------------
def processFile(iFileName, path=""):
    baseName = os.path.basename(iFileName)[:-6]
    oFileName = os.path.join(Options.dirName, path, baseName) + ".js"
    
    # read the file
    with open(iFileName) as iFile:
        contents = iFile.read()

    # compile the contents
    contents = compile(contents, iFileName, path, baseName)
    
    # create output directory
    oDir = os.path.dirname(oFileName)
    if not os.path.exists(oDir):
        os.makedirs(oDir)
        
    # write output file
    with open(oFileName, "w") as oFile:
        oFile.write(contents)
    
    log("generated module %s/%s in %s" % (path, baseName, oFileName))

#-------------------------------------------------------------------------------
# process a directory
#-------------------------------------------------------------------------------
def processDir(iDirName, path=""):
    verbose("processDir:  %s path: %s" % (iDirName, path))

    # get entries in directory
    for entry in os.listdir(iDirName):
        fullName = os.path.join(iDirName, entry)
        
        # recursively process subdirectories
        if os.path.isdir(fullName):
            if not entry.startswith("."):
                processDir(fullName, os.path.join(path, entry))
            continue
        
        # if it's a scoop file, process it
        if entry.endswith(ExtensionScoop):
            processFile(fullName, path)

#-------------------------------------------------------------------------------
# compile a scoop file
#-------------------------------------------------------------------------------
def compile(source, iFileName, path, baseName):

    # split file into lines
    lines = source.split("\n")

    # initialize directive list    
    directives = []
    
    # get the directives from the lines
    patternDirective = re.compile(r"^[\w\$\._@]+")
    for lineNo, line in enumerate(lines):
        if patternDirective.match(line):
            directive = Directive.fromLine(line, lineNo)
            if None == directive:
                error("%s:%d unknown directive found: '%s'" % (iFileName, lineNo, line))
            
            directives.append(directive)
            
    # calculate the body and comments for the directives
    prevDirective = None
    for index, directive in enumerate(directives):
    
        nextDirective = None
        if index != len(directives) - 1: 
            nextDirective = directives[index+1]

        directive.calculateBodyAndComments(lines, prevDirective, nextDirective)        
        
        prevDirective = directive
    
    # compile the directives
    firstDirective = True
    lastDirective  = None
    for directive in directives:
        directive.compile()
        
        if firstDirective:
            firstDirective = False
            directive.line = ";var scooj = require('scooj'); %s" % directive.line
        else:
            directive.line = "%s%s" % (lastDirective.endingSuffix(), directive.line)
            
        lastDirective = directive
        
    if lastDirective:
        suffix = lastDirective.endingSuffix()
        if suffix == "": suffix = ";"
        lastDirective.body.append(suffix)    
        
    # generate the output
    lines = []
    className = "???"
    for directive in directives:
        comments = "\n".join(directive.comments)
        body     = "\n".join(directive.body)
        line     = directive.line
        
        # replace super invocations
        if directive.getClassName(): className = directive.getClassName()
        
        if directive.isSuperReplaceable():
            body = replaceSuperInvocations(className, directive.getMethodName(), body)
        
        if len(directive.comments): comments = "%s\n" % comments
        if len(directive.body):     body     = "\n%s" % body
        lines.append("%s%s%s" % (comments, line, body))

    # return the compiled content
    return "\n".join(lines)        

#-------------------------------------------------------------------------------
# replace super method invocations
#-------------------------------------------------------------------------------
def replaceSuperInvocations(className, methodName, methodBody):
    pattern1 = re.compile(r"([^\w\$])super\(\s*\)")
    pattern2 = re.compile(r"([^\w\$])super\(")
    pattern3 = re.compile(r"([^\w\$])super\.([\w\$]*)\(\s*\)")
    pattern4 = re.compile(r"([^\w\$])super\.([\w\$]*)\(")
    
    if not methodName:
        methodName = "null"
    else:
        methodName = '"%s"' % methodName
    
    methodBody = pattern1.sub(r'\1' + className + r'.$super(this, ' + methodName + ')', methodBody)
    methodBody = pattern2.sub(r'\1' + className + r'.$super(this, ' + methodName + ',', methodBody)
    methodBody = pattern3.sub(r'\1' + className + r'.$super(this, "\2")'              , methodBody)
    methodBody = pattern4.sub(r'\1' + className + r'.$super(this, "\2", '             , methodBody)
    
    return methodBody

#-------------------------------------------------------------------------------
# base directive
#-------------------------------------------------------------------------------
class Directive:
    
    classes = []

    #---------------------------------------------------------------------------
    @staticmethod
    def fromLine(line, lineNo):
        for cls in Directive.classes:
            match = cls.match(line)
            if match:
                return cls(line, lineNo, match)
                
        return None
    
    #---------------------------------------------------------------------------
    @classmethod
    def match(cls, line):
        return cls.matchPattern.match(line)
        
    #---------------------------------------------------------------------------
    def __init__(self, line, lineNo, match):
        self.line     = line
        self.lineNo   = lineNo
        self.match    = match
        self.comments = []
        self.body     = []

    #---------------------------------------------------------------------------
    def compile(self):
        raise Exception("subclass responsibility")

    #---------------------------------------------------------------------------
    def endingSuffix(self):
        return ""

    #---------------------------------------------------------------------------
    def calculateBodyAndComments(self, lines, prevDirective, nextDirective):
        if None == prevDirective:
            self.comments = lines[0 : self.lineNo]
        else:
            prevBodyIndex = prevDirective.lineNo + len(prevDirective.body)
            self.comments = lines[prevBodyIndex+1 : self.lineNo]
            
        if None == nextDirective:
            self.body = lines[self.lineNo + 1 : ]
            return
            
        self.body = lines[self.lineNo + 1 : nextDirective.lineNo - 1]

    #---------------------------------------------------------------------------
    def getClassName(self):       return None
    def getMethodName(self):      return None
    def isSuperReplaceable(self): return False

#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
class DirectiveClass(Directive):

    matchPattern = re.compile("^class\s+([\w$_]+)\s*(\(.*\))?\s*(<\s*(\S+))?\s*$")

    #---------------------------------------------------------------------------
    def __init__(self, line, lineNo, match):
        Directive.__init__(self, line, lineNo, match)

    #---------------------------------------------------------------------------
    def compile(self):
        className      = self.match.group(1)
        methodParms    = self.match.group(2)
        superclassName = self.match.group(4)
        
        self.className = className
        
        if not methodParms: methodParms = "()"
        
        if not superclassName:
            superclassText = ""
        else:
            superclassText = "%s, " % superclassName

        self.line = "var %s = scooj.defClass(module, %sfunction %s%s {" 
        self.line = self.line % (className, superclassText, className, methodParms)
            
    #---------------------------------------------------------------------------
    def endingSuffix(self):
        return "}); "

    #---------------------------------------------------------------------------
    def getClassName(self):       return self.className
    def isSuperReplaceable(self): return True
        
#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
class DirectiveMixin(Directive):

    matchPattern = re.compile("^mixin\s+(\S+)\s*$")

    #---------------------------------------------------------------------------
    def __init__(self, line, lineNo, match):
        Directive.__init__(self, line, lineNo, match)

    #---------------------------------------------------------------------------
    def compile(self):
        extensionName  = self.match.group(1)

        self.line = "scooj.useMixin(module, %s)" 
        self.line = self.line % (extensionName)
        
#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
class DirectiveStaticMethod(Directive):

    matchPattern = re.compile("^static\s+method\s+([\w$_]+)\s*(\(.*\))?\s*$")

    #---------------------------------------------------------------------------
    def __init__(self, line, lineNo, match):
        Directive.__init__(self, line, lineNo, match)

    #---------------------------------------------------------------------------
    def compile(self):
        methodName  = self.match.group(1)
        methodParms = self.match.group(2)
        
        self.methodName = methodName
        
        if not methodParms: methodParms = "()"
        
        self.line = "scooj.defStaticMethod(module, function %s%s {" 
        self.line = self.line % (methodName, methodParms)
            
    #---------------------------------------------------------------------------
    def endingSuffix(self):
        return "}); "

    #---------------------------------------------------------------------------
    def getMethodName(self):  return self.methodName
        
#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
class DirectiveStaticGetter(Directive):

    matchPattern = re.compile("^static\s+getter\s+([\w$_]+)\s*$")
    
    #---------------------------------------------------------------------------
    def __init__(self, line, lineNo, match):
        Directive.__init__(self, line, lineNo, match)

    #---------------------------------------------------------------------------
    def compile(self):
        methodName  = self.match.group(1)
        
        self.methodName = methodName
        
        self.line = "scooj.defStaticGetter(module, function %s() {" 
        self.line = self.line % (methodName)
            
    #---------------------------------------------------------------------------
    def endingSuffix(self):
        return "}); "

    #---------------------------------------------------------------------------
    def getMethodName(self):  return self.methodName
        
#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
class DirectiveStaticSetter(Directive):

    matchPattern = re.compile("^static\s+setter\s+([\w$_]+)\s*(\(.*\))\s*$")

    #---------------------------------------------------------------------------
    def __init__(self, line, lineNo, match):
        Directive.__init__(self, line, lineNo, match)

    #---------------------------------------------------------------------------
    def compile(self):
        methodName  = self.match.group(1)
        methodParms = self.match.group(2)
        
        self.methodName = methodName
        
        self.line = "scooj.defStaticSetter(module, function %s%s {" 
        self.line = self.line % (methodName, methodParms)
            
    #---------------------------------------------------------------------------
    def endingSuffix(self):
        return "}); "

    #---------------------------------------------------------------------------
    def getMethodName(self):  return self.methodName
        
#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
class DirectiveMethod(Directive):

    matchPattern = re.compile("^method\s+([\w$_]+)\s*(\(.*\))?\s*$")

    #---------------------------------------------------------------------------
    def __init__(self, line, lineNo, match):
        Directive.__init__(self, line, lineNo, match)

    #---------------------------------------------------------------------------
    def compile(self):
        methodName  = self.match.group(1)
        methodParms = self.match.group(2)
        
        self.methodName = methodName

        if not methodParms: methodParms = "()"
        
        self.line = "scooj.defMethod(module, function %s%s {" 
        self.line = self.line % (methodName, methodParms)
            
    #---------------------------------------------------------------------------
    def endingSuffix(self):
        return "}); "

    #---------------------------------------------------------------------------
    def getMethodName(self):      return self.methodName
    def isSuperReplaceable(self): return True
        
#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
class DirectiveGetter(Directive):

    matchPattern = re.compile("^getter\s+([\w$_]+)\s*$")

    #---------------------------------------------------------------------------
    def __init__(self, line, lineNo, match):
        Directive.__init__(self, line, lineNo, match)

    #---------------------------------------------------------------------------
    def compile(self):
        methodName  = self.match.group(1)
        
        self.methodName = methodName
        
        self.line = "scooj.defGetter(module, function %s() {" 
        self.line = self.line % (methodName)
            
    #---------------------------------------------------------------------------
    def endingSuffix(self):
        return "}); "

    #---------------------------------------------------------------------------
    def getMethodName(self):      return self.methodName
    def isSuperReplaceable(self): return True
        
#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
class DirectiveSetter(Directive):

    matchPattern = re.compile("^setter\s+([\w$_]+)\s*(\(.*\))\s*$")
    
    #---------------------------------------------------------------------------
    def __init__(self, line, lineNo, match):
        Directive.__init__(self, line, lineNo, match)

    #---------------------------------------------------------------------------
    def compile(self):
        methodName  = self.match.group(1)
        methodParms = self.match.group(2)
        
        self.methodName = methodName
        
        self.line = "scooj.defSetter(module, function %s%s {" 
        self.line = self.line % (methodName, methodParms)
            
    #---------------------------------------------------------------------------
    def endingSuffix(self):
        return "}); "

    #---------------------------------------------------------------------------
    def getMethodName(self):      return self.methodName
    def isSuperReplaceable(self): return True
        
#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
class DirectiveFunction(Directive):

    matchPattern = re.compile("^function\s+([\w$_]+)\s*(\(.*\))?\s*$")

    #---------------------------------------------------------------------------
    def __init__(self, line, lineNo, match):
        Directive.__init__(self, line, lineNo, match)

    #---------------------------------------------------------------------------
    def compile(self):
        functionName  = self.match.group(1)
        functionParms = self.match.group(2)

        if not functionParms: functionParms = "()"
        
        self.line = "var %s = function %s%s {" 
        self.line = self.line % (functionName, functionName, functionParms)
            
    #---------------------------------------------------------------------------
    def endingSuffix(self):
        return "}; "
        
#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
class DirectiveStatic(Directive):

    matchPattern = re.compile("^static\s*$")
    
    #---------------------------------------------------------------------------
    def __init__(self, line, lineNo, match):
        Directive.__init__(self, line, lineNo, match)

    #---------------------------------------------------------------------------
    def compile(self):
        self.line = "// static code run on first require()"

#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
class DirectiveRequire(Directive):

    matchPattern = re.compile("^require\s+([\w$\.\-/]+)(\s+as\s+([\w$.-]+))?\s*$")
    
    #---------------------------------------------------------------------------
    def __init__(self, line, lineNo, match):
        Directive.__init__(self, line, lineNo, match)

    #---------------------------------------------------------------------------
    def compile(self):
        moduleName = self.match.group(1)
        varName    = self.match.group(3)
        
        if not varName: varName = os.path.basename(moduleName)
        
        self.line = "var %s = require('%s');" % (varName, moduleName)
        
#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
Directive.classes.extend([
    DirectiveClass,
    DirectiveMixin,
    DirectiveStaticMethod,
    DirectiveStaticGetter,
    DirectiveStaticSetter,
    DirectiveMethod,
    DirectiveGetter,
    DirectiveSetter,
    DirectiveFunction,
    DirectiveStatic,
    DirectiveRequire,
])

#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
def parseArgs():
    usage        = "usage: %s [options] FILE FILE ..." % PROGRAM
    version      = "%s %s" % (PROGRAM,VERSION)
    description  = getHelp()
        
    parser = optparse.OptionParser(usage=usage, version=version, description=description)
    
    parser.add_option("-o", "--out", dest="dirName", metavar="DIR", default=".",
        help="generate .js files in DIR (default: %default)"
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
if __name__ == '__main__':
    main()

