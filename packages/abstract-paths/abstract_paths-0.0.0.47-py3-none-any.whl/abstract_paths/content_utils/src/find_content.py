from .file_utils import findGlobFiles
from ...file_handlers.file_readers import read_any_file
from abstract_utilities import make_list
import os
from typing import *

def stringInContent(
            content,
            strings,
            total_strings=False
        ):
    found = [string for string in strings if string in content]
    if found:
        if total_strings:
            if len(strings) == len(found):
                return True
            return False
        return True
    return False
def get_contents(
    full_path=None,
    parse_lines=False,
    content=None
    ):
    if full_path:
        content = content or read_any_file(full_path)
    if content:
        if parse_lines:
            content = str(content).split('\n')
        return make_list(content)
    return []
def find_file(content,spec_line,strings,total_strings=False):
   lines = content.split('\n')
   if len(lines) >= spec_line:
       return stringInContent(
            lines[spec_line],
            strings,
            total_strings=total_strings
            )
   return False
def find_lines(content,strings,total_strings=False):
   lines = content.split('\n')
   line_nums = []
   for i,line in enumerate(lines):
       if stringInContent(
            line,
            strings,
            total_strings=total_strings
            ):
           line_nums.append({"line":i+1,"content":line})
   return line_nums
def findContent(directory: str,
                paths: Optional[Union[bool, str]] = True,
                exts: Optional[Union[bool, str, List[str]]] = True,
                recursive: bool = True,
                strings: list=[],
                total_strings=False,
                parse_lines=False,
                spec_line=False,
                get_lines=False
                ):
    found_paths = []
    globFiles = findGlobFiles(directory,paths,exts,recursive)
    file_paths = [file for file in globFiles if file and os.path.isfile(file)]
    for file_path in file_paths:
        if file_path:
            og_content = read_any_file(file_path)
            contents = get_contents(
                    file_path,
                    parse_lines=parse_lines,
                    content = og_content
                    )
            found = False
            for content in contents:
             
                if stringInContent(content, strings,total_strings):
                    found = True
                    if spec_line != False and isinstance(spec_line,int):
                        found = find_file(og_content,
                                          spec_line,
                                          strings,
                                          total_strings=total_strings)
                    
                    if found:
                        if get_lines:
                            lines = find_lines(og_content,strings=strings,total_strings=total_strings)
                            if lines:
                                file_path={"file_path":file_path,"lines":lines}
                        found_paths.append(file_path)
                        break
                
    return found_paths
def return_function(start_dir=None,preferred_dir=None,basenames=None,functionName=None):
    if basenames:
        basenames = make_list(basenames)
        abstract_file_finder = AbstractFileFinderImporter(start_dir=start_dir,preferred_dir=preferred_dir)
        paths = abstract_file_finder.find_paths(basenames)
        func = abstract_file_finder.import_function_from_path(paths[0], functionName)
        return func
def getLineNums(file_path):
    lines=[]
    if file_path and isinstance(file_path,dict):
        lines = file_path.get('lines')
        file_path = file_path.get('file_path')
    return file_path,lines
def get_line_content(obj):
    line,content=None,None
    if obj and isinstance(obj,dict):
        line=obj.get('line')
        content = obj.get('content')
    print(f"line: {line}\ncontent: {content}")
    return line,content
def get_edit(file_path):
    if file_path and os.path.isfile(file_path):
        os.system(f"code {file_path}")
        input()
def editLines(file_paths):
    for file_path in file_paths:
        file_path,lines = getLineNums(file_path)
        for obj in lines:
            line,content = get_line_content(obj)
        get_edit(file_path)
def findContentAndEdit(
    directory: str,
    paths: Optional[Union[bool, str]] = True,
    exts: Optional[Union[bool, str, List[str]]] = True,
    recursive: bool = True,
    strings: list=[],
    total_strings=True,
    parse_lines=False,
    spec_line=False,
    get_lines=True,
    edit_lines=True
    ):
    if isinstance(exts,list):
        exts ='|'.join(exts)
    
    file_paths = findContent(
        directory=directory,
        paths=paths,
        exts=exts,
        recursive=recursive,
        strings=strings,
        total_strings=total_strings,
        parse_lines=parse_lines,
        spec_line=spec_line,
        get_lines=get_lines
        )
    if edit_lines:
        editLines(file_paths)
    return file_paths
