from commandant import builtins
from commandant.controller import CommandController

from kanban import NAME, VERSION, SUMMARY, URL
from kanban import commands, help_topics


def main(argv):
    """Run the command named in C{argv}.

    If a command name isn't provided the C{help} command is shown.

    @param argv: A list command-line arguments.  The first argument should be
       the name of the command to run.  Any further arguments are passed to
       the command.
    """
    if len(argv) < 2:
        argv.append("help")

    controller = CommandController(NAME, VERSION, SUMMARY, URL)
    controller.load_module(builtins)
    controller.load_module(commands)
    controller.load_module(help_topics)
    controller.install_bzrlib_hooks()
    controller.run(argv[1:])
