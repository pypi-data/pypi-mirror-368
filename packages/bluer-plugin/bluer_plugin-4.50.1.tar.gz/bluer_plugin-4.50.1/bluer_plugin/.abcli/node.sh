#! /usr/bin/env bash

function bluer_plugin_node() {
    local task=$1

    local function_name=bluer_plugin_node_$task
    if [[ $(type -t $function_name) == "function" ]]; then
        $function_name "${@:2}"
        return
    fi
    bluer_ai_log "bluer-plugin: node: 🌀"
}

bluer_ai_source_caller_suffix_path /node
