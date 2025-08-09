from pytracer import trace, instrumented, global_monitor, generate_html_report
import time

@trace()
def fast_task():
    time.sleep(0.001)

@trace()
def slow_task():
    time.sleep(0.005)

@trace()
def raises():
    raise ValueError("demo exception from raises()")

@trace()
def parent_task():
    fast_task()
    slow_task()
    try:
        raises()
    except Exception:
        pass

if __name__ == "__main__":
    print("Running demo functions...")
    parent_task()
    fast_task()
    try:
        raises()
    except Exception:
        pass

    # Generate HTML report
    generate_html_report(global_monitor, "out/pytracer_report.html")
    print("\nReport generated: pytracer_report.html")
