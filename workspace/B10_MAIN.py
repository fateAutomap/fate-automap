import B08_CONSTANTS as c
import B09_FUNCTIONS as f

def main():

    global view_mode, enc_scroll, enc_sort_key

    global dbg_crosshair,dbg_hex,dbg_tint,dbg_enc_coords,dbg_inspector
    global show_grid,beacon,follow_player

    # Initialize late-binding addresses
    global ADDR_CLASS_TABLE, ADDR_SUBMAP_INDEX, ADDR_MAP_ID, ADDR_COORDS
    global ADDR_PARTY_BASE, ADDR_ENCOUNTERS, ADDR_MAP_BUFFER
    global MAP_ADDR, MAP_ID_ADDR, COORD_ADDR, ENCOUNTER_ADDR, BASE_CLASS_TABLE
    global memory_mode

    print("\n===== FateAutomap run:", time.ctime(), "=====\n")

    screenshot_counter=next_index(VERSION+"_screenshot","png")
    dump_counter=next_index(VERSION+"_memdump","bin")



    pid=detect_emulator()

    if pid:
        process=kernel.OpenProcess(PROCESS_ALL_ACCESS,False,pid)
        if not process:
            print("ERROR: OpenProcess failed. Try running as Administrator.")
            pid = None

    if not pid:
        print("No live emulator engine found, checking for local dump file...")

        bins=[f for f in os.listdir() if f.lower().endswith(".bin")]

        if not bins:
            print("CRITICAL: No dump file found either. Exiting.")
            return

        dump_file=bins[0]
        print("Fallback Mode: Loading dump file:",dump_file)

        global dump_data
        with open(dump_file,"rb") as f:
            dump_data=bytearray(f.read())

        memory_mode="dump"
        process=None
    else:
        memory_mode="process"

    # ------------------------------------------------
    # RESOLVE VERSION AND ANCHOR OFFSET (v225)
    # ------------------------------------------------
    # Identity Discovery: Search for version-specific anchors
    print("Searching for game identity...")
    
    found_profile = None
    global_offset = 0

    # Scan through profiles to identify game version strictly by memory anchor
    for vid, profile in VERSION_PROFILES.items():
        print(f"Checking {vid} anchor...")
        matches = find_bytes(process, profile["pattern"])
        if matches:
            found_profile = profile
            global_offset = matches[0] - profile["base_anchor"]
            print(f"IDENTITY CONFIRMED: {vid} found at {hex(matches[0])} (Shift: {hex(global_offset)})")
            break

    if not found_profile:
        print("CRITICAL ERROR: Unknown Game Identity. No memory anchors matched.")
        print("Ensure Amiga Emulator is running with Fate - Gates of Dawn playing.")
        sys.exit(1)

    # Bind Final Addresses
    ADDR_CLASS_TABLE  = found_profile["ADDR_CLASS_TABLE"]  + global_offset
    ADDR_SUBMAP_INDEX = found_profile["ADDR_SUBMAP_INDEX"] + global_offset
    ADDR_MAP_ID       = found_profile["ADDR_MAP_ID"]       + global_offset
    ADDR_COORDS       = found_profile["ADDR_COORDS"]       + global_offset
    ADDR_PARTY_BASE   = found_profile["ADDR_PARTY_BASE"]   + global_offset
    ADDR_ENCOUNTERS   = found_profile["ADDR_ENCOUNTERS"]   + global_offset
    ADDR_MAP_BUFFER   = found_profile["ADDR_MAP_BUFFER"]   + global_offset

    # Print final resolved map
    print("--- Memory Map Binding Complete ---")
    print(f"ADDR_COORDS:       {hex(ADDR_COORDS)}")
    print(f"ADDR_MAP_BUFFER:   {hex(ADDR_MAP_BUFFER)}")
    print("-----------------------------------")

    MAP_ADDR=ADDR_MAP_BUFFER
    MAP_ID_ADDR=ADDR_MAP_ID
    COORD_ADDR=ADDR_COORDS
    ENCOUNTER_ADDR=ADDR_ENCOUNTERS
    BASE_CLASS_TABLE=ADDR_CLASS_TABLE

    class_names=read_class_table(process)

    # --- determine desired window position ---
    if os.path.exists(WINDOW_POS_FILE):
        try:
            x,y = map(int,open(WINDOW_POS_FILE).read().split(","))
        except:
            x,y = 100,100
    else:
        x,y = 100,100

    pygame.init()
    pygame.key.set_repeat(300, 50)  # delay, interval (ms)
    screen=pygame.display.set_mode((1100,850),pygame.RESIZABLE)
    pygame.display.set_caption(VERSION)

    # --- force window position ---
    try:
        hwnd = pygame.display.get_wm_info()['window']
        ctypes.windll.user32.MoveWindow(hwnd, x, y, 1100, 850, False)
    except:
        pass

    render_surface=pygame.Surface((1100,850))

    # ------------------------------------------------
    # RENDERING ARCHITECTURE
    # ------------------------------------------------
    
    draw_target = render_surface

    font=pygame.font.SysFont("Courier New",14)
    debug_font=pygame.font.SysFont("Courier",8)   # smaller hex font

    clock=pygame.time.Clock()

    zoom=1.0
    offset=[0,0]
    dragging=False

    encounters=[]
    last_update=0
    current_rows = [] # tracking rows for synchronized sorting logic

    running=True

    while running:

        for event in pygame.event.get():

            if event.type==pygame.QUIT:
                running=False

            if view_mode=="encounter" and event.type==pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                draw_x = 0
                for key, _, width in ENC_COLS:
                    if draw_x <= mx <= draw_x + width:
                        enc_sort_key = key
                        # Re-sort local data to maintain synchronization with draw call
                        if enc_sort_key == "index": current_rows.sort(key=lambda r: r["index"])
                        elif enc_sort_key == "x": current_rows.sort(key=lambda r: r["x"])
                        elif enc_sort_key == "y": current_rows.sort(key=lambda r: r["y"])
                        elif enc_sort_key == "attitude": current_rows.sort(key=lambda r: r["attitude"])
                        elif enc_sort_key == "dist": current_rows.sort(key=lambda r: r["dist"])
                        elif enc_sort_key.startswith("q"): current_rows.sort(key=lambda r: r[enc_sort_key])
                        elif enc_sort_key.startswith("t"): current_rows.sort(key=lambda r: r[enc_sort_key] or "")
                        break
                    draw_x += width

            if event.type==pygame.KEYDOWN:

                if event.key==pygame.K_q:
                    running=False

                if event.key==pygame.K_F2:
                    view_mode = "encounter" if view_mode=="map" else "map"

                if event.key==pygame.K_F3: dbg_enc_coords=not dbg_enc_coords
                if event.key==pygame.K_F12:
                    if pid:
                        focus_emulator(pid)
                if event.key==pygame.K_F4:
                    dbg_crosshair=not dbg_crosshair
                    pygame.mouse.set_visible(not dbg_crosshair)
                if event.key==pygame.K_F5: dbg_hex=not dbg_hex
                if event.key==pygame.K_F6: dbg_tint=not dbg_tint
                if event.key==pygame.K_F9: dbg_inspector=not dbg_inspector

                if view_mode=="encounter":
                    if event.key in (pygame.K_UP, pygame.K_KP8): enc_scroll=max(0,enc_scroll-1)
                    if event.key in (pygame.K_DOWN, pygame.K_KP2): enc_scroll+=1
                    if event.key in (pygame.K_PAGEUP, pygame.K_KP9): enc_scroll=max(0,enc_scroll-10)
                    if event.key in (pygame.K_PAGEDOWN, pygame.K_KP3): enc_scroll+=10

                if event.key==pygame.K_g: show_grid=not show_grid

                if event.key==pygame.K_c:
                    follow_player = not follow_player

                if event.key==pygame.K_b:
                    beacon = not beacon

                # maximize health
                if event.key==pygame.K_h:
                    for slot in range(28):
                        base = ADDR_PARTY_BASE + slot * CHAR_SIZE + CHAR_H
                        raw = read_mem(process, base, 4)
                        maxhp = raw[2:4]
                        write_mem(process, base, maxhp + maxhp)

                # maximize mana
                if event.key==pygame.K_m:
                    for slot in range(28):
                        base = ADDR_PARTY_BASE + slot * CHAR_SIZE + CHAR_M
                        raw = read_mem(process, base, 4)
                        maxmp = raw[2:4]
                        write_mem(process, base, maxmp + maxmp)

                # zeroize hunger
                if event.key==pygame.K_f:
                    for slot in range(28):
                        base = ADDR_PARTY_BASE + slot * CHAR_SIZE + CHAR_F
                        write_mem(process, base, b"\x00\x00")

                # zeroize thirst
                if event.key==pygame.K_d:
                    for slot in range(28):
                        base = ADDR_PARTY_BASE + slot * CHAR_SIZE + CHAR_D
                        write_mem(process, base, b"\x00\x00")

                # add 1000 piasters
                if event.key==pygame.K_p:
                    for slot in range(28):
                        base = ADDR_PARTY_BASE + slot * CHAR_SIZE + CHAR_P
                        raw = read_mem(process, base, 4)
                        val = int.from_bytes(raw, "big")
                        val += 1000
                        write_mem(process, base, val.to_bytes(4, "big"))
        
                # teleport
                if event.key==pygame.K_t:
                    mx,my=pygame.mouse.get_pos()
