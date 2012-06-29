from translator import *
import test # Remove after development
import unittest
if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(test.TranslatorTest)
    unittest.TextTestRunner(verbosity=2).run(suite)
    a = Translator()
    s = None
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
            print(a.visit(code))
            print(dump(origcode))
