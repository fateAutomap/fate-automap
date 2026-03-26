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


