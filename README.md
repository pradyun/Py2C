Py2C
====
Py2C is a translator for translating implicitly statically typed Python code 
into human-readable C code, a bit like what humans would write. The code has no
Python API calls. The generated code can be run without Python headers as it 
does not embed Python.

> Note: Curently we are under-going a major code refactor, so we aren't
> producing any output. But as a part of the conversion, we do have the code
> becoming much more readable and maintainable. Since this project is still
> young, we haven't worked much on the wiki but it will be brought up to date
> once we start generating C/C++ code (some distance from here).

Here's Py2C in action on Hello World:

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

Or if you think it is OK to have a special header file in this file:

```c
#include "iostream"
#include "pythonic.h"

int main() {
    Python::print("Hello World!");
    return 0;
}
```

Py2C is also extensible though a fixer API, which can be used to accommodate for
API changes across the languages, for third party packages.

For more details, refer to the wiki pages on GitHub.
