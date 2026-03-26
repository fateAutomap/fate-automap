# ================================================================
# 6 PROGRAM DOCUMENTATION
# ================================================================
#
# ------------------------------------------------
# PURPOSE
# ------------------------------------------------
#
# The Fate Automap is an external visualization tool for the
# Amiga RPG:
#
#     Fate – Gates of Dawn
#
# The program attaches to a running emulator and reads the
# emulator's memory in real time. From this memory the automap
# reconstructs the game world and renders a live map display.
#
#
# ------------------------------------------------
# CORE TECHNOLOGY
# ------------------------------------------------
#
# Language
#
#     Python
#
# Rendering Components
#
#     PIL / ImageDraw      → image generation
#     pygame               → display window and input loop
#
# Memory Access
#
#     Windows process memory APIs via ctypes
#
#     OpenProcess
#     ReadProcessMemory
#     WriteProcessMemory   (optional utilities)
#
#
# ------------------------------------------------
# RENDERING PIPELINE
# ------------------------------------------------
#
# The automap uses a layered rendering architecture.
#
#     memory space
#         ↓
#     tile model
#         ↓
#     renderer (image generation)
#         ↓
#     presentation (pygame window)
#
# The renderer converts decoded map data into a pixel image.
# The presentation layer displays that image and handles user
# interaction.
#
#
# ------------------------------------------------
# MAP SYSTEM
# ------------------------------------------------
#
# Fate contains two primary map types.
#
# Interior Maps
#
#     56 × 56 tiles
#     1 byte per tile
#
# Wilderness Map
#
#     640 × 400 world space
#
# The automap reads these structures directly from emulator RAM
# and converts them into screen coordinates.
#
#
# ------------------------------------------------
# MEMORY ACCESS MODEL
# ------------------------------------------------
#
# The automap operates as an external observer of emulator memory.
#
# The program does NOT:
#
#     modify the Fate executable
#     read game data files
#
# Instead it reconstructs the game world directly from the
# emulator's in-memory data structures.
#
# ------------------------------------------------
# MEMORY VOLATILITY AND ACCESS POLICY
# ------------------------------------------------
#
# The automap treats emulator memory as a volatile data source.
#
# Even when operating on static memory dumps, the program uses
# the same data access and decoding pipeline as with live emulator
# memory. This ensures behavioral consistency and avoids divergence
# between test and runtime environments.
#
# As a result:
#
#     • All emulator-derived data must be read fresh
#     • No long-term caching of memory-derived structures is allowed
#     • The program does not distinguish between "live" and "dump"
#       beyond the underlying read_mem() implementation
#
# This design guarantees that memory dumps act as faithful,
# deterministic snapshots of emulator state while preserving
# identical processing logic from either emulator or memory snapshot.
#
#
# ------------------------------------------------
# SUPPORTED EMULATORS
# ------------------------------------------------
#
# The automap currently supports:
#
#     FS-UAE
#     WinUAE
#
# Both emulators expose the Amiga RAM space inside the host
# process memory. The automap attaches to that process and reads
# memory blocks using the Windows API.
#
#
# ------------------------------------------------
# MEMORY ANCHOR STRATEGY
# ------------------------------------------------
#
# Emulator memory locations may shift between launches.
# Absolute addresses therefore cannot be trusted.
#
# The automap instead searches for known in-memory identifiers
# that act as anchors.
#
# Example
#
#     the string "Winwood"
#
# Once an anchor location is found, all other game structures
# are located relative to that position.
#
# This makes the automap resilient across:
#
#     Fate v1.6
#     Fate v1.7
#     FS-UAE
#     WinUAE
#
#
# ------------------------------------------------
# ENCOUNTER DATA
# ------------------------------------------------
#
# Encounters are stored in a fixed-size table.
#
# Structure
#
#     99 entries
#     24 bytes per entry
#
# Each entry contains:
#
#     encounter position
#     group composition
#     encounter attitude
#
# Encounter markers on the automap are rendered from this table.
#
#
# ------------------------------------------------
# COORDINATE SYSTEMS
# ------------------------------------------------
#
# Fate coordinate origin:
#
#     lower-left corner
#
# PC graphics coordinate origin:
#
#     upper-left corner
#
# When rendering the map the automap therefore performs a
# Y-axis inversion to convert between these coordinate systems.
#
#
# ------------------------------------------------
# GAMEPLAY UTILITIES
# ------------------------------------------------
#
# The automap includes optional helper features.
#
# These utilities operate by writing values back into emulator RAM.
#
# Examples
#
#     teleport player
#     restore health
#     restore mana
#     replenish food
#     replenish drink
#     add piasters
#
#
# ------------------------------------------------
# DEBUGGING FEATURES
# ------------------------------------------------
#
# Several visualization modes assist reverse-engineering.
#
# Examples
#
#     tile hex view
#     tile tint mode
#     encounter coordinate display
#     cursor crosshair
#     screenshot capture
#
# These tools help analyze map structures and verify memory
# decoding behavior.
#

