from .file_utils import findGlobFiles
from ..imports import *
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
    return content or []
def find_file(content,spec_line,strings,total_strings=False):
   lines = content.split('\n')
   if len(lines) >= spec_line:
       return stringInContent(
            lines[spec_line],
            strings,
            total_strings=total_strings
            )
   return False   
def findContent(directory: str,
                paths: Optional[Union[bool, str]] = True,
                exts: Optional[Union[bool, str, List[str]]] = True,
                recursive: bool = True,
                strings: list=[]
                total_strings=False,
                parse_lines=False,
                spec_lines=False
                ):
    found_paths = []
    globFiles = findGlobFiles(directory,paths,exts,recursive)
    for file_path in globFiles:
        if file_path:
            og_content or read_any_file(full_path)
            contents = get_contents(
                    full_path,
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
                        found_paths.append(file_path)
                        break
                
    return found_paths
