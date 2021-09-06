import os
import re
import shutil


def fcopy(filename, destination):
    if os.path.isdir(filename):
        return shutil.copytree(filename, destination)
    else:
        return shutil.copy2(filename, destination)


def fmove(filename, destination):
    return shutil.move(filename, destination)


def fdelete(filename, ignore_errors=False, onerror=None):
    if os.path.isdir(filename):
        shutil.rmtree(filename, ignore_errors, onerror)
    else:
        os.remove(filename)


def mkdir(dirname):
    return os.mkdir(dirname)


def fread(filename, mode='r'):
    with open(filename, mode) as f:
        return f.readlines()


def fwrite(filename, lines, mode='w'):
    with open(filename, mode) as f:
        f.writelines(lines)


def fappend(filename, lines, mode='a'):
    with open(filename, mode) as f:
        f.writelines(lines)


def frename(filename, new_name):
    os.rename(filename, new_name)


def fcompare(file1, file2):
    lines1 = fread(file1)
    lines2 = fread(file2)
    if len(lines1) != len(lines2):
        return False
    for i in range(len(lines1)):
        if lines1[i].rstrip() != lines2[i].rstrip():
            return False
    return True


def which(program):
    def is_exe(exe_file):
        return os.path.isfile(exe_file) and os.access(exe_file, os.X_OK)

    for path in os.environ["PATH"].split(os.pathsep):
        exe_file = os.path.join(path, program)
        if is_exe(exe_file):
            return exe_file
        exe_file += '.exe'
        if is_exe(exe_file):
            return exe_file


class Usage:
    def __init__(self, file, line, line_number):
        self.line_number = line_number
        self.line = line
        self.file = file

    def __str__(self):
        return f'{self.line}' \
               f'{self.file}:{self.line_number}\n'


class FileObject:
    def __init__(self, path, folder, filename, basename=None, ext=None):
        self.ext = ext
        self.filename = filename
        self.basename = basename if basename else filename
        self.folder = folder
        self.path = path

    def __eq__(self, other):
        return self.path == other.path

    def __str__(self):
        return str(self.path)


def floop(path='.', recurse=True, ext=None, dirs_only=False):
    if not os.path.isdir(path):
        dir, filename = os.path.split(path)
        p, ext = os.path.splitext(filename)
        yield FileObject(path, dir, filename, p, ext)
    else:
        if recurse:
            for root_path, folders, files in os.walk(path):
                if not dirs_only:
                    for file in files:
                        f, extension = os.path.splitext(file)
                        if ext:
                            if extension in ext:
                                yield FileObject(os.path.join(root_path, file), root_path, file, f, extension)
                        else:
                            yield FileObject(os.path.join(root_path, file), root_path, file, f, extension)
                else:
                    for folder in folders:
                        yield FileObject(os.path.join(root_path, folder), root_path, folder)
        else:
            for file in os.listdir(path):
                p = os.path.join(path, file)
                if os.path.isdir(p) == dirs_only:
                    if dirs_only:
                        yield FileObject(p, path, file)
                    else:
                        f, extension = os.path.splitext(file)
                        if ext:
                            if extension in ext:
                                yield FileObject(p, path, file, f, extension)
                        else:
                            yield FileObject(p, path, file, f, extension)


def find(term=None, path='.', recurse=True, ext=None, dirs_only=False, file_filter=None, line_filter=None, output=True):
    usages = []
    for file in floop(path, recurse, ext, dirs_only):
        if file_filter is None or file_filter(file):
            line_number = 1
            try:
                for line in fread(file.path):
                    if line_filter is None or line_filter(line):
                        if not term or term in line:
                            if not line.endswith('\n'):
                                line += '\n'
                            usages.append(Usage(file.path, line, line_number))
                    line_number += 1
            except UnicodeDecodeError:
                pass
    if output:
        print('\n'.join([str(x) for x in usages]))
    return usages


def finder(regex, path='.', recurse=True, ext=None, dirs_only=False, file_filter=None, output=True):
    return find(path=path, recurse=recurse, ext=ext, dirs_only=dirs_only, file_filter=file_filter, output=output,
                line_filter=lambda line: re.search(regex, line))


class Replacement(Usage):
    def __init__(self, file, line, line_number, replacement=None):
        super().__init__(file, line, line_number)
        self.replacement = replacement

    def __str__(self):
        l = self.line + '\n' if not self.line.endswith('\n') else self.line
        return f'{l}' \
               f'{self.replacement}' \
               f'{self.file}:{self.line_number}\n'


def replace(term=None, replace='', replace_func=None,
            path='.', recurse=True, ext=None, dirs_only=False,
            file_filter=None, line_filter=None,
            simulate=True, output=True
            ):
    replacements = []
    for file in floop(path, recurse, ext, dirs_only):
        if file_filter is None or file_filter(file):
            line_number = 1
            n_lines = []
            replaced = False
            try:
                for line in fread(file.path):
                    replacement = None
                    if line_filter is None or line_filter(line):
                        if not term or term in line:
                            usage = Replacement(file.path, line, line_number)
                            replaced = True
                            if replace_func:
                                replacement = replace_func(usage)
                            else:
                                replacement = line.replace(replace)
                            if replacement is not None and replacement is not line:
                                if not replacement.endswith('\n'):
                                    replacement += '\n'
                                usage.replacement = replacement
                                replacements.append(usage)
                                n_lines.append(replacement)
                    if replacement is None:
                        n_lines.append(line)
                    line_number += 1
                if replaced and not simulate:
                    fwrite(file.path, n_lines)
            except UnicodeDecodeError:
                pass
    if output:
        print('\n'.join(str(x) for x in replacements))
    return replacements


def replacer(regex, re_replace='',
             path='.', recurse=True, ext=None, dirs_only=False,
             file_filter=None, line_filter=None,
             simulate=True, output=True):
    return replace(replace=re_replace,
                   path=path, recurse=recurse, ext=ext, dirs_only=dirs_only,
                   file_filter=file_filter, line_filter=line_filter,
                   simulate=simulate, output=output,
                   replace_func=lambda usage: re.sub(regex, re_replace, usage.line))
