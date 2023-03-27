
class DrawQueue(object):
    instance = None
    queue = []

    def __new__(cls, *args, **kwargs):
        if cls.instance == None:
            cls.instance = super().__new__(cls)
        return cls.instance


    def push(self, any):
        self.queue.append(any)


    def pop(self):
        if len(self.queue) == 0:
            return None
        return self.queue.pop()
