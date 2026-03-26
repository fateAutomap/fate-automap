# ============================================================
# TEST HARNESS V026 (COMMENT-ENRICHED)
# ============================================================
#
# PURPOSE
# ------------------------------------------------------------
# This program performs regression testing on Python modules.
#
# It allows a human to:
#   1. Select a known-good baseline file
#   2. Select a file under test
#   3. Automatically run a suite of tests (from JSON)
#   4. Compare structural differences (function-level diff)
#   5. Save all results to a versioned output file
#
# DESIGN PRINCIPLES
# ------------------------------------------------------------
# - The harness is GENERIC (does not depend on automap logic)
# - The JSON file defines WHAT to test
# - The harness defines HOW to test it
#
# EXCEPTION (IMPORTANT)
# ------------------------------------------------------------
# This version includes ONE intentional non-generic behavior:
#
#   It PREFERS files matching:
#       FateAutomapV###.py
#
#   WHY:
#       In practice, the working directory contains many .py files,
#       and the user workflow centers on automap versions.
#
#   SAFETY:
#       If no such files are found, it falls back to ALL .py files.
#
#   IMPACT:
#       This is a usability optimization, not a hard dependency.
#
# ============================================================

# v031: auto-select latest testsV###.json and increment results
import os
import re
import json
import sys
import traceback
import importlib.util
from datetime import datetime
import io

MAX_FILES = 9

# ------------------------------------------------------------
# FUNCTION: extract_functions
# PURPOSE:
#   (Describe what this function does.)
# INPUTS:
#   (Describe parameters and expectations.)
# OUTPUTS:
#   (Describe return value.)
# NOTES:
#   (Assumptions, edge cases, risks.)
# ------------------------------------------------------------
def extract_functions(code):
    functions = {}
    lines = code.splitlines()
    py_pattern = re.compile(r'^\s*def\s+(\w+)\s*\(.*\)\s*:')
    i = 0
    while i < len(lines):
        line = lines[i]
        match = py_pattern.match(line)
        if match:
            name = match.group(1)
            start = i
            indent = len(line) - len(line.lstrip())
            j = i + 1
            while j < len(lines):
                next_line = lines[j]
                if next_line.strip() == "":
                    j += 1
                    continue
                next_indent = len(next_line) - len(next_line.lstrip())
                if next_indent <= indent:
                    break
                j += 1
            end = j
            body_lines = lines[start:end]
            functions[name] = {
                "signature": line.strip(),
                "lines": len(body_lines)
            }
            i = j
        else:
            i += 1
    return functions

# ------------------------------------------------------------
# FILE DISCOVERY: recent python files
# ------------------------------------------------------------
# PURPOSE:
#   Identify candidate files for testing.
#
# BEHAVIOR:
#   - Prefer FateAutomapV###.py files (workflow optimization)
#   - Fallback to all .py files if none found
#
# RISK:
#   If naming convention changes, preference may fail silently,
#   but fallback ensures continued operation.
def get_recent_files(directory):
    all_files = [
        f for f in os.listdir(directory)
        if os.path.isfile(os.path.join(directory, f))
        and f.endswith(".py")
    ]

    # Prefer FateAutomap versioned files
    fa_files = [
        f for f in all_files
        if re.match(r"(?i)fateautomapv\d+.*\.py$", f)
    ]

    target = fa_files if fa_files else all_files

    target.sort(key=lambda f: os.path.getmtime(os.path.join(directory, f)), reverse=True)
    return target[:MAX_FILES]

# ------------------------------------------------------------
# FUNCTION: print_files
# PURPOSE:
#   (Describe what this function does.)
# INPUTS:
#   (Describe parameters and expectations.)
# OUTPUTS:
#   (Describe return value.)
# NOTES:
#   (Assumptions, edge cases, risks.)
# ------------------------------------------------------------
def print_files(files, directory):
    print("\nRecent Python Files:\n")
    for i, f in enumerate(files):
        path = os.path.join(directory, f)
        mtime = datetime.fromtimestamp(os.path.getmtime(path))
        print(f"[{i}] {f}  ({mtime.strftime('%Y-%m-%d %H:%M:%S')})")

# ------------------------------------------------------------
# FUNCTION: select_file
# PURPOSE:
#   (Describe what this function does.)
# INPUTS:
#   (Describe parameters and expectations.)
# OUTPUTS:
#   (Describe return value.)
# NOTES:
#   (Assumptions, edge cases, risks.)
# ------------------------------------------------------------
def select_file(prompt, files):
    while True:
        try:
            idx = int(input(prompt))
            if 0 <= idx < len(files):
                return files[idx]
        except:
            pass
        print("Invalid selection. Try again.")

# ------------------------------------------------------------
# FUNCTION: analyze_diff
# PURPOSE:
#   (Describe what this function does.)
# INPUTS:
#   (Describe parameters and expectations.)
# OUTPUTS:
#   (Describe return value.)
# NOTES:
#   (Assumptions, edge cases, risks.)
# ------------------------------------------------------------
def analyze_diff(old_code, new_code):
    old = extract_functions(old_code)
    new = extract_functions(new_code)

    missing = sorted(list(set(old) - set(new)))
    added   = sorted(list(set(new) - set(old)))

    return {
        "missing": missing,
        "added": added,
        "old_size": len(old_code),
        "new_size": len(new_code),
        "old_lines": len(old_code.splitlines()),
        "new_lines": len(new_code.splitlines()),
    }

