Py2C
====
Py2C is a compiler for compiling implicitly statically typed Python code
into human-readable C++ code, something like what humans might actually write.
The generated code can be compiled without Python headers as it does not embed
Python.  But you need Python to compile it. :)

NEW! Mailing-List: https://groups.google.com/forum/#!forum/py2c-dev

> Since this project is still in the planning stage as of now.
  (i.e. **Not producing output**)
  The wiki pages will be brought up to date once the code generator start
  generating C++ code...

  For an idea of how far the project has reached, check the [Milestones][1]
  on Github issues.

Here's Py2C in action on Hello World:

```python
print("Hello World!")
```

would compile to something like (Or so is planned :)

```c
#include <iostream.h>

using namespace std;

int main() {
    cout<<"Hello World!\n";
    return 0;
}
```

Or if you think it is OK to have a special header file in the generated file
it would compile to (Or so is planned :)

```c
#include <iostream.h>
#include "py2c.h"

int main() {
    Py::print(Py::str("Hello World!"));
    return 0;
}
```

Py2C is also extensible though a fixer API, which can be used to accommodate
for API changes across the languages, for third party packages (like numpy).

For more details, refer to the wiki pages on GitHub <sub>Not ready yet</sub>.

  [1]: https://github.com/pradyun/Py2C/issues/milestones
