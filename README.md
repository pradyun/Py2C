Py2C
====

Py2C is a Python to C/C++ translator (converter). Py2C translates Python to pure
human-readable C/C++ like humans would write without any Python API calls.
The generated code can be run without Python installed and does not embed Python.

For example:

```python
print("Hello World!")
```

would translate to something like

```c
#include "iostream"

using namespace std;

int main() {
    cout<<"Hello World!\n";
    return 0;
}
```
Or if you think it is ok to have a special header file in this file,

```c
#include "iostream"
#include "pythonic.h"

int main() {
    Python::print("Hello World!");
    return 0;
}


**Isn't this the same as Cython?**  
No, Cython converts Python code into C code with Python API calls, that does the
same thing as the Python code. 
Py2C, on the other hand, aims to convert Python code to readable C/C++. 
Pure C/C++ is (usually) faster than C/C++ riddled with Python API calls which
just give 5x improvement. Honestly, performance isn't something we are really
bothered about, but we should be able to give a substantial boost.

Although we shall try to convert the sources to as close to pure, readable C/C++
code as directly possible, i.e. without any extra header files, unless the
option is passed to allow.


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
generating C/C++ code (some distance from here).