# MAP MODE SWITCH: '90' denotes wilderness; anything else treated as city.
                    if map_name=="90":
                        cx,cy=cursor_tile(mx,my,offset,sx,sy,WILD_W,WILD_H)
# CRITICAL: Submap index anchors current viewport into global map.
                        sub_index_full = int.from_bytes(read_mem(process, ADDR_SUBMAP_INDEX, 2), "big")
# NOTE: sub_index stored in wider field; mask ensures only 8-bit index is used.
                        sub_index = sub_index_full & 0xFF
                        wx, wy = buffer_to_tile(cx, cy, sub_index)
                        cx, cy = wx, wy
                    else:
                        cx,cy=cursor_tile(mx,my,offset,sx,sy,CITY_W,CITY_H)
                    write_coords(process,cx,cy)

                # screenshot
                if event.key==pygame.K_F7:
                    name=f"{VERSION}_screenshot_{screenshot_counter:03d}.png"
                    pygame.image.save(screen, os.path.join(BASE_DIR, name))
                    screenshot_counter+=1

                # game memory dump from emulator
                if event.key==pygame.K_F8:
                    data=read_mem(process,DUMP_START,DUMP_SIZE)
                    base=f"{VERSION}_memdump_{dump_counter:03d}"
                    open(os.path.join(BASE_DIR, base+".bin"),"wb").write(data)
                    open(os.path.join(BASE_DIR, base+".txt"),"w").write(data.hex())
                    dump_counter+=1

            if event.type==pygame.MOUSEWHEEL:
                if view_mode=="encounter":
                    enc_scroll=max(0,enc_scroll-event.y)
                    continue
                mx,my=pygame.mouse.get_pos()

