from parameters import *
import subprocess
import os
import argparse
import random

my_env = os.environ.copy()

def generate(n):

    if GENERATE_CLEARS_DATA:
        if os.path.isdir(my_env["DATA_DIRECTORY"]):
            cmd = "rm -rf $DATA_DIRECTORY/*"
            subprocess.run(cmd, env=my_env, shell=True, text=True, executable="/bin/zsh")
            # subprocess.run(["rm", "-rf", "$DATA_DIRECTORY/*"])
            print(f"data directory cleared")

    ciphers_created = []
    total_time = 0
    for _ in range(n):
        plaintext = PLAINTEXT
        if plaintext == 2:
            plaintext = random.getrandbits(1)
        
        next_n = 0
        next_dir = f"{my_env["DATA_DIRECTORY"]}/cipher_{next_n}_dir"
        while os.path.isdir(next_dir):
            next_n += 1
            next_dir = f"{my_env["DATA_DIRECTORY"]}/cipher_{next_n}_dir"
        cmd = f"mkdir {next_dir}"
        subprocess.run(cmd, env=my_env, shell=True, text=True, executable="/bin/zsh")

        encrypt_stdout_n__txt = "/dev/null"
        if INCLUDE_ENCRYPT_STDOUT_N__TXT:
            encrypt_stdout_n__txt = f"{next_dir}/encrypt_stdout_{next_n}.txt"

        cmd = f"time python3 -m src.encrypt.encrypt -y \"{plaintext}\" -c \"{next_n}\" >{encrypt_stdout_n__txt}"
        res = subprocess.run(cmd, env=my_env, shell=True, text=True, executable="/bin/zsh", capture_output=True)

        cmd = f"echo 'cipher {next_n} created in {res.stderr[:-1]}'"
        subprocess.run(cmd, env=my_env, shell=True, text=True, executable="/bin/zsh")
        
        ciphers_created.append(str(next_n))
        total_time += float(res.stderr[:-2])

        if INCLUDE_PRIV_N__TXT:
            path = f"{next_dir}/priv_{next_n}.txt"
            with open(path, 'w') as file:
                file.write(plaintext)

        if INCLUDE_CIPHER_N__TXT:
            path = f"{next_dir}/cipher_{next_n}.txt"
            with open(path, 'w') as file:
                cmd = f"h5dump --width=1 '{next_dir}/cipher_{next_n}.hdf5'"
                cipher = subprocess.run(cmd, env=my_env, shell=True, text=True, executable="/bin/zsh", capture_output=True)
                file.write(cipher.stdout)

    if n > 1:
        cmd = f"echo '{n} ciphers ({", ".join(ciphers_created)}) created in {total_time}s'"
        subprocess.run(cmd, env=my_env, shell=True, text=True, executable="/bin/zsh")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="Generate")

    parser.add_argument("n", type=int)

    args = parser.parse_args()

    generate(args.n)

