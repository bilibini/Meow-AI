try:
    a=0/0
    print(a)
except Exception as e:
    print(e)
    print(e.__dict__)
    print(type(e))