# MAP MODE SWITCH: '90' denotes wilderness; anything else treated as city.
                if map_name=="90":
                    bx,by=cursor_tile(mx,my,offset,sx,sy,WILD_W,WILD_H)
# CRITICAL: Submap index anchors current viewport into global map.
                    sub_index_full = int.from_bytes(read_mem(process, ADDR_SUBMAP_INDEX, 2), "big")
# NOTE: sub_index stored in wider field; mask ensures only 8-bit index is used.
                    sub_index = sub_index_full & 0xFF
                    wx, wy = buffer_to_tile(bx, by, sub_index)
                else:
                    wx, wy = cursor_tile(mx,my,offset,sx,sy,CITY_W,CITY_H)

                zoom*=1.1 if event.y>0 else 0.9

# MAP MODE SWITCH: '90' denotes wilderness; anything else treated as city.
                if map_name=="90":
                    sx=(map_w/WILD_W)*zoom
                    sy=(win_h/WILD_H)*zoom
                    bx, by = tile_to_buffer(wx, wy, sub_index)
                    px = offset[0] + (bx+0.5)*sx
                    py = offset[1] + (WILD_H-by-0.5)*sy
                else:
                    sx=(map_w/CITY_W)*zoom
                    sy=(win_h/CITY_H)*zoom
                    px = offset[0] + (wx+0.5)*sx
                    py = offset[1] + (CITY_H-wy-0.5)*sy

                offset[0] += mx - px
                offset[1] += my - py


            if event.type==pygame.MOUSEBUTTONDOWN:
                # v249: prevent map interactions while in encounter view
                if view_mode=="encounter":
                    continue
                if event.button==1:
                    dragging=True
                if event.button==3:
                    mx,my=pygame.mouse.get_pos()
