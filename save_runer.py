import traceback

def runer():

    while True:
        k = None
        try:
            k = input()
            int(k)
            f(k)
        except Exception as e:
            r = traceback
            print (k, e.args, e, type(e))
            print (r)
        else:
            print('SHA')
        print('No else')

def f(l):
    #assert int(l) < 10, 'Very big number'
    if int(l) > 10:
        raise MyExept('qwe')

class MyExept(Exception):
    def __init__(self, a):
        pass

    def __call__(self, *args, **kwargs):
        return Exception(*args)

#s = MyExept(0)
#try:
#    int('1')
#except Exception:
#    print(1)
#else:
#    print(2)
#runer()

def space_cut(word):
    n = len(word)
    back = 0
    front = 0
    last_char = word[-1]
    first_char = word[0]
    while last_char == ' ' and back + 1 < n:
        back += 1
        last_char = word[-back - 1]
    while first_char == ' ' and front + 1 < n:
        front += 1
        first_char = word[front]
    return word[front:n - back]


def a(e):
    e = 'R'
    return e
e = 'r'
#print(space_cut('  lki io  '), 's',e,a(e),e)
