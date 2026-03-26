"""
FateAutomap
=================

External automap for the Amiga RPG:
    Fate – Gates of Dawn

This tool attaches to a running Amiga emulator process (FS‑UAE or WinUAE)
and reads emulator RAM directly using the Windows API (ReadProcessMemory).

The automap reconstructs dungeon maps by decoding game memory rather than
using pre‑rendered map images.

Key memory structures discovered via reverse‑engineering (2019 project):

MAP MEMORY
----------
Interior maps are stored as a 56 x 56 tile grid.
Each tile is encoded as a single byte containing wall bitmasks.

Wall bits:
    0x01  right wall
    0x10  left wall
    0x40  top wall
    0x04  bottom wall

ENCOUNTER TABLE
---------------
99 entries, 24 bytes each.

Fields:
    byte 0   x coordinate
    byte 1   y coordinate
    byte 2   group count
    byte 3   class id (group 1)
    byte 13  attitude flags

Attitude flags:
    0x01  hostile
    0x82  friendly
    other neutral

CLASS TABLE
-----------
256 class records of 0x40 bytes each.
Class names are ASCII padded with 0xA7 characters.

Example:
    "Merchant\xA7\xA7\xA7..."

PARTY STRUCTURE
---------------
Each character block is separated by 500 bytes.

Relevant offsets:
    +0x4C  HP current
    +0x4E  HP max
    +0x50  MP current
    +0x52  MP max

Utilities restore values by copying max → current.

COORDINATE SYSTEM
-----------------
Fate uses a bottom‑left origin coordinate system.
Pygame uses a top‑left origin.

Therefore the Y axis must be inverted when rendering map tiles.

This version preserves the functional code from V225c but restores
technical documentation derived from the original 2019 research notes.
"""


# Fate Automap
# Version V223
# Adds:
# - Classic side panel
# - Grid toggle (g)
# - Beacon pulse (b)

import ctypes, subprocess, re, os, pygame, time

VERSION = "FateAutomapV237"

PROCESS_ALL_ACCESS = 0x1F0FFF
TARGETS = ["fs-uae.exe","winuae.exe"]

BASE_CLASS_TABLE = 0x80002EFA
MAP_ADDR = 0x800A4EA4

# Active map identifier ("00","90")
MAP_ID_ADDR = 0x8000B9ED

# RAM dump region
DUMP_START = 0x80000000
DUMP_SIZE  = 0xC0000

COORD_ADDR = 0x800545D0
ENCOUNTER_ADDR = 0x8005BED8

CLASS_RECORD_SIZE = 0x40
CLASS_NAME_LEN = 16
CLASS_COUNT = 256

WORLD_SIZE = (56,56)

HUNGER_ADDR = 0x80050E92
THIRST_ADDR = 0x80050E94
HEALTH_ADDR = 0x80050EC0
MANA_ADDR = 0x80050EC4
CASH_ADDR = 0x80050EA0

CHAR_STRIDE = 500
MAX_PARTY = 28
PANEL_WIDTH = 240

kernel = ctypes.windll.kernel32

dbg_hex=False
dbg_tint=False
dbg_enc_index=False

show_grid=False
beacon=False

beacon_radius=40
last_pulse=time.time()

crosshair_mode=False
class_names=[]

heatmap_stride = 60
dump_counter = 1


WALL_MASK = 0x01 | 0x10 | 0x40 | 0x04

BIT_COLORS = {
    0x02:(0,120,255,90),
    0x08:(0,200,120,90),
    0x20:(255,140,0,90),
    0x80:(0,220,220,90)
}

TERRAIN_PALETTE = {
    0:(120,180,120),
    2:(100,200,100),
    8:(30,120,30),
    10:(20,90,20),
    32:(150,110,70),
    34:(160,120,80),
    40:(120,80,50),
    42:(100,70,40),
    128:(20,40,160),
    130:(40,90,200),
    136:(60,120,220),
    138:(80,150,230),
    160:(90,110,60),
    162:(110,130,70),
    168:(140,140,120),
    170:(140,140,140)
}

