Py2C
====
Py2C is a compiler for compiling implicitly statically typed Python code
into human-readable C++ code, a bit like what humans would write (Or can at
least read). The code has no Python API calls. The generated code can be
compiled without Python headers as it does not embed Python.

> Note: Currently it isn't producing any output. The tests for the code "has"
  implementation to be written before implementing anything.
  (As I'm experimenting with TDD) So, it's taking some time to implement the stuff

> Since this project is still young, I haven't worked much on the wiki but it
  will be brought up to date once the generators start generating C++ code
  (some time before that happens).

Here's Py2C in action on Hello World:

```python
print("Hello World!")
```

would compile to something like

```c
#include <iostream.h>

using namespace std;

int main() {
    cout<<"Hello World!\n";
    return 0;
}
```

Or if you think it is OK to have a special header file in this file:

```c
#include <iostream.h>
#include "pythonic.h"

int main() {
    Python::print("Hello World!");
    return 0;
}
```

Py2C is also extensible though a fixer API, which can be used to accommodate for
API changes across the languages, for third party packages.

For more details, refer to the wiki pages on GitHub<sub>Not ready yet</sub>.
