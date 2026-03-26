# ============================================================
# TEST HARNESS V037 (CLEAN BUILD)
# ============================================================

import os
import re
import json
import sys
import traceback
import importlib.util
import inspect
from datetime import datetime
import io

# ------------------------------------------------------------
def extract_functions(code):
    funcs = {}
    for line in code.splitlines():
        m = re.match(r'^\s*def\s+(\w+)\(', line)
        if m:
            funcs[m.group(1)] = True
    return funcs

# ------------------------------------------------------------
def analyze_diff(old_code, new_code):
    old = set(extract_functions(old_code))
    new = set(extract_functions(new_code))
    return {
        "missing": sorted(old - new),
        "added": sorted(new - old),
        "old_lines": len(old_code.splitlines()),
        "new_lines": len(new_code.splitlines()),
    }

# ------------------------------------------------------------
def print_diff(diff):
    print("====================================")
    print("DIFF CHECK")
    print("====================================")
    print(f"Line count: {diff['new_lines']-diff['old_lines']:+}")
    print(f"Functions: +{len(diff['added'])}, -{len(diff['missing'])}")
    if diff["missing"]:
        print("❌ Missing:", diff["missing"])
        return False
    print("✅ DIFF OK")
    return True

# ------------------------------------------------------------
def load_modules(c_name, f_name):
    c_spec = importlib.util.find_spec(c_name)
    c = importlib.util.module_from_spec(c_spec)
    c_spec.loader.exec_module(c)

    f_spec = importlib.util.find_spec(f_name)
    f = importlib.util.module_from_spec(f_spec)
    f_spec.loader.exec_module(f)

    c.memory_mode = "dump"
    c.dump_data = bytearray()

    return c, f

# ------------------------------------------------------------
def next_results_file(directory):
    files = [f for f in os.listdir(directory) if re.match(r"testsV\d+\.results", f)]
    if not files:
        return "testsV001.results"
    nums = [int(re.search(r"(\d+)", f).group(1)) for f in files]
    return f"testsV{max(nums)+1:03d}.results"

# ------------------------------------------------------------
def run_tests(c, f, tests):
    passed = 0
    failed = 0
    results = {}

    for group in tests:
        print("====================================")
        print(group.get("group",""))
        print("====================================")

        if "required" in group:
            with open(group["required"], "rb") as fh:
                c.dump_data = bytearray(fh.read())

        for t in group["tests"]:
            fn = getattr(f, t["function"], None)
            if not fn:
                print("❌ missing function")
                failed += 1
                continue

            args = t.get("args", [])
            result = fn(*args) if args else fn(None)

            if isinstance(result, tuple):
                result = list(result)

            if result == t["expected"]:
                print("✅", t["function"])
                passed += 1
            else:
                print("❌", t["function"], "expected", t["expected"], "got", result)
                failed += 1
                results[t["function"]] = False

    return passed, failed

# ------------------------------------------------------------
def main():
    tests_file = max([f for f in os.listdir() if f.startswith("testsV") and f.endswith(".json")])
    print("Using tests file:", tests_file)

    data = json.load(open(tests_file))
    modules = data.get("modules", {})
    tests = data.get("tests", data)

    c, f = load_modules(modules["constants"], modules["functions"])

    buffer = io.StringIO()
    sys.stdout = buffer

    print("Run:", datetime.now())

    passed, failed = run_tests(c, f, tests)

    diff_ok = True
    print("\n(no diff in single mode)")

    print("\nRESULT:", passed, "passed,", failed, "failed")

    sys.stdout = sys.__stdout__
    output = buffer.getvalue()
    print(output)

    fname = next_results_file(os.getcwd())
    print("Writing results to:", fname)

    with open(fname, "w", encoding="utf-8") as f_out:
        f_out.write(output)

# ------------------------------------------------------------
if __name__ == "__main__":
    main()
