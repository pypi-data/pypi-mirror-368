import time


class stopwatch:
    def __init__(self):
        self.timers = {}

    def click(self, tag):
        """Start or stop the timer for the given tag."""
        if tag not in self.timers:  # Start new timer
            self.timers[tag] = {"running": True, "lap": time.time(), "total": 0.0}
            return
        if not self.timers[tag]["running"]:  # Resume timer
            self.timers[tag]["running"] = True
            self.timers[tag]["lap"] = time.time()
        else:  # Pause timer
            self.timers[tag]["running"] = False
            self.timers[tag]["total"] += time.time() - self.timers[tag]["lap"]
            return self.timers[tag]["total"]

    def read(self, tag):
        """Read the elapsed time of a given timer."""
        return self.timers.get(tag, {}).get("total", 0.0)

    def read_sum(self):
        """Get the sum of all recorded times."""
        return sum(timer["total"] for timer in self.timers.values())

    def timer(self, tag):
        """Context manager for timing a block of code."""

        class TimerContext:
            def __init__(self, stopwatch, tag):
                self.stopwatch = stopwatch
                self.tag = tag

            def __enter__(self):
                self.stopwatch.click(self.tag)  # Start timer

            def __exit__(self, exc_type, exc_value, traceback):
                self.stopwatch.click(self.tag)  # Stop timer

        return TimerContext(self, tag)
