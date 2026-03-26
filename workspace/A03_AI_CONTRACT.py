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


