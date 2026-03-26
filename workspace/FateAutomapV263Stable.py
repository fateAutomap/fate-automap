# Fate Automap v259
# Comment-enriched (encounter system finalized)
# No logic changes

# Fate Automap v253
# Comment-enriched, no logic changes

# ================================================================
# FATE – GATES OF DAWN AUTOMAP
# Single‑File Development Workspace
# ================================================================
#
# Combined documentation and executable program.
#

# ================================================================
# CONTENTS
# ================================================================
# 0 GUIDANCE FOR THE HUMAN
# 1 SESSION OBJECTIVES
# 2 WORKFLOW FOR SUCCESSFUL HUMAN-AI COLLABORATION
# 3 AI CONTRACT
# 4 PROJECT CONTEXT SEED
# 5 EVALUATION
# 6 PROGRAM DOCUMENTATION (Narrative Style)
# 7 FUTURE IDEAS
# 8 PROGRAM SOURCE CODE
# ================================================================

# ================================================================
# 0 FOR THE HUMAN
# ================================================================
#
# Prompting is the broad skill of providing input to AI systems
#   so that they can do useful work.
# 1. Prompt Craft: Tells autonomous agents what to do.
#    Synchronous. Session-based. Individual skill.
#    Knowing how to structure a query.
#    Must have clear instructions.
#    Must provide clear examples and counter-examples.
#    Need to include appropriate guardrails.
#    Need to include an explicit output format.
#    Be very clear about resolving ambiguity and conflict so that
#      the model doesn't have to make it up on the fly.
#    This scope might be maybe 200 tokens.
# 2. Context Engineering: Tells agents what to know.
#    The set of strategies for curating and maintaing the optimal
#      set of tolkens during an LLM task.
#    Providing relevant tokens to the LLM for inference.
#    Shift from crafting a single instruction to curating the
#      entire information environment an agent operates within.
#    All of the system prompts.
#    All of the tool definitions.
#    All of the retrieved documents.
#    All of the message history.
#    All of the memory systems.
#    The MCP connection.
#    This is the discipline that produces claude.md files,
#      agent specifications, rag pipeline design, memory architectures.
#    Ensures a coding agent understands project conventions.
#    Ensures a research agent has access to the right documents.
#    Ensures a customer service agent can retrieve releavant
#      account history.
#    LLMs degrade as you give them more information, so retrieval
#      quality drops as context grows.
#    Better context infrastructure minimizes this liability.
#    This seems like OpenBrain.
#    This scope might be 1 million tokens.
# 3. Intent Engineering: Tells agents what to want.
#    Practice of encoding organizational purpose.
#    Translate organizational goals, values, trade-off heirarchies,
#      decision boundaries into infrastructure that agents can
#      act against.
#    Intent engineering sits above context engineering the way
#      strategy sits above tactics.
# 4. Specification Engineering: tells agent what success looks like.
#    Practice of writing documents across your organization
#      that autonomous agents can execute against
#      over extended time horizons without human intervention.
#    Ensuring organization's entire informational corpus is
#      agent ingestible and fungible.
#    Specifications are complete structured internally consGL NCCCistent
#      descriptions of what an output should be for a given task.
#    Define how quality is measured.
#    Allow you to apply agents across large swaths of your context
#      with the confidence that what the agent reads
#      will be relevant.
#    Specifications provide a pattern such that
#      an initial agent sets up the environment,
#      a progress log documents what's been done,
#      a coding agent then makes incremental progress
#      against a structured plan every session.
#    The specification becomes the scaffolding that lets
#      multiple agents produce coherent output across sessions.
#
# 5. Human workflow
#    Direct the agent to interview me in detail. 
#    Ask about technical implementation,
#      user interace/user experience (UI/UX), edge cases,
#      concerns, and trade-offs.
#    Don't ask obvious questions -- dig into the hard parts.
#    The agent then writes the spec with the human.

