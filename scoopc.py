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
    for lineNo, line in enumerate(lines):
        if patternDirective.match(line):
            directive = Directive.fromLine(line, lineNo)
            if None == directive:
                error("%s:%d unknown directive found: '%s'" % (iFileName, lineNo, line))
            
            directives.append(directive)
            
    paddedDirectives      = [None, None]
    paddedDirectives[1:1] = directives
    
    for index, directive in enumerate(paddedDirectives):
        if None == directive: continue
        
        prevDirective = paddedDirectives[index-1]
        nextDirective = paddedDirectives[index+1]

        directive.calculateBodyAndComments(lines, prevDirective, nextDirective)        
            
    firstDirective = True
    for directive in directives:
        directive.compile(firstDirective)
        firstDirective = False
        
    lines = []
    className = "???"
    for directive in directives:
        comments = "\n".join(directive.comments)
        body     = "\n".join(directive.body)
        line     = directive.line
        
        if directive.getClassName(): className = directive.getClassName()
        
        if directive.isSuperReplaceable():
            body = replaceSuperInvocations(className, directive.getMethodName(), body)
        
        if len(comments): comments = "%s\n" % comments
        if len(body):     body     = "\n%s" % body
        lines.append("%s%s%s" % (comments, line, body))

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
#
#-------------------------------------------------------------------------------
class Directive:
    
    classes = []

    #---------------------------------------------------------------------------
    @staticmethod
    def fromLine(line, lineNo):
        for cls in Directive.classes:
            if cls.match(line):
                return cls(line, lineNo)
                
        return None
    
    #---------------------------------------------------------------------------
    def __init__(self, line, lineNo):
        self.line     = line
        self.lineNo   = lineNo
        self.comments = []
        self.body     = []

    #---------------------------------------------------------------------------
    def compile(self, firstDirective):
        raise Exception("subclass responsibility")

    #---------------------------------------------------------------------------
    def firstDirectivePrefix(self):
        return "var scooj = require('scooj'); "

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
    def getClassName(self):  return None
    def getMethodName(self): return None
    
    def isSuperReplaceable(self): return False
        

#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
class DirectiveClass(Directive):
    matchPattern = re.compile("^class\s+([\w$_]+)\s*(\(.*\))?\s*(<\s*([\w$_]+))?\s*$")

    #---------------------------------------------------------------------------
    @staticmethod
    def match(line):
        return DirectiveClass.matchPattern.match(line)
    
    #---------------------------------------------------------------------------
    def __init__(self, line, lineNo):
        Directive.__init__(self, line, lineNo)

    #---------------------------------------------------------------------------
    def compile(self, firstDirective):
        match = DirectiveClass.matchPattern.match(self.line)
        
        className      = match.group(1)
        methodParms    = match.group(2)
        superclassName = match.group(4)
        
        self.className = className
        
        if not methodParms: methodParms = "()"

        self.line = "var %s = scooj.defClass(module, %sfunction %s%s {" 
        
        if not superclassName:
            superclassText = ""
        else:
            superclassText = "%s, " % superclassName

        self.line = self.line % (className, superclassText, className, methodParms)
        
        if firstDirective: self.line = "%s%s" % (self.firstDirectivePrefix(), self.line)
            
        if 0 == len(self.body):
            self.body += "});"
        
        else:
            self.body[len(self.body)-1] = self.body[len(self.body)-1] + "});"
            
    #---------------------------------------------------------------------------
    def getClassName(self):  return self.className
    def getMethodName(self): return None
    
    def isSuperReplaceable(self): return True
        
#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
class DirectiveStaticMethod(Directive):
    matchPattern = re.compile("^static\s+method\s+([\w$_]+)\s*(\(.*\))?\s*$")

    #---------------------------------------------------------------------------
    @staticmethod
    def match(line):
        return DirectiveStaticMethod.matchPattern.match(line)
    
    #---------------------------------------------------------------------------
    def __init__(self, line, lineNo):
        Directive.__init__(self, line, lineNo)

    #---------------------------------------------------------------------------
    def compile(self, firstDirective):
        match = DirectiveStaticMethod.matchPattern.match(self.line)
        
        methodName  = match.group(1)
        methodParms = match.group(2)
        
        self.methodName = methodName
        
        if not methodParms: methodParms = "()"
        
        self.line = "scooj.defStaticMethod(function %s%s {" 
        
        self.line = self.line % (methodName, methodParms)
            
        if firstDirective: self.line = "%s%s" % (self.firstDirectivePrefix(), self.line)
            
        if 0 == len(self.body):
            self.body += "});"
        
        else:
            self.body[len(self.body)-1] = self.body[len(self.body)-1] + "});"

    #---------------------------------------------------------------------------
    def getMethodName(self):  return self.methodName
        
