/* Linux launcher for the adjacent, inspectable Python and Bash runtime. */
#define _POSIX_C_SOURCE 200809L
#include <errno.h>
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#ifndef CLI_HELP_VERSION
#define CLI_HELP_VERSION "development"
#endif

int main(int argc, char **argv) {
    char root[PATH_MAX];
    char target[PATH_MAX];
    ssize_t length = readlink("/proc/self/exe", root, sizeof(root) - 1);
    if (length < 0 || (size_t)length >= sizeof(root) - 1) {
        fputs("cli-help: cannot locate the Linux executable\n", stderr);
        return 1;
    }
    root[length] = '\0';
    char *slash = strrchr(root, '/');
    if (!slash) return 1;
    *slash = '\0';
    if (argc == 2 && strcmp(argv[1], "--version") == 0) {
        puts("CLI Interactive Help Menu " CLI_HELP_VERSION);
        return 0;
    }
    const char *relative = "cli_help/main.py";
    const char *program = getenv("CLI_HELP_PYTHON");
    if (!program || !*program) program = "python3";
    int first_argument = 1;
    if (argc > 1) {
        if (strcmp(argv[1], "install") == 0) relative = "install.sh";
        else if (strcmp(argv[1], "update") == 0) relative = "update.sh";
        else if (strcmp(argv[1], "uninstall") == 0) relative = "uninstall.sh";
        else if (strcmp(argv[1], "review-update") == 0) relative = "review-update.sh";
        else if (strcmp(argv[1], "update-from-github") == 0) relative = "update-from-github.sh";
        if (strcmp(relative, "cli_help/main.py") != 0) {
            program = "bash";
            first_argument = 2;
        }
    }
    int written = snprintf(target, sizeof(target), "%s/%s", root, relative);
    if (written < 0 || (size_t)written >= sizeof(target)) {
        fputs("cli-help: runtime path is too long\n", stderr);
        return 1;
    }
    if (access(target, R_OK) != 0) {
        fputs("cli-help: adjacent runtime is missing; extract the complete release archive\n", stderr);
        return 1;
    }
    char **arguments = calloc((size_t)argc + 2, sizeof(*arguments));
    if (!arguments) return 1;
    arguments[0] = (char *)program;
    arguments[1] = target;
    for (int index = first_argument; index < argc; index++) {
        arguments[index - first_argument + 2] = argv[index];
    }
    /* Forward literal argv entries. No shell command string is constructed. */
    execvp(program, arguments);
    int saved_errno = errno;
    free(arguments);
    fprintf(stderr, "cli-help: cannot start %s: %s\n", program, strerror(saved_errno));
    return 127;
}
