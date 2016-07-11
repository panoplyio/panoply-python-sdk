class Emitter(object):
    _events = None

    def __init__(self):
        self._events = {}

    def on(self, name, fn):
        self._events.setdefault(name, []).append(fn)
        return self

    def fire(self, name, data):
        for fn in self._events.get("*", []):
            fn(name, data)

        for fn in self._events.get(name, []):
            fn(data)

        return self