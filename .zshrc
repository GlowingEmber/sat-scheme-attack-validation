clearData() {
    if [ ! -z "$( ls -A $DATA_DIRECTORY )" ]; then
        rm -rf $DATA_DIRECTORY/*
    fi
}

alias generate="python3 generate.py"
alias encrypt="./generate.zsh"
alias cleardata=clearData
alias codebreak="python3 -m src.codebreak.codebreak"
alias decrypt="python3 -m src.decrypt.decrypt"

export DATA_DIRECTORY="./data"
export TIMEFMT='%U'