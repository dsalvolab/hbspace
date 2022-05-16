# 
# This file is part of the Health Behavior in Space software (https://github.com/dsalvolab/hbspace).
# Copyright (c) 2022 Umberto Villa.
# 
# This program is free software: you can redistribute it and/or modify  
# it under the terms of the GNU General Public License as published by  
# the Free Software Foundation, version 3.
#
# This program is distributed in the hope that it will be useful, but 
# WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU 
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License 
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#

class ParameterList(object):
    """
    A small abstract class for storing parameters and their description.
    This class will raise an exception if the key one tries to access is not present
    """
    def __init__(self):
        """
        data is a dictionary where each value is the pair (value, description)
        """
        self._data = {}
        self._data_doc = {}
        
    def add_param(self, key, default, docstring):
        assert key not in self._data
        
        self._data[key] = default
        self._data_doc[key] = docstring
        
    def __getitem__(self,key):
        if key in self._data:
            return self._data[key]
        else:
            raise ValueError(key)
        
    def __setitem__(self,key, value):
        if key in self._data:
            self._data[key] = value
        else:
            raise ValueError(key)
        
    def keys(self):
        return self._data.keys()
        
    def showMe(self, indent=""):
        for k in sorted(self._data.keys()):
            print( indent, "---")
            if type(self._data[k]) == ParameterList:
                print( indent, k, "(ParameterList):", self._data_doc[k])
                self._data[k].showMe(indent+"    ")
            else:
                print( indent, k, "({0}):".format(self._data[k]),  self._data_doc[k] )
        
        print( indent, "---")