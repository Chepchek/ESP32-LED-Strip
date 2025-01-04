import gc

import utime


def show_memory():
    """
    Display the current memory state of the ESP32 in the console.

    Parameters:
    None

    Returns:
    None. Prints memory usage information to the console.
    """
    free = gc.mem_free()
    alloc = gc.mem_alloc()
    total = free + alloc
    print("-" * 20)
    print(f"Used memory: {alloc} bytes ({alloc / total:.1%})")
    print(f"Free memory: {free} bytes ({free / total:.1%})")
    print(f"Total memory: {total} bytes")
    print("-" * 20)
    utime.sleep_ms(100)  # small pause for readability


print ("\nMemory before cleaning:")
show_memory()

print ("\nclearing memory...")
gc.collect()

print ("\nMemory after clearing:")
show_memory()
