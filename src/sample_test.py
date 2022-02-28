class Cat:
    def __init__(self, inputName):
        self.name = inputName
    def meow(self):
        print('meow!')
    def baby(self):
        print("kitty")

class Dog:
    def __init__(self, inputName):
        self.name = inputName
    def woof(self):
        print('bark!')
    def baby(self):
        print("puppy")

def testMethod(animal):
    animal.meow()

if __name__ == '__main__':
    dog = Cat()
    testMethod(dog)