#!/usr/bin/env python3

import argparse
import os
import pathlib
import re
import subprocess
import sys

script_dir = pathlib.Path(os.path.dirname(os.path.realpath(__file__)))
m2c_path = script_dir / "tools/mips_to_c/mips_to_c.py"

project_dir = pathlib.Path("/home/ethteck/repos/papermario")
src_dir = project_dir / "src"
asm_dir = project_dir / "ver/us/asm/nonmatchings"

asm_pattern = re.compile(r"^INCLUDE_ASM\(.*\);.*\n", flags=re.MULTILINE)
build_command = "ninja"

def check_build():
    try:
        result = subprocess.run(build_command, stdout=subprocess.PIPE, cwd=project_dir)
        if result.returncode == 0:
            return 1 # Matching
    except:
        pass

    if "computed checksum did NOT match" in result.stdout.decode():
        return 2 # Not matching
    else:
        return 3 # Not building


def run_mips_to_c(file_path):
    try:
        result = subprocess.run([m2c_path, file_path], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        if result.returncode != 0:
            return None
        ret = result.stdout.decode()
        if "subroutine" in ret:
            print(str(file_path) + " " + str(len(ret)))
        return ret
    except:
        return None


def get_asm_file_path(dir_name, file_name):
    for root, dirs, files in os.walk(asm_dir):
        if root.endswith(dir_name) and file_name in files:
            return pathlib.Path(root) / file_name
    return None
    

def handle_func(func_match, c_path, c_text):
    # PM-specific behavior
    func_split =  func_match.group(0).split(",")

    asm_dir_name = func_split[1].replace("\"", "").strip()

    func_name = func_split[2]
    func_name = func_name.split(",")[0]
    func_name = func_name.split(")")[0]
    func_name = func_name.strip()

    asm_file_path = get_asm_file_path(asm_dir_name, func_name + ".s")
    if not asm_file_path:
        print("Error! could not find {func_name} referenced in {c_path.name}")
        return c_text

    m2c_out = run_mips_to_c(asm_file_path)
    if not m2c_out:
        print(f"mips_to_c failed on {func_name}")
        return c_text
    
    new_c_text = c_text[:func_match.span(0)[0]] + m2c_out + c_text[func_match.span(0)[1]:]
    
    with open(c_path, "w", newline="\n") as f:
        f.write(new_c_text)
    
    build_result = check_build()
    if build_result == 1:
        print(f"Instantly matched {func_name} !")
        return new_c_text
    else:
        if build_result == 2:
            print(f"Build finished but did not match on {func_name} - running permuter (TODO)")
            # TODO Run permuter for a bit and see if we can get the score to 0
            with open(c_path, "w", newline="\n") as f:
                f.write(c_text)
        else:
            with open(c_path, "w", newline="\n") as f:
                f.write(c_text)
        return c_text


def handle_file(file_path):
    with open(file_path) as f:
        c_text = f.read()
    
    asm_funcs = []
    for func in re.finditer(asm_pattern, c_text):
        asm_funcs.append(func)
    
    if len(asm_funcs) > 0:
        asm_funcs.reverse()
        for func in asm_funcs:
            c_text = handle_func(func, file_path, c_text)


def main(args):
    for root, dirs, files in os.walk(src_dir):
        for file in files:
            if check_build() != 1:
                print("The build is not stable; Aborting!")
                sys.exit(1)
            # TODO remove jp thing later
            if file.endswith(".c") and "jp" not in root:
                handle_file(pathlib.Path(root) / file)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bootstraps decompilation by running mips_to_c and the permuter")
    args = parser.parse_args()

    main(args)
