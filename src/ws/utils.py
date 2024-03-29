import traceback

from channels.exceptions import StopConsumer


def catch_exception(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except StopConsumer:
            raise
        except Exception:
            print(traceback.format_exc().strip("\n"), "<--- from consumer")
            raise

    return


class Notify:
    """Уведомление."""

    def init(self, action=None, data=None):
        self.action = action
        self.data = data

    @property
    def as_notify(self):
        return {"action": self.action, "type": "notify", "data": self.data}

    @property
    def as_success_response(self):
        return {"action": self.action, "type": "response", "status": "success", "data": self.data}

    @property
    def as_fail_response(self):
        return {"action": self.action, "type": "response", "status": "fail", "data": self.data}

    def str(self):
        return f"{self.action}, {self.data}"
