#!/usr/bin/env python

#-------------------------------------------------------------------------------
# Copyright (c) 2010 Patrick Mueller
# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license.php
#-------------------------------------------------------------------------------

import os
import re
import sys
import subprocess
import optparse

PROGRAM = os.path.basename(sys.argv[0])
VERSION = "1.1.0"

ExtensionScoop      = ".scoop"
ExtensionJavaScript = ".coffee"

Options = None

CompileErrors = 0

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
def processFile(iFileName, path=""):
    baseName = os.path.basename(iFileName)[:-6]
    oFileName = os.path.join(Options.dirName, path, baseName) + ExtensionJavaScript

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
def compile(source, iFileName, path, baseName):

    # split file into lines
    lines = source.split("\n")

    # initialize directive list
    directives = []

    # get the directives from the lines
    patternDirective = re.compile(r"^[\w\$\._@]+")
    for lineNo, line in enumerate(lines):
        if patternDirective.match(line):
            directive = Directive.fromLine(iFileName, line, lineNo)
            if None == directive:
                errorFile(iFileName, lineNo, "unknown directive found: '%s'" % line)

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
            directive.comments = """
#-------------------------------------------------------------------------------
# weinre is available under *either* the terms of the modified BSD license *or* the
# MIT License (2008). See http:#opensource.org/licenses/alphabetical for full text.
#
# Copyright (c) 2010, 2011 IBM Corporation
#-------------------------------------------------------------------------------
""".split("\n")

        else:
            directive.line = "%s%s" % (lastDirective.endingSuffix(), directive.line)

        lastDirective = directive

    if lastDirective:
        suffix = lastDirective.endingSuffix()
#        if suffix == "": suffix = ";"
        lastDirective.body.append(suffix)

    # generate the output
    lines = []
    className = "???"
    firstClass = True
    reComment2 = re.compile(r"^  //")
    reCommentA = re.compile(r"\s*//")

    for directive in directives:
        if directive.isFunction(): continue

        directive.comments = [reComment2.sub("  #",line) for line in directive.comments]
        directive.comments = [reCommentA.sub("#",  line) for line in directive.comments]

        comments = "\n".join(directive.comments)
        body     = "\n".join(directive.body)
        line     = directive.line

        # replace super invocations
        if directive.getClassName(): className = directive.getClassName()

        if directive.isSuperReplaceable():
            body = replaceSuperInvocations(className, directive.getMethodName(), body)

        if directive.isClass():
            if firstClass:
                firstClass = False

                line = "module.exports = %s" % line

        if len(directive.comments): comments = "%s\n" % comments
        if len(directive.body):     body     = "\n%s" % body
        lines.append("%s%s%s" % (comments, line, body))

        if directive.isClass():
            if firstClass: firstClass = False

    for directive in directives:
        if not directive.isFunction(): continue

        directive.comments = [reComment2.sub("  #",line) for line in directive.comments]
        directive.comments = [reCommentA.sub("#",  line) for line in directive.comments]

        comments = "\n".join(directive.comments)
        body     = "\n".join(directive.body)
        line     = directive.line

        if len(directive.comments): comments = "%s\n" % comments
        if len(directive.body):     body     = "\n%s" % body
        lines.append("%s%s%s" % (comments, line, body))

    # return the compiled content
    lines = [fixComment(line) for line in lines]

    return "\n".join(lines)

#-------------------------------------------------------------------------------
returnPattern = re.compile(r".*\s*return\s*$")

#-------------------------------------------------------------------------------
def fixComment(line):
    comm_old_c = "#-----------------------------------------------------------------------------"
    comm_new_c = "#-------------------------------------------------------------------------------"
    comm_old_m = "  #-----------------------------------------------------------------------------"
    comm_new_m = "    #---------------------------------------------------------------------------"

    line = line.replace(comm_old_m, comm_new_m)
    line = line.replace(comm_old_c, comm_new_c)

    return line

#-------------------------------------------------------------------------------
def fixReturns(body):
    body = body.split("\n")
    newBody = []

    for line in body:
        if returnPattern.match(line):
            line = "%s;" % line

        newBody.append(line)
    return "\n".join(newBody)

