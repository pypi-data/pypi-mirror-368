import argparse
from r3make.core import build_project
from r3make.util import log, load_config

# import cli commands
from r3make.cmd.gitdeps import gitdeps
from r3make.cmd.clangdcmd import clangdcmd

def cli_arg(parser: argparse.ArgumentParser, name: str, default: str=None, help: str=None):
    short = name[0]
    parser.add_argument(
        f"-{short.lower()}", f"-{short.upper()}", f"--{name.lower()}", f"--{name.capitalize()}",
        action="store_true",
        default=default,
        help=help
        
    )

def main():
    parser = argparse.ArgumentParser(description="r3make - JSON-based C build tool")
    cli_arg(
        parser,
        "file",
        default="r3make.json",
        help="Path to r3make config file (default: r3make.json)",
    )
    cli_arg(
        parser,
        "target",
        default="main",
        help="Compilation target (default: main)",
    )
    cli_arg(
        parser,
        "verbose",
        help="Enable verbose output",
    )
    cli_arg(
        parser,
        "noFiles",
        help="Delete object files after build",
    )
    cli_arg(
        parser,
        "buildEach",
        help="Build each source file as its own target",
    )
    cli_arg(
        parser,
        "run",
        help="Run an executable after building",
    )
    cli_arg(
        parser,
        "clangdCmd",
        help="Generate clangd LSP compilation configuration. (for vim/neovim users)",

    )

    args = parser.parse_args()
    config = load_config(args.target, args.file)

    if config:
        gitdeps(args.target, config, verbose=args.verbose)
        build_project(
            cfg=config,
            target=args.target,
            run=args.run,
            verbose=args.verbose,
            nofiles=args.nofiles,
            buildeach=args.buildeach,
            clangdcmd=args.clangdcmd
        )
        if clangdcmd:
            if not clangdcmd(main_config):
                log("Failed to generate clangd LSP 'compile_commands.json'", "error")
            else:
                log("Generated clangd LSP 'compile_commands.json'", "success")
    else:
        log(f"Failed to load config: {args.target} {args.file}")
        exit(1)
