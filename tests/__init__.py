# Used in testing
if __name__ == '__main__':
    import os
    import sys
    sys.path.insert(1, os.path.dirname(os.path.realpath(__file__)))
    import tests.run_tests as run_tests
    run_tests.main()

