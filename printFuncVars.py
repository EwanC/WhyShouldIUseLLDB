#!/usr/bin/python

import lldb
import os,sys

#
# Usage: python printFuncVars <function name>
#      
# Script prints all the variables in function specified as an argument.
# WARNING: No error checking is done in this script.


# Create a new debugger instance
debugger = lldb.SBDebugger.Create()
debugger.SetAsync (False)

target = debugger.CreateTargetWithFileAndArch ("./a.out", lldb.LLDB_ARCH_DEFAULT)

# Set breakpoint on function defined by command line arg. WARNING: No error checking.
main_bp = target.BreakpointCreateByName (sys.argv[1], target.GetExecutable().GetFilename());

process = target.LaunchSimple (None, None, os.getcwd())

if process.GetState() == lldb.eStateStopped:
    # Get the first thread
    thread = process.GetThreadAtIndex (0)
    # Get the first frame
    frame = thread.GetFrameAtIndex (0)
    Vars = frame.get_all_variables() 
    print("all variables: ")
    for var in Vars:
        print str(var)
