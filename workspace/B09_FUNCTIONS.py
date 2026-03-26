import B08_CONSTANTS_v001 as c


# ================================================================
# 9 FUNCTIONS
# ================================================================

def get_process_list():
    processes = []

    snapshot = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
    if snapshot == -1:
        return processes

    try:
        entry = PROCESSENTRY32()
        entry.dwSize = ctypes.sizeof(PROCESSENTRY32)

        success = Process32First(snapshot, ctypes.byref(entry))

        while success:
            processes.append((entry.szExeFile, entry.th32ProcessID))  # IMPORTANT
            success = Process32Next(snapshot, ctypes.byref(entry))

    finally:
        CloseHandle(snapshot)

    return processes

# ------------------------------------------------
# CANONICAL COORDINATE SYSTEMS (AUTHORITATIVE)

# ============================================================
# DATA FLOW PIPELINE (AUTHORITATIVE MODEL)
# ============================================================
#
# emulator memory
#     ↓ read_mem()
# memory_space (raw bytes)
#     ↓ decode
# tile_space (authoritative world coordinates)
#     ↕
# buffer_space (viewport window)
#     ↕
# render_space (screen pixels)
#     ↓
# display
#
# Directionality:
#   memory → tile        (one-way for map data)
#   tile ↔ buffer        (core transforms)
#   buffer ↔ render      (UI transforms)
#   tile → memory        (limited writes only)
#
# NOTE:
#   Some code paths bypass buffer_space intentionally.
#   See DESIGN DEVIATION comments.
# ============================================================

# ============================================================
# TRANSFORM POLICY (CANONICAL CONVERGENCE)
# ============================================================
#
# Non-canonical code is allowed if stable.
#
# RULE:
#   If such code is modified, it MUST be converted to canonical transforms.
#
# This enables safe, gradual convergence without breaking working behavior.
# ============================================================

# ------------------------------------------------
#
# 1. memory_space
#    - Raw emulator values
#    - Read/write boundary only (no transforms)
#
# 2. tile_space (AUTHORITATIVE)
#    - Complete map representation
#    - Wilderness: 640x400
#    - City/Dungeon: 56x56
#
# 3. buffer_space (VIEW WINDOW)
#    - Local view into tile_space
#
#    ORDERING NOTE:
#      buffer_space appears first in transforms
#      for consistency of usage (cursor → tile)
#
#    Cases:
#      City/Dungeon:
#        buffer_space == tile_space
#
#      Wilderness:
#        buffer_space = window(tile_space)
#        anchored by submap_index (ADDR_SUBMAP_INDEX)
#
# 4. render_space
#    - Screen pixels (UI only)
#
#
# TRANSFORM RESPONSIBILITIES
#
#   tile ↔ buffer   (CORE LOGIC)
#   buffer ↔ render (UI)
#   memory → tile (one-way only, never updates emulator map)
#
#
# INVARIANTS
#
#   - tile_space is central authority
#   - ALL transforms pass through tile_space
#   - submap_index is ONLY valid anchor
#   - player position MUST NOT be used as a basis for transforms
#   - transforms must be consistent and non-drifting
#
#

# ============================================================
# BUFFER SPACE (120×120 TILE VIEWPORT)
# ============================================================
#
# Wilderness rendering uses a buffer-space viewport:
#
#     buffer_space = 120 × 120 tiles
#
# This corresponds to:
#
#     3 × 3 blocks (each block = 40 × 40 tiles)
#
# Layout:
#
#     [ block above-left ] [ block above ] [ block above-right ]
#     [ block left       ] [ CURRENT     ] [ block right       ]
#     [ block below-left ] [ block below ] [ block below-right ]
#
# ------------------------------------------------------------
# CENTER BLOCK ALIGNMENT
# ------------------------------------------------------------
#
# The current block (identified by sub_index) is positioned
# in the CENTER of the buffer.
#
# Since each block is 40×40 tiles:
#
#     buffer coordinate (40,40)
#
# corresponds to:
#
#     tile-space coordinate (origin_x, origin_y)
#
# where:
#
#     origin_x = col * 40
#     origin_y = row * 40
#
# ------------------------------------------------------------
# TRANSFORM IMPLICATION
# ------------------------------------------------------------
#
# To convert buffer → tile:
#
#     (cx - 40) gives offset from block origin
#
#     wx = origin_x + (cx - 40)
#     wy = origin_y + (cy - 40)
#
# INVARIANT:
#
#     buffer (40,40) ↔ tile (origin_x, origin_y)
#
# Any violation of this alignment will cause large-scale
# coordinate displacement errors.
# ============================================================


