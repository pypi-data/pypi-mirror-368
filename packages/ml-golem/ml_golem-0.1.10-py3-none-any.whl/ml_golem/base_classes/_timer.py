import time

class Timer:

    def start(self):
        self.start_time = time.time()

    def stop(self):
        if self.start_time is None:
            raise ValueError("Timer has not been started.")
        elapsed_time = time.time() - self.start_time
        self.start_time = None
        return elapsed_time

    def format_time(self, elapsed_time):
        hours, rem = divmod(elapsed_time, 3600)
        minutes, seconds = divmod(rem, 60)
        return f"{int(hours):02}:{int(minutes):02}:{seconds:05.2f}"