NIBBLE_PALETTE = {
    0xB:(120,200,120),   # light green - grassland
    0x4:(80,50,30),      # dark brown - impassible mountain
    0x2:(40,140,40),     # medium green - forest fringe
    0x6:(170,140,90),    # light brown - foothills
    0x1:(0,80,0),        # dark green - impassible forest
    0x5:(130,90,50),     # medium brown - hills
    0xA:(150,0,0),       # dark red - road
    0x3:(0,220,0),       # bright green - unknown terrain
    0x9:(0,0,130),       # dark blue - deep water
    0x8:(80,180,220),    # light blue - marsh / shallow water
    0xC:(255,0,0)        # same as 9
}



# -------------------------------------------------
# Locate emulator process (FS‑UAE or WinUAE)
# -------------------------------------------------
def detect_emulator():

    try:
        tasks=subprocess.check_output(["tasklist"]).decode(errors="ignore").splitlines()
    except:
        return None

    for line in tasks:
        m=re.match(r"(\S+)\s+(\d+)",line)
        if m:
            name=m.group(1).lower()
            pid=int(m.group(2))
            if name in TARGETS:
                return pid
    return None

def read_mem(process,addr,size):
    buffer=ctypes.create_string_buffer(size)
    bytesRead=ctypes.c_size_t()
    kernel.ReadProcessMemory(process,ctypes.c_void_p(addr),buffer,size,ctypes.byref(bytesRead))
    return buffer.raw

def write_mem(process,addr,data):
    buf=ctypes.create_string_buffer(bytes(data))
    count=ctypes.c_size_t()
    kernel.WriteProcessMemory(process,ctypes.c_void_p(addr),buf,len(data),ctypes.byref(count))

def read_coords(process):
    raw=read_mem(process,COORD_ADDR,12)
    x=int.from_bytes(raw[0:4],"big")
    y=int.from_bytes(raw[4:8],"big")
    return x,y

def write_coords(process,x,y):
    write_mem(process,COORD_ADDR,x.to_bytes(4,"big"))
    write_mem(process,COORD_ADDR+4,y.to_bytes(4,"big"))

# -------------------------------------------------
# Read 56x56 tile map memory from emulator RAM
# -------------------------------------------------
def read_map(process, size):
    return read_mem(process, MAP_ADDR, size)

# -------------------------------------------------
# Load class names from CLASS_TABLE
# Names are padded with 0xA7
# -------------------------------------------------
def read_class_table(process):
    names=[]
    for i in range(CLASS_COUNT):
        addr = BASE_CLASS_TABLE + i*CLASS_RECORD_SIZE
        raw = read_mem(process,addr,CLASS_NAME_LEN)
        name = raw.split(b"\xA7")[0].decode(errors="ignore")
        names.append(name)
    return names

