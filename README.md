 -----

> WARNING: `git rebase -i` and `git push --force` may be run on this branch at any point of time because I'm mad and evil!

 -----

> The project is **not** functional yet. It's just in pre-alpha/planning stage...

 -----

# Py2C

[![Build Status][travis-badge]][travis-page] [![Coverage Status][coveralls-badge]][coveralls-page] [![Gitter][gitter-image]][gitter-page] ![Project Status][project-pre-alpha-badge]

A trans-compiler for compiling Python code into human-readable C++ code, somewhat like what humans might actually write. It would have to be really smart and that's the aim!

This project is currently focused on statically typed programs and optimizing them. This means the current scope of the project is limited. On some future date, this project may also support all of Python's dynamic nature, subject to whether such a change is helpful and feasible for the project.

The idea is that even in highly dynamic languages (like Python) variables often end up holding (references to) values have only one "type". This is a major area for improving performance as statically typed languages (like C++) often are better with, well, typed variables. So if these one-type variables can be in a faster language, why not have them there?

But for those gains, you'll have to leave the comforts of Python and write C++ code. And here's where Py2C is supposed to come in! You can just tweak the existing Python code a bit and pass it through Py2C and it automagically outputs C++ code that does that same thing as the Python code, just a whole lot faster!

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

If it is needed, a special header file is included in the generated file. For example, the above example would compile to something like:

```cpp
#include "py2c.h"

int main() {
    py2c::print(py2c::str("Hello World!"));
    return 0;
}
```

If all goes as planned, Py2C will also be extendable to accommodate for API changes across the languages, for third party packages (like NumPy, Qt etc).

  [pep-484]: https://www.python.org/dev/peps/pep-0484

  [travis-page]: https://travis-ci.org/pradyunsg/Py2C
  [travis-badge]: https://travis-ci.org/pradyunsg/Py2C.svg
  [coveralls-page]: https://coveralls.io/r/pradyunsg/Py2C?branch=develop
  [coveralls-badge]: https://img.shields.io/coveralls/pradyunsg/Py2C.svg?style=flat
  [gitter-image]: https://img.shields.io/badge/Gitter-Chat_Room-1DCD73.svg?style=flat
  [gitter-page]: https://gitter.im/pradyunsg/Py2C

  [project-on-hold-badge]: https://img.shields.io/badge/project-on--hold-lightgrey.svg?style=flat
  [project-pre-alpha-badge]: https://img.shields.io/badge/project-pre--alpha-ff5d37.svg?style=flat
  [project-alpha-badge]: https://img.shields.io/badge/project-alpha-orange.svg?style=flat
  [project-beta-badge]: https://img.shields.io/badge/project-beta-yellow.svg?style=flat
  [project-rc-badge]: https://img.shields.io/badge/project-release--candidate-green.svg?style=flat
  [project-stable-badge]: https://img.shields.io/badge/project-stable-brightgreen.svg?style=flat
  [project-discontinued-badge]: https://img.shields.io/badge/project-discontinued-DD4444.svg?style=flat
