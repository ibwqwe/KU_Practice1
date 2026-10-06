"""
Shell emulator. Stage 5: touch and rm commands (VFS in memory).
"""

import sys
import json
import tkinter as tk

VFS_NAME = "myVFS"


def parse_args(argv):
    """
    Parse command line arguments.

    Supported:
        vfs=<path>     — path to VFS JSON file
        script=<path>  — path to startup script

    Returns tuple (vfs_path, script_path).
    """
    vfs_path = None
    script_path = None

    for arg in argv:
        if arg.startswith("vfs="):
            vfs_path = arg[4:]
        elif arg.startswith("script="):
            script_path = arg[7:]
        else:
            print(f"unknown arg: {arg}")

    return vfs_path, script_path


def make_default_vfs():
    """
    Return default VFS.

    Used when VFS path is not given or loading failed.
    """
    return {
        "name": "default",
        "root": {
            "type": "dir",
            "children": {
                "readme.txt": {
                    "type": "file",
                    "content": "default VFS"
                },
                "docs": {
                    "type": "dir",
                    "children": {
                        "info.txt": {
                            "type": "file",
                            "content": "info"
                        }
                    }
                }
            }
        }
    }


def load_vfs(path):
    """
    Read VFS from a JSON file.

    Returns tuple (vfs, error):
        - on success: (vfs dict, None)
        - on error:   (None, error text)
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            vfs = json.load(f)
    except FileNotFoundError:
        return None, f"file not found: {path}"
    except json.JSONDecodeError as e:
        return None, f"bad JSON: {e}"
    except Exception as e:
        return None, f"read error: {e}"

    if "root" not in vfs or "name" not in vfs:
        return None, "no 'name' or 'root' in JSON"

    return vfs, None


def find_motd(vfs):
    """
    Search for motd file in VFS root.

    Returns motd content if present, else None.
    """
    root = vfs["root"]
    children = root.get("children", {})

    if "motd" in children:
        node = children["motd"]
        if node.get("type") == "file":
            return node.get("content", "")

    return None


def split_path(path):
    """
    Split path into list of non-empty parts.

    Examples:
        "/home/user"   -> ["home", "user"]
        "home//user/"  -> ["home", "user"]
        ""             -> []
    """
    parts = []
    for part in path.split("/"):
        if part and part != ".":
            parts.append(part)
    return parts


def split_parent(path):
    parts = split_path(path)
    if not parts:
        return "", ""

    name = parts[-1]
    parent_parts = parts[:-1]
    parent = "/".join(parent_parts)

    if path.startswith("/") and parent:
        parent = "/" + parent

    return parent, name


def get_node(vfs, cwd, path):
    if path == "":
        parts = list(cwd)
    elif path.startswith("/"):
        parts = split_path(path)
    else:
        parts = list(cwd) + split_path(path)

    node = vfs["root"]
    result_parts = []

    for part in parts:
        if part == "..":
            if result_parts:
                result_parts.pop()
            continue

        if node.get("type") != "dir":
            cur = "/".join(result_parts) or "/"
            return None, None, f"not a dir: {cur}"

        children = node.get("children", {})
        if part not in children:
            full = "/" + "/".join(result_parts + [part])
            return None, None, f"no such path: {full}"

        node = children[part]
        result_parts.append(part)

    return node, result_parts, None


def cmd_ls(vfs, cwd, args):
    """
    ls command — list dir contents or show file name.
    """
    path = args[0] if args else ""

    node, _, error = get_node(vfs, cwd, path)
    if error:
        return f"ls: {error}"

    if node.get("type") == "file":
        return path

    children = node.get("children", {})
    if not children:
        return ""

    return "\n".join(sorted(children.keys()))


def cmd_cd(vfs, cwd, args):
    """
    cd command — change current directory.

    Returns (text, new_cwd).
    """
    path = args[0] if args else "/"

    node, new_cwd, error = get_node(vfs, cwd, path)
    if error:
        return f"cd: {error}", cwd

    if node.get("type") != "dir":
        return f"cd: not a dir: {path}", cwd

    return "", new_cwd


def cmd_cat(vfs, cwd, args):
    """
    cat command — print file content.
    """
    if not args:
        return "cat: no file"

    path = args[0]
    node, _, error = get_node(vfs, cwd, path)
    if error:
        return f"cat: {error}"

    if node.get("type") != "file":
        return f"cat: is a dir: {path}"

    return node.get("content", "")


def cmd_tac(vfs, cwd, args):
    """
    tac command — like cat, but lines are reversed.
    """
    if not args:
        return "tac: no file"

    path = args[0]
    node, _, error = get_node(vfs, cwd, path)
    if error:
        return f"tac: {error}"

    if node.get("type") != "file":
        return f"tac: is a dir: {path}"

    content = node.get("content", "")
    lines = content.split("\n")
    lines.reverse()
    return "\n".join(lines)


def cmd_touch(vfs, cwd, args):
    """
    touch command — create empty file in VFS (in memory).

    Rules:
        - no argument — error;
        - parent dir missing — error;
        - parent is not a dir — error;
        - file already exists — error.

    Changes are in memory only. JSON on disk is untouched.
    """
    if not args:
        return "touch: no file"

    path = args[0]
    parent_path, name = split_parent(path)

    if not name:
        return f"touch: bad path: {path}"

    parent_node, _, error = get_node(vfs, cwd, parent_path)
    if error:
        return f"touch: {error}"

    if parent_node.get("type") != "dir":
        return f"touch: not a dir: {parent_path or '/'}"

    children = parent_node.setdefault("children", {})
    if name in children:
        return f"touch: already exists: {name}"

    children[name] = {"type": "file", "content": ""}
    return ""


def cmd_rm(vfs, cwd, args):
    """
    rm command — remove file from VFS (in memory).

    Rules:
        - no argument — error;
        - parent dir missing — error;
        - file not found — error;
        - node is a dir — error.

    Changes are in memory only. JSON on disk is untouched.
    """
    if not args:
        return "rm: no file"

    path = args[0]
    parent_path, name = split_parent(path)

    if not name:
        return f"rm: bad path: {path}"

    parent_node, _, error = get_node(vfs, cwd, parent_path)
    if error:
        return f"rm: {error}"

    if parent_node.get("type") != "dir":
        return f"rm: not a dir: {parent_path or '/'}"

    children = parent_node.get("children", {})
    if name not in children:
        full = "/" + "/".join(split_path(parent_path) + [name])
        return f"rm: no such file: {full}"

    if children[name].get("type") == "dir":
        return f"rm: is a dir: {name}"

    del children[name]
    return ""


class Window:
    """
    Application window.

    Handles output area, input field and command execution
    in context of current VFS and cwd.
    """

    def __init__(self, root, vfs, motd=None, script_path=None):
        self.root = root
        self.vfs = vfs
        self.cwd = []

        root.title(f"Emulator - {VFS_NAME}")
        root.geometry("700x450")
        root.minsize(500, 300)

        self.entry = tk.Entry(root, font=("Consolas", 12))
        self.entry.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=(0, 5))
        self.entry.bind("<Return>", self.on_enter)
        self.entry.focus_set()

        self.output = tk.Text(root, font=("Consolas", 11))
        self.output.pack(
            side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5
        )

        if motd:
            self.print_line(motd)

        self.print_line(
            f"{VFS_NAME}: cmds: ls, cd, cat, tac, touch, rm, exit"
        )

        if script_path:
            run_script(self, script_path)

    def print_line(self, text):
        """
        Append one line to output area.
        """
        self.output.insert(tk.END, text + "\n")
        self.output.see(tk.END)

    def on_enter(self, event):
        """
        Handle Enter press in input field.
        """
        text = self.entry.get()
        self.entry.delete(0, tk.END)

        if not text.strip():
            return

        self.print_line(f"{VFS_NAME}$ {text}")

        result = self.execute(text)
        if result is not None:
            self.print_line(result)

    def execute(self, text):
        """
        Execute one command.

        Returns text for output. For silent commands (like successful
        cd) returns None to avoid printing an empty line.
        """
        parts = text.split()
        command = parts[0]
        args = parts[1:]

        if command == "exit":
            self.print_line("exit: bye")
            self.root.destroy()
            return None

        if command == "ls":
            return cmd_ls(self.vfs, self.cwd, args)

        if command == "cd":
            out, new_cwd = cmd_cd(self.vfs, self.cwd, args)
            self.cwd = new_cwd
            return out or None

        if command == "cat":
            return cmd_cat(self.vfs, self.cwd, args)

        if command == "tac":
            return cmd_tac(self.vfs, self.cwd, args)

        if command == "touch":
            out = cmd_touch(self.vfs, self.cwd, args)
            return out or None

        if command == "rm":
            out = cmd_rm(self.vfs, self.cwd, args)
            return out or None

        return f"unknown command: '{command}'"


def run_script(window, path):
    """
    Execute startup script line by line.

    If a command closes the window (exit), execution stops.
    """
    window.print_line(f"--- run script: {path} ---")

    try:
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        window.print_line(f"script not found: {path}")
        return

    for raw in lines:
        line = raw.strip()

        if not line or line.startswith("#"):
            continue

        window.print_line(f"{VFS_NAME}$ {line}")

        result = window.execute(line)
        if result is not None:
            window.print_line(result)

        if not window.root.winfo_exists():
            return

    window.print_line("--- script done ---")


def main():
    """
    Application entry point.
    """
    vfs_path, script_path = parse_args(sys.argv[1:])

    print(f"VFS: {vfs_path}")
    print(f"Script: {script_path}")

    if vfs_path:
        vfs, error = load_vfs(vfs_path)
        if error:
            print(f"VFS load error: {error}")
            vfs = make_default_vfs()
            vfs_load_error = f"VFS load error: {error}"
        else:
            vfs_load_error = None
    else:
        vfs = make_default_vfs()
        vfs_load_error = None

    motd = find_motd(vfs)

    root = tk.Tk()
    window = Window(root, vfs, motd=motd, script_path=script_path)

    if vfs_load_error:
        window.output.insert("1.0", vfs_load_error + "\n")

    root.mainloop()


if __name__ == "__main__":
    main()