# MAP MODE SWITCH: '90' denotes wilderness; anything else treated as city.
                    if map_name=="90":
                        cx,cy=cursor_tile(mx,my,offset,sx,sy,WILD_W,WILD_H)
# CRITICAL: Submap index anchors current viewport into global map.
                        sub_index_full = int.from_bytes(read_mem(process, ADDR_SUBMAP_INDEX, 2), "big")
# NOTE: sub_index stored in wider field; mask ensures only 8-bit index is used.
                        sub_index = sub_index_full & 0xFF
                        wx, wy = buffer_to_tile(cx, cy, sub_index)
                        cx, cy = wx, wy
                    else:
                        cx,cy=cursor_tile(mx,my,offset,sx,sy,CITY_W,CITY_H)
                    write_coords(process,cx,cy)

            if event.type==pygame.MOUSEBUTTONUP:
                if event.button==1:
                    dragging=False

            if event.type==pygame.MOUSEMOTION and dragging:
                offset[0]+=event.rel[0]
                offset[1]+=event.rel[1]
                follow_player = False

        if time.time()-last_update>0.5:
            encounters = read_encounters(process)
            class_names = read_class_table(process)
            last_update = time.time()

        if view_mode=="encounter":
            cur_x,cur_y=read_coords(process)
            enc_scroll, current_rows = draw_encounter_screen(
                draw_target, font, encounters, class_names, enc_scroll, cur_x, cur_y
            )
            screen.blit(draw_target,(0,0))
            pygame.display.flip()
            clock.tick(30)
            continue

        draw_target.fill((0,0,0))

        map_name=read_mem(process, MAP_ID_ADDR, 2).decode(errors="ignore")

        win_w,win_h=screen.get_size()
        map_w=win_w-PANEL_WIDTH

# MAP MODE SWITCH: '90' denotes wilderness; anything else treated as city.
        if map_name=="90":
            raw=read_mem(process, MAP_ADDR, WILD_STRIDE*WILD_H)
            sx=(map_w/WILD_W)*zoom
            sy=(win_h/WILD_H)*zoom

            tile_px = int(min(sx, sy))
            hex_font_size = max(6, tile_px - 2)
            hex_font = pygame.font.SysFont("Courier", hex_font_size)

            for y in range(WILD_H):
                for xb in range(WILD_STRIDE):
                    byte=raw[y*WILD_STRIDE+xb]
                    hi=(byte>>4)&0xF
                    lo=byte&0xF

                    for i,val in enumerate((hi,lo)):
                        x=xb*2+i
                        cx=int(offset[0]+x*sx)
                        cy=int(offset[1]+(WILD_H-y-1)*sy)
                        r=pygame.Rect(cx,cy,int(sx+0.5)+1,int(sy+0.5)+1)
                        pygame.draw.rect(draw_target,NIBBLE_PALETTE.get(val,(0,0,0)),r)

                        if dbg_tint:
                            base = NIBBLE_PALETTE.get(val,(0,0,0))
                            scaled = (int(base[0] * TINT_BRIGHTNESS), int(base[1] * TINT_BRIGHTNESS), int(base[2] * TINT_BRIGHTNESS))
                            tint = pygame.Surface((r.width, r.height), pygame.SRCALPHA)
                            tint.fill((scaled[0],scaled[1],scaled[2],120))
                            draw_target.blit(tint, r.topleft)

                        if dbg_hex:
                            text=hex_font.render(f"{val:X}",True,(255,255,255))
                            draw_target.blit(text,(cx+2,cy+2))

            # --- WILDERNESS GRID ---
            if show_grid:
