#! /usr/bin/env bash

function bluer_ai_log() {
    local task=$1

    if [ "$task" == "verbose" ]; then
        local what=${2:-on}

        if [ "$what" == "on" ]; then
            touch $abcli_path_git/verbose
            bluer_ai_set_log_verbosity
        elif [ "$what" == "off" ]; then
            rm $abcli_path_git/verbose
            bluer_ai_set_log_verbosity
        else
            bluer_ai_log_error "@log: verbose: $what: command not found."
            return 1
        fi

        return
    fi

    bluer_ai_log_local "$@"

    bluer_ai_log_remote "$@"
}

function bluer_ai_log_error() {
    local message="$@"

    printf "❗️ ${RED}$message$NC\n"

    echo "error: $message" >>$bluer_ai_log_filename
}

function bluer_ai_log_remote() {
    echo "$@" >>$bluer_ai_log_filename
}

function bluer_ai_log_warning() {
    local message="$@"

    printf "$YELLOW$message$NC\n"

    echo "warning: $message" >>$bluer_ai_log_filename
}

function bluer_ai_set_log_verbosity() {
    if [[ -f $abcli_path_git/verbose ]]; then
        set -x
    else
        set +x
    fi
}

bluer_ai_set_log_verbosity

if [ -z "$bluer_ai_log_filename" ]; then
    export bluer_ai_log_filename=$abcli_path_git/bluer_ai.log
fi
