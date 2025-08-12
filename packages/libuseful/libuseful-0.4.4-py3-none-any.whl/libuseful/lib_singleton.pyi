__all__ = ['Singleton']

class Singleton:
    @classmethod
    def get_instance(cls, *args, **kargs): ...