# ============================================================
# CORE PRINCIPLE: TILE vs BUFFER SPACE
# ============================================================
#
# There is only one real wilderness map.
#
#     Buffer-space does not redefine tiles — it reindexes tile-space.
#
# The wilderness map exists in tile-space:
#
#     640 × 400 tiles (authoritative world coordinates)
#
# Buffer-space (120 × 120) is simply a viewport into this map,
# centered on the current 40×40 block.
#
# Each buffer coordinate maps directly to a tile in the wilderness map:
#
#     buffer (cx, cy) ↔ tile (wx, wy)
#
# The transform is a SHIFT in origin, not a change in scale:
#
#     wx = origin_x + (cx - 40)
#     wy = origin_y + (cy - 40)
#
# IMPORTANT:
#
#     Treating buffer coordinates as independent or "local tiles"
#     will cause large positional errors (e.g., 40+ tile offsets).
#
# Mnemonic:
#
#     buffer = view (relative)
#     tile   = truth (absolute)
#
# ============================================================


# ============================================================
# WILDERNESS MEMORY LAYOUT (PACKED TILES)
# ============================================================
#
# Wilderness tiles are stored in packed format:
#
#     1 byte = 2 tiles
#
#         high nibble (bits 7–4) → first tile
#         low nibble  (bits 3–0) → second tile
#
# ------------------------------------------------------------
# STRIDE VS WIDTH
# ------------------------------------------------------------
#
# Buffer width (tile-space):
#
#     120 tiles per row
#
# Memory stride (byte-space):
#
#     60 bytes per row
#
# Because:
#
#     120 tiles ÷ 2 tiles per byte = 60 bytes
#
# ------------------------------------------------------------
# IMPLICATION
# ------------------------------------------------------------
#
# Memory must be DECODED into tile-space:
#
#     byte_index = row * 60 + (col // 2)
#
#     if col is even:
#         tile = high nibble
#     else:
#         tile = low nibble
#
# IMPORTANT:
#
#     Do NOT treat stride as tile width.
#     Stride is measured in BYTES, not tiles.
#
# ============================================================


# ------------------------------------------------------------
# STRIDE RELATIONSHIP (SANITY CHECK)
# ------------------------------------------------------------
#
# buffer width (tile-space) = memory stride (bytes) × tiles per byte
#
#     buffer width        =     memory stride      ×    tiles per byte
#         120             =          60             ×          2
#
# This relationship must always hold.
#
# If it does not, tile decoding will be incorrect.
# ------------------------------------------------------------

# ------------------------------------------------
# CANONICAL TRANSFORMS
# ------------------------------------------------

# WHY: Converts local 120x120 buffer view into absolute 640x400 wilderness coordinates.
# CRITICAL: Depends on 40x40 submap tiling; any change breaks world alignment.

def buffer_to_tile(cx, cy, sub_index):
    # --- wilderness transform (buffer → world) ---
    col = sub_index & 0x0F
    row = sub_index >> 4
    origin_x = col * 40
    origin_y = row * 40

    wx = origin_x + (cx - 40)
    wy = origin_y + (cy - 40)

    # --- clamp to wilderness bounds ---
# INVARIANT: Wilderness X bounds [0,639]; prevents invalid rendering/teleport.
    wx = max(0, min(639, wx))
# INVARIANT: Wilderness Y bounds [0,399]; prevents invalid rendering/teleport.
    wy = max(0, min(399, wy))

    return wx, wy

