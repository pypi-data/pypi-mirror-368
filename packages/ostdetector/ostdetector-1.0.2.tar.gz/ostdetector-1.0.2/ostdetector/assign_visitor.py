import ast

class AssignVisitor(ast.NodeVisitor):
    def __init__(self, libs, project_name, project_hash, file):   
        self.project_name = project_name
        self.project_hash = project_hash
        self.filename = file
        self.libs_os = libs
        self.modules = set()
        self.chamadas = dict()
        self.assigns = []
        
    def tratar_modulos(self, node, module, package):
        key = node.name
        if node.asname:
            key = node.asname
        if module in self.libs_os:
            self.chamadas[key] = [module, package] # package_name -> [package, module]
        
    def visit_Import(self, node):
        for name in node.names: 
            module = name.name.split(".")[0]    
            self.tratar_modulos(name, module, None)
            self.modules.add(name.name.split(".")[0])
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node):
        if node.module is not None and node.level == 0:
            module = node.module.split(".")[0]
            [self.tratar_modulos(nam, module, nam.name) for nam in node.names ]    
            self.modules.add(module)
        self.generic_visit(node) 

    def gerar_url(self, line):
          return f'https://github.com/{self.project_name}/blob/{self.project_hash}{self.filename}#L{line}' 
       
    def name(self, parent, line, ctx):
        if isinstance(parent.value, ast.Name):
                package = parent.value
                if package.id and package.id in self.chamadas: 
                    module_temp = self.chamadas[package.id]
                    if module_temp[0] in self.libs_os and any(parent.attr in item for item in self.libs_os.values()): 
                        # print(f'({line}) {parent.value.id}.{parent.attr} key: {package.id} ({ctx}) file: {self.filename}')
                        url = self.gerar_url(line)
                        self.assigns.append(
                            [
                                self.project_name, self.project_hash, line, 
                                module_temp[0], parent.attr, 
                                self.filename, url
                            ]
                        )
    
    def visit_Assign(self, node):
        parent = node.value
        self.p = node
        if isinstance(parent, ast.Attribute):
            self.name(parent, node.lineno, "attribute")
        elif isinstance(parent, ast.Call):
            if isinstance(parent.func, ast.Attribute):
                self.name(parent.func, node.lineno, "call-att")
        elif isinstance(parent, ast.Subscript):
            call = parent.value
            if isinstance(call, ast.Call):
                if isinstance(call.func, ast.Attribute):
                    self.name(call.func, node.lineno, "sub-call")
            if isinstance(call, ast.Attribute):
                self.name(call, node.lineno, "sub-att")
        elif isinstance(parent, ast.Compare):
            if isinstance(parent.left, ast.Attribute):
                self.name(parent.left, node.lineno, "compare-att")
        elif isinstance(parent, ast.IfExp):
            if isinstance(parent.test, ast.Call):
                if isinstance(parent.test.func, ast.Attribute):
                    self.name(parent.test.func, node.lineno, "if-call")
        elif isinstance(parent, ast.Tuple) or isinstance(parent, ast.List):
            for value in parent.elts:
                if isinstance(value, ast.UnaryOp):
                    value = value.operand
                if isinstance(value, ast.Call):
                    if isinstance(value.func, ast.Attribute):
                        self.name(value.func, node.lineno, "tuple-call")
                    for arg in value.args:    
                        if isinstance(arg, ast.Attribute):
                            self.name(arg, node.lineno, "tuple-call-arg")
                if isinstance(value, ast.Attribute):
                    self.name(value, node.lineno, "tuple-att")
        self.generic_visit(node) 