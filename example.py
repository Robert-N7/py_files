import re

from files import replace, find, replacer, floop


# simulate replacing all numbers by their double
replacer('\d+', lambda match: str(int(match.group(0)) * 2),
         path='example.py')

# print all py files in current directory recursively
for x in floop(ext='.py'):
    print(x.path)