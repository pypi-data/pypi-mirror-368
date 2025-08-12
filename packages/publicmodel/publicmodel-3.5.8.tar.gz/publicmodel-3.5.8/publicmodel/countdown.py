import time

from publicmodel.common import value4


class CommonTimer:
    def __init__(self, round_off=2):
        self.round_off = round_off
        self.start_time = time.time()

    def stop_timing(self):
        end_time = time.time()
        elapsed_time = end_time - self.start_time
        if not self.round_off:
            return value4(elapsed_time)
        else:
            elapsed_time = value4(round(elapsed_time, self.round_off))
            return elapsed_time


if __name__ == '__main__':
    timer = CommonTimer()
    time.sleep(2)
    a = timer.stop_timing()
    print(a)
