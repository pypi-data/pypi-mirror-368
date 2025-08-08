import os
if os.name == 'nt':
    import ctypes

# https://learn.microsoft.com/en-us/windows/win32/fileio/file-attribute-constants
FILE_ATTRIBUTE_HIDDEN = 0x00000002

def folder_is_hidden(path):
    if os.name == 'nt':
        # reference from https://stackoverflow.com/a/40737095/19618354
        attribute = ctypes.windll.kernel32.GetFileAttributesW(path)
        return (attribute & FILE_ATTRIBUTE_HIDDEN) != 0
    else:
        return path.startswith('.') #linux-osx
