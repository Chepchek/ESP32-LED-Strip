import gc

import utime


def show_memory():
    free = gc.mem_free()
    alloc = gc.mem_alloc()
    total = free + alloc
    print("-" * 20)
    print(f"Используемая память: {alloc} байт ({alloc / total:.1%})")
    print(f"Свободная память: {free} байт ({free / total:.1%})")
    print(f"Общая память: {total} байт")
    print("-" * 20)
    utime.sleep_ms(100)  # небольшая пауза для удобства чтения


print("Память до очистки:")
show_memory()

print("\nОчистка памяти...")
gc.collect()

print("\nПамять после очистки:")
show_memory()
