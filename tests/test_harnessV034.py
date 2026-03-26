# ============================================================
# TEST HARNESS V034 (DUAL-MODULE + JSON-DRIVEN MODULES)
# ============================================================
#
# Enhancements:
# - Supports JSON-driven module selection
# - Supports dual-module comparison (old vs new)
# - Backward compatible with single-module + expected tests
# - Keeps existing workflow and output format
#
# JSON OPTIONS:
# ------------------------------------------------------------
# {
#   "modules": {
#     "constants": "B08_CONSTANTS_v002",
#     "functions": "B09_FUNCTIONS_v002"
#   }
# }
#
# OR (dual mode):
# {
#   "modules": {
#     "old": {
#       "constants": "B08_CONSTANTS_v002",
#       "functions": "B09_FUNCTIONS_v002"
#     },
#     "new": {
#       "constants": "B08_CONSTANTS_v003",
#       "functions": "B09_FUNCTIONS_v003"
#     }
#   }
# }
#
# Tests:
# ------------------------------------------------------------
# {
#   "function": "read_coords",
#   "expected": [x,y]
# }
#
# OR:
# {
#   "function": "read_coords",
#   "compare": "old_vs_new"
# }
#
# ============================================================

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
def get_recent_files(directory):
    all_files = [
        f for f in os.listdir(directory)
        if os.path.isfile(os.path.join(directory, f))
        and f.endswith(".py")
    ]

    fa_files = [
        f for f in all_files
        if re.match(r"(?i)B10_MAIN_v\d+.*\.py$", f)
    ]

    target = fa_files if fa_files else all_files
    target.sort(key=lambda f: os.path.getmtime(os.path.join(directory, f)), reverse=True)
    return target[:MAX_FILES]

# ------------------------------------------------------------
def print_files(files, directory):
    print("\nRecent Python Files:\n")
    for i, f in enumerate(files):
        path = os.path.join(directory, f)
        mtime = datetime.fromtimestamp(os.path.getmtime(path))
        print(f"[{i}] {f}  ({mtime.strftime('%Y-%m-%d %H:%M:%S')})")

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
def load_versioned_modules(c_name, f_name):
    # load constants
    c_spec = importlib.util.find_spec(c_name)
    c = importlib.util.module_from_spec(c_spec)
    c_spec.loader.exec_module(c)

    # load functions
    f_spec = importlib.util.find_spec(f_name)
    f = importlib.util.module_from_spec(f_spec)
    f_spec.loader.exec_module(f)

    # initialize shared state
    c.memory_mode = "dump"
    c.dump_data = bytearray()

    return c, f

# ------------------------------------------------------------
def load_dump(c, f, filename):
    print(f"Switching dump file: {filename}")

    with open(filename, "rb") as fh:
        c.dump_data = bytearray(fh.read())

    for vid, profile in c.VERSION_PROFILES.items():
        matches = f.find_bytes(None, profile["pattern"])
        if matches:
            offset = matches[0] - profile["base_anchor"]

            c.COORD_ADDR        = profile["ADDR_COORDS"] + offset
            c.ENCOUNTER_ADDR    = profile["ADDR_ENCOUNTERS"] + offset
            c.ADDR_SUBMAP_INDEX = profile["ADDR_SUBMAP_INDEX"] + offset

            print(f"Resolved version: {vid}")
            return

# ------------------------------------------------------------
def run_tests(config, tests):
    print("====================================")
    print("FUNCTION TESTS")
    print("====================================")

    passed = 0
    failed = 0
    function_results = {}

    dual_mode = "old" in config and "new" in config

    if dual_mode:
        c_old, f_old = load_versioned_modules(
            config["old"]["constants"],
            config["old"]["functions"]
        )
        c_new, f_new = load_versioned_modules(
            config["new"]["constants"],
            config["new"]["functions"]
        )
    else:
        c_new, f_new = load_versioned_modules(
            config["constants"],
            config["functions"]
        )
        c_old = f_old = None

    for group_block in tests:
        print("====================================")
        print(group_block.get("group", "UNGROUPED"))
        print("====================================")

        required = group_block.get("required")
        if required:
            if dual_mode:
                load_dump(c_old, f_old, required)
                load_dump(c_new, f_new, required)
            else:
                load_dump(c_new, f_new, required)

        for i, test in enumerate(group_block.get("tests", [])):
            fn_name = test["function"]
            args = test.get("args", [])
            expected = test.get("expected")
            compare = test.get("compare")

            print(f"[{i}] {fn_name}({args})")

            try:
                if dual_mode and compare == "old_vs_new":
                    fn_old = getattr(f_old, fn_name, None)
                    fn_new = getattr(f_new, fn_name, None)

                    old_result = fn_old(*args) if args else fn_old(None)
                    new_result = fn_new(*args) if args else fn_new(None)

                    if old_result == new_result:
                        print("  ✅ PASS (match)")
                        passed += 1
                    else:
                        print("  ❌ FAIL (mismatch)")
                        print("     old:", old_result)
                        print("     new:", new_result)
                        failed += 1
                else:
                    fn = getattr(f_new, fn_name, None)
                    result = fn(*args) if args else fn(None)

                    if isinstance(result, tuple):
                        result = list(result)

                    if result == expected:
                        print("  ✅ PASS")
                        passed += 1
                    else:
                        print("  ❌ FAIL")
                        print("     expected:", expected)
                        print("     got:", result)
                        failed += 1

            except Exception:
                print("  ❌ EXCEPTION")
                traceback.print_exc()
                failed += 1

            print()

    print("====================================")
    print(f"{passed} passed, {failed} failed")
    return failed == 0

# ------------------------------------------------------------
def get_latest_tests_file(directory):
    files = [f for f in os.listdir(directory) if re.match(r"testsV\d+\.json$", f)]
    if not files:
        return None

    def extract_version(f):
        m = re.search(r"testsV(\d+)\.json", f)
        return int(m.group(1)) if m else -1

    files.sort(key=extract_version, reverse=True)
    return files[0]

# ------------------------------------------------------------
def main():
    directory = os.getcwd()
    files = get_recent_files(directory)

    print_files(files, directory)
    base_file = select_file("Select KNOWN GOOD BASELINE: ", files)
    new_file = select_file("Select FILE UNDER TEST: ", files)

    tests_file = get_latest_tests_file(directory)
    if not tests_file:
        print("No tests file found.")
        return

    with open(tests_file, "r") as f:
        data = json.load(f)

    modules_cfg = data.get("modules", {})
    tests = data if isinstance(data, list) else data.get("tests", [])

    run_tests(modules_cfg, tests)

if __name__ == "__main__":
    main()
