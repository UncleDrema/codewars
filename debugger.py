from functools import wraps


class Debugger(object):
    attribute_accesses = []
    method_calls = []

    @staticmethod
    def log_getattr(cls, attr_name, value):
        Debugger.attribute_accesses.append({
            'action': 'get',
            'class': cls,
            'attribute': attr_name,
            'value': value
        })

    @staticmethod
    def log_setattr(cls, attr_name, value):
        Debugger.attribute_accesses.append({
            'action': 'set',
            'class': cls,
            'attribute': attr_name,
            'value': value
        })

    @staticmethod
    def log_call(cls, method_name, args, kwargs):
        Debugger.method_calls.append({
            'class': cls,
            'method': method_name,
            'args': args,
            'kwargs': kwargs
        })


class Meta(type):
    def __new__(cls, name, bases, attrs):
        new_class = super().__new__(cls, name, bases, attrs)

        def new_getattribute(self, name):
            value = object.__getattribute__(self, name)
            Debugger.log_getattr(new_class, name, value)

            if callable(value):
                @wraps(value)
                def wrapper(*args, **kwargs):
                    real_args = tuple([self] + list(args))
                    Debugger.log_call(new_class, value.__name__, real_args, kwargs)
                    return value(*args, **kwargs)

                return wrapper
            else:
                return value

        new_class.__getattribute__ = new_getattribute

        def new_setattr(self, name, value):
            Debugger.log_setattr(new_class, name, value)
            object.__setattr__(self, name, value)

        new_class.__setattr__ = new_setattr
        return new_class

    def __call__(cls, *args, **kwargs):
        instance = super().__call__(*args, **kwargs)
        real_args = tuple([instance] + list(args))
        Debugger.log_call(cls, '__init__', real_args, kwargs)

        return instance