# ------------------------------------------------------------
# FUNCTION: print_diff
# PURPOSE:
#   (Describe what this function does.)
# INPUTS:
#   (Describe parameters and expectations.)
# OUTPUTS:
#   (Describe return value.)
# NOTES:
#   (Assumptions, edge cases, risks.)
# ------------------------------------------------------------
def print_diff(report):
    print("====================================")
    print("DIFF CHECK")
    print("====================================")

    size_diff = report["new_size"] - report["old_size"]
    line_diff = report["new_lines"] - report["old_lines"]

    print(f"File size:  {size_diff:+} bytes")
    print(f"Line count: {line_diff:+} lines")
    print(f"Functions:  +{len(report['added'])} added, -{len(report['missing'])} removed")

    if report["missing"]:
        print("❌ Missing Functions:")
        for fn in report["missing"]:
            print(f"- {fn}")
        print("DIFF RESULT: ❌ FAIL")
        return False

    print("DIFF RESULT: ✅ PASS")
    return True

# ------------------------------------------------------------
# FUNCTION: load_module
# PURPOSE:
#   (Describe what this function does.)
# INPUTS:
#   (Describe parameters and expectations.)
# OUTPUTS:
#   (Describe return value.)
# NOTES:
#   (Assumptions, edge cases, risks.)
# ------------------------------------------------------------
def load_module(filepath):
    spec = importlib.util.spec_from_file_location("target_module", filepath)
    module = importlib.util.module_from_spec(spec)
    sys.modules["target_module"] = module
    spec.loader.exec_module(module)

    module.memory_mode = "dump"
    module.dump_data = bytearray()

    return module

# ------------------------------------------------------------
# FUNCTION: load_dump_into_module
# PURPOSE:
#   (Describe what this function does.)
# INPUTS:
#   (Describe parameters and expectations.)
# OUTPUTS:
#   (Describe return value.)
# NOTES:
#   (Assumptions, edge cases, risks.)
# ------------------------------------------------------------
def load_dump_into_module(module, filename):
    print(f"Switching dump file: {filename}")

    with open(filename, "rb") as f:
        module.dump_data = bytearray(f.read())

    if hasattr(module, "VERSION_PROFILES") and hasattr(module, "find_bytes"):
        for vid, profile in module.VERSION_PROFILES.items():
            matches = module.find_bytes(None, profile["pattern"])
            if matches:
                offset = matches[0] - profile["base_anchor"]
                module.COORD_ADDR        = profile["ADDR_COORDS"] + offset
                module.ENCOUNTER_ADDR    = profile["ADDR_ENCOUNTERS"] + offset
                module.ADDR_SUBMAP_INDEX = profile["ADDR_SUBMAP_INDEX"] + offset
                print(f"Resolved version: {vid}")
                return

# ------------------------------------------------------------
# FUNCTION: run_tests
# PURPOSE:
#   (Describe what this function does.)
# INPUTS:
#   (Describe parameters and expectations.)
# OUTPUTS:
#   (Describe return value.)
# NOTES:
#   (Assumptions, edge cases, risks.)
# ------------------------------------------------------------
def run_tests(module, tests):
    print("====================================")
    print("FUNCTION TESTS")
    print("====================================")

    passed = 0
    failed = 0
    function_results = {}

    for group_block in tests:
        print("====================================")
        print(group_block.get("group", "UNGROUPED"))

        type_ = group_block.get("type")
        note  = group_block.get("note")

        if type_:
            print(f"TYPE: {type_}")
        if note:
            print(f"NOTE: {note}")

        print("====================================")

        required = group_block.get("required")
        if required:
            if not os.path.exists(required):
                print(f"❌ REQUIRED DUMP NOT FOUND: {required}")
                failed += 1
                continue
            load_dump_into_module(module, required)

        for i, test in enumerate(group_block.get("tests", [])):
            fn_name = test["function"]
            args = test.get("args", [])
            expected = test.get("expected")

            if fn_name not in function_results:
                function_results[fn_name] = True

            print(f"[{i}] {fn_name}({args})")

            try:
                fn = getattr(module, fn_name, None)
                if fn is None:
                    print("  ❌ FAIL: function missing")
                    failed += 1
                    function_results[fn_name] = False
                    continue

                if args == [None] or args == []:
                    result = fn(None)
                else:
                    result = fn(*args)

                if isinstance(result, tuple):
                    result = list(result)

                if result == expected:
                    print("  ✅ PASS")
                    passed += 1
                else:
                    print("  ❌ FAIL")
                    print(f"     expected: {expected}")
                    print(f"     got:      {result}")
                    failed += 1
                    function_results[fn_name] = False

            except Exception:
                print("  ❌ EXCEPTION")
                traceback.print_exc()
                failed += 1
                function_results[fn_name] = False

            print()

    print("====================================")
    print(f"{passed} passed, {failed} failed")
    return failed == 0, passed, failed, function_results



