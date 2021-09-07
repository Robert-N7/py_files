import re

from files import replace, find, replacer, floop, fwrite, fappend, fread, fcompare, fcopy, fdelete, fmove

# simulate replacing all numbers by their double
replacer('\d+', lambda match: str(int(match.group(0)) * 2),
         path='example.py')

# print all py files in current directory recursively
for x in floop(ext='.py', path='example.py'):
    print(f'Comments from {x.path}')
    for l in fread(x.path):
        if l.startswith('#'):
            print(l.rstrip())


fwrite('test.txt', ['Hello', 'World'], separator='\n')
fcopy('test.txt', 'test2.txt')
if fcompare('test.txt', 'test2.txt'):
    print('\nThey are equal\n')

fappend('test.txt', 'Whatever')
replace(term='Hello', replace='Yellow', path='test*.txt', simulate=False)

# wild cards
fcopy('test*.txt', 'tmp*.txt')
fdelete('tmp*.txt')

fcopy('test.txt', 'test3.txt')
fmove('t[em][sp]*.txt', '[2]tmp.txt')
replace(term='World', path='t?tmp.txt')
