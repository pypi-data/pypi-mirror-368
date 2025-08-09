import os
import subprocess
import tempfile
from ee07.chem_api import handle_chemical_function
from ee07.utils import extract_chem_functions, clean_cpp_code

def run_code(code: str):
    """Main runner to execute EE07 code, supporting both C++ and EEL functions"""
    # STEP 1: Extract and process EE07-specific functions (like react(), bind(), etc.)
    ee07_functions = extract_chem_functions(code)
    chemical_outputs = []

    for func in ee07_functions:
        result = handle_chemical_function(func)
        if result:
            chemical_outputs.append(result)
    
    # STEP 2: Clean the code to convert to pure C++ before compiling
    cleaned_cpp_code = clean_cpp_code(code)

    # STEP 3: Create a temporary C++ file and compile it
    with tempfile.NamedTemporaryFile(suffix=".cpp", delete=False) as tmp:
        tmp.write(cleaned_cpp_code.encode('utf-8'))
        cpp_file_path = tmp.name

    exe_file_path = cpp_file_path.replace(".cpp", "")
    compile_result = subprocess.run(["g++", cpp_file_path, "-o", exe_file_path],
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Compilation error
    if compile_result.returncode != 0:
        print("C++ Compilation Error:\n")
        print(compile_result.stderr.decode())
        return

    # STEP 4: Run compiled binary
    run_result = subprocess.run([exe_file_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    print("EE07 (C++ compatible) Program Output:\n")
    print(run_result.stdout.decode())

    if chemical_outputs:
        print("\n EE07 Chemical Functions Output:\n")
        for o in chemical_outputs:
            print(o)

    # Clean up
    os.remove(cpp_file_path)
    os.remove(exe_file_path)
