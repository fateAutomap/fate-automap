# Fate Automap (Windows)

External automap tool for  
**Fate – Gates of Dawn (Amiga)**

---

## Overview

Fate Automap connects to a running emulator and reads game memory in real time to render a live map of the world.

Supports:
- FS-UAE
- WinUAE

---

## Features

- Real-time wilderness and city automap  
- Encounter visualization and tracking  
- **Encounter index system (F2 ↔ F3 linked)**  
- Player tracking and centering  
- Grid overlay and coordinate display  
- Memory dump and screenshot tools  
- Debug inspector and tile visualization modes  
- Teleport and gameplay utilities  
- **One-key return to emulator (F12)**  

---

## New in This Version

- Encounter entries now have a **stable index**
  - Consistent between map (F3) and list (F2)
- F3 display now shows:
  ```
  [index](x,y)
  ```
- Enables practical gameplay decisions:
  - Identify encounter composition from F2
  - Match it to map position via index
- Added **F12: Focus Emulator**
  - Instantly switch back to the game window
- Improved internal consistency and reliability

---

## How to Use

1. Start emulator  
2. Load Fate  
3. Run FateAutomap.exe  

If detection fails, try running as Administrator.

---

## Controls

### Gameplay
h Heal  
m Mana  
f Food  
d Drink  
p Piasters  
t Teleport  

---

### Map
c Turn Center Party ON/OFF  
b Turn Beacon ON/OFF  
g Turn Grid ON/OFF  

---

### Debug
F3 Turn Encounter index display ON/OFF  
F4 Turn Crosshair ON/OFF  
F5 Turn Hex ON/OFF  
F6 Turn Tint ON/OFF  
F9 Turn Inspector ON/OFF  

---

### Other
F2 Encounter table  
F7 Screenshot  
F8 Memory dump  
F12 Focus Emulator  

---

## Output Files

Saved next to executable:
- Screenshots  
- Memory dumps  
- console.txt log  

---

## Notes

- Uses Windows memory APIs  
- Antivirus may flag (false positive)  
- Source included for transparency  

---

## Troubleshooting

- Check console.txt if crash  
- Run as administrator if needed  
- Click automap window to receive input  

---

Enjoy exploring Fate!
