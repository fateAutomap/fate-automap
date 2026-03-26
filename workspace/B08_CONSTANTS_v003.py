# ================================================================
# 8 IMPORTS
# ================================================================

# Standard library
import os
import sys
import time
import re
import traceback
import ctypes
from ctypes import wintypes
import py_compile

# Third-party
import pygame



# ------------------------------------------------
# From Windows API, get process list
# ------------------------------------------------

TH32CS_SNAPPROCESS = 0x00000002

CreateToolhelp32Snapshot = ctypes.windll.kernel32.CreateToolhelp32Snapshot
Process32First = ctypes.windll.kernel32.Process32FirstW
Process32Next = ctypes.windll.kernel32.Process32NextW
CloseHandle = ctypes.windll.kernel32.CloseHandle

class PROCESSENTRY32(ctypes.Structure):
    _fields_ = [
        ("dwSize", wintypes.DWORD),
        ("cntUsage", wintypes.DWORD),
        ("th32ProcessID", wintypes.DWORD),
        ("th32DefaultHeapID", ctypes.POINTER(wintypes.ULONG)),
        ("th32ModuleID", wintypes.DWORD),
        ("cntThreads", wintypes.DWORD),
        ("th32ParentProcessID", wintypes.DWORD),
        ("pcPriClassBase", wintypes.LONG),
        ("dwFlags", wintypes.DWORD),
        ("szExeFile", wintypes.WCHAR * 260),
    ]




# ------------------------------------------------
# BASE DIRECTORY RESOLUTION (PY vs EXE)
# ------------------------------------------------
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ------------------------------------------------
# --- consistent window location at startup.
# ------------------------------------------------

WINDOW_POS_FILE = os.path.join(BASE_DIR, "window_pos.txt")

# ------------------------------------------------
# Dumpfiles share same base name with this program
# ------------------------------------------------

VERSION=os.path.basename(__file__)

# ------------------------------------------------
# Define full access rights in Windows API code
# ------------------------------------------------
PROCESS_ALL_ACCESS=0x1F0FFF

# v222: Added specific targeting to avoid launcher false positives
ENGINE_TARGETS=["fs-uae.exe","winuae.exe"]
kernel=ctypes.windll.kernel32

# -------------------------------------------------------
# VERSION PROFILES: BASE MEMORY LOCATIONS IN THE EMULATOR
# -------------------------------------------------------
VERSION_PROFILES = {
    "v1.6": {
        "pattern": bytes.fromhex("2D 2D 2D 2D 2D 20 A7 A7 A7 A7 A7 A7 A7 A7 A7 00 00 00 00 00 00 00 00 00 57 6F 6F 64 65 6E 20 A7"),
        "base_anchor":        0x8005F8C8,
        "ADDR_CLASS_TABLE":   0x80002EFA,
        "ADDR_SUBMAP_INDEX":  0x8000B578,
        "ADDR_MAP_ID":        0x8000B9ED,
        "ADDR_COORDS":        0x800545D0,
        "ADDR_PARTY_BASE":    0x80050E74,
        "ADDR_ENCOUNTERS":    0x8005BED8,
        "ADDR_MAP_BUFFER":    0x800A4EA4
    },
    "v1.7": {
        "pattern": bytes.fromhex("4B 65 69 6E 65 20 A7 A7 A7 A7 A7 A7 A7 A7 A7 00 00 00 00 00 00 00 00 00 48 6F 6C 7A 20 A7 A7"),
        "base_anchor":        0x8005FA52,
        "ADDR_CLASS_TABLE":   0x80002EFA,
        "ADDR_SUBMAP_INDEX":  0x8000B5DE,
        "ADDR_MAP_ID":        0x8000BA59,
        "ADDR_COORDS":        0x8005475A,
        "ADDR_PARTY_BASE":    0x80050FFE,
        "ADDR_ENCOUNTERS":    0x8005C062,
        "ADDR_MAP_BUFFER":    0x800A534E  
    }
}

ADDR_GAME_BEGIN   = 0x80000000