# WHY: Inverse transform; maps world coords back into current viewport.
# NOTE: Must remain mathematically symmetric with buffer_to_tile to avoid drift.

def tile_to_buffer(wx, wy, sub_index):
    col = sub_index & 0x0F
    row = sub_index >> 4
    origin_x = col * 40
    origin_y = row * 40
    cx = (wx - origin_x) + 40
    cy = (wy - origin_y) + 40
    return cx, cy

def buffer_to_render(cx, cy, offset, sx, sy, height):
    px = int(offset[0] + (cx + 0.5) * sx)
    py = int(offset[1] + (height - cy - 0.5) * sy)
    return px, py

def render_to_buffer(mx, my, offset, sx, sy, height):
    cx = int((mx - offset[0]) / sx - 0.5)
    cy = int(height - ((my - offset[1]) / sy) - 0.5)
    return cx, cy

def buffer_to_world(bx, by, anchor_row, anchor_col):
    origin_x = anchor_col * 40
    origin_y = anchor_row * 40
    local_x = bx - 40
    local_y = by - 40
    return origin_x + local_x, origin_y + local_y



# ------------------------------------------------
# CONSOLE LOGGING AND COMPILE SAFETY
# ------------------------------------------------
# All console output is redirected to console.txt.
# The file is overwritten on each run.


if __name__ == "__main__":
    log = open(os.path.join(BASE_DIR, "console.txt"), "w", buffering=1)
    sys.stdout = log
    sys.stderr = log

# ------------------------------------------------
# Verify that the file compiles before continuing
# ------------------------------------------------
# Skip compile check when running as packaged EXE

if not getattr(sys, 'frozen', False):
    try:
        py_compile.compile(__file__, doraise=True)
    except py_compile.PyCompileError as e:
        print("COMPILE ERROR:\n")
        print(e)
        sys.exit(1)



# ------------------------------------------------
# Returns the next unused sequential index for
# a filename with the given prefix and extension
# ------------------------------------------------
def next_index(prefix,ext):
    i=1
    while os.path.exists(os.path.join(BASE_DIR, f"{prefix}_{i:03d}.{ext}")):
        i+=1
    return i


# ================================================================
# VERSION DETECTION HELPERS (v263)
# ================================================================

def detect_version(process):
    for vid, profile in VERSION_PROFILES.items():
        matches = find_bytes(process, profile["pattern"])
        if matches:
            return vid, matches[0], profile
    return None, None, None


def resolve_addresses(profile, match_address):
    offset = match_address - profile["base_anchor"]
    return {
        "COORD_ADDR":        profile["ADDR_COORDS"] + offset,
        "ENCOUNTER_ADDR":    profile["ADDR_ENCOUNTERS"] + offset,
        "ADDR_SUBMAP_INDEX": profile["ADDR_SUBMAP_INDEX"] + offset
    }


#de

# ------------------------------------------------
# Scans running processes and return the PID of
# a supported emulator if found, otherwise None.
# ------------------------------------------------

def detect_emulator():
    try:
        print("Scanning tasks for emulators...")
        tasks = get_process_list()
    except Exception as e:
        print(f"Process scan error: {e}")
        return None
    
    found_engine = None

    for name, pid in tasks:
        name = name.lower()

        if name in ENGINE_TARGETS:
            print(f"FOUND EMULATOR ENGINE: {name} (PID: {pid})")
            found_engine = pid
            return found_engine
    
    print("FAIL: No matching emulator found.")
    return None

# ------------------------------------------------
# If an emulator process has been found
# read or write from/into that process
# Otherwise if a memory dump file has been found
# read from that dump file
# ------------------------------------------------
# CORE ABSTRACTION: All memory access flows through this function.
# DESIGN: Enables identical behavior between live emulator and memory dump.
def read_mem(process,addr,size):

    global dump_data
    global memory_mode

    if memory_mode=="process":
        buffer=ctypes.create_string_buffer(size)
        bytesRead=ctypes.c_size_t()
        kernel.ReadProcessMemory(process,ctypes.c_void_p(addr),buffer,size,ctypes.byref(bytesRead))
        return buffer.raw

    # dump mode
    offset=addr-DUMP_START

    if offset<0 or offset+size>len(dump_data):
        return b"\x00"*size

    return dump_data[offset:offset+size]

