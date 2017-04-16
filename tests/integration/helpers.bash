#!/bin/bash

function assert_no_dashboards() {
    run grafcli ls /remote/localhost
    [ "$status" -eq 0 ]
    [ "$output" = "" ]
}

function assert_only_dashboard() {
    run grafcli ls /remote/localhost
    [ "$status" -eq 0 ]
    [ "$output" = "$1" ]
}

function assert_dashboards() {
    run grafcli ls /remote/localhost
    for dashboard in "$@"; do
        in_array "$dashboard" "${lines[@]}"
    done
}


function in_array() {
    local element
    for element in "${@:2}"; do
        [[ "$element" == "$1" ]] && return 0;
    done

    return 1
}
