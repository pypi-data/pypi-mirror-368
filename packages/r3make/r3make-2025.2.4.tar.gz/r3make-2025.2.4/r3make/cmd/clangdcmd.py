from r3make.util import os, json

def clangdcmd(main_config, config_path) -> None:
    project_root = os.path.dirname(os.path.abspath(config_path))
    commands = []
    seen = set()

    for target, data in main_config.items():
        includes = [f"-I{inc}" for inc in data.get("includes", [])]
        defines = [f"-D{d}" for d in data.get("defines", [])]
        flags = data.get("flags", [])
        sources = []
        for pattern in data.get("sources", []):
            sources.extend(__import__("glob").glob(pattern, recursive=True))

        for src in sources:
            abs_src = os.path.abspath(src)
            if abs_src in seen:
                continue
            seen.add(abs_src)

            cmd_parts = ["gcc"] + flags + defines + includes + ["-c", abs_src]
            commands.append({
                "directory": project_root,
                "command": " ".join(cmd_parts),
                "file": abs_src
            })

    with open(os.path.join(project_root, "compile_commands.json"), "w") as f:
        json.dump(commands, f, indent=2)

    return True

