import sys
import os

print("Python Path:")
for path in sys.path:
    print(path)

print("\nCurrent Directory:")
print(os.getcwd())

try:
    import supabase
    print("\nSupabase Version:")
    print(supabase.__version__)
except ImportError as e:
    print("\nError importing supabase:", e) 