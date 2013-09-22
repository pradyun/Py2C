Py2C
====

Py2C is a Python to C/C++ translator (converter). Py2C translates Python to pure human-readable C/C++ like humans would write without any Python API calls. The generated code can be run without Python installed and does not embed Python. For example:

```python
print("Hello World to Py2C!")
```
would translate to

```c
#include "iostream"
using namespace std; //If you want you can make Py2C not add this and use std::cout instead of cout
int main()
{
    cout<<"Hello World to Py2C!\n";
    return 0;
}
```

NOTE: Curently we are under-going a code refactor, so we aren't producing any output..