def write_mem(process,addr,data):

    global dump_data
    global memory_mode

    if memory_mode=="process":
        buf=ctypes.create_string_buffer(bytes(data))
        count=ctypes.c_size_t()
        kernel.WriteProcessMemory(process,ctypes.c_void_p(addr),buf,len(data),ctypes.byref(count))
        return

    # dump mode (modify RAM buffer only)
    offset=addr-DUMP_START

    if offset<0 or offset+len(data)>len(dump_data):
        return

    dump_data[offset:offset+len(data)]=data


# ------------------------------------------------
# BYTE PATTERN SEARCH (PROCESS OR DUMP)
# ------------------------------------------------
# WHY: Anchor-based memory discovery replaces fragile absolute addresses.
# RISK: False positives possible if pattern is not unique.
def find_bytes(process, pattern, start=DUMP_START, size=DUMP_SIZE, chunk_size=0x1000):
    matches = []
    pat_len = len(pattern)
    overlap = pat_len - 1
    addr = start
    end = start + size

    while addr < end:
        read_size = min(chunk_size + overlap, end - addr)
        data = read_mem(process, addr, read_size)

        if not data:
            addr += chunk_size
            continue

        i = 0
        while True:
            i = data.find(pattern, i)
            if i == -1:
                break
            matches.append(addr + i)
            i += 1

        addr += chunk_size

    return matches


def read_coords(process):
    raw=read_mem(process, COORD_ADDR,12)
    x=int.from_bytes(raw[0:4],"big")
    y=int.from_bytes(raw[4:8],"big")
    return x,y

def write_coords(process,x,y):
    write_mem(process, COORD_ADDR,x.to_bytes(4,"big"))
    write_mem(process, COORD_ADDR+4,y.to_bytes(4,"big"))

def read_class_table(process):
    names=[]
    for i in range(CLASS_COUNT):
        addr=BASE_CLASS_TABLE+i*CLASS_RECORD_SIZE
        raw=read_mem(process,addr,CLASS_NAME_LEN)
        # Handle special German characters and padding
        name=raw.split(b"\x00")[0].split(b"\xA7")[0].decode(errors="ignore").strip()
        names.append(name)
    return names

# ------------------------------------------------
# Read encounter table which always has 99 entries
# ------------------------------------------------
# WHY: Encounter table includes empty slots; must filter groups==0.
# BUG CLASS: Failure here causes ghost or shifted encounters.

# ============================================================
# ENCOUNTER TABLE STRUCTURE
# ============================================================
#
# The encounter table is a list of fixed-size records read from
# memory_space. Each record represents a potential encounter.
#
# Each entry has the form:
#
#     (ex, ey, att, groups)
#
# where:
#
#     ex, ey   = tile-space coordinates (wilderness map tiles)
#     att      = class index (see below)
#     groups   = number of encounter groups
#
# ------------------------------------------------------------
# VALIDITY
# ------------------------------------------------------------
#
# An entry is considered valid only if:
#
#     groups != 0
#
# Entries with groups == 0 are unused and must be skipped.
#
# ------------------------------------------------------------
# COORDINATE SYSTEM
# ------------------------------------------------------------
#
# Encounter coordinates are defined in tile-space and are aligned
# with the wilderness map tiles (not buffer-space).
#
# ------------------------------------------------------------
# SPARSITY
# ------------------------------------------------------------
#
# The encounter table is sparse and NOT spatially ordered.
#
# ============================================================


# ------------------------------------------------------------
# ENCOUNTER TYPE (CLASS TABLE REFERENCE)
# ------------------------------------------------------------
#
# The "att" field is an index into a separate table
# (referred to here as the "class table").
#
# encounter entry → class index → class table → definition
#
# INFERRED:
# The term "class table" is descriptive and not confirmed
# from original game documentation.
#
# ------------------------------------------------------------