# ------------------------------------------------
# LATE-BINDING GLOBALS (INITIALIZED IN MAIN)
# ------------------------------------------------
ADDR_CLASS_TABLE  = 0
ADDR_SUBMAP_INDEX = 0
ADDR_MAP_ID       = 0
ADDR_COORDS       = 0
ADDR_PARTY_BASE   = 0
ADDR_ENCOUNTERS   = 0
ADDR_MAP_BUFFER   = 0

# ------------------------------------------------
# CHARACTER TRAITS OFFSETS FROM ADDR_PARTY_BASE
# ------------------------------------------------
CHAR_H=0x4C
CHAR_M=0x50
CHAR_F=0x1E
CHAR_D=0x20
CHAR_P=0x2C

# ------------------------------------------------
# MEMORY MAP BY USAGE (ALIASES)
# ------------------------------------------------
MAP_ADDR=0
MAP_ID_ADDR=0
COORD_ADDR=0
ENCOUNTER_ADDR=0
BASE_CLASS_TABLE=0

# ------------------------------------------------
# ARCHITECTURAL AND STRUCTURAL DEFINITIONS
# ------------------------------------------------
CLASS_RECORD_SIZE=0x40
CLASS_NAME_LEN=16
CLASS_COUNT=256

CITY_W=56
CITY_H=56

WILD_W=120
WILD_H=120
WILD_STRIDE=60

PANEL_WIDTH=240

DUMP_START=0x80000000
DUMP_SIZE=0xC0000

CHAR_SIZE = 0x1F4  # 500 bytes per character

# ------------------------------------------------
# MEMORY SOURCE MODE
#
# process → live emulator RAM
# dump    → RAM buffer loaded from *.bin
# ------------------------------------------------

memory_mode="process"
dump_data=None


# ------------------------------------------------
# INITIAL GAME STATES
# ------------------------------------------------

dbg_crosshair=True
dbg_hex=False
dbg_tint=False
dbg_enc_coords=False
dbg_inspector=False
view_mode = "map"
enc_scroll = 0
enc_sort_key = "index"   # v148: active column sort

show_grid=False
beacon=False
follow_player=False
beacon_pos=None
beacon_map=None


# ------------------------------------------------
# Defines tile color mapping, tint intensity, and
# a cache for hex-rendering fonts.
# ------------------------------------------------

NIBBLE_PALETTE={
0x1:(0,80,0),
0x2:(40,140,40),
0x3:(0,220,0),
0x4:(80,50,30),
0x5:(130,90,50),
0x6:(170,140,90),
0x7:(138,154,91),
0x8:(80,180,220),
0x9:(0,0,130),
0xA:(150,0,0),
0xB:(120,200,120),
0xC:(255,0,0)
}

TINT_BRIGHTNESS = 0.25

hex_font_cache = {}

# ------------------------------------------------
# ENCOUNTER TABLE COLUMN DEFINITION (SHARED)
# ------------------------------------------------
ENC_COLS = [
    ("index","IDX",40),
    ("x","X",45),
    ("y","Y",45),
    ("attitude","AT",50),
    ("q0","Q1",35),
    ("t0","T1",110),
    ("q1","Q2",35),
    ("t1","T2",110),
    ("q2","Q3",35),
    ("t2","T3",110),
    ("q3","Q4",35),
    ("t3","T4",110),
    ("q4","Q5",35),
    ("t4","T5",110),
    ("dist","DST",60)
]


# ------------------------------------------------------------
# WINDOW FOCUS (CTYPES VERSION — NO DEPENDENCIES)
# ------------------------------------------------------------
_user32 = ctypes.windll.user32

_EnumWindows = _user32.EnumWindows
_EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)

_GetWindowThreadProcessId = _user32.GetWindowThreadProcessId
_IsWindowVisible = _user32.IsWindowVisible
_SetForegroundWindow = _user32.SetForegroundWindow
_ShowWindow = _user32.ShowWindow

_SW_RESTORE = 9


