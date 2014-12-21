> This project is still in the planning/pre-alpha stages. It is **not working**. 

## Py2C

[![Build Status](https://travis-ci.org/pradyun/Py2C.svg?branch=master)](https://travis-ci.org/pradyun/Py2C) [![Coverage Status](https://img.shields.io/coveralls/pradyun/Py2C.svg)](https://coveralls.io/r/pradyun/Py2C?branch=master)

A trans-compiler for compiling Python code into hopefully human-readable C++ code, (hopefully) somewhat like what humans might actually write.

This project is currently focused on statically typed programs and optimizing them. This means the current scope of the project is limited. On some future date, this project may also support the entire dynamism of Python, subject to whether such a change is helpful and feasible for the project.

The idea is that even in highly dynamic languages (like Python) variables often end up holding (references to) values have only one "type". This is a major area for improving performance as statically typed languages (like C++) often are better with, well, typed variables. So if these one-type variables can be in a faster language, why not have them there?

Well because then you have to leave the comforts of Python and write C++ code. And here's where Py2C's supposed to come in! You can just tweak the existing Python code a bit and pass it through Py2C and it automagically outputs C++ code that does that same thing as the Python code, just a whole lot faster!

Here's Py2C in action (rather Py2C's planned action) on "Hello World!":

```python
print("Hello World!")
```

The above should compile to something like:

```cpp
#include <iostream.h>

int main() {
   std::cout << "Hello World!\n";
   return 0;
}
```

If you think it is OK to have a special header file in the generated file
it would compile to

```cpp
#include "py2c.h"

int main() {
    py2c::print(py2c::str("Hello World!"));
    return 0;
}
```

Py2C is also extensible though a modifier API, which can be used to accommodate
for API changes across the languages, for third party packages (like NumPy).