# ------------------------------------------------------------
# MEMORY DESIGN RATIONALE (ENCOUNTER + CLASS TABLE)
# ------------------------------------------------------------
#
# Indirection allows:
#   • reuse of entity definitions
#   • compact encounter records
#
# ============================================================


# ------------------------------------------------------------
# CLASS TABLE CONTEXT (DYNAMIC)
# ------------------------------------------------------------
#
# The class table is context-dependent and may change with
# time or location.
#
# Therefore:
#     att value alone does NOT uniquely identify an encounter.
#
# ------------------------------------------------------------


# ------------------------------------------------------------
# CONTEXT RELOAD
# ------------------------------------------------------------
#
# Disk activity events may replace BOTH:
#   • encounter_table (positions)
#   • class_table     (definitions)
#
# ------------------------------------------------------------


# ------------------------------------------------------------
# ENCOUNTER DYNAMICS (OBSERVED)
# ------------------------------------------------------------
#
# Normal:
#   • incremental movement
#
# Context reload:
#   • abrupt global shift in positions and types
#
# ------------------------------------------------------------


# ------------------------------------------------------------
# CLASS TABLE NULL HANDLING
# ------------------------------------------------------------
#
# If class_table[att] is null:
#   • entry is ignored
#
# ------------------------------------------------------------


# ------------------------------------------------------------
# ENCOUNTER INDEXING (F2 / F3 CONSISTENCY)
# ------------------------------------------------------------
#
# Index must be assigned at READ time and stored with each entry.
# Never derive from iteration order.
#
# ------------------------------------------------------------

def read_encounters(process):
    raw=read_mem(process,ENCOUNTER_ADDR,24*99)
    enc=[]
    idx = 0
    for i in range(0,24*99,24):
        x=raw[i]
        y=raw[i+1]
        groups=raw[i+2]
        attitude=raw[i+13]

        # Ignore encounters with 0 members
        if groups==0:
            continue

        group_list=[]
        for g in range(5):
            cid=raw[i+3+g]
            cnt=raw[i+8+g]
            if cnt>0:
                group_list.append((cid,cnt))

        enc.append((idx, x, y, attitude, group_list))
        idx += 1
    return enc


# ------------------------------------------------
# Decode encounter table attitude byte
# ------------------------------------------------
def decode_att(att):
    if att & 0x01:
        return "H"
    if att & 0x08:
        return "F+J"
    if att & 0x02:
        return "F"
    return "?"
def encounter_color(att):
    if att==0x01: return (255,60,60)
    if att==0x82: return (80,255,120)
    return (255,255,80)

# ------------------------------------------------
# Convert mouse screen coordinates into
# tile coordinates within the current map view.
# ------------------------------------------------
def cursor_tile(mx,my,offset,sx,sy,w,h):
    cx=int((mx-offset[0])/sx)
    cy=int(h-((my-offset[1])/sy)-1)
    return cx,cy

