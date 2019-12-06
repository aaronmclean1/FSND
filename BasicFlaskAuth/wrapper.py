from functools import wraps

def add_greeting(greeting=''):
    def greeting_decorator(f):

        @wraps(f)
        def wraps_decorator(*args, **kwargs):
            # for key, value in kwargs.items():
            #     print ("%s == %s" %(key, value))
            # for arg in args:
            #     print (arg)
            print(greeting)
            away = 'Do not disturb'
            return f(away, *args, **kwargs)
        return wraps_decorator
    return greeting_decorator

@add_greeting("what time is it? ")

# away has to be listed first in function args
def print_name(away, name):
    print(name)
    print(away)

print_name("aaron")