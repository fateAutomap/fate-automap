#########################################
#               Intended As             #
#           A Companion Program         #
#                   to                  #
#          "Fate Gates of Dawn"         #
#########################################

# This program is intended to provide an automap
# for the program,
# "Fate Gates of Dawn"
# (Commodore Amiga version)

# It is expected that "Fate Gates of Dawn"
# (hereafter referred to as "Fate")
# is running under either FS-UAE or WinUAE emulator
# on Microsoft Windows
# (programmed and tested on Windows 10 home edition)

# Broad brush strokes:
# Find the Windows 10 process ID for FSUAE or WinUAE.
# Discover what virtual memory under that process is readable.
# Scan any readable virtual memory for unique "fingerprints".
#   "Fingerprints" refers to
#   (hopefully) unique sequences of data
#   within memory
#   that are a fixed offset
#   from memory locations of interest.
# Construct the Fate automap from Fate memory locations of interest.
# Provide other features by manipulating Fate memory locations of interest.

import re
import sys
import ctypes
# import psutil
from ctypes.wintypes import WORD, DWORD, LPVOID
import subprocess


# determine the size of the pointer for this system
"""https://msdn.microsoft.com/en-us/library/aa383751#DWORD_PTR"""
if ctypes.sizeof(ctypes.c_void_p) == ctypes.sizeof(ctypes.c_ulonglong):
    DWORD_PTR = ctypes.c_ulonglong
elif ctypes.sizeof(ctypes.c_void_p) == ctypes.sizeof(ctypes.c_ulong):
    DWORD_PTR = ctypes.c_ulong

###########################################################
# Find the Windows 10 process ID for FSUAE or WinUAE.
###########################################################

"""https://docs.python.org/3/library/subprocess.html#subprocess.check_output"""
"""https://stackoverflow.com/questions/13525882/tasklist-output"""

# Given the application name, return the process ID.
# imageNames should be a list or array of strings.
# When a match is discovered, its PID is returned.
# Dependencies:
#   re.match
#   sys.exit
#  subprocess.check_output

def getProcessID(imageNames):

    thePID = 0
    WinTasks = subprocess.check_output(['tasklist']).decode('cp866', 'ignore').split("\r\n")
    for WinTask in WinTasks:
        m = re.match(b'(.*?)\\s+(\\d+)\\s+(\\w+)\\s+(\\w+)\\s+(.*?)\\s.*', WinTask.encode())
        for imageName in imageNames:
            if m is not None:
                if m.group(1).decode() == imageName:
                    thePID=int(m.group(2).decode())
                    break
            
    if(thePID==0):
        s=" or "
        print()
        print()
        print("Python could not find any process named", s.join(imageNames),".")
        print("Please ensure that either", s.join(imageNames), "is running.")
        print("Under windows, task manager shows running processes.")
        print("This program will not work unless either", s.join(imageNames))
        print("is already running and in the windows process list,")
        print("and visible within the windows task manager.")
        sys.exit()

    return thePID
    

###########################################################
#    Discover memory addresses within FSUAE or WinUAE.    #
###########################################################

