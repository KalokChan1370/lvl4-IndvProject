class test:
    def __init__(self, name, percentage, grade):
        self.name = name
        self.percentage = percentage
        self.grade = grade

    def foo(self):
        print(f"{self.name} got a percentage of {self.percentage} and a grade of {self.grade}")


python = test("Python", 85.5, "A")
python.foo()