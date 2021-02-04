from time import sleep
import sys
import random
import abc
from datetime import datetime

# sys.stderr = open("/tmp/virtual_system/sensor_err.txt", 'w')
# sys.stdout = open("/tmp/virtual_system/sensor_out.txt", 'w')
from typing import List

sys.path.append("/home/marco/.local/lib/python3.6/site-packages")
sys.path.append("/virtual_system/")


class Actuator(metaclass=abc.ABCMeta):

    # methods
    @abc.abstractmethod
    def execute(self):
        return NotImplementedError


class TimedActuator(Actuator):

    def __init__(self, execution_time):
        # state
        super().__init__()
        self._state = "idle"
        self._execution_time = execution_time

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, state):
        # switch on
        print("new state " + state)
        old_state = self._state
        self._state = state
        if old_state == "idle" and state == "execute":
            self.execute(self._execution_time)

    @state.deleter
    def state(self):
        del self._state

    @property
    def execution_time(self):
        return self._execution_time

    @execution_time.setter
    def execution_time(self, execution_time):
        self._execution_time = execution_time

    @execution_time.deleter
    def execution_time(self):
        del self._execution_time

    # methods

    @abc.abstractmethod
    def execute(self, execution_time: int = 1):
        # no actual action
        sleep(execution_time)
        return NotImplementedError


class MockSub:
    # methods
    @abc.abstractmethod
    def alert(self, value):
        return


class MockTimedActuator(TimedActuator):

    def __del__(self):
        self._output.close()

    def __init__(self, execution_time: int = 3, file_name: str = "output"):
        super().__init__(execution_time)
        self._output = open(file_name, "a+")
        self.subscribers = []

    def execute(self, execution_time: int = -1):
        if execution_time == -1:
            execution_time = self._execution_time
        print("execute mocked")
        self._state = "execute"
        self._output.write("\n---Actuator.execute(" + str(execution_time) + ")\n")
        self._output.write("Actuator start execute @ " + str(datetime.now().strftime("%H:%M:%S")) + "\n")
        sleep(execution_time)
        self._output.write("Actuator finish execute @ " + str(datetime.now().strftime("%H:%M:%S")) + "\n")
        self._output.flush()
        self._state = "idle"

    def subscribe(self, sub: MockSub):
        self.subscribers.append(sub)


def main():
    mock = MockTimedActuator(file_name="prova_pycharm")
    # mock = MockTimedActuator()
    mock.execute()
    mock.execute(7)
    mock.state = "execute"


if __name__ == "__main__":
    main()
