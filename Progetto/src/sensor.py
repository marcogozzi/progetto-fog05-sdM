from time import sleep
import sys
import random
import abc
import threading

# sys.stderr = open("/tmp/virtual_system/sensor_err.txt", 'w')
# sys.stdout = open("/tmp/virtual_system/sensor_out.txt", 'w')
from typing import List

sys.path.append("/home/marco/.local/lib/python3.6/site-packages")
sys.path.append("/virtual_system/")


class Sensor(metaclass=abc.ABCMeta):

    def __init__(self, um):
        # state
        self.value = 0
        self.um = um

    # methods
    @abc.abstractmethod
    def measure(self):
        return value


class AutomaticSensor(Sensor):

    def __init__(self, um, delay=0):
        # state
        super().__init__(um)
        self._state = "off"
        self.handle = None
        self.delay = delay
        self.repeater = None

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, state):
        # switch on
        old_state = self._state
        self._state = state
        if old_state == "off" and state == "on":
            self.measure_repeat()

    @state.deleter
    def state(self):
        del self._state

    @property
    def delay(self):
        return self._delay

    @delay.setter
    def delay(self, delay):
        self._delay = delay
        if self.state == "on":
            self.measure()

    @delay.deleter
    def delay(self):
        del self._delay

    # methods

    @abc.abstractmethod
    def measure(self):
        # no actual measurement...
        # value = ...
        return value

    def measure_repeat(self):
        self.measure()
        if self.state == "on":
            self.repeater = threading.Timer(self._delay, self.measure_repeat)
            self.repeater.start()

    def start_measuring(self):
        if self.state != "on":
            self.state = "on"
        # print("measuring started, state is " + self.state)

    def stop_measuring(self):
        if self.state != "off":
            self.state = "off"
            self.repeater.cancel()


class MockSub:
    # methods
    @abc.abstractmethod
    def alert(self, value):
        return


class MockSensor(AutomaticSensor):

    def __init__(self, um, delay=1, threshold=0):
        # state
        super().__init__(um, delay)
        self.threshold = threshold
        self.subscribers = []

    @property
    def threshold(self):
        return self._threshold

    @threshold.setter
    def threshold(self, threshold):
        self._threshold = threshold

    @threshold.deleter
    def threshold(self):
        del self._threshold

    def measure(self):
        # mocking measurement...
        self.value = random.randint(1, 100)
        if self.value > self._threshold:
            [subscriber.alert(self.value) for subscriber in self.subscribers]
        return self.value

    def subscribe(self, sub: MockSub):
        self.subscribers.append(sub)


def main():
    mock = MockSensor("cm", 2, 5)
    mock.start_measuring()
    for i in range(15):
        print("iteration " + str(i) + " ... " + str(mock.value))
        sleep(1)

    mock.stop_measuring()


if __name__ == "__main__":
    main()
