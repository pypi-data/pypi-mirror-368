
"""
author = its_me_abi
date = 1/8/2025

"""
class ArgManager:
    """
    commandline argument manager , get ,set values and produce command list"
    alternative to inbuilt argument parser
    """
    def __init__(self, exename = "" ):
        self.exe_name = exename  # prefix of command usualy "java" like executable name
        self.args = {}

    def _last_occurrence_item(self,lst, value):
        try:
            return len(lst) - 1 - lst[::-1].index(value)
        except ValueError:
            return None

    def _delete_last(self,lst , item):
        index = self._last_occurrence_item(lst , item)
        if index is not None:
           return lst.pop(index)

    def set_arg(self, key, val,delete = False):
        if key in self.args.keys():
            if isinstance(self.args[key],list):
                if delete:
                    self._delete_last( self.args[key] , val )
                    if self.args[key] is list:
                        pass
                    return
                self.args[key].append(val)
            else:
                if delete :
                    if self.args[key] == val:
                       del self.args[key]
                    return
                oldval = self.args[key]
                self.args[key] = [oldval, val]
        else:
            if delete:
                return
            self.args[key]=val

    def get_arg(self, key):
        if key in self.args.keys():
            val = self.args[key]
            if isinstance(val,list) and len(val)==1:
                return val[0]
            return val

    def toString(self):
        return " ".join(self.tolist())

    def tolist(self):
        cli = []
        for key, value in self.args.items():
            if isinstance(value, bool):
                if value:
                    cli.append(f"{key}")
            elif isinstance(value, list):
                for v in value:
                    cli.extend([f"{key}", str(v)])
            elif value is not None:
                cli.extend([f"{key}", str(value)])
        if self.exe_name:
            cli = [self.exe_name] + cli
        return cli


if __name__ == "__main__":
    a = ArgManager("java")

    #a.set_arg("--helo_duplicate", 2)
    a.set_arg("--helo_duplicate", 1)
    a.set_arg("--helo_duplicate", 11,delete=True)
    print ( a.get_arg("--helo_duplicate") )
    a.set_arg("--helo_boolean_value", True) # arguemnt without values
    a.set_arg("script_path_like", True)
    print(" converted to cli list " ,a.tolist())
    print(" converted to cli string ", a.toString())