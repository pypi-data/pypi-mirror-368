#! /usr/bin/env bash

function test_bluer_ai_string_after() {
    bluer_ai_assert \
        $(bluer_ai_string_after \
            "this-is-a-test" \
            "") \
        ""
    [[ $? -ne 0 ]] && return 1

    bluer_ai_assert \
        $(bluer_ai_string_after \
            "this-is-a-test" \
            "was") \
        ""
    [[ $? -ne 0 ]] && return 1

    bluer_ai_assert \
        $(bluer_ai_string_after \
            "this-is-a-test" \
            "is") \
        "-is-a-test"
    [[ $? -ne 0 ]] && return 1

    bluer_ai_assert \
        $(bluer_ai_string_after \
            "this-is-a-test-that-is-very-important" \
            "is") \
        "-is-a-test-that-is-very-important"
    [[ $? -ne 0 ]] && return 1

    bluer_ai_assert \
        $(bluer_ai_string_after \
            "this-is-a-test-that-is-very-important-and-now-is-running" \
            "is") \
        "-is-a-test-that-is-very-important-and-now-is-running"
}

function test_bluer_ai_string_before() {
    bluer_ai_assert \
        $(bluer_ai_string_before \
            "this-is-a-test" \
            "") \
        ""
    [[ $? -ne 0 ]] && return 1

    bluer_ai_assert \
        $(bluer_ai_string_before \
            "this-is-a-test" \
            "was") \
        ""
    [[ $? -ne 0 ]] && return 1

    bluer_ai_assert \
        $(bluer_ai_string_before \
            "this-is-a-test" \
            "is") \
        "th"
    [[ $? -ne 0 ]] && return 1

    bluer_ai_assert \
        $(bluer_ai_string_before \
            "this-is-a-test-that-is-very-important" \
            "is") \
        "th"
    [[ $? -ne 0 ]] && return 1

    bluer_ai_assert \
        $(bluer_ai_string_before \
            "this-is-a-test-that-is-very-important-and-now-is-running" \
            "is") \
        "th"
}

function test_bluer_ai_string_random() {
    bluer_ai_assert \
        $(bluer_ai_string_random) \
        - non-empty
}

function test_bluer_ai_string_timestamp() {
    bluer_ai_assert \
        $(bluer_ai_string_timestamp) \
        - non-empty
}

function test_bluer_ai_string_timestamp_short() {
    bluer_ai_assert \
        $(bluer_ai_string_timestamp_short) \
        - non-empty
}

function test_bluer_ai_string_today() {
    bluer_ai_assert \
        $(bluer_ai_string_today) \
        - non-empty
}
