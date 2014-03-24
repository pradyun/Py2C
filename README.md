
> This project is still in the planning/pre-alpha stages.
> It is **NOT producing any useful output**.

Py2C
====
Py2C for compiling Python code into (hopefully fairly) human-readable C++
code, (hopefully) somewhat like what humans might actually write.

This project is currently focused on statically typed programs and optimizing
them. This means the current scope of the project is limited. On some future
date, this project may also support the entire dynamism of Python, subject to
whether such a change is helpful and feasible for the project.

The idea is that even in highly dynamic languages (like Python) often
variables end up holding (references to) values have only one "type".
This is a major area for improving performance as statically typed languages
(like C++) often are better with, well, typed variables!

> The documentation is hosted in the Github wiki as of now, but it needs to be
> be written for most part.


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
for API changes across the languages, for third party packages (like Numpy),
just like it is used to optimize the C code internally. The details of the API
have to be decided..

If you are interested in participating in the development of this project,
read the 'Contributing' page in the wiki.

For more details, refer to the (currently mostly non-existent) GitHub wiki
pages.
