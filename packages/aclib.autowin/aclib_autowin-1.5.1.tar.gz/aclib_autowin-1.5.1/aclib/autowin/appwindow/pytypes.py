from typing import Callable
from functools import wraps
from aclib.winlib import winapi

class reactive_dict(dict):
    __old = dict
    __new = dict
    __diffkeys = str

    def __init__(self, data: dict={}, *, on_update: Callable[[__old, __new, __diffkeys], None]=None):
        super().__init__(data)
        self.__update_event = on_update

    def update(self, data: dict={}, **kwargs):
        old = self.copy()
        super().update(data, **kwargs)
        if self.__update_event:
            diffkeys = '|'.join(k for k, v in self.items() if k not in old or old[k] is not v)
            self.__update_event(old, self, diffkeys)

    def unref(self):
        self.__update_event = None

def apptask(task, task_thread=0):
    @wraps(task)
    def wrappedtask(self, *args, **kwargs):
        task_tid = task_thread or winapi.GetWindowThreadProcessId(self.handle)[0]
        if winapi.GetCurrentThreadId() == task_tid:
            return task(self, *args, **kwargs)
        return winapi.RequestMsgloopTask(task, task_tid, self, *args, **kwargs)
    return wrappedtask
