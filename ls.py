#!/usr/bin/python
#
# Taken from http://lldb.llvm.org/python-reference.html
# Usage:
#
#(lldb) command script import ~/ls.py
#
#(lldb) ls -l ~/LLVM/llvm/tools/lldb
#total 88
#drwxrwxr-x  4 ewan ewan 4096 Mar 30 16:32 cmake
#-rw-rw-r--  1 ewan ewan 1205 Mar 30 16:32 CMakeLists.txt 


import lldb
import commands
import optparse
import shlex

def ls(debugger, command, result, internal_dict):
    print >>result, (commands.getoutput('/bin/ls %s' % command))

# And the initialization code to add your commands 
def __lldb_init_module(debugger, internal_dict):
    debugger.HandleCommand('command script add -f ls.ls ls')
    print 'The "ls" python command has been installed and is ready for use.'
