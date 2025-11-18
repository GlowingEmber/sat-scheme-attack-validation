from collections import defaultdict
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
    os.makedirs(my_env["DATA_DIRECTORY"], exist_ok=True)
    if GENERATE_CLEARS_DATA:
        if (
            os.path.isdir(my_env["DATA_DIRECTORY"])
            and len(os.listdir(my_env["DATA_DIRECTORY"])) > 0
        ):
            run_zsh("rm -rf $DATA_DIRECTORY/*")
            print(f"data directory cleared")

    ciphers = []
    t = 0
    codebreak_results = defaultdict(int)
    for _ in range(n):

        plaintext = PLAINTEXT
        if PLAINTEXT == "r":
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

        ### codebreak_success_n__txt
        if AUTOMATICALLY_TEST_CODEBREAK:
            cmd = f"python3 -m src.decrypt.decrypt {next_n}"
            decryption = int(run_zsh(cmd, capture=True).stdout[:-1])

            cmd = f"python3 -m src.codebreak.codebreak {next_n}"
            code = codebreak = int(run_zsh(cmd, capture=True).stdout[:-1])

            if codebreak >= 0:
                code = int(codebreak == decryption)
            codebreak_results[code] += 1

            codes = {
                1: ("success", "green"),
                0: ("failure", "red"),
                -1: ("error 1", "yellow"),
                -2: ("error 2", "yellow"),
                -3: ("error 3", "yellow"),
                -4: ("error 4", "yellow"),
                -100: ("unknown error", "yellow"),
            }
            result_str = codes.get(code, codes.get(-100))

            try:
                from termcolor import colored
                result_str = colored(result_str[0], result_str[1])
            except:
                result_str = result_str[0]

            w = max(codebreak_results, key=lambda c: len(codes[c]))

            print(f"{result_str} (y={decryption} \u2227 attack(pub,c)={codebreak})\n")
            print(f"{len(ciphers)} cipher{'' if len(ciphers) == 1 else 's'} total")

            for n in codebreak_results.keys():

                current_count = codebreak_results[n]
                total_count = len(ciphers)

                result_string = codes.get(n, codes.get(-100))

                try:
                    from termcolor import colored
                    result_string = colored(result_string[0], result_string[1])
                except:
                    result_string = result_string[0]
                
                result_str = result_string
                format_str = "{:>{w}}"
                percent_str = f"{round(100 * current_count / len(ciphers), 2)}"
                fraction_str = f"{current_count}/{len(ciphers)}"

                s = f"{result_str} {format_str.format(percent_str, w=str(w+3))}% ({fraction_str})"
                print(s)

            print("=" * 30)

    if n > 1:
        print(f"{n} ciphers ({", ".join(ciphers)}) created in {round(t,2)}s")


if __name__ == "__main__":

    parser = argparse.ArgumentParser(prog="Generate")
    parser.add_argument("n", type=int)
    args = parser.parse_args()

    generate(args.n)
