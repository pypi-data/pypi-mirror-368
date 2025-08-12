#!/usr/local/bin/python3

import os
import sys

# os.system('ls -l')
# os.system('git status')
# os.system('pwd')


print(sys.version)
print(sys.executable)

execfile("xyz.py")  # execute another file in folder

print(sys.prefix)  # where pip stores modules
os.system("ls " + sys.prefix)

print("hoi")
