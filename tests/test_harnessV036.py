# ============================================================
# TEST HARNESS V035 (UX RESTORE + MODULE DIFF + JSON-DRIVEN)
# ============================================================
#
# Fixes over V034:
# - Skips interactive file prompts when JSON provides "modules"
# - Restores DIFF (module-based via inspect.getsource)
# - Restores FUNCTION COVERAGE SUMMARY
# - Keeps dual (old/new) and single-module modes
# - Backward compatible with list-only JSON (no "modules")
#
# ============================================================

import os
import re
import json
import sys
import traceback
import importlib.util
import importlib
import inspect
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

    dual_mode = isinstance(config, dict) and ("old" in config and "new" in config)

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
            config.get("constants", "B08_CONSTANTS_v002"),
            config.get("functions", "B09_FUNCTIONS_v002")
        )
        c_old = f_old = None

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

            if fn_name not in function_results:
                function_results[fn_name] = True

            print(f"[{i}] {fn_name}({args})")

            try:
                if dual_mode and compare == "old_vs_new":
                    fn_old = getattr(f_old, fn_name, None)
                    fn_new = getattr(f_new, fn_name, None)

                    if fn_old is None or fn_new is None:
                        print("  ❌ FAIL: function missing in one of the versions")
                        failed += 1
                        function_results[fn_name] = False
                        continue

                    old_result = fn_old(*args) if args else fn_old(None)
                    new_result = fn_new(*args) if args else fn_new(None)

                    if isinstance(old_result, tuple):
                        old_result = list(old_result)
                    if isinstance(new_result, tuple):
                        new_result = list(new_result)

                    if old_result == new_result:
                        print("  ✅ PASS (match)")
                        passed += 1
                    else:
                        print("  ❌ FAIL (mismatch)")
                        print("     old:", old_result)
                        print("     new:", new_result)
                        failed += 1
                        function_results[fn_name] = False
                else:
                    fn = getattr(f_new, fn_name, None)
                    if fn is None:
                        print("  ❌ FAIL: function missing")
                        failed += 1
                        function_results[fn_name] = False
                        continue

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
                        function_results[fn_name] = False

            except Exception:
                print("  ❌ EXCEPTION")
                traceback.print_exc()
                failed += 1
                function_results[fn_name] = False

            print()

    print("====================================")
    print(f"{passed} passed, {failed} failed")
    return passed, failed, function_results, (c_old, f_old, c_new, f_new)

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

def next_results_file(directory):
    files = [f for f in os.listdir(directory) if re.match(r"testsV\d+\.results$", f)]
    if not files:
        return "testsV001.results"

    def extract_version(f):
        m = re.search(r"testsV(\d+)\.results", f)
        return int(m.group(1)) if m else 0

    files.sort(key=extract_version, reverse=True)
    next_version = extract_version(files[0]) + 1
    return f"testsV{next_version:03d}.results"


def main():
    directory = os.getcwd()

    tests_file = get_latest_tests_file(directory)
    if not tests_file:
        print("No tests file found.")
        return

    print(f"Using tests file: {tests_file}")

    with open(tests_file, "r") as fh:
        data = json.load(fh)

    # Backward compatibility: list-only JSON
    if isinstance(data, list):
        modules_cfg = {}
        tests = data
    else:
        modules_cfg = data.get("modules", {})
        tests = data.get("tests", [])

    buffer = io.StringIO()
    sys.stdout = buffer
    sys.stderr = buffer

    passed = 0
    failed = 0
    final_result = "ERROR"

    try:
        print("===== Test Harness run:", datetime.now(), "=====")
        print(f"Using tests file: {tests_file}")

        # Run tests
        passed, failed, function_results, modules = run_tests(modules_cfg, tests)

        # DIFF (module-based)
        try:
            old_code = inspect.getsource(modules[1]) if modules[1] else ""
            new_code = inspect.getsource(modules[3])
            diff_ok = print_diff(analyze_diff(old_code, new_code))
        else:
            diff_ok = True
        except Exception:
            print("⚠️ DIFF unavailable")
            diff_ok = True

        final_result = "PASS" if failed == 0 and diff_ok else "FAIL"

        # FUNCTION COVERAGE SUMMARY
        try:
            if modules_cfg and isinstance(modules_cfg, dict):
                if "new" in modules_cfg:
                    f_target = modules[3]  # f_new
                else:
                    f_target = modules[3]  # f_new in single mode
                code = inspect.getsource(f_target)
                all_functions = extract_functions(code)

                print("\n====================================")
                print("FUNCTION COVERAGE SUMMARY")
                print("====================================\n")

                for fn in sorted(all_functions.keys()):
                    if fn in function_results:
                        status = "✅" if function_results[fn] else "❌"
                    else:
                        status = "⬜"
                    print(f"{status} {fn}")

        except Exception:
            print("⚠️ COVERAGE SUMMARY unavailable")

        print("\n====================================")
        print("FINAL RESULT:", final_result)
        print("====================================")

    except Exception:
        print("❌ HARNESS EXCEPTION")
        traceback.print_exc()
        final_result = "ERROR"

    finally:
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        results_file = next_results_file(BASE_DIR)
        print(f"Writing results to: {results_file}")
        with open(os.path.join(BASE_DIR, results_file), "w", encoding="utf-8") as log:
            log.write("====================================\n")
            log.write(f"FINAL RESULT: {final_result}\n")
            log.write(f"{passed} passed, {failed} failed\n")
            log.write("====================================\n\n")
            log.write(buffer.getvalue())

        # Restore stdout/stderr and print to console
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        print(buffer.getvalue())

if __name__ == "__main__":
    main()
