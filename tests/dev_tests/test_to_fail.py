import sys
RESULT = False

print("This test will fail and it's OK")

try:
    a = 1/0
    RESULT = True
except Exception as e:
    sys.print_exception(e, sys.stderr)
    print()
