import sys
try:
    import ctypes
    from ctypes.util import find_library
except ImportError:
    ctypes = None

PR_SET_PDEATHSIG  = 1  ## /* Second arg is a signal */
PR_GET_PDEATHSIG  = 2  ## /* Second arg is a ptr to return the signal */

PR_SET_NAME = 15
PR_GET_NAME = 16

if ctypes and sys.platform == 'linux2':
    libc = ctypes.CDLL(find_library('c'))
    def set_proc_name(name):
        libc.prctl(PR_SET_NAME, ctypes.c_char_p(name), 0, 0, 0)
       
    def get_proc_name():
        name = ctypes.create_string_buffer(16)
        libc.prctl(PR_GET_NAME, name, 0, 0, 0)
        return name.value

    def set_proc_deathsig(signo):
        libc.prctl(PR_SET_PDEATHSIG, signo, 0, 0, 0)

else:
    set_proc_deathsig = None
    set_proc_name = None
    get_proc_name = None
