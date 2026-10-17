# Bash Readline integration for the interactive help browser.
# Source this file from an interactive Bash session; Bash 4.4+ is required.

if [[ -z ${BASH_VERSION:-} ]] || (( BASH_VERSINFO[0] < 4 || (BASH_VERSINFO[0] == 4 && BASH_VERSINFO[1] < 4) )); then
    printf '%s\n' 'interactive-help requires Bash 4.4 or newer.' >&2
    return 1
fi

_CLI_HELP_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"

# Update only Readline's pending buffer after a complete helper response.
# Cancellation and helper failures produce no response and preserve both values.
_cli_help_widget() {
    local -a response=()
    local python_command=${CLI_HELP_PYTHON:-python3}
    if ! command -v -- "$python_command" >/dev/null 2>&1; then
        printf '\ninteractive-help: Python 3 is unavailable: %s\n' "$python_command" >&2
        return 0
    fi
    mapfile -d '' -t response < <(
        CLI_HELP_LINE="$READLINE_LINE" CLI_HELP_POINT="$READLINE_POINT" \
            PYTHONCOERCECLOCALE=0 PYTHONUTF8=0 \
            "$python_command" "$_CLI_HELP_ROOT/cli_help/main.py" --bash
    )
    if (( ${#response[@]} == 2 )) && [[ ${response[0]} =~ ^[0-9]+$ ]]; then
        READLINE_LINE=${response[1]}
        READLINE_POINT=${response[0]}
    fi
    return 0
}

# Bind the configured Readline sequence. Rebinding removes the former plugin
# binding; existing bindings on the selected sequence are replaced explicitly.
cli_help_bind() {
    local key=${CLI_HELP_KEY:-'\eh'}
    local keymap=${CLI_HELP_KEYMAP:-emacs-standard}
    if [[ $key == *[!a-zA-Z0-9\\\[\]\~\^\?\_\;\-]* || -z $key ]]; then
        printf '%s\n' 'interactive-help: invalid Readline key sequence.' >&2
        return 1
    fi
    case "$keymap" in
        emacs-standard|emacs-meta|vi-insertion|vi-command) ;;
        *) printf '%s\n' 'interactive-help: unsupported Readline keymap.' >&2; return 1 ;;
    esac
    if ! bind -m "$keymap" -x "\"$key\":_cli_help_widget"; then
        return 1
    fi
    if [[ -n ${_CLI_HELP_BOUND_KEY:-} ]] && \
       [[ $_CLI_HELP_BOUND_KEY != "$key" || $_CLI_HELP_BOUND_MAP != "$keymap" ]]; then
        bind -m "$_CLI_HELP_BOUND_MAP" -r "$_CLI_HELP_BOUND_KEY"
    fi
    _CLI_HELP_BOUND_KEY=$key
    _CLI_HELP_BOUND_MAP=$keymap
}

# Remove the plugin binding from this session. Other shell settings are retained.
cli_help_unbind() {
    if [[ -n ${_CLI_HELP_BOUND_KEY:-} ]]; then
        bind -m "$_CLI_HELP_BOUND_MAP" -r "$_CLI_HELP_BOUND_KEY"
        unset _CLI_HELP_BOUND_KEY _CLI_HELP_BOUND_MAP
    fi
}

if [[ $- == *i* ]]; then
    cli_help_bind
fi
