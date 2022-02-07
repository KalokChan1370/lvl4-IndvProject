import ast 
import astpretty
class Node:
    def __init__(self, item):
        self.container = item
        self.children = []

    def add_children(self, input_collection):
        self.children = input_collection

with open ("test.py", "r") as q:
    custom = []
    tree = ast.parse(q.read())
    for node in ast.walk(tree):
        a = Node(node)
        col = ast.iter_child_nodes(node)
        a.add_children(col)
        custom.append(a)


for node in custom:
    for c in node.children:
        astpretty.pprint(c)


