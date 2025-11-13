from parameters import *
import subprocess
import os
import argparse
import random

my_env = os.environ.copy()


def run_zsh(cmd, capture=False):
    return subprocess.run(
        cmd,
        env=my_env,
        shell=True,
        text=True,
        executable="/bin/zsh",
        capture_output=capture,
    )


def generate(n):

    if GENERATE_CLEARS_DATA:
        if os.path.isdir(my_env["DATA_DIRECTORY"]):
            run_zsh("rm -rf $DATA_DIRECTORY/*")
            print(f"data directory cleared")

    ciphers = []
    t = 0
    for _ in range(n):

        plaintext = PLAINTEXT
        if PLAINTEXT == 2:
            plaintext = random.getrandbits(1)

        #####

        next_n = 0
        next_dir = f"{my_env["DATA_DIRECTORY"]}/cipher_{next_n}_dir"
        while os.path.isdir(next_dir):
            next_n += 1
            next_dir = f"{my_env["DATA_DIRECTORY"]}/cipher_{next_n}_dir"
        os.mkdir(next_dir)

        #####

        encrypt_stdout_n__txt = "/dev/null"
        if INCLUDE_ENCRYPT_STDOUT_N__TXT:
            encrypt_stdout_n__txt = f"{next_dir}/encrypt_stdout_{next_n}.txt"

        #####

        cmd = f'time python3 -m src.encrypt.encrypt -n "{next_n}" -y "{plaintext}" >{encrypt_stdout_n__txt}'
        res = run_zsh(cmd, capture=True)
        print(f"cipher {next_n} created in {res.stderr[:-1]}")

        ciphers.append(str(next_n))
        t += float(res.stderr[:-2])

        ### plaintext_n__txt
        path = f"{next_dir}/plaintext_{next_n}.txt"
        with open(path, "w") as file:
            file.write(str(plaintext))

        ### ciphertext_n__txt
        if INCLUDE_CIPHERTEXT_N__TXT:
            path = f"{next_dir}/ciphertext_{next_n}.txt"
            with open(path, "w") as file:
                cmd = f"h5dump --width=1 '{next_dir}/ciphertext_{next_n}.hdf5'"
                cipher = run_zsh(cmd, capture=True)
                file.write(cipher.stdout)

    if n > 1:
        print(f"{n} ciphers ({", ".join(ciphers)}) created in {t}s")


if __name__ == "__main__":

    parser = argparse.ArgumentParser(prog="Generate")
    parser.add_argument("n", type=int)
    args = parser.parse_args()

    generate(args.n)