# ================================================================
# 1 SESSION OBJECTIVES
# ================================================================
#
# [OBJECTIVE] Perform regression testing
#
# ================================================================
# 2 WORKFLOW FOR SUCCESSFUL HUMAN-AI COLLABORATION
# ================================================================
#
#  1 Always start from last stable version.
#  2 Provide the entire file to the AI.
#  3 AI proposes plan before modifying code.
#  4 AI first updates "session objectives" describing current effort.
#  4 Code changes (PROGRAM SOURCE CODE) must be minimal diff patches.
#  5 Structural sections (non-code sections) must be replaced completely,
#    not partially edited.
#  6 Table-of-contents entries must match headers exactly.
#  7 AI must add explanatory comments when modifying code,
#    but must not delete or rewrite existing comments,
#    only updating existing comments when they document
#    behavior that is being changed by the code modification.
#  8 Before generating any new file version, the AI must copy the
#    AI CONTRACT section verbatim from the previous version
#    before making any other modifications.
#  9 AI must verify that the resulting code compiles under the
#    Python interpreter (no syntax errors) before presenting a
#    new file version to the human.
# 10 AI produces a concise before/after change summary and
#    validates no unintended regressions
# 11 AI provides a COMPLETE updated file as a direct download when possible,
#    otherwise as a single-block full file requiring no
#    manual assembly, but with a "one-click copy-all" button
#    to avoid huge left-mouse-click dragging.
# 12 End sessions with: “update context seed” when needed.


# ===== CONTRACT MUST BE COPIED VERBATIM - DO NOT REWRITE =====
# ================================================================
# 3 AI CONTRACT (IMMUTABLE)
# ================================================================
# PURPOSE
#
# This contract defines collaboration rules between the human
# operator and the AI assistant for development of the Fate Automap.
#
# Goals
#
#   • minimize human effort
#   • prevent AI rewrite churn
#   • preserve reverse-engineering knowledge
#   • maintain a stable working codebase