# ------------------------------------------------
# Menu and some information is presented in right sidebar
# ------------------------------------------------
def draw_sidebar(draw_target,font,x,y,process,map_name,offset,sx,sy):
    w,h=draw_target.get_size()
    panel_x=w-PANEL_WIDTH
    pygame.draw.rect(draw_target,(30,30,30),(panel_x,0,PANEL_WIDTH,h))

    y0=20
    def line(text,color=(220,220,220)):
        nonlocal y0
        t=font.render(text,True,color)
        draw_target.blit(t,(panel_x+10,y0))
        y0+=20

    line("GAMEPLAY",(0,200,200))
    line("h Heal")
    line("m Mana")
    line("f Food")
    line("d Drink")
    line("p Piasters")
    line("t Teleport")

    y0+=8
    line("MAP",(0,200,200))
    line(f"b Turn Beacon {'OFF' if beacon else 'ON'}")
    line(f"c Turn Center Party {'OFF' if follow_player else 'ON'}")
    line(f"g Turn Grid {'OFF' if show_grid else 'ON'}")
    line("F12 Focus Emulator")

    y0+=8
    line("MOUSE",(0,200,200))
    line("Wheel Zoom")
    line("L Drag")
    line("R Teleport")

    y0+=8
    line("DEBUG",(0,200,200))
    line("F2 Encounter Table")
    line(f"F3 Turn Encounter x,y {'OFF' if dbg_enc_coords else 'ON'}")
    line(f"F4 Turn Crosshair {'OFF' if dbg_crosshair else 'ON'}")
    line(f"F5 Turn Hex {'OFF' if dbg_hex else 'ON'}")
    line(f"F6 Turn Tint {'OFF' if dbg_tint else 'ON'}")
    line("F7 Screenshot")
    line("F8 RAM dump")
    line(f"F9 Turn Inspector {'OFF' if dbg_inspector else 'ON'}")

    y0+=8
    line("POSITION",(0,200,200))
    line(f"(x,y)=({x},{y})")

    y0+=8
    if dbg_inspector:
        y0+=8
        line("INSPECTOR",(0,200,200))
        try:
            rx, ry = read_coords(process)
            line(f"RAM   : {rx},{ry}")
            try:
# CRITICAL: Submap index anchors current viewport into global map.
                sub_index_full = int.from_bytes(read_mem(process, ADDR_SUBMAP_INDEX, 2), "big")
# NOTE: sub_index stored in wider field; mask ensures only 8-bit index is used.
                sub_index = sub_index_full & 0xFF
                row = sub_index >> 4
                col = sub_index & 0x0F
                line(f"anchor: {sub_index:02X} (r{row},c{col})")
            except:
                line("anchor ERR",(255,80,80))
        except Exception as e:
            line("RAM ERR",(255,80,80))
        try:
            mx,my=pygame.mouse.get_pos()
# MAP MODE SWITCH: '90' denotes wilderness; anything else treated as city.
            if map_name=="90":
                bx,by=cursor_tile(mx,my,offset,sx,sy,WILD_W,WILD_H)
                lx = bx - 40
                ly = by - 40

# CRITICAL: Submap index anchors current viewport into global map.
                sub_index = read_mem(process, ADDR_SUBMAP_INDEX, 1)[0]
                col = sub_index & 0x0F
                row = sub_index >> 4
                origin_x = col * 40
                origin_y = row * 40

                wx = origin_x + lx
                wy = origin_y + ly

                # --- LEFT COLUMN ---
                y_start = y0
                line(f"buffer: {bx},{by}")
                line(f"local : {lx},{ly}")

                # --- RIGHT COLUMN ---
                y0 = y_start
                old_panel_x = panel_x
                panel_x += 120

                line(f"origin: {origin_x},{origin_y}")
                line(f"world : {wx},{wy}")

                panel_x = old_panel_x
                y0 = max(y0, y_start + 40)

            else:
                tx,ty=cursor_tile(mx,my,offset,sx,sy,CITY_W,CITY_H)
                line(f"tile: {tx},{ty}")
        except Exception as e:
            line("ERROR",(255,80,80))
            line(str(e)[:30],(255,80,80))


