class BasePlugin(object):

    @classmethod
    def __str__(cls):
        return cls.__name__

    @classmethod
    def push(cls):
        raise NotImplementedError