# ------------------------------------------------
# CONTRACT IMMUTABILITY
# ------------------------------------------------
#
# This section is immutable.
#
# When generating new versions of this file (v005, v006, etc.)
# the AI must copy the AI CONTRACT section verbatim.
#
# The AI must NOT:
#
#   • summarize the contract
#   • rewrite the contract
#   • reorder the contract
#   • reformat the contract
#   • regenerate the contract
#
# If a request would modify the contract, the AI must:
#
#   1. STOP
#   2. explain the requested change
#   3. ask for explicit permission
#
# ------------------------------------------------
# SECTION OWNERSHIP
# ------------------------------------------------
#
# Human may edit ANY section at any time.
#
# AI restrictions:
#
# AI must NEVER modify the following sections unless explicitly asked:
#
#   WORKFLOW FOR SUCCESSFUL HUMAN-AI COLLABORATION
#   AI CONTRACT
#
# AI may modify ONLY when explicitly instructed:
#
#   PROJECT CONTEXT SEED
#   PROGRAM SOURCE CODE
#   PROGRAM DOCUMENTATION
#
# SESSION OBJECTIVES
# Normally edited only by the human.
#
# ------------------------------------------------
# ARCHITECTURAL INVARIANTS
# ------------------------------------------------
#
# The following structures must never be removed or simplified.
#
# 1. Coordinate separation
#
#    memory space
#    tile space
#    rendering space
#    display space
#
# 2. Rendering pipeline
#
#    memory → tile model → renderer → display
#
#    The renderer must produce an intermediate artifact
#    (image buffer or surface) independent of the display loop.
#
# 3. Anchor-based memory addressing
#
#    Memory access must remain anchor-based rather than relying
#    solely on absolute addresses.
#
# 4. Documentation authority
#
#    The V214 documentation and its successors define the
#    intended architecture.
#
# ------------------------------------------------
# CODE MODIFICATION RULES
# ------------------------------------------------
#
# When modifying PROGRAM SOURCE CODE the AI must operate in
# SURGICAL PATCH MODE.
#
# Rules
#
#   • modify the smallest number of lines possible
#   • do not refactor
#   • do not rename variables
#   • do not reorder code
#   • do not change formatting
#   • do not remove comments
#   • preserve existing behavior unless explicitly instructed
#
# If a requested change would require architectural redesign,
# the AI must explain the issue instead of rewriting the program.
#
# ------------------------------------------------
# CODE APPLICATION MODEL
# ------------------------------------------------
#
# The human operator does NOT perform manual code edits.
#
# Updated workflow:
#
#   1. AI proposes a minimal surgical patch plan
#   2. Human reviews and explicitly approves the plan
#   3. AI applies the agreed changes
#   4. AI provides a COMPLETE updated file
#   5. Human replaces the file and tests
#
# The AI is responsible for:
#
#   • correct placement of all code changes
#   • maintaining proper indentation
#   • ensuring no duplicate or conflicting code blocks
#   • preserving all existing functionality unless explicitly changed
#
# The human operator must NOT be required to:
#
#   • locate insertion points
#   • manually merge code
#   • resolve indentation issues
#
# All code changes must be delivered fully integrated.
#
# ------------------------------------------------
# COMPILATION REQUIREMENT
# ------------------------------------------------
#
# Any code produced or modified by the AI must compile successfully
# under the Python interpreter before being presented to the human.
#
# The AI must verify that:
#
#   • the code contains no syntax errors
#   • the program can be parsed by the Python interpreter
#
# If the AI cannot ensure this, it must explicitly warn the human
# before presenting the code.
#
# ------------------------------------------------
# FILE DELIVERY REQUIREMENT
# ------------------------------------------------
#
# The AI must always provide complete, ready-to-run files.
#
# The AI must NOT provide:
#
#   • partial snippets
#   • "find and replace" instructions
#   • manual patch steps
#
# All updates must be delivered as:
#
#   • a full file replacement
#   • preserving all unchanged content verbatim
#
# The file must:
#
#   • compile successfully
#   • reflect only the agreed changes
#   • maintain version continuity (v015 → v016, etc.)
#
# The human operator will:
#
#   • download or copy the full file
#   • replace the previous version
#   • run and test
#
# VERSIONING REQUIREMENT
#
# Every delivered file must increment the version number.
#
# Rules:
#
#   • version number must increase sequentially (v015 → v016 → v017)
#   • filename must reflect the new version
#   • internal VERSION variable must match the filename
#
# The AI must NEVER reuse or overwrite a previous version number.
#
# Each delivered file represents a distinct, testable snapshot.
#
# ------------------------------------------------
# CONTEXT SEED RULES
# ------------------------------------------------
#
# The PROJECT CONTEXT SEED is long-form technical documentation.
#
# AI must preserve narrative explanations and historical reasoning.
#
# AI must NOT summarize or compress the document.
#
# When updating context seed:
#
#   • integrate new discoveries
#   • correct inaccurate information
#   • preserve explanations
#   • maintain readability for humans
#
# ------------------------------------------------
# SESSION BEHAVIOR
# ------------------------------------------------
#
# Typical session workflow
#
#   1 human edits SESSION OBJECTIVES
#   2 human provides the file to the AI
#   3 AI proposes plan
#   4 AI provides minimal code patch if requested
#   5 human tests
#   6 human may request context update
#
# ------------------------------------------------
# PRIMARY DESIGN PRINCIPLE
# ------------------------------------------------
#
# The automap codebase is considered stable.
#
# AI collaboration focuses on incremental improvements and
# reverse-engineering discoveries.
#
# Large rewrites are prohibited unless explicitly requested.
#
# ------------------------------------------------
# CONTRACT INTEGRITY CHECK
# ------------------------------------------------
#
# If the AI detects that the contract text has changed compared
# to earlier versions, the AI must immediately notify the human.
#
# The AI must never silently modify this contract.
#
# ===== CONTRACT MUST BE COPIED VERBATIM - DO NOT REWRITE =====


