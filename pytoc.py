from converter import *
import test # Remove after development
import unittest
suite = unittest.TestLoader().loadTestsFromTestCase(test.PyToCTest)
unittest.TextTestRunner(verbosity=2).run(suite)
s = '''while True:
    pyaar(u)
    while False:print(he)
    ouoyoyoy
    esahah();'''
a = Converter()
while s not in ("quit","exit"):
    try:
        code = parse(s)
    except SyntaxError:
        traceback.print_exc()
    else:
        origcode = copy.deepcopy(code)
        print(a.visit(code))
        #print(dump(origcode))
    try:
        s = ""
        line = True
        print("code:")
        while line:
            line = input()
            s+=line
    except (EOFError,KeyboardInterrupt):
        print("Exiting...")
        break
