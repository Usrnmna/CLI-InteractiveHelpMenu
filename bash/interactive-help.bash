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
    local before_size after_size
    before_size=$(stty size </dev/tty 2>/dev/null) || before_size=
    bind -m "$_CLI_HELP_BOUND_MAP" '"\e[989~":""'
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
    after_size=$(stty size </dev/tty 2>/dev/null) || after_size=
    if [[ -n $before_size && -n $after_size && $before_size != "$after_size" ]]; then
        # Readline must perform this after bind -x returns, when it owns the
        # display again. clear-screen redraws input without clearing scrollback.
        bind -m "$_CLI_HELP_BOUND_MAP" '"\e[989~":clear-screen'
    fi
    return 0
}

# Bind the configured sequence to a widget/redraw macro. The two internal keys
# let Readline recover its geometry after a resize, outside the shell callback.
# Reserved-key conflicts are rejected before any existing binding is modified.
cli_help_bind() {
    local key=${CLI_HELP_KEY:-'\eh'}
    local keymap=${CLI_HELP_KEYMAP:-emacs-standard}
    local internal binding bound_key
    if [[ $key == *[!a-zA-Z0-9\\\[\]\~\^\?\_\;\-]* || -z $key ]]; then
        printf '%s\n' 'interactive-help: invalid Readline key sequence.' >&2
        return 1
    fi
    case "$keymap" in
        vi-insertion) keymap=vi-insert ;;
        # A macro is replayed from the root map. Normalize the meta-map prefix
        # so both private dispatch sequences resolve in that same root map.
        emacs-meta) key="\e$key"; keymap=emacs-standard ;;
        emacs-standard|vi-command) ;;
        *) printf '%s\n' 'interactive-help: unsupported Readline keymap.' >&2; return 1 ;;
    esac
    for internal in '\e[988~' '\e[989~'; do
        if [[ $key == "$internal"* || $internal == "$key"* ]]; then
            printf '%s\n' 'interactive-help: key conflicts with an internal Readline sequence.' >&2
            return 1
        fi
        if [[ ${_CLI_HELP_BOUND_MAP:-} != "$keymap" ]]; then
            while IFS= read -r binding; do
                [[ $binding == \"* ]] || continue
                bound_key=${binding%%\":*}
                bound_key=${bound_key#\"}
                if [[ -n $bound_key && ( $internal == "$bound_key"* || $bound_key == "$internal"* ) ]]; then
                    printf 'interactive-help: Readline sequence %s is already bound in %s.\n' "$internal" "$keymap" >&2
                    return 1
                fi
            done < <(bind -m "$keymap" -p; bind -m "$keymap" -s; bind -m "$keymap" -X)
        fi
    done
    if ! bind -m "$keymap" -x '"\e[988~":_cli_help_widget'; then
        return 1
    fi
    bind -m "$keymap" '"\e[989~":""'
    bind -m "$keymap" "\"$key\":\"\e[988~\e[989~\""
    if [[ -n ${_CLI_HELP_BOUND_KEY:-} ]] && \
       [[ $_CLI_HELP_BOUND_KEY != "$key" || $_CLI_HELP_BOUND_MAP != "$keymap" ]]; then
        bind -m "$_CLI_HELP_BOUND_MAP" -r "$_CLI_HELP_BOUND_KEY"
        if [[ $_CLI_HELP_BOUND_MAP != "$keymap" ]]; then
            bind -m "$_CLI_HELP_BOUND_MAP" -r '\e[988~'
            bind -m "$_CLI_HELP_BOUND_MAP" -r '\e[989~'
        fi
    fi
    _CLI_HELP_BOUND_KEY=$key
    _CLI_HELP_BOUND_MAP=$keymap
}

# Remove the plugin binding from this session. Other shell settings are retained.
cli_help_unbind() {
    if [[ -n ${_CLI_HELP_BOUND_KEY:-} ]]; then
        bind -m "$_CLI_HELP_BOUND_MAP" -r "$_CLI_HELP_BOUND_KEY"
        bind -m "$_CLI_HELP_BOUND_MAP" -r '\e[988~'
        bind -m "$_CLI_HELP_BOUND_MAP" -r '\e[989~'
        unset _CLI_HELP_BOUND_KEY _CLI_HELP_BOUND_MAP
    fi
}

if [[ $- == *i* ]]; then
    cli_help_bind
fi