def findAddresses(PID):

    # inputs: Process ID (PID)
    # outputs a list of the following application virtual memory addresses:
    # address1
    # address2
    # address3
    # address4

    
    # Define unique "Fate:Gates of Dawn" fingerprints #
    
    # Unique fingerprint pointing to somewhat after Encounter Types table
    # (Encounter Types table starts at this match location minus 0x1CD0 bytes)
    # This table lists all creatures that may be encountered on the current map
    fingerprint1 = bytearray("Gordshelm".encode())
    offset1 = -7408
    address1 = None

    # Unique fingerprint pointing to just before the Filename of the current map image
    # (map image filename starts at this match location + 3 bytes)
    # This filename corresponds to the current game map
    fingerprint2 = bytearray("D:c".encode())
    offset2 = len(fingerprint2)
    address2 = None
    
    # Unique fingerprint points to two bytes prior to Winwood and characters
    # (character address space starts at this match location + 2 bytes)
    # Each character is comprised of 500 bytes
    # There are 28 characters including Winwood (Winwood is always first)
    fingerprint3 = bytearray((chr(0x00)+chr(0x00)+"Winwood").encode())
    offset3 = 2
    address3 = None
        
    # Unique fingerprint pointing to just before start of Encounters table
    # (Encounters table starts at this match location + 15 bytes)
    # Each encounter entry is comprised of 24 bytes
    fingerprint4 = bytearray("W+A+D+S+CrMeMg".encode())
    offset4 = len(fingerprint4)
    address4 = None
        
    # calculate the maximum length of any of the fingerprints
    fmax = max(len(fingerprint1),len(fingerprint2),len(fingerprint3),len(fingerprint4))

    # in C, size_t is an unsigned integer type of at least 16 bits
    # that is often passed to/from a function to indicate the size of a return argument
    SIZE_T = ctypes.c_size_t            

    # SYSTEM_INFO class will be populated by GetSystemInfo() function.
    # It contains information about the current computer system.
    # This includes the architecture and type of the processor,
    # the number of processors in the system,
    # the page size, pointers to the lowest and highest memory addresses
    # accessible to applications and dynamic-link libraries (DLLs),
    # and other such information.
    """https://docs.microsoft.com/en-us/windows/win32/api/sysinfoapi/nf-sysinfoapi-getsysteminfo"""
    """https://docs.microsoft.com/en-us/windows/win32/api/sysinfoapi/ns-sysinfoapi-system_info"""
    """https://msdn.microsoft.com/en-us/library/ms724958"""
    class SYSTEM_INFO(ctypes.Structure):        
        class _U(ctypes.Union):
            class _S(ctypes.Structure):
                _fields_ = (('wProcessorArchitecture', WORD),
                            ('wReserved', WORD))
            _fields_ = (('dwOemId', DWORD), # obsolete
                        ('_s', _S))
            _anonymous_ = ('_s',)
        _fields_ = (('_u', _U),
                    ('dwPageSize', DWORD),
                    ('lpMinimumApplicationAddress', LPVOID),
                    ('lpMaximumApplicationAddress', LPVOID),
                    ('dwActiveProcessorMask', DWORD_PTR),
                    ('dwNumberOfProcessors', DWORD),
                    ('dwProcessorType', DWORD),
                    ('dwAllocationGranularity', DWORD),
                    ('wProcessorLevel', WORD),
                    ('wProcessorRevision', WORD))
        _anonymous_ = ('_u',)

    LPSYSTEM_INFO = ctypes.POINTER(SYSTEM_INFO)
    sysinfo = SYSTEM_INFO()
    ctypes.windll.kernel32.GetSystemInfo.restype = None
    ctypes.windll.kernel32.GetSystemInfo.argtypes = (LPSYSTEM_INFO,)


    # MEMORY_BASIC_INFORMATION class will be populated by VirtualQueryEx() function.
    # It will be used to know which bits of application memory are active and accessible.
    # It will be initiated with zero BaseAddress and continue until the query returns an error.
    class MEMORY_BASIC_INFORMATION(ctypes.Structure):
        """https://docs.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-virtualqueryex"""
        """https://docs.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-memory_basic_information"""
        """https://msdn.microsoft.com/en-us/library/aa366775"""
        _fields_ = (('BaseAddress', LPVOID),
                    ('AllocationBase', LPVOID),
                    ('AllocationProtect', DWORD),
                    ('RegionSize', SIZE_T),
                    ('State', DWORD),
                    ('Protect', DWORD),
                    ('Type', DWORD))

    mbi = MEMORY_BASIC_INFORMATION()

    MEMORY_STATES = {
        0x01000: "MEM_COMMIT ",
        0x10000: "MEM_FREE   ",
        0x02000: "MEM_RESERVE"}
    MEMORY_PROTECTIONS = {
        0x10: "PAGE_EXECUTE          ",
        0x20: "PAGE_EXECUTE_READ     ",
        0x40: "PAGEEXECUTE_READWRITE ",
	0x80: "PAGE_EXECUTE_WRITECOPY",
        0x01: "PAGE_NOACCESS         ",
        0x04: "PAGE_READWRITE        ",
        0x08: "PAGE_WRITECOPY        "}
    MEMORY_TYPES = {
        0x1000000: "MEM_IMAGE  ",
        0x0040000: "MEM_MAPPED ",
        0x0020000: "MEM_PRIVATE"}

    # 1st, Retrieve information about the current system
    ctypes.windll.kernel32.GetSystemInfo(ctypes.byref(sysinfo))
    
    # 2nd, get a handle to the Open process.
    PROCESS_QUERY_INFORMATION = 0x0400
    PROCESS_VM_READ = 0x0010
    myHandle = ctypes.windll.kernel32.OpenProcess(PROCESS_QUERY_INFORMATION|PROCESS_VM_READ, False, PID)

    # 3rd, search memory between min and max application addresses for data of interest 
    MEM_COMMIT = 0x00001000;
    PAGE_READWRITE = 0x04;

    # Establish a buffer to read blocks of memory from the application of interest.
    # This should be more efficient than reading a byte at a time, for example.

    myBuffer = bytearray(0x1000+fmax)               # bytearray is a contiguous mutable block of memory
    myBufferSize = len(myBuffer)-fmax
    myBufferPtr = ctypes.c_char * myBufferSize
    myBufferPtr = myBufferPtr.from_buffer(myBuffer) # this pointer stores address of the buffer bytearray

    
    bytes_read = SIZE_T()

    # scan through the application's virtual memory space.
    # quit when VirtualQueryEx() returns an error.
    current_address = sysinfo.lpMinimumApplicationAddress
    while ctypes.windll.kernel32.VirtualQueryEx(myHandle,current_address,ctypes.byref(mbi),ctypes.sizeof(mbi)) != 0:

        
    
        #ctypes.windll.kernel32.VirtualQueryEx(myHandle,current_address,ctypes.byref(mbi),ctypes.sizeof(mbi))
        # only inspect committed memory that can be read and written

        mySpaces = "                  "
        print(
            "curaddr =",
            mySpaces[0:(10-len(hex(current_address)))],                    hex(current_address),
            "size =",
            mySpaces[0:(10-len(hex(mbi.RegionSize)))],                     hex(mbi.RegionSize),
            end=" ")


        # all possible states/protections/types have not been enumerated in this subroutine
        # this approach avoids aborting on print errors from dictionary match failures
        try:
            print(MEMORY_STATES[mbi.State],end=" ")
        except:
            print("           ",end=" ")

        try:
            print(MEMORY_PROTECTIONS[mbi.Protect],end=" ")
        except:
            print("                      ",end=" ")

        try:
            print(MEMORY_TYPES[mbi.Type],end=" ")
        except:
            print("           ",end=" ")
            
        
        
        if (mbi.State == MEM_COMMIT) and (mbi.Protect == PAGE_READWRITE):
            index = current_address
            end = current_address + mbi.RegionSize            

            print("readable  ")

            
            while index < end:

                """https://msdn.microsoft.com/en-us/windows/desktop/ms680553"""
                ctypes.windll.kernel32.ReadProcessMemory(
                    myHandle,
                    index,
                    myBufferPtr,
                    myBufferSize,
                    ctypes.byref(bytes_read))

                if bytes_read.value == 0:
                    break

                bytesToSearch = min(myBufferSize,bytes_read.value)
                if address1 == None:
                    i = myBuffer.find(fingerprint1,0,bytesToSearch)
                    if i > -1:
                        address1 = index+i+offset1
                if address2 == None:
                    i = myBuffer.find(fingerprint2,0,bytesToSearch)
                    if i  > -1:
                        address2 = index+i+offset2
                if address3 == None:
                    i = myBuffer.find(fingerprint3,0,bytesToSearch)
                    if i > -1:
                        address3 = index+i+offset3
                if address4 == None:
                    i = myBuffer.find(fingerprint4,0,bytesToSearch)
                    if i > -1:
                        address4 = index+i+offset4
                
                if ((address1 != None) and 
                    (address2 != None) and
                    (address3 != None) and
                    (address4 != None)):

                    # release process handle
                    ctypes.windll.kernel32.FreeLibrary(myHandle)

                    return [address1,address2,address3,address4]

                # index is incremented by less than the full buffer size
                # to ensure that, if a fingerprint is incomplete because
                # it was split across a buffer read boundary,
                # the adjacent buffer read will contain the complete fingerprint.
                
                index += (myBufferSize-fmax)
                #print()
        else:
            print("unreadable")
            
        current_address += mbi.RegionSize

    # if all addresses have been found, then 
    # the program should never get to this point,
    

    # release process handle
    ctypes.windll.kernel32.FreeLibrary(myHandle)
    print()
    print("Cannot continue without the necessary fingerprints.")
    print("Specifically, could not find these fingerprints:")
    if(address1==None):
        print("    ",fingerprint1.decode('utf8'))
    if(address2==None):
        print("    ",fingerprint2.decode('utf8'))
    if(address3==None):
        print("    ",fingerprint3.decode('utf8'))
    if(address4==None):
        print("    ",fingerprint4.decode('utf8'))
    print("This is a programmer failure that requires program correction.")
    print("(Sorry! I wish your programmer was more skilled...)")
    sys.exit()



################################################
#-------------- begin program ------------------
################################################

if __name__ == '__main__':


    # ----------- from the name of the process, get the Windows process ID ---------------

    myPID=getProcessID(["fs-uae.exe","winuae.exe"])

    # ---------- find addresses to the areas of interest within Fate memory --------------
    [address1,address2,address3,address4] = findAddresses(myPID)

    try:
        print(myPID)
    except:
        print("invalid PID")

    try:
        print(hex(address1))
    except:
        print("invalid address1")

    try:
        print(hex(address2))
    except:
        print("invalid address2")

    try:
        print(hex(address3))
    except:
        print("invalid address3")

    try:
        print(hex(address4))
    except:
        print("invalid address4")

    

    ##################################################################

    
    
    

    
