import bisect
import datetime
import itertools

from gopro_overlay.entry import Entry
from gopro_overlay.timeunits import Timeunit


def pairwise(iterable):  # Added in itertools v3.10
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = itertools.tee(iterable)
    next(b, None)
    return zip(a, b)


class Timeseries:

    def __init__(self, entries=None):
        self.entries = {}
        self.dates = []
        self.modified = False
        if entries is not None:
            self.add(*entries)

    def stepper(self, step: Timeunit):
        self.check_modified()
        return Stepper(self, step)

    @property
    def min(self) -> datetime.datetime:
        self.check_modified()
        return self.dates[0]

    @property
    def max(self) -> datetime.datetime:
        self.check_modified()
        return self.dates[-1]

    def __len__(self):
        self.check_modified()
        return len(self.dates)

    def check_modified(self):
        if self.modified:
            self._update()

    def _update(self):
        self.dates = sorted(list(self.entries.keys()))
        self.modified = False

    def add(self, *entries: Entry):
        for e in entries:
            self.entries[e.dt] = e
        self.modified = True

    def get(self, dt: datetime.datetime, interpolate=True) -> Entry:
        self.check_modified()
        if not self.dates or dt < self.dates[0]:
            raise ValueError("Date is before start")
        if dt > self.dates[-1]:
            raise ValueError("Date is after end")
        if dt in self.entries:
            return self.entries[dt]
        else:
            if not interpolate:
                raise KeyError(f"Date {dt} not found")

            greater_idx = bisect.bisect_left(self.dates, dt)
            lesser_idx = greater_idx - 1

            return self.entries[self.dates[lesser_idx]].interpolate(self.entries[self.dates[greater_idx]], dt)

    def items(self):
        self.check_modified()
        return [self.entries[k] for k in self.dates]

    def process_deltas(self, processor, skip=1):
        self.check_modified()
        diffs = list(zip(self.dates, self.dates[skip:]))

        for a, b in diffs:
            updates = processor(self.entries[a], self.entries[b], skip)
            if updates:
                self.entries[a].update(**updates)

    def process_accel(self, processor, skip=1):
        self.check_modified()
        diffs = list(zip(self.dates, self.dates[skip:]))

        for a, b in diffs:
            updates = processor(self.entries[a], self.entries[b], skip)
            if updates:
                self.entries[b].update(**updates)
    
    def process(self, processor):
        self.check_modified()
        for e in self.dates:
            updates = processor(self.entries[e])
            if updates:
                self.entries[e].update(**updates)


class Stepper:

    def __init__(self, timeseries, step: Timeunit):
        self._timeseries = timeseries
        self._step = step.timedelta()

    def __len__(self):
        return int((self._timeseries.max - self._timeseries.min) / self._step) + 1

    def steps(self):
        end = self._timeseries.max
        running = self._timeseries.min
        while running <= end:
            yield running
            running += self._step