# ------------------------------------------------
# --- encounter screen ---
# ------------------------------------------------
def draw_encounter_screen(draw_target, font, encounters, class_names, scroll, px, py):
    global enc_sort_key

    w, h = draw_target.get_size()
    draw_target.fill((255, 255, 255))

    line_h = 18
    header_h = 40
    mx, my = pygame.mouse.get_pos()

    # --- build structured rows ---
    rows = []
    for idx, ex, ey, att, groups in encounters:
        row = {
            "index": idx,
            "x": ex,
            "y": ey,
            "attitude": decode_att(att),
            "dist": abs(ex - px) + abs(ey - py)
        }
        for g in range(5):
            if g < len(groups):
                cid, cnt = groups[g]
                name = class_names[cid] if cid < len(class_names) else ""
                row[f"q{g}"] = cnt
                row[f"t{g}"] = name
            else:
                row[f"q{g}"] = 0
                row[f"t{g}"] = ""
        rows.append(row)

    # --- v153: column-specific stable sorting ---
    if enc_sort_key == "index":
        rows.sort(key=lambda r: r["index"])
    elif enc_sort_key == "x":
        rows.sort(key=lambda r: r["x"])
    elif enc_sort_key == "y":
        rows.sort(key=lambda r: r["y"])
    elif enc_sort_key == "attitude":
        rows.sort(key=lambda r: r["attitude"])
    elif enc_sort_key == "dist":
        rows.sort(key=lambda r: r["dist"])
    elif enc_sort_key.startswith("q"):
        rows.sort(key=lambda r: r[enc_sort_key])
    elif enc_sort_key.startswith("t"):
        rows.sort(key=lambda r: r[enc_sort_key] or "")


    visible_rows = (h - header_h) // line_h
    max_scroll = max(0, len(rows) - visible_rows)
    scroll = max(0, min(scroll, max_scroll))

    # 1. Row Hover Highlight
    row_index = (my - header_h) // line_h
    if 0 <= row_index < visible_rows and my > header_h:
        data_idx = row_index + scroll
        if data_idx < len(rows):
            pygame.draw.rect(draw_target, (230, 255, 230), (0, header_h + (row_index * line_h), w, line_h))

    # Column Hover Highlight
    hover_col_x = None
    hover_col_w = None
    draw_x_tmp = 0
    for key_tmp, _, width_tmp in ENC_COLS:
        if draw_x_tmp <= mx <= draw_x_tmp + width_tmp:
            hover_col_x = draw_x_tmp
            hover_col_w = width_tmp
            break
        draw_x_tmp += width_tmp

    if hover_col_x is not None:
        pygame.draw.rect(draw_target, (235, 255, 235), (hover_col_x, 0, hover_col_w, h))

    # 2. Columns: Highlight, Headers, and Data
    draw_x = 0
    for key, label, width in ENC_COLS:
        if key == enc_sort_key:
            pygame.draw.rect(draw_target, (240, 240, 255), (draw_x, 0, width, h))

        h_color = (0, 100, 200) if key == enc_sort_key else (0, 0, 0)
        draw_target.blit(font.render(label, True, h_color), (draw_x + 5, 10))
        pygame.draw.line(draw_target, (200, 200, 200), (draw_x, 0), (draw_x, h), 1)

        for i in range(visible_rows):
            idx = i + scroll
            if idx >= len(rows): break

            row = rows[idx]
            y_pos = header_h + (i * line_h)
            val = row[key]

            if key in ("x", "y"):
                disp = f"{val:03}"
            elif isinstance(val, int) and val < 100:
                disp = f"{val:02}"
            else:
                disp = str(val)

            draw_target.blit(font.render(disp, True, (0, 0, 0)), (draw_x + 5, y_pos))
        
        draw_x += width

    # Return rows to ensure the main loop stays synchronized with the drawn state
    return scroll, rows 

# ------------------------------------------------
# Main application loop: initializes emulator access,
# handles input, updates state, and renders the automap.
# ------------------------------------------------
# ENTRY POINT: Controls lifecycle (attach → resolve → render loop).
# TIMING SENSITIVE: Small changes can expose rendering artifacts.

# ============================================================
# TEMPORAL PIPELINE (FRAME EXECUTION MODEL)
# ============================================================
#
#   READ → INPUT → PROCESS → RENDER → DISPLAY
#
# READ PHASE is the entry point into memory_space.
#
# ============================================================


def _get_hwnd_from_pid(target_pid):
    hwnds = []
    @_EnumWindowsProc
    def callback(hwnd, lParam):
        pid = wintypes.DWORD()
        _GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        if pid.value == target_pid and _IsWindowVisible(hwnd):
            hwnds.append(hwnd)
        return True
    _EnumWindows(callback, 0)
    return hwnds[0] if hwnds else None

def focus_emulator(pid):
    hwnd = _get_hwnd_from_pid(pid)
    if hwnd:
        _ShowWindow(hwnd, _SW_RESTORE)
        _SetForegroundWindow(hwnd)

