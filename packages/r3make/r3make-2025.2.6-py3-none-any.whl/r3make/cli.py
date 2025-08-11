import argparse
from r3make.core import build_project
from r3make.util import log, load_config

# import cli commands
from r3make.cmd.gitdeps import gitdeps
from r3make.cmd.clangdcmd import clangdcmd

def cli_arg(parser: argparse.ArgumentParser, shorthand: str, name: str, default: str=None, help: str=None):
    parser.add_argument(
        f"-{shorthand.lower()}", f"-{shorthand.capitalize()}", f"--{name.lower()}", f"--{name.capitalize()}",
        action="store_true",
        default=default,
        help=help
        
    )

def main():
    parser = argparse.ArgumentParser(description="r3make - JSON-based C build tool")
    cli_arg(
        parser,
        "f", "file",
        default="r3make.json",
        help="Path to r3make config file (default: r3make.json)",
    )
    cli_arg(
        parser,
        "t", "target",
        default="main",
        help="Compilation target (default: main)",
    )
    cli_arg(
        parser,
        "v", "verbose",
        help="Enable verbose output",
    )
    cli_arg(
        parser,
        "nf", "noFiles",
        help="Delete object files after build",
    )
    cli_arg(
        parser,
        "be", "buildEach",
        help="Build each source file as its own target",
    )
    cli_arg(
        parser,
        "r", "run",
        help="Run an executable after building",
    )
    cli_arg(
        parser,
        "ccmd", "clangdCmd",
        help="Generate clangd LSP compilation configuration. (for vim/neovim users)",

    )

    args = parser.parse_args()
    config = load_config(args.target, args.file)

    if config:
        gitdeps(args.target, config, verbose=args.verbose)
        build_project(
            main_config=config,
            target=args.target,
            run=args.run,
            verbose=args.verbose,
            nofiles=args.nofiles,
            buildeach=args.buildeach,
            clangdcmd=args.clangdcmd
        )
        if clangdcmd:
            if not clangdcmd(config):
                log("Failed to generate clangd LSP 'compile_commands.json'", "error")
            else:
                log("Generated clangd LSP 'compile_commands.json'", "success")
    else:
        log(f"Failed to load config: {args.target} {args.file}")
        exit(1)