#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
class DirectiveMethod(Directive):
    matchPattern = re.compile("^method\s+([\w$_]+)\s*(\(.*\))?\s*$")

    #---------------------------------------------------------------------------
    @staticmethod
    def match(line):
        return DirectiveMethod.matchPattern.match(line)
    
    #---------------------------------------------------------------------------
    def __init__(self, line, lineNo):
        Directive.__init__(self, line, lineNo)

    #---------------------------------------------------------------------------
    def compile(self, firstDirective):
        match = DirectiveMethod.matchPattern.match(self.line)
        
        methodName  = match.group(1)
        methodParms = match.group(2)
        
        self.methodName = methodName

        if not methodParms: methodParms = "()"
        
        self.line = "scooj.defMethod(function %s%s {" 
        
        self.line = self.line % (methodName, methodParms)
            
        if firstDirective: self.line = "%s%s" % (self.firstDirectivePrefix(), self.line)
            
        if 0 == len(self.body):
            self.body += "});"
        
        else:
            self.body[len(self.body)-1] = self.body[len(self.body)-1] + "});"

    #---------------------------------------------------------------------------
    def getMethodName(self):  return self.methodName
    
    def isSuperReplaceable(self): return True
        
#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
class DirectiveFunction(Directive):
    matchPattern = re.compile("^function\s+([\w$_]+)\s*(\(.*\))?\s*$")

    #---------------------------------------------------------------------------
    @staticmethod
    def match(line):
        return DirectiveFunction.matchPattern.match(line)
    
    #---------------------------------------------------------------------------
    def __init__(self, line, lineNo):
        Directive.__init__(self, line, lineNo)

    #---------------------------------------------------------------------------
    def compile(self, firstDirective):
        match = DirectiveFunction.matchPattern.match(self.line)
        
        functionName  = match.group(1)
        functionParms = match.group(2)

        if not functionParms: functionParms = "()"
        
        self.line = "var %s = function %s%s {" 
        
        self.line = self.line % (functionName, functionName, functionParms)
            
        if firstDirective: self.line = "%s%s" % (self.firstDirectivePrefix(), self.line)
            
        if 0 == len(self.body):
            self.body += "};"
        
        else:
            self.body[len(self.body)-1] = self.body[len(self.body)-1] + "};"
            
        
#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
class DirectiveStatic(Directive):
    matchPattern = re.compile("^static\s*$")

    #---------------------------------------------------------------------------
    @staticmethod
    def match(line):
        return DirectiveStatic.matchPattern.match(line)
    
    #---------------------------------------------------------------------------
    def __init__(self, line, lineNo):
        Directive.__init__(self, line, lineNo)

    #---------------------------------------------------------------------------
    def compile(self, firstDirective):
        self.line = ""

        if firstDirective: self.line = "%s%s" % (self.firstDirectivePrefix(), self.line)
        
#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
class DirectiveRequire(Directive):
    matchPattern = re.compile("^require\s+([\w$\.\-/]+)(\s+as\s+([\w$.-]+))?\s*$")

    #---------------------------------------------------------------------------
    @staticmethod
    def match(line):
        return DirectiveRequire.matchPattern.match(line)
    
    #---------------------------------------------------------------------------
    def __init__(self, line, lineNo):
        Directive.__init__(self, line, lineNo)

    #---------------------------------------------------------------------------
    def compile(self, firstDirective):
        match = DirectiveRequire.matchPattern.match(self.line)
        
        moduleName = match.group(1)
        varName    = match.group(3)
        
        if not varName: varName = os.path.basename(moduleName)
        
        self.line = "var %s = require('%s');" % (varName, moduleName)
        
        if firstDirective: self.line = "%s%s" % (self.firstDirectivePrefix(), self.line)
        
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
def parseArgs():
    usage        = "usage: %s [options] FILE FILE ..." % PROGRAM
    version      = "%s %s" % (PROGRAM,VERSION)
    description  = getHelp()
        
    parser = optparse.OptionParser(usage=usage, version=version, description=description)
    
    parser.add_option("-o", "--out", dest="dirName", metavar="DIR", default=".",
        help="generate .js files in DIR (default: %default)"
    )
    
    parser.add_option("-t", "--transportD", dest="transportD", action="store_true", default=False,
        help="generate Transport/D compatible module files"
    )
    
    parser.add_option("-q", "--quiet", dest="quiet", action="store_true", default=False,
        help="be quiet"
    )
    
    parser.add_option("-f", "--framework", dest="framework", metavar="FRAMEWORK", default="scooj",
        help="framework to generate for - one of 'scooj' or 'dojo'"
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