# -------------------------------------------------
# Decode encounter table (99 x 24 byte records)
# -------------------------------------------------
def read_encounters(process):
    raw=read_mem(process,ENCOUNTER_ADDR,24*99)
    enc=[]
    for i in range(0,24*99,24):
        x=raw[i]
        y=raw[i+1]
        groups=raw[i+2]
        class_id=raw[i+3]
        attitude=raw[i+13]
        if groups==0:
            continue
        enc.append((x,y,attitude,class_id,i//24))
    return enc

def encounter_color(att):
    if att==0x01:
        return (200,0,0)
    if att==0x82:
        return (40,180,90)
    return (200,160,60)

# -------------------------------------------------
# Convert mouse position to map tile coordinate
# -------------------------------------------------
def cursor_tile(screen,offset,zoom,map_geom):
    mx,my=pygame.mouse.get_pos()
    win_w,win_h=screen.get_size()
    map_w=win_w-PANEL_WIDTH
    sx=(map_w/map_geom["w"])*zoom
    sy=(win_h/map_geom["h"])*zoom
    cx=int((mx-offset[0])/sx)
    cy=int(map_geom["h"]-((my-offset[1])/sy)-1)
    cx=max(0,min(map_geom["w"]-1, cx))
    cy=max(0,min(map_geom["h"]-1, cy))
    return cx,cy

def center_map(screen,offset,zoom,x,y):
    win_w,win_h=screen.get_size()
    map_w=win_w-PANEL_WIDTH
    sx=(map_w/map_geom["w"])*zoom
    sy=(win_h/map_geom["h"])*zoom
    px=(x+0.5)*sx
    py=(map_geom["h"]-y-0.5)*sy
    offset[0]=map_w/2 - px
    offset[1]=win_h/2 - py

def draw_panel(screen,font,x,y,cx,cy):

    w,h=screen.get_size()
    panel_x=w-PANEL_WIDTH
    pygame.draw.rect(screen,(30,30,30),(panel_x,0,PANEL_WIDTH,h))

    y0=20

    def line(text,color=(220,220,220)):
        nonlocal y0
        t=font.render(text,True,color)
        screen.blit(t,(panel_x+10,y0))
        y0+=22

    line("GAMEPLAY",(0,200,200))
    line("h Heal")
    line("m Mana")
    line("f Food")
    line("d Drink")
    line("p Piasters")
    line("t Teleport")
    y0+=10
    line("MAP",(0,200,200))
    line("b Beacon")
    line("g Grid")
    line("c Center Party")
    y0+=10
    line("MOUSE",(0,200,200))
    line("L drag map")
    line("R teleport")
    line("Wheel zoom")


    y0+=10
    line("DEBUG",(0,200,200))
    line("F4 Encounter Index")
    line("F5 Crosshair")
    line("F6 Tile Hex")
    line("F7 Tile Tint")
    line("F8 Dump RAM")
    line(f"]/[ Heatmap Stride Up/Down now {heatmap_stride}")

    y0+=10
    line("POSITION",(0,200,200))
    line(f"(x,y) = ({x},{y})")

    y0+=10


# -------------------------------------------------
# Gameplay utilities (party status manipulation)
# -------------------------------------------------
def heal_party(process):
    for i in range(MAX_PARTY):
        addr = HEALTH_ADDR + i*CHAR_STRIDE
        raw = read_mem(process,addr,4)
        maxhp = raw[2:4]
        write_mem(process,addr,maxhp)

def restore_mana(process):
    for i in range(MAX_PARTY):
        addr = MANA_ADDR + i*CHAR_STRIDE
        raw = read_mem(process,addr,4)
        maxmp = raw[2:4]
        write_mem(process,addr,maxmp)

def feed_party(process):
    for i in range(MAX_PARTY):
        addr = HUNGER_ADDR + i*CHAR_STRIDE
        write_mem(process,addr,b"\x00\x00")

def drink_party(process):
    for i in range(MAX_PARTY):
        addr = THIRST_ADDR + i*CHAR_STRIDE
        write_mem(process,addr,b"\x00\x00")

def add_piasters(process):
    for i in range(MAX_PARTY):
        addr = CASH_ADDR + i*CHAR_STRIDE
        raw = read_mem(process,addr,4)
        gold = int.from_bytes(raw,"big")
        if gold < 500000:
            gold += 1000
        write_mem(process,addr,gold.to_bytes(4,"big"))


def main():

    global dbg_hex,dbg_tint,dbg_enc_index,show_grid,beacon,beacon_radius,last_pulse

    pid=detect_emulator()
    if not pid:
        print("No emulator found")
        return

    process=kernel.OpenProcess(PROCESS_ALL_ACCESS,False,pid)

    global class_names
    class_names = read_class_table(process)

    pygame.init()
    screen=pygame.display.set_mode((1100,850),pygame.RESIZABLE)
    pygame.display.set_caption(VERSION)

    font=pygame.font.SysFont("Arial",14)
    debug_font=pygame.font.SysFont("Courier",12)

    clock=pygame.time.Clock()

    zoom=1.0
    offset=[0,0]
    dragging=False

    encounters=[]
    last_update=0

    running=True

    while running:

        for event in pygame.event.get():

            if event.type==pygame.QUIT:
                running=False

            if event.type==pygame.KEYDOWN:

                global heatmap_stride, dump_counter

                if event.key==pygame.K_RIGHTBRACKET:
                    heatmap_stride += 1
                if event.key==pygame.K_LEFTBRACKET:
                    heatmap_stride -= 1

                if event.key==pygame.K_F8:
                    data = read_mem(process, DUMP_START, DUMP_SIZE)
                    filename = f"{VERSION}_memdump_{dump_counter:03d}.bin"
                    with open(filename,"wb") as f:
                        f.write(data)
                    print("Memory dump saved:", filename)
                    dump_counter += 1

                if event.key==pygame.K_F3:
                    filename = f"{VERSION}_screenshot_{dump_counter:03d}.png"
                    pygame.image.save(screen, filename)
                    print("Screenshot saved:", filename)


                if event.type==pygame.KEYDOWN and event.key==pygame.K_q:
                    running=False

                if event.type==pygame.KEYDOWN and event.key==pygame.K_F5:
                    global crosshair_mode
                    crosshair_mode = not crosshair_mode
                    pygame.mouse.set_visible(not crosshair_mode)

                if event.type==pygame.KEYDOWN and event.key==pygame.K_F6:
                    dbg_hex=not dbg_hex

                if event.type==pygame.KEYDOWN and event.key==pygame.K_F7:
                    dbg_tint=not dbg_tint

                if event.type==pygame.KEYDOWN and event.key==pygame.K_F4:
                    dbg_enc_index=not dbg_enc_index

                if event.type==pygame.KEYDOWN and event.key==pygame.K_g:
                    show_grid=not show_grid

                if event.type==pygame.KEYDOWN and event.key==pygame.K_b:
                    beacon=not beacon

                if event.type==pygame.KEYDOWN and event.key==pygame.K_c:
                    x,y=read_coords(process)
                    center_map(screen,offset,zoom,x,y)

                if event.type==pygame.KEYDOWN and event.key==pygame.K_t:
                    cx,cy=cursor_tile(screen,offset,zoom,map_geom)
                    write_coords(process,cx,cy)

                if event.type==pygame.KEYDOWN and event.key==pygame.K_h:
                    heal_party(process)

                if event.type==pygame.KEYDOWN and event.key==pygame.K_m:
                    restore_mana(process)

                if event.type==pygame.KEYDOWN and event.key==pygame.K_f:
                    feed_party(process)

                if event.type==pygame.KEYDOWN and event.key==pygame.K_d:
                    drink_party(process)

                if event.type==pygame.KEYDOWN and event.key==pygame.K_p:
                    add_piasters(process)

            if event.type==pygame.MOUSEWHEEL:
                if event.y>0: zoom*=1.1
                else: zoom*=0.9

            if event.type==pygame.MOUSEBUTTONDOWN:
                if event.button==1: dragging=True
                if event.button==3:
                    cx,cy=cursor_tile(screen,offset,zoom,map_geom)
                    write_coords(process,cx,cy)

                if event.type==pygame.KEYDOWN and event.key==pygame.K_h:
                    heal_party(process)
                if event.type==pygame.KEYDOWN and event.key==pygame.K_m:
                    restore_mana(process)
                if event.type==pygame.KEYDOWN and event.key==pygame.K_f:
                    feed_party(process)
                if event.type==pygame.KEYDOWN and event.key==pygame.K_d:
                    drink_party(process)
                if event.type==pygame.KEYDOWN and event.key==pygame.K_p:
                    add_piasters(process)

            if event.type==pygame.MOUSEBUTTONUP:
                if event.button==1: dragging=False

            if event.type==pygame.MOUSEMOTION and dragging:
                offset[0]+=event.rel[0]
                offset[1]+=event.rel[1]

        if time.time()-last_update>0.5:
            encounters=read_encounters(process)
            last_update=time.time()

        screen.fill((0,0,0))

        map_name = read_mem(process, MAP_ID_ADDR, 2).decode(errors="ignore")

        # determine render geometry (single source of truth)
        if map_name == "90":   # wilderness
            map_geom = {"w": heatmap_stride * 2, "h": 80}
        else:                  # city / dungeon
            map_geom = {"w": 56, "h": 56}


        if map_name == "90":   # wilderness
            map_bytes = 4800
        else:                  # city / dungeon
            map_bytes = 3584

        map_raw = read_map(process, map_bytes)


        win_w,win_h=screen.get_size()
        map_w=win_w-PANEL_WIDTH

        sx=(map_w/map_geom["w"])*zoom
        sy=(win_h/map_geom["h"])*zoom

        if map_name == "90":
            for i,val in enumerate(map_raw):

                mx=i%heatmap_stride
                my=i//heatmap_stride

                if my>=80:
                    continue

                tile_x_base = mx*2
                cy=int(offset[1]+(79-my)*sy)

                high = (val >> 4) & 0x0F
                low  = val & 0x0F

                for n,tile in enumerate((high,low)):
                    tx = tile_x_base + n
                    cx=int(offset[0]+tx*sx)
                    r=pygame.Rect(cx,cy,int(sx)+1,int(sy)+1)


                
                
                hi = (val >> 4) & 0xF
                lo = val & 0xF

                full = int(sx)
                half1 = full // 2
                half2 = full - half1

                r1 = pygame.Rect(cx, cy, half1+1, int(sy)+1)
                r2 = pygame.Rect(cx + half1, cy, half2+1, int(sy)+1)

                c1 = NIBBLE_PALETTE.get(hi,(0,0,0))
                c2 = NIBBLE_PALETTE.get(lo,(0,0,0))

                pygame.draw.rect(screen,c1,r1)
                pygame.draw.rect(screen,c2,r2)


                if dbg_hex:
                    text=debug_font.render(f"{val:02X}",True,(140,140,140))
                    screen.blit(text,(cx+2,cy+2))

        else:
                    for i,val in enumerate(map_raw[:56*56]):

                        mx = i % 56
                        my = i // 56

                        cx=int(offset[0]+mx*sx)
                        cy=int(offset[1]+(79-my)*sy)

                        r=pygame.Rect(cx,cy,int(sx)+1,int(sy)+1)

                        if show_grid:
                            pygame.draw.rect(screen,(50,50,50),r,1)

                        if dbg_tint:
                            unknown_bits=val & ~WALL_MASK
                            for bit,color in BIT_COLORS.items():
                                if unknown_bits & bit:
                                    s=pygame.Surface((int(sx),int(sy)),pygame.SRCALPHA)
                                    s.fill(color)
                                    screen.blit(s,(cx,cy))

                        if val & 0x01:
                            pygame.draw.line(screen,(180,0,0),r.topright,r.bottomright,2)
                        if val & 0x10:
                            pygame.draw.line(screen,(180,0,0),r.topleft,r.bottomleft,2)
                        if val & 0x40:
                            pygame.draw.line(screen,(180,0,0),r.topleft,r.topright,2)
                        if val & 0x04:
                            pygame.draw.line(screen,(180,0,0),r.bottomleft,r.bottomright,2)

                        if dbg_hex:
                            text=debug_font.render(f"{val:02X}",True,(140,140,140))
                            screen.blit(text,(cx+2,cy+2))

        x,y=read_coords(process)

        px=int(offset[0]+(x+0.5)*sx)
        py=int(offset[1]+(map_geom["h"]-y-0.5)*sy)

        pygame.draw.circle(screen,(0,200,200),(px,py),6)
        pygame.draw.circle(screen,(255,255,255),(px,py),7,1)

        if beacon:
            if time.time()-last_pulse>0.5:
                beacon_radius=40
                last_pulse=time.time()

            pygame.draw.circle(screen,(200,0,0),(px,py),beacon_radius,2)
            beacon_radius-=2

        mx,my=pygame.mouse.get_pos()
        cx,cy=cursor_tile(screen,offset,zoom,map_geom)

        label=font.render(f"{cx*2},{cy}",True,(255,255,255))
        screen.blit(label,(mx-10,my-18))

        for ex,ey,att,class_id,idx in encounters:

            sxp=int(offset[0]+(ex+0.5)*sx)
            syp=int(offset[1]+(map_geom["h"]-ey-0.5)*sy)

            color=encounter_color(att)

            pygame.draw.circle(screen,color,(sxp,syp),4)

            if class_id < len(class_names):
                name = class_names[class_id]
            else:
                name = str(class_id)
            if dbg_enc_index:
                name=f"{name} #{idx}"

            text=font.render(name,True,color)
            screen.blit(text,(sxp+6,syp-6))


        mx,my = pygame.mouse.get_pos()

        if crosshair_mode:
            pygame.draw.line(screen,(255,255,0),(mx-10,my),(mx+10,my),1)
            pygame.draw.line(screen,(255,255,0),(mx,my-10),(mx,my+10),1)

        draw_panel(screen,font,x,y,cx,cy)

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()

if __name__=="__main__":
    main()