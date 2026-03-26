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

