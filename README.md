Py2C
====
Py2C is a translator for translating implicitly statically typed Python code 
into human-readable C++ code, a bit like what humans would write. The code has no
Python API calls. The generated code can be run without Python headers as it 
does not embed Python.

> Note: Curently it isn't producing any output. The starting design itself is 
  extensible with a lot of scope for improvement if needed.<br>

> Since this project is still young, I haven't worked much on the wiki but it
  will be brought up to date once the generaters start generating C++ code
  (some time before that happens).

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

For more details, refer to the wiki pages on GitHub<sub>Not ready yet</sub>.
