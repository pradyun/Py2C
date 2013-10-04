Py2C
====

Py2C is a Python to C/C++ translator (converter). Py2C translates Python to pure
human-readable C/C++ like humans would write without any Python API calls.
The generated code can be run without Python installed and does not embed Python.

For example:

```python
print("Hello World to Py2C!")
```

would translate to something like

```c
#include "iostream"

using namespace std;

int main() {
    cout<<"Hello World to Py2C!\n";
    return 0;
}
```

**Isn't this the same as Cython?**  
No, Py2C aims to convert Python code to pure C/C++. Pure C/C++ is faster than
C/C++ riddled with Python API calls which just give 5x improvement.
Py2C aims to give almost the same performance as C/C+ code, *almost*.

----------
Although we do intend on supporting the standard library, we currently are focusing
on converting the sources. This means that one needs to manually change the generated
code, to support the changes. What one can do is write a "fixer" (not implemented yet)
for the same, so that once the new C AST is generated, the fixer can visit it's nodes,
and in turn change it to include the API changes etc.

----------

Note: Curently we are under-going a major code refactor, so we aren't producing 
any output. But as a part of the conversion, we do have the code becoming much
more readable and maintainable. Since this project is still young, we haven't
worked much on the wiki but it will be brought up to date once we start 
generating C/C++.

