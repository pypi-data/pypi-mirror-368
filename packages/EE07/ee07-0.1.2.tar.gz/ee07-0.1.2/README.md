# EE07: Double-E Language for Chemical System Programming

**EE07** (Double-E Language) is a programming language that fully supports C++ syntax and features, while introducing **chemical system programming** using inbuilt intelligence.

Write, test, and simulate chemical systems directly in C++-style code with chemical functions like `react()`, `structure()`, `bind()`, `release()`, and more.

## Features

- Full support for all C++ syntax (OOP, file I/O, templates, etc.)
- Chemical intelligence powered by PubChem API
- New datatypes: `iupac`, `comm`, `fm`
- Inbuilt functions: `react()`, `bind()`, `structure()`, `release()`, `delay()`, `trig()`, `save()` and more
- Use EE07 inside notebooks like Google Colab

## Installation
pip install EE07

## Usage (Example)
from EE07 import run_code

run_code("""
#include <iostream>
using namespace std;

int main() {
    cout << "EE07 is live!" << endl;

    structure("glucose");

    react("glucose", "oxygen");

    trig("temperature > 310");

    return 0;

}
""")