#-------------------------------------------------------------------------------
def replaceSuperInvocations(className, methodName, methodBody):
    if True: return methodBody

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
def js2cs(body, params, indent):
    global CompileErrors
    origBody = body

    if params == "": params = "()"

#    body = fixReturns(body)
    body = "function __x__%s {\n%s\n}" % (params, body.rstrip())

    process = subprocess.Popen(["js2coffee"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdout, stderr) = process.communicate(body)

    if (stderr != ""):
        body = "### FIXME compile error\n%s\n###\n" % origBody
        lines = body.split("\n")
        CompileErrors += 1
        print "compile error %d" % CompileErrors

    else:
        lines = stdout.split("\n")[1:]

    return ["%s%s" % (indent,line) for line in lines]

#-------------------------------------------------------------------------------
class Directive:

    classes = []

    #---------------------------------------------------------------------------
    @staticmethod
    def fromLine(fileName, line, lineNo):
        for cls in Directive.classes:
            match = cls.match(line)
            if match:
                return cls(fileName, line, lineNo, match)

        return None

    #---------------------------------------------------------------------------
    @classmethod
    def match(cls, line):
        return cls.matchPattern.match(line)

    #---------------------------------------------------------------------------
    def __init__(self, fileName, line, lineNo, match):
        self.fileName = fileName
        self.line     = line
        self.lineNo   = lineNo
        self.match    = match
        self.comments = []
        self.body     = []

    #---------------------------------------------------------------------------
    def isClass(self):
        return False

    #---------------------------------------------------------------------------
    def isInit(self):
        return False

    #---------------------------------------------------------------------------
    def isFunction(self):
        return False

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
class DirectiveClass(Directive):

    matchPattern = re.compile("^class\s+([\w$_]+)\s*(\(.*\))?\s*(<\s*(\S+))?\s*$")

    #---------------------------------------------------------------------------
    def __init__(self, fileName, line, lineNo, match):
        Directive.__init__(self, fileName, line, lineNo, match)

    #---------------------------------------------------------------------------
    def isClass(self):
        return True

    #---------------------------------------------------------------------------
    def compile(self):
        className      = self.match.group(1)
        methodParms    = self.match.group(2)
        superclassName = self.match.group(4)

        self.className = className

        if not methodParms:
            methodParms = ""
        else:
            methodParms = " " + methodParms

        if not superclassName:
            superclassText = ""
        else:
            superclassText = " extends %s" % superclassName

        line1 = "class %s%s" % (className, superclassText)
        line2 = "    constructor:%s ->" % methodParms

        self.line = "%s\n\n%s" % (line1, line2)

        self.body = js2cs("\n".join(self.body), methodParms, "    ")

    #---------------------------------------------------------------------------
    def endingSuffix(self):
        return ""

    #---------------------------------------------------------------------------
    def getClassName(self):       return self.className
    def isSuperReplaceable(self): return True

#-------------------------------------------------------------------------------
class DirectiveMixin(Directive):

    matchPattern = re.compile("^mixin\s+(\S+)\s*$")

    #---------------------------------------------------------------------------
    def __init__(self, fileName, line, lineNo, match):
        Directive.__init__(self, fileName, line, lineNo, match)

    #---------------------------------------------------------------------------
    def compile(self):
        extensionName  = self.match.group(1)

        self.line = "scooj.useMixin(module, %s)"
        self.line = self.line % (extensionName)

#-------------------------------------------------------------------------------
class DirectiveStaticMethod(Directive):

    matchPattern = re.compile("^static\s+((bind)\s+)?method\s+([\w$_]+)\s*(\(.*\))?\s*$")

    #---------------------------------------------------------------------------
    def __init__(self, fileName, line, lineNo, match):
        Directive.__init__(self, fileName, line, lineNo, match)

    #---------------------------------------------------------------------------
    def compile(self):
        isBound     = self.match.group(2)
        methodName  = self.match.group(3)
        methodParms = self.match.group(4)

        self.methodName = methodName

        if not methodParms:
            methodParms = ""
        else:
            methodParms = " " + methodParms

        self.line = "    @%s:%s ->" % (methodName, methodParms)

        self.comments = ["  %s" % line for line in self.comments]
        self.body = js2cs("\n".join(self.body), methodParms, "    ")

    #---------------------------------------------------------------------------
    def endingSuffix(self):
        return ""

    #---------------------------------------------------------------------------
    def getMethodName(self):  return self.methodName

#-------------------------------------------------------------------------------
class DirectiveStaticGetter(Directive):

    matchPattern = re.compile("^static\s+getter\s+([\w$_]+)\s*$")

    #---------------------------------------------------------------------------
    def __init__(self, fileName, line, lineNo, match):
        Directive.__init__(self, fileName, line, lineNo, match)

    #---------------------------------------------------------------------------
    def compile(self):
        methodName  = self.match.group(1)

        self.methodName = methodName

        self.line = "### FIXME\nstatic getter %s"
        self.line = self.line % (methodName)
        self.body.append("###\n")

    #---------------------------------------------------------------------------
    def endingSuffix(self):
        return ""

    #---------------------------------------------------------------------------
    def getMethodName(self):  return self.methodName

#-------------------------------------------------------------------------------
class DirectiveStaticSetter(Directive):

    matchPattern = re.compile("^static\s+setter\s+([\w$_]+)\s*(\(.*\))\s*$")

    #---------------------------------------------------------------------------
    def __init__(self, fileName, line, lineNo, match):
        Directive.__init__(self, fileName, line, lineNo, match)

    #---------------------------------------------------------------------------
    def compile(self):
        methodName  = self.match.group(1)
        methodParms = self.match.group(2)

        self.methodName = methodName

        self.line = "### FIXME\nstatic setter %s%s"
        self.line = self.line % (methodName, methodParms)
        self.body.append("###\n")

    #---------------------------------------------------------------------------
    def endingSuffix(self):
        return ""

    #---------------------------------------------------------------------------
    def getMethodName(self):  return self.methodName

#-------------------------------------------------------------------------------
class DirectiveMethod(Directive):

    matchPattern = re.compile("^((bind)\s+)?method\s+([\w$_]+)\s*(\(.*\))?\s*$")

    #---------------------------------------------------------------------------
    def __init__(self, fileName, line, lineNo, match):
        Directive.__init__(self, fileName, line, lineNo, match)

    #---------------------------------------------------------------------------
    def compile(self):
        isBound     = self.match.group(2)
        methodName  = self.match.group(3)
        methodParms = self.match.group(4)

        self.methodName = methodName

        if not methodParms:
            methodParms = ""
        else:
            methodParms = " " + methodParms

        self.line = "    %s:%s ->" % (methodName, methodParms)

        self.comments = ["  %s" % line for line in self.comments]
        self.body = js2cs("\n".join(self.body), methodParms, "    ")

    #---------------------------------------------------------------------------
    def endingSuffix(self):
        return ""

    #---------------------------------------------------------------------------
    def getMethodName(self):      return self.methodName
    def isSuperReplaceable(self): return True

#-------------------------------------------------------------------------------
class DirectiveGetter(Directive):

    matchPattern = re.compile("^getter\s+([\w$_]+)\s*$")

    #---------------------------------------------------------------------------
    def __init__(self, fileName, line, lineNo, match):
        Directive.__init__(self, fileName, line, lineNo, match)

    #---------------------------------------------------------------------------
    def compile(self):
        methodName  = self.match.group(1)

        self.methodName = methodName

        self.line = "### FIXME getter %s"
        self.line = self.line % (methodName)
        self.body.append("###\n")

    #---------------------------------------------------------------------------
    def endingSuffix(self):
        return ""

    #---------------------------------------------------------------------------
    def getMethodName(self):      return self.methodName
    def isSuperReplaceable(self): return True

#-------------------------------------------------------------------------------
class DirectiveSetter(Directive):

    matchPattern = re.compile("^setter\s+([\w$_]+)\s*(\(.*\))\s*$")

    #---------------------------------------------------------------------------
    def __init__(self, fileName, line, lineNo, match):
        Directive.__init__(self, fileName, line, lineNo, match)

    #---------------------------------------------------------------------------
    def compile(self):
        methodName  = self.match.group(1)
        methodParms = self.match.group(2)

        self.methodName = methodName

        self.line = "### FIXME setter %s%s"
        self.line = self.line % (methodName, methodParms)
        self.body.append("###\n")

    #---------------------------------------------------------------------------
    def endingSuffix(self):
        return ""

    #---------------------------------------------------------------------------
    def getMethodName(self):      return self.methodName
    def isSuperReplaceable(self): return True

#-------------------------------------------------------------------------------
class DirectiveFunction(Directive):

    matchPattern = re.compile("^function\s+([\w$_]+)\s*(\(.*\))?\s*$")

    #---------------------------------------------------------------------------
    def __init__(self, fileName, line, lineNo, match):
        Directive.__init__(self, fileName, line, lineNo, match)

    #---------------------------------------------------------------------------
    def isFunction(self):
        return True

    #---------------------------------------------------------------------------
    def compile(self):
        functionName  = self.match.group(1)
        functionParms = self.match.group(2)

        if not functionParms: functionParms = "()"

        self.line = "function %s%s {"
        self.line = self.line % (functionName, functionParms)


        if not functionParms:
            functionParms = ""
        else:
            functionParms = " " + functionParms

        self.line = "%s = %s ->" % (functionName, functionParms)

        self.body = js2cs("\n".join(self.body), functionParms, "  ")


    #---------------------------------------------------------------------------
    def endingSuffix(self):
        return ""

#-------------------------------------------------------------------------------
class DirectiveStatic(Directive):

    matchPattern = re.compile("^static\s*$")

    #---------------------------------------------------------------------------
    def __init__(self, fileName, line, lineNo, match):
        Directive.__init__(self, fileName, line, lineNo, match)
        logFile(fileName, lineNo, "the static directive is deprecated - use init instead")

    #---------------------------------------------------------------------------
    def compile(self):
        self.line = "// static code run on first require()"

#-------------------------------------------------------------------------------
class DirectiveInit(Directive):

    matchPattern = re.compile("^init\s*$")

    #---------------------------------------------------------------------------
    def __init__(self, fileName, line, lineNo, match):
        Directive.__init__(self, fileName, line, lineNo, match)

    #---------------------------------------------------------------------------
    def isInit(self):
        return True

    #---------------------------------------------------------------------------
    def compile(self):
        self.line = "### FIXME init"
        self.body.append("###")

#-------------------------------------------------------------------------------
class DirectiveRequire(Directive):

    matchPattern = re.compile("^require\s+([\w$\.\-/]+)(\s+as\s+([\w$.-]+))?\s*$")

    #---------------------------------------------------------------------------
    def __init__(self, fileName, line, lineNo, match):
        Directive.__init__(self, fileName, line, lineNo, match)

    #---------------------------------------------------------------------------
    def compile(self):
        moduleName = self.match.group(1)
        varName    = self.match.group(3)

        if not varName: varName = os.path.basename(moduleName)

        self.line = "%s = require('%s')" % (varName, moduleName)

#-------------------------------------------------------------------------------
class DirectiveRequireClass(Directive):

    matchPattern = re.compile("^requireClass\s+([\w$\.\-/]+)(\s+as\s+([\w$.-]+))?\s*$")

    #---------------------------------------------------------------------------
    def __init__(self, fileName, line, lineNo, match):
        Directive.__init__(self, fileName, line, lineNo, match)

    #---------------------------------------------------------------------------
    def compile(self):
        moduleName = self.match.group(1)
        varName    = self.match.group(3)

        if not varName: varName = os.path.basename(moduleName)

        self.line = "%s = require('%s')" % (varName, moduleName)

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
    DirectiveInit,
    DirectiveRequire,
    DirectiveRequireClass
])

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
def verbose(message):
    if not Options.verbose: return

    print "%s: %s" % (PROGRAM, message)

#-------------------------------------------------------------------------------
def log(message):
    if Options.quiet: return

    print "%s: %s" % (PROGRAM, message)

#-------------------------------------------------------------------------------
def logFile(fileName, lineNo, message):
    log("%s:%d: %s" % (fileName, lineNo, message))

#-------------------------------------------------------------------------------
def error(message):
    print "%s: %s" % (PROGRAM, message)
    exit(1)

#-------------------------------------------------------------------------------
def errorFile(fileName, lineNo, message):
    error("%s:%d: %s" % (fileName, lineNo, message))

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
if __name__ == '__main__':
    main()

