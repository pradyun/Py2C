__author__ = "Ramchandra Apte <maniandram01@gmail.com>"
__license__ = '''
Copyright (C) 2012 Ramchandra Apte <maniandram01@gmail.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License at LICENSE.txt for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''
from translator import *
import test # Remove after development
import unittest
import copy
import traceback
#add after development if __name__ == "__main__":
suite = unittest.TestLoader().loadTestsFromTestCase(test.TranslatorTest)
unittest.TextTestRunner(verbosity=2).run(suite)
a = Translator()
a.visit(parse("def g():pass"))
s = ""
while s not in ("quit","exit"):
    try:
        s = ""
        line = True
        print("code:")
        while line:
            line = input()
            s+=line+"\n"
    except (EOFError,KeyboardInterrupt):
        print("Exiting...")
        break
    try:
        code = parse(s)
    except SyntaxError:
        traceback.print_exc()
    else:
        origcode = copy.deepcopy(code)
        try:s = a.visit(code)
        except:
            traceback.print_exc()
        else:print(s)
        print(dump(origcode))
