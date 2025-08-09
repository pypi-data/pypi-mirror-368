import subprocess
import tempfile
import os

def run_cpp_code(cpp_code: str):
    with tempfile.NamedTemporaryFile(suffix=".cpp", delete=False) as tmp:
        tmp.write(cpp_code.encode('utf-8'))
        cpp_file_path = tmp.name

    exe_file_path = cpp_file_path.replace(".cpp", "")
    compile_result = subprocess.run(["g++", cpp_file_path, "-o", exe_file_path],
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if compile_result.returncode != 0:
        return compile_result.stderr.decode()

    run_result = subprocess.run([exe_file_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    os.remove(cpp_file_path)
    os.remove(exe_file_path)

    return run_result.stdout.decode()
