import ast
import os
import shutil
from ostdetector.get_repo import Repo
from ostdetector.writer_csv import WriterCSV
from ostdetector.collect_visitor import CallVisitor
from ostdetector.assign_visitor import AssignVisitor

class Detector:
    def __init__(self, repository, output_dir="data"):   
        self.repository = repository
        self.output_dir = output_dir
        if not output_dir:
            self.output_dir = "data"
        self.libs_os =  dict()
        self.libs_os['sys'] = [ 'platform', 'getwindowsversion']
        self.libs_os['os'] = ['name', 'supports_bytes_environ', 'name']
        self.libs_os['platform'] = ['platform', 'system', 'version', 'uname','win32_edition','win32_ver','win32_is_iot','mac_ver','libc_ver', 'freedesktop_os_release']
        self.decorators = ['pytest.mark.skipif', 'mark.skipif', 'skipif', 'pytest.mark.xfail', 'mark.xfail' ,'xfail', 'unittest.skipUnless','skipUnless', 'unittest.skipIf', 'skipIf']
        self.heads_decorator = ['project_name','project_hash', 'line', 'module', 'package', 'platform', 'decorator', 'reason',  'filename','func_def', 'class_def', 'url']
        self.heads_compare = ['project_name','project_hash','line', 'module', 'package', 'platform', 'file', 'function', 'method_type','url']
        self.heads_project_metadata = ['project_name','project_hash', 'libos_use', 'tests_files', 'tests_files_libos_use', 'tests_files_libos_use_and_call',
                                'count_calls_libos_in_code', 'count_calls_libos_in_decorator', 'count_class_decorator', 'count_method_decorator']
        self.heads_assigns = ['project_name','project_hash', 'line', 'module', 'package', 'filename', 'url']
    
    def all_files(self, dir, extension='.py'):
        """ 
        List all files in dir
        """
        from pathlib import Path
        path = Path(dir)
        files = []
        for file in path.rglob(pattern=f'*{extension}'):
            files.append(file)
        return files
            
    def clone(self, repo_name):
        parent = os.path.dirname(self.output_dir)
        if parent == "":
            os.makedirs(self.output_dir, exist_ok=True)
        dir = f'{self.output_dir}/{repo_name}'
        url = f'https://github.com/{repo_name}'
        repo = Repo(repo_name,url)
        local = repo.clone_at(dir)
        print(f'clone: {repo.name}')
        commit_hash = local.commit_head()
        return repo.name, commit_hash, local.path()

    def collect(self):
        projects_metadata = []
        assigns = []

        project_libos_use = 0 # number of projects using os-libs 
        count_tests_files = 0 # number of tests files 
        count_tests_files_libos_use = 0 # number of tests files that declare and use the os-libs 
        count_tests_files_libos_use_and_call = 0 # number of different tests files that declare, use the os-libs and call specifics methods
        count_calls_libos_in_code = 0 # number of calls to os-libs in code
        count_calls_libos_in_decorator = 0 # number of calls to os-libs in decorator
        count_class_decorator = 0 
        count_method_decorator = 0
        
        project_name, project_hash, project_dir = self.clone(self.repository)
        packages = []
        razions = []
        for python_file in self.all_files(project_dir):
            if python_file.is_dir(): continue #only files
            filename = str(python_file).replace(project_dir,"")
            if not 'test' in filename: continue #only test files
            
            try: # fill data
                parser = ast.parse(open(python_file, 'rb').read())
                monitor = CallVisitor(self.libs_os, 
                                        project_name,
                                        project_hash,
                                        filename,
                                        self.decorators)                    
                monitor.visit(parser)
                
                verify = AssignVisitor(self.libs_os, 
                                        project_name,
                                        project_hash,
                                        filename)
                verify.visit(parser)
                count_tests_files = count_tests_files + 1 #all tests
                
                if not monitor.modules:  continue #only files declare libs_os
                if not set(self.libs_os.keys()).intersection(monitor.modules): continue
                                    
                if len(monitor.package_os) > 0:
                    packages.extend(monitor.package_os)
                        
                if len(monitor.razions) > 0:
                    for row in monitor.razions:
                        row_temp = []    
                        for v in self.heads_decorator:
                            row_temp.extend([row[v]])
                            if v == "func_def" and str(row[v]).strip() == "": 
                                count_class_decorator = count_class_decorator + 1
                                
                        razions.append(row_temp)
                
                if len(verify.assigns) > 0:
                    assigns.extend(verify.assigns)
                    
                project_libos_use = 1 #project uses libos
                count_tests_files_libos_use = count_tests_files_libos_use + 1 #only tests use libos
                count_calls_libos_in_code = count_calls_libos_in_code + len(monitor.package_os) 
                count_calls_libos_in_decorator = count_calls_libos_in_decorator+ len(monitor.razions)
                
                if (len(monitor.package_os) > 0 or len(monitor.razions) > 0):
                    count_tests_files_libos_use_and_call = count_tests_files_libos_use_and_call +1
                    
            except SyntaxError as ex:
                print(f'SyntaxError: {ex} in {python_file}') 
        
        count_method_decorator = count_calls_libos_in_decorator - count_class_decorator # method = all - class
        
        projects_metadata.append([
            project_name, project_hash,project_libos_use,
            count_tests_files, count_tests_files_libos_use, count_tests_files_libos_use_and_call, 
            count_calls_libos_in_code,count_calls_libos_in_decorator,
            count_class_decorator, count_method_decorator
        ])
        
        writer = WriterCSV(name=f'experiment_{project_name.replace("/","_")}_compare', path=f"{self.output_dir}")
        writer.write(head=self.heads_compare, rows=packages)
        
        writer = WriterCSV(name=f'experiment_{project_name.replace("/","_")}_reasons', path=f"{self.output_dir}")
        writer.write(head=self.heads_decorator, rows=razions) 
        
        writer = WriterCSV(name=f'experiment_{project_name.replace("/","_")}_metadata', path=f"{self.output_dir}")
        writer.write(head=self.heads_project_metadata, rows=projects_metadata) 
        
        writer = WriterCSV(name=f'experiment_{project_name.replace("/","_")}_assigns', path=f"{self.output_dir}")
        writer.write(head=self.heads_assigns, rows=assigns) 

        shutil.rmtree(project_dir)    