# CRITICAL: Submap index anchors current viewport into global map.
                sub_index_full = int.from_bytes(read_mem(process, ADDR_SUBMAP_INDEX, 2), "big")
# NOTE: sub_index stored in wider field; mask ensures only 8-bit index is used.
                sub_index = sub_index_full & 0xFF

                # Vertical Lines & Labels (X-Axis)
                for wx in range(0, 640, 5):
                    bx, _ = tile_to_buffer(wx, 0, sub_index)
                    if 0 <= bx < 120:
                        px = int(offset[0] + bx * sx)
                        color = (120,120,120) if wx % 10 == 0 else (60,60,60)
                        pygame.draw.line(draw_target, color, (px, offset[1]), (px, offset[1] + WILD_H * sy))

                        if wx % 10 == 0:
                            label = font.render(str(wx), True, (200,200,200))
                            # Labels on Top and Bottom
                            draw_target.blit(label, (px - label.get_width()//2, offset[1] - 18))
                            draw_target.blit(label, (px - label.get_width()//2, offset[1] + WILD_H * sy + 4))

                # Horizontal Lines & Labels (Y-Axis)
                for wy in range(0, 400, 5):
                    _, by = tile_to_buffer(0, wy, sub_index)
                    if 0 <= by < 120:
                        py = int(offset[1] + (WILD_H - by) * sy)
                        color = (120,120,120) if wy % 10 == 0 else (60,60,60)
                        pygame.draw.line(draw_target, color, (offset[0], py), (offset[0] + WILD_W * sx, py))

                        if wy % 10 == 0:
                            label = font.render(str(wy), True, (200,200,200))
                            # Labels on Left and Right
                            draw_target.blit(label, (offset[0] - label.get_width() - 5, py - label.get_height()//2))
                            draw_target.blit(label, (offset[0] + WILD_W * sx + 5, py - label.get_height()//2))

        else:
            raw=read_mem(process, MAP_ADDR, CITY_W*CITY_H)
            sx=(map_w/CITY_W)*zoom
            sy=(win_h/CITY_H)*zoom

            tile_px = int(min(sx, sy))
            font_size = max(6, tile_px - 2)
            if font_size not in hex_font_cache:
                hex_font_cache[font_size] = pygame.font.SysFont("Courier", font_size)
            hex_font = hex_font_cache[font_size]

            for i,val in enumerate(raw):
                mx=i%CITY_W
                my=i//CITY_W
                cx=int(offset[0]+mx*sx)
                cy=int(offset[1]+(CITY_H-my-1)*sy)
                r=pygame.Rect(cx,cy,int(sx)+1,int(sy)+1)

                if val & 0x01: pygame.draw.line(draw_target,(180,0,0),r.topright,r.bottomright,2)
                if val & 0x10: pygame.draw.line(draw_target,(180,0,0),r.topleft,r.bottomleft,2)
                if val & 0x40: pygame.draw.line(draw_target,(180,0,0),r.topleft,r.topright,2)
                if val & 0x04: pygame.draw.line(draw_target,(180,0,0),r.bottomleft,r.bottomright,2)

                if val == 0x55:
                    color = (180,0,0)
                    step = max(4, int(min(sx,sy)//3))
                    old_clip = draw_target.get_clip()
                    draw_target.set_clip(r)
                    w, h = r.width, r.height
                    for d in range(-h, w, step):
                        x1 = r.left + max(d, 0)
                        y1 = r.top + max(-d, 0)
                        x2 = r.left + min(w, w + d)
                        y2 = r.top + min(h, h - d)
                        pygame.draw.line(draw_target, color, (x1,y1), (x2,y2), 2)
                    draw_target.set_clip(old_clip)

                if dbg_tint and val != 0x55:
                    masked = val & 0xAA
                    if masked != 0:
                        alpha = 160 if val == 0xAA else 90
                        base = ((val * 53) % 256, (val * 97) % 256, (val * 193) % 256)
                        tint = pygame.Surface((r.width, r.height), pygame.SRCALPHA)
                        tint.fill((base[0], base[1], base[2], alpha))
                        draw_target.blit(tint, r.topleft)

                if dbg_hex:
                    text = hex_font.render(f"{val:02X}", True, (220,220,220))
                    tx = cx + (r.width - text.get_width()) // 2
                    ty = cy + (r.height - text.get_height()) // 2
                    draw_target.blit(text, (tx, ty))

            # --- CITY GRID (5-tile minor, 10-tile major) ---
            if show_grid:
                # Vertical lines & labels
                for tx in range(0, CITY_W, 5):
                    px = int(offset[0] + tx * sx)
                    color = (120, 120, 120) if tx % 10 == 0 else (60, 60, 60)
                    pygame.draw.line(draw_target, color, (px, offset[1]), (px, offset[1] + CITY_H * sy))
                    if tx % 10 == 0:
                        lbl = font.render(str(tx), True, (200, 200, 200))
                        draw_target.blit(lbl, (px - lbl.get_width()//2, offset[1] - 18))
                        draw_target.blit(lbl, (px - lbl.get_width()//2, offset[1] + CITY_H * sy + 4))

                # Horizontal lines & labels
                for ty in range(0, CITY_H, 5):
                    py = int(offset[1] + (CITY_H - ty) * sy)
                    color = (120, 120, 120) if ty % 10 == 0 else (60, 60, 60)
                    pygame.draw.line(draw_target, color, (offset[0], py), (offset[0] + CITY_W * sx, py))
                    if ty % 10 == 0:
                        lbl = font.render(str(ty), True, (200, 200, 200))
                        draw_target.blit(lbl, (offset[0] - lbl.get_width() - 5, py - lbl.get_height()//2))
                        draw_target.blit(lbl, (offset[0] + CITY_W * sx + 5, py - lbl.get_height()//2))

        cur_x,cur_y=read_coords(process)
# INVARIANT: Wilderness X bounds [0,639]; prevents invalid rendering/teleport.
        cur_x = max(0, min(639, cur_x))
# INVARIANT: Wilderness Y bounds [0,399]; prevents invalid rendering/teleport.
        cur_y = max(0, min(399, cur_y))

# MAP MODE SWITCH: '90' denotes wilderness; anything else treated as city.
        if map_name=="90":
            sx=(map_w/WILD_W)*zoom
            sy=(win_h/WILD_H)*zoom
# CRITICAL: Submap index anchors current viewport into global map.
            sub_index_full = int.from_bytes(read_mem(process, ADDR_SUBMAP_INDEX, 2), "big")
# NOTE: sub_index stored in wider field; mask ensures only 8-bit index is used.
            sub_index = sub_index_full & 0xFF
            col = sub_index & 0x0F
            row = sub_index >> 4
            origin_x, origin_y = col * 40, row * 40
            bx, by = (cur_x - origin_x) + 40, (cur_y - origin_y) + 40
            bx, by = max(0, min(119, bx)), max(0, min(119, by))
            px=int(offset[0]+(bx+0.5)*sx)
            py=int(offset[1]+(WILD_H-by-0.5)*sy)
        else:
            sx=(map_w/CITY_W)*zoom
            sy=(win_h/CITY_H)*zoom
            px=int(offset[0]+(cur_x+0.5)*sx)
            py=int(offset[1]+(CITY_H-cur_y-0.5)*sy)

        pygame.draw.circle(draw_target,(0,200,200),(px,py),6)
        if follow_player:
# MAP MODE SWITCH: '90' denotes wilderness; anything else treated as city.
            if map_name=="90":
# CRITICAL: Submap index anchors current viewport into global map.
                sub_index_full = int.from_bytes(read_mem(process, ADDR_SUBMAP_INDEX, 2), "big")
# NOTE: sub_index stored in wider field; mask ensures only 8-bit index is used.
                sub_index = sub_index_full & 0xFF
                bx, by = tile_to_buffer(cur_x, cur_y, sub_index)
                offset[0] = (map_w/2) - (bx+0.5)*sx
                offset[1] = (win_h/2) - (WILD_H-by-0.5)*sy
            else:
                offset[0] = (map_w/2) - (cur_x+0.5)*sx
                offset[1] = (win_h/2) - (CITY_H-cur_y-0.5)*sy
        if beacon:
            bpx, bpy = px, py
            t = time.time()
            radius = int(6 + (44 - 6) * (1 - ((t * 1.5) % 1.0)))
            pygame.draw.circle(draw_target,(255,0,0),(bpx,bpy),radius,2)
        pygame.draw.circle(draw_target,(255,255,255),(px,py),7,1)

        # RENDER LOOP: Encounter plotting logic restored to use Map-specific context

# DESIGN DEVIATION:
# Encounter rendering bypasses buffer_space and maps tile → render directly.
#
# STATUS:
#   Stable behavior preserved.
#
# POLICY:
#   If modified, must be converted to canonical transforms.
#
# RISK:
#   Possible misalignment if transform logic changes.
#
# DEBUG:
#   Compare against tile_to_buffer() if issues arise.
        for idx,ex,ey,att,groups in encounters:
            class_id = groups[0][0] if groups else 0
            
# MAP MODE SWITCH: '90' denotes wilderness; anything else treated as city.
            if map_name=="90":
                # Wilderness scaling logic + local wilderness clamping
# INVARIANT: Wilderness X bounds [0,639]; prevents invalid rendering/teleport.
# INVARIANT: Wilderness Y bounds [0,399]; prevents invalid rendering/teleport.
                ex_c, ey_c = max(0, min(639, ex)), max(0, min(399, ey))
                sxp, syp = int(offset[0]+(ex_c+0.5)*sx), int(offset[1]+(WILD_H-ey_c-0.5)*sy)
            else:
                # City scaling logic: Restored CITY_H basis and non-wilderness sx/sy
                # v248: prune invalid city encounters outside 56x56 bounds
                if ex > 55 or ey > 55:
                    continue
                sxp, syp = int(offset[0]+(ex+0.5)*sx), int(offset[1]+(CITY_H-ey-0.5)*sy)
            
            color=encounter_color(att)
            pygame.draw.circle(draw_target,(0,0,0),(sxp,syp),5)
            pygame.draw.circle(draw_target,color,(sxp,syp),4)
            name=class_names[class_id] if class_id<len(class_names) else ""
#            if dbg_enc_coords: name=f"{name}({ex},{ey}){class_id}"
            if dbg_enc_coords: name=f"{idx}({ex},{ey})"
            if name:
# NOTE: Double text rendering creates outline effect.
# RISK: Can introduce visual jitter depending on timing/frame sync.
                draw_target.blit(font.render(name, True, (0,0,0)), (sxp+7, syp-5))
# NOTE: Double text rendering creates outline effect.
# RISK: Can introduce visual jitter depending on timing/frame sync.
                draw_target.blit(font.render(name, True, color), (sxp+6, syp-6))

        mx,my=pygame.mouse.get_pos()
# MAP MODE SWITCH: '90' denotes wilderness; anything else treated as city.
        if map_name=="90": cx,cy=cursor_tile(mx,my,offset,sx,sy,WILD_W,WILD_H)
        else: cx,cy=cursor_tile(mx,my,offset,sx,sy,CITY_W,CITY_H)

        label=font.render(f"{cx},{cy}",True,(255,255,255))
        draw_target.blit(label,(mx-10,my-18))

        if dbg_crosshair:
            pygame.draw.line(draw_target,(255,255,0),(mx-10,my),(mx+10,my),1)
            pygame.draw.line(draw_target,(255,255,0),(mx,my-10),(mx,my+10),1)

        draw_sidebar(draw_target,font,cur_x,cur_y,process,map_name,offset,sx,sy)

        screen.blit(draw_target,(0,0))
        pygame.display.flip()
        clock.tick(30)

    try:
        hwnd = pygame.display.get_wm_info()['window']
        rect = ctypes.wintypes.RECT()
        ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(rect))
        open(WINDOW_POS_FILE,"w").write(f"{rect.left},{rect.top}")
    except: pass
    pygame.quit()

if __name__=="__main__":
    main()


