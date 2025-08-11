import argparse
from r3make.core import build_project
from r3make.util import log, load_config

# import cli commands
from r3make.cmd.gitdeps import gitdeps
from r3make.cmd.clangdcmd import clangdcmd

def cli_arg(name: str, default: str, help: str, parser: argparse.ArgumentParser):
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
        "file",
        default="r3make.json",
        help="Path to r3make config file (default: r3make.json)",
        parser=parser
    )
    cli_arg(
        "target",
        default="main",
        help="Compilation target (default: main)",
        parser=parser
    )
    cli_arg(
        "verbose",
        action="store_true",
        help="Enable verbose output",
        parser=parser
    )
    cli_arg(
        "noFiles",
        action="store_true",
        help="Delete object files after build",
        parser=parser
    )
    cli_arg(
        "buildEach",
        help="Build each source file as its own target",
        parser=parser
    )
    cli_arg(
        "run",
        action="store_true",
        help="Run an executable after building",
        parser=parser
    )
    cli_arg(
        "clangdCmd",
        help="Generate clangd LSP compilation configuration. (for vim/neovim users)",
        parser=parser

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
