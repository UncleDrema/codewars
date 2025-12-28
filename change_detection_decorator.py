def change_detection(cls):
    """ Decorator for get_change of class attributes """
    print(dir(cls))
    return cls

@change_detection
class Struct:
    x = 42
    def __init__(self, y=0):
        self.y = y

a = Struct(11)

print(Struct.x)
print(a.x)
print(a.y)