# ================================================================
# 4 PROJECT CONTEXT SEED
# ================================================================
#
# The context seed records discoveries and evolving knowledge about
# Fate – Gates of Dawn memory structures and automap behavior.
#
# Key confirmed discoveries include:
#
# • Encounter class table may contain empty entries with value 0x00.
#   These are not printable ASCII and must not be appended as labels.
#
# • Wilderness map dimensions: 640 × 400 tiles.
#
# • Interior maps: 56 × 56 tiles.
#
# • Coordinate system conversion:
#     Fate origin: lower‑left
#     PC window origin: upper‑left
#     therefore Y axis inversion is required.
#
# • Version-Specific Shifts: 
#   Between v1.6 and v1.7, the memory blocks shift.
#   Segment 1 (Submap Index/Map ID) shifts by +0x66 in confirmed V1.7.
#   Segment 2 (Party/Coords/Encounters/Buffer) shifts by +0x18A.
#

# ================================================================
# 5 EVALUATION
# ================================================================
#
#  - HERE ARE THE THINGS THAT MUST BE TRUE IN ORDER FOR
#    THE OUTPUT TO BE SAFE AND USEFUL IN OUR WORLD
#  - THE CHECKS THAT MIGHT CATCH A DISASTER BEFORE IT HAPPENS

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

# ================================================================
# 7 FUTURE IDEAS
# ================================================================
#
# Automated regression test harness
#
# Rescale entire window contents because hard to read on
#    different monitors.
#

# ================================================================
# 8 PROGRAM SOURCE CODE
# ================================================================

import ctypes, subprocess, re, pygame, time, os
import sys, traceback, py_compile

# ------------------------------------------------
# BASE DIRECTORY RESOLUTION (PY vs EXE)
# ------------------------------------------------
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))



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
# MEMORY → TILE (READ-ONLY HELPERS)
# ------------------------------------------------

def wilderness_memory_to_tile(process):
    """
    Returns player position in wilderness tile_space (640x400).
    Source: COORD_ADDR
    """
    raw = read_mem(process, COORD_ADDR, 12)
    x = int.from_bytes(raw[0:4], "big")
    y = int.from_bytes(raw[4:8], "big")
    return x, y


def city_memory_to_tile(process):
    """
    Returns player position in city/dungeon tile_space (56x56).
    Source: COORD_ADDR
    """
    raw = read_mem(process, COORD_ADDR, 12)
    x = int.from_bytes(raw[0:4], "big")
    y = int.from_bytes(raw[4:8], "big")
    return x, y


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
# --- consistent window location at startup.
# ------------------------------------------------
WINDOW_POS_FILE = os.path.join(BASE_DIR, "window_pos.txt")
print("\n===== FateAutomap run:", time.ctime(), "=====\n")

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
# Dumpfiles share same base name with this program
# ------------------------------------------------
VERSION=os.path.basename(__file__)

# ------------------------------------------------
# Define full access rights in Windows API code
# ------------------------------------------------
PROCESS_ALL_ACCESS=0x1F0FFF

# v222: Added specific targeting to avoid launcher false positives
ENGINE_TARGETS=["fs-uae.exe","winuae.exe"]
LAUNCHER_TARGETS=["fs-uae-launcher.exe"]
kernel=ctypes.windll.kernel32

# ------------------------------------------------
# VERSION PROFILES (LATE-BINDING MAP)
# ------------------------------------------------
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
        "ADDR_SUBMAP_INDEX":  0x8000B5DE, # UPDATED: Verified fix for wilderness transitions
        "ADDR_MAP_ID":        0x8000BA59,
        "ADDR_COORDS":        0x8005475A,
        "ADDR_PARTY_BASE":    0x80050FFE,
        "ADDR_ENCOUNTERS":    0x8005C062,
        "ADDR_MAP_BUFFER":    0x800A534E  
    }
}

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
ADDR_GAME_BEGIN   = 0x80000000

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
# Returns the next unused sequential index for
# a filename with the given prefix and extension
# ------------------------------------------------
def next_index(prefix,ext):
    i=1
    while os.path.exists(os.path.join(BASE_DIR, f"{prefix}_{i:03d}.{ext}")):
        i+=1
    return i