# ------------------------------------------------------------
# FUNCTION: get_latest_tests_file
# PURPOSE:
#   (Describe what this function does.)
# INPUTS:
#   (Describe parameters and expectations.)
# OUTPUTS:
#   (Describe return value.)
# NOTES:
#   (Assumptions, edge cases, risks.)
# ------------------------------------------------------------
def get_latest_tests_file(directory):
    files = [
        f for f in os.listdir(directory)
        if re.match(r"testsV\d+\.json$", f)
    ]
    if files:
        # ------------------------------------------------------------
        # FUNCTION: extract_version
        # PURPOSE:
        #   (Describe what this function does.)
        # INPUTS:
        #   (Describe parameters and expectations.)
        # OUTPUTS:
        #   (Describe return value.)
        # NOTES:
        #   (Assumptions, edge cases, risks.)
        # ------------------------------------------------------------
        def extract_version(f):
            m = re.search(r"testsV(\d+)\.json", f)
            return int(m.group(1)) if m else -1
        files.sort(key=extract_version, reverse=True)
        return files[0]
    return None


# ------------------------------------------------
# NEW: Incrementing results file generator
# ------------------------------------------------
def next_results_file(directory):
    files = [
        f for f in os.listdir(directory)
        if re.match(r"testsV\d+\.results$", f)
    ]
    if not files:
        return "testsV001.results"

    # ------------------------------------------------------------
    # FUNCTION: extract_version
    # PURPOSE:
    #   (Describe what this function does.)
    # INPUTS:
    #   (Describe parameters and expectations.)
    # OUTPUTS:
    #   (Describe return value.)
    # NOTES:
    #   (Assumptions, edge cases, risks.)
    # ------------------------------------------------------------
    def extract_version(f):
        m = re.search(r"testsV(\d+)\.results", f)
        return int(m.group(1)) if m else 0

    files.sort(key=extract_version, reverse=True)
    next_version = extract_version(files[0]) + 1

    return f"testsV{next_version:03d}.results"


# ------------------------------------------------------------
# MAIN EXECUTION FLOW
# ------------------------------------------------------------
# STEP-BY-STEP:
#   1. Discover recent files
#   2. Prompt user to select baseline + test file
#   3. Locate latest testsV###.json
#   4. Generate next results file name
#   5. Buffer all output (stdout/stderr)
#   6. Run diff analysis
#   7. Execute tests
#   8. Write results to disk
#
# NOTE:
#   Output buffering ensures a clean, complete log file.
def main():
    directory = os.getcwd()
    files = get_recent_files(directory)
    if len(files) < 2:
        print("Need at least 2 Python files.")
        return

    print_files(files, directory)
    base_file = select_file("Select KNOWN GOOD BASELINE: ", files)
    new_file = select_file("Select FILE UNDER TEST: ", files)

    tests_file = get_latest_tests_file(os.getcwd())
    if not tests_file:
        print("No testsV###.json found.")
        return

    results_file = next_results_file(os.getcwd())
    print(f"Using tests file: {tests_file}")
    print(f"Writing results to: {results_file}")

    buffer = io.StringIO()
    sys.stdout = buffer
    sys.stderr = buffer

    passed = 0
    failed = 0
    final_result = "ERROR"

    try:
        print("===== Test Harness run:", datetime.now(), "=====")
        print(f"BASELINE: {base_file}")
        print(f"NEW:      {new_file}")
        print(f"Using tests file: {tests_file}")

        with open(base_file, "r", encoding="utf-8", errors="ignore") as f:
            old_code = f.read()
        with open(new_file, "r", encoding="utf-8", errors="ignore") as f:
            new_code = f.read()

        diff_ok = print_diff(analyze_diff(old_code, new_code))

        with open(tests_file, "r") as f:
            tests = json.load(f)

        module = load_module(new_file)
        tests_ok, passed, failed, function_results = run_tests(module, tests)

        final_result = "PASS" if diff_ok and tests_ok else "FAIL"

        
        # -------------------------------
        # FUNCTION COVERAGE SUMMARY
        # -------------------------------
        all_functions = extract_functions(new_code)

        print("\n====================================")
        print("FUNCTION COVERAGE SUMMARY")
        print("====================================\n")

        for fn in sorted(all_functions.keys()):
            if fn in function_results:
                status = "✅" if function_results[fn] else "❌"
            else:
                status = "⬜"
            print(f"{status} {fn}")

        print("====================================")
        print("FINAL RESULT:", final_result)
        print("====================================")

    except Exception:
        print("❌ HARNESS EXCEPTION")
        traceback.print_exc()
        final_result = "ERROR"

    finally:
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(BASE_DIR, results_file), "w", encoding="utf-8") as log:
            log.write("====================================\n")
            log.write(f"FINAL RESULT: {final_result}\n")
            log.write(f"{passed} passed, {failed} failed\n")
            log.write("====================================\n\n")
            log.write(buffer.getvalue())
if __name__ == "__main__":
    main()
