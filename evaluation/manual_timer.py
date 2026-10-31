import time

for i in range(1, 11):
    input(f"Press Enter to start reviewing C{i:02d}...")
    start = time.perf_counter()

    input("Press Enter after recording your review...")
    elapsed = time.perf_counter() - start

    print(f"C{i:02d}: {elapsed:.1f} seconds\n")