screenshot_counter=next_index(VERSION+"_screenshot","png")
dump_counter=next_index(VERSION+"_memdump","bin")

# ------------------------------------------------
# Defines tile color mapping, tint intensity, and
# a cache for hex-rendering fonts.
# ------------------------------------------------
NIBBLE_PALETTE={
0xB:(120,200,120),
0x4:(80,50,30),
0x2:(40,140,40),
0x6:(170,140,90),
0x1:(0,80,0),
0x5:(130,90,50),
0xA:(150,0,0),
0x3:(0,220,0),
0x9:(0,0,130),
0x8:(80,180,220),
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
]

for g in range(5):
    ENC_COLS.append((f"q{g}",f"Q{g+1}",35))
    ENC_COLS.append((f"t{g}",f"T{g+1}",110))

ENC_COLS.append(("dist","DST",60))



# ------------------------------------------------
# Scans running processes and return the PID of
# a supported emulator if found, otherwise None.
# ------------------------------------------------
def detect_emulator():
    try:
        # v222: Enhanced logging and prioritization
        print("Scanning tasks for emulators...")
        tasks=subprocess.check_output(["tasklist"]).decode(errors="ignore").splitlines()
    except Exception as e:
        print(f"Subprocess error: {e}")
        return None
    
    found_engine = None
    found_launcher = None

    for line in tasks:
        m=re.match(r"(\S+)\s+(\d+)",line)
        if m:
            name=m.group(1).lower()
            pid=int(m.group(2))
            
            if name in ENGINE_TARGETS:
                print(f"FOUND EMULATOR ENGINE: {name} (PID: {pid})")
                found_engine = pid
            elif name in LAUNCHER_TARGETS:
                found_launcher = pid

    if found_engine:
        if found_launcher:
            print(f"INFO: Both emulator and launcher found. Prioritizing engine PID {found_engine}.")
        return found_engine
    
    if found_launcher:
        print(f"WARNING: Only launcher found (PID {found_launcher}). Selecting as fallback.")
        return found_launcher

    print("FAIL: No matching emulator or launcher found in tasklist.")
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


# ------------------------------------------------------------
# WINDOW FOCUS (CTYPES VERSION — NO DEPENDENCIES)
# ------------------------------------------------------------
import ctypes
from ctypes import wintypes

_user32 = ctypes.windll.user32

_EnumWindows = _user32.EnumWindows
_EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)

_GetWindowThreadProcessId = _user32.GetWindowThreadProcessId
_IsWindowVisible = _user32.IsWindowVisible
_SetForegroundWindow = _user32.SetForegroundWindow
_ShowWindow = _user32.ShowWindow

_SW_RESTORE = 9

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

def main():

    global view_mode, enc_scroll, enc_sort_key

    global screenshot_counter,dump_counter
    global dbg_crosshair,dbg_hex,dbg_tint,dbg_enc_coords,dbg_inspector
    global show_grid,beacon,follow_player

    # Initialize late-binding addresses
    global ADDR_CLASS_TABLE, ADDR_SUBMAP_INDEX, ADDR_MAP_ID, ADDR_COORDS
    global ADDR_PARTY_BASE, ADDR_ENCOUNTERS, ADDR_MAP_BUFFER
    global MAP_ADDR, MAP_ID_ADDR, COORD_ADDR, ENCOUNTER_ADDR, BASE_CLASS_TABLE
    global memory_mode

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
        print("Ensure Fate - Gates of Dawn is running and loaded in the emulator.")
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


def resolve_memory_layout(process):
    vid, match, profile = detect_version(process)
    if vid is None:
        return None
    addrs = resolve_addresses(profile, match)
    return vid, addrs
