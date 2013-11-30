# Imported, has to be package import
if __name__ != '__main__':
    from . import runner
    tests = runner.load()
else:
    import os
    import sys
    sys.path.append(os.path.dirname(os.path.realpath(__file__)))

    import runner
    runner.main(buffer=True)
