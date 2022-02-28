import ast
import astpretty

'''wrapper class for ast.<class>'''


class Node:
    def __init__(self, item):
        self.container = item
        self.children = []

    def add_children(self, input_collection):
        self.children = input_collection


'''helper function to collect ast.<class> objects'''
def buildTree():
    custom_tree = []
    with open("sample_test.py", "r") as source:
        tree = ast.parse(source.read())
        for node in ast.walk(tree):
            a = Node(node)
            collection = ast.iter_child_nodes(node)
            a.add_children(collection)
            custom_tree.append(a)
    return custom_tree


'''@dic_rules - rulebase for object types @var_assigns current tracked variables'''
dic_rules = {}
var_assigns = {}


'''@node method ast node'''
def buildRule(node):
    global dic_rules
    for stmt in node.body:
        if isinstance(stmt, ast.FunctionDef) and stmt.name != '__init__':
            dic_rules[node.name] = stmt.name


'''check whether assigned object variable is passed into method parameters'''
def variable_used_in_scope(var, node):
    for elem in node.body:
        if isinstance(elem, ast.Expr):
            if elem.value.args[0].id == var:
                print(f'we got a hit, method: {elem.value.func.id}, uses variable: {elem.value.args[0].id}')
                return elem.value.func.id
    return None


def get_method_node(target):
    for elem in ast.Module(tree[0].container).body.body:
        if isinstance(elem, ast.FunctionDef) and elem.name == target:
            return elem


'''@node ast.class, @target monitored method call'''
def finder(node, oldVar=None, method=None, newVar=None, begin=True):
    '''start by getting all classes, rules and id main'''
    if begin:
        for elem in node.body.body:
            if isinstance(elem, ast.ClassDef):
                buildRule(elem)  # create object rulebase
        for elem in node.body.body:
            if isinstance(elem, ast.If):
                for i in elem.body:
                    if isinstance(i, ast.Assign):
                        print("elem:", ast.dump(elem))
                        print("target,",i.targets[0].id)
                        updateVarAssignment(i.targets[0].id, i.value.func.id)
                        # is it used within the scope?
                        target_method = variable_used_in_scope(i.targets[0].id, elem)
                        if target_method is not None:
                            # we found it, method is passed to a method in scope
                            finder(node, i.targets[0].id, target_method, None, False)
    else:
        global var_assigns
        node2 = get_method_node(method)
        #update the reference to the new scopped varaible. Assumes the varaible id will change.
        newVar = node2.args.args[0].arg
        print(newVar)
        var_assigns[newVar] = var_assigns[oldVar]
        del var_assigns[oldVar]
        for elem in node2.body:
            if isinstance(elem, ast.Expr) and elem.value.func.value.id == newVar:
                # does it make an illegal argument?
                print(elem.value.func.attr)
                print(dic_rules[var_assigns[newVar]])
                if elem.value.func.attr not in dic_rules[
                    var_assigns[newVar]
                ]:
                    print('This is what we are looking for')


'''@var varaible name, @cType variable type'''
def updateVarAssignment(var, cType):
    global var_assigns
    if var in var_assigns:
        print(f'varaible, {var} already assigned?')
    else:
        var_assigns[var] = cType


tree = []


'''assumes first if is main, tr[0] is root ast module'''
def main():
    global var_assigns, tree
    tree = buildTree()
    root = ast.Module(tree[0].container)
    finder(root)

if __name__ == "__main__":
    main()