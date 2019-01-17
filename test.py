import time

class test:
    aaa = 1

    def __init__(self, bbb):
        self.bbb = bbb
    
    def func(self, callback):
        ccc = 0
        while ccc<100:
            ccc += 1
            callback(ccc)
            time.sleep(0.2)

    def callbackA(self,argument):
        string = str(self.aaa) + ' ' +str(self.bbb) + ' ' +str(argument)
        print(string)
    
    def execute(self):
        self.func(self.callbackA)

test = test(2)
test.execute()