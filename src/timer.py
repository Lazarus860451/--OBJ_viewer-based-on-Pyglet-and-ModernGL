import time

timings = {}


def start_timer(name):
    """start time"""
    timings[name + '_start'] = time.time()


def end_timer(name):
    """end time, time taken"""
    start_time = timings.get(name + '_start')
    if start_time:
        elapsed = time.time() - start_time
        timings[name] = elapsed
        print(f"  {name}: {elapsed:.3f} seconds")


def print_all_timings():
    """print"""
    print("\n" + "=" * 50)
    print("Performance Statistics")
    print("=" * 50)

    total = 0

    order = [
        'Window create', 'Model load', 'Shader compile',
        'Texture load', 'Renderer init', 'Total init'
        ]
    for name in order:
        if name in timings:
            print(f"  {name:12}: {timings[name]:.3f} seconds")
            total = total + timings[name]

    print("-" * 50)
    print(f"  {'Total':12}: {total:.3f} seconds")
    print("=" * 50)
