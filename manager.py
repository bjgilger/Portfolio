#!/usr/bin/env python3
"""
A simple, interactive command-line file manager.

This script provides a basic shell interface for navigating a file system
and performing common operations like listing files, moving, copying,
and removing files and directories.
"""

import pathlib
import shutil
import sys
from typing import Callable, Dict, List, Optional

class FileManager:
    """
    Encapsulates the state and operations for a command-line file manager.
    """

    def __init__(self, start_dir: str):
        """
        Initializes the FileManager.

        Args:
            start_dir: The directory where the file manager session will begin.
        """
        try:
            # Resolve to get the absolute path and handle symbolic links
            self.current_dir = pathlib.Path(start_dir).resolve(strict=True)
        except FileNotFoundError:
            print(f"Error: Starting directory '{start_dir}' not found.")
            sys.exit(1)
        
        # Maps user command strings to the methods that handle them
        self._commands: Dict[str, Callable[[List[str]], None]] = {
            "ls": self._handle_ls,
            "cd": self._handle_cd,
            "pwd": self._handle_pwd,
            "cp": self._handle_cp,
            "mv": self._handle_mv,
            "rm": self._handle_rm,
            "mkdir": self._handle_mkdir,
            "help": self._handle_help,
            "quit": self._handle_quit,
        }

    def run(self) -> None:
        """Starts the main interactive loop for the file manager."""
        print("Simple File Manager. Type 'help' for a list of commands.")
        while True:
            try:
                prompt = f"{self.current_dir.name} > "
                raw_command = input(prompt).strip()
                if not raw_command:
                    continue

                parts = raw_command.split()
                command_name = parts[0].lower()
                args = parts[1:]

                handler = self._commands.get(command_name)
                if handler:
                    handler(args)
                else:
                    print(f"Error: Command '{command_name}' not found.")

            except KeyboardInterrupt:
                self._handle_quit()

    def _handle_ls(self, args: List[str]) -> None:
        """Lists files and directories."""
        show_details = "-l" in args or "-lh" in args
        human_readable = "-lh" in args

        try:
            items = sorted(list(self.current_dir.iterdir()), key=lambda p: (p.is_file(), p.name.lower()))
            for item in items:
                if show_details:
                    size = item.stat().st_size
                    size_str = self._human_readable_size(size) if human_readable else str(size)
                    print(f"{item.name:<30} {size_str}")
                else:
                    print(item.name)
        except PermissionError:
            print("Error: Permission denied.")

    def _handle_cd(self, args: List[str]) -> None:
        """Changes the current directory."""
        if not args:
            print("Usage: cd <directory>")
            return
        
        target_dir = self.current_dir / args[0]
        try:
            # Use resolve() to handle '..' and get the canonical path
            new_dir = target_dir.resolve(strict=True)
            if new_dir.is_dir():
                self.current_dir = new_dir
            else:
                print(f"Error: '{args[0]}' is not a directory.")
        except FileNotFoundError:
            print(f"Error: Directory '{args[0]}' not found.")
        except PermissionError:
            print("Error: Permission denied.")

    def _handle_pwd(self, args: Optional[List[str]] = None) -> None:
        """Prints the current working directory."""
        print(self.current_dir)

    def _handle_mkdir(self, args: List[str]) -> None:
        """Creates a new directory."""
        if not args:
            print("Usage: mkdir <directory_name>")
            return
        
        new_dir = self.current_dir / args[0]
        try:
            new_dir.mkdir()
            print(f"Directory '{new_dir.name}' created.")
        except FileExistsError:
            print(f"Error: '{new_dir.name}' already exists.")
        except PermissionError:
            print("Error: Permission denied.")

    def _handle_rm(self, args: List[str]) -> None:
        """Removes a file or directory."""
        if not args:
            print("Usage: rm <file_or_directory> or rm <*.ext>")
            return

        target_str = args[0]
        # Handle batch deletion by extension
        if target_str.startswith("*."):
            glob_pattern = target_str
            targets = list(self.current_dir.glob(glob_pattern))
            if not targets:
                print(f"No files found matching '{glob_pattern}'.")
                return
            
            prompt = f"You are about to delete {len(targets)} file(s). Are you sure? (y/n) "
            if not self._confirm_action(prompt):
                print("Deletion cancelled.")
                return

            for target in targets:
                try:
                    target.unlink()
                    print(f"Removed '{target.name}'.")
                except OSError as e:
                    print(f"Error removing '{target.name}': {e}")
            return

        # Handle single file/directory deletion
        target = self.current_dir / target_str
        try:
            if not target.exists():
                print(f"Error: '{target_str}' not found.")
                return
            
            prompt = f"You are about to permanently delete '{target.name}'. Are you sure? (y/n) "
            if not self._confirm_action(prompt):
                print("Deletion cancelled.")
                return

            if target.is_dir():
                shutil.rmtree(target)
            else:
                target.unlink()
            print(f"Removed '{target.name}'.")
        except PermissionError:
            print("Error: Permission denied.")
        except OSError as e:
            print(f"Error: {e}")

    def _handle_cp(self, args: List[str]) -> None:
        """Copies a file or directory."""
        if len(args) != 2:
            print("Usage: cp <source> <destination>")
            return
        self._perform_file_operation(shutil.copy2, args[0], args[1], "Copied")

    def _handle_mv(self, args: List[str]) -> None:
        """Moves (renames) a file or directory."""
        if len(args) != 2:
            print("Usage: mv <source> <destination>")
            return
        self._perform_file_operation(shutil.move, args[0], args[1], "Moved")
    
    def _perform_file_operation(self, op_func: Callable, src_str: str, dst_str: str, op_name: str) -> None:
        """A generic helper for copy and move operations."""
        source = self.current_dir / src_str
        destination = self.current_dir / dst_str

        if not source.exists():
            print(f"Error: Source '{src_str}' not found.")
            return

        # Determine the final destination path
        if destination.is_dir():
            final_dest = destination / source.name
        else:
            final_dest = destination

        if final_dest.exists():
            prompt = f"'{final_dest.name}' already exists. Overwrite? (y/n) "
            if not self._confirm_action(prompt):
                print(f"{op_name} operation cancelled.")
                return
        
        try:
            if op_func == shutil.copy2 and source.is_dir():
                 # For copying directories, use copytree
                 shutil.copytree(source, final_dest, dirs_exist_ok=True)
            else:
                 op_func(source, final_dest)
            print(f"{op_name} '{source.name}' to '{final_dest}'.")
        except Exception as e:
            print(f"Error during {op_name.lower()} operation: {e}")

    def _handle_help(self, args: Optional[List[str]] = None) -> None:
        """Prints the help message."""
        print("\nAvailable Commands:")
        print("  ls [-l, -lh]       - List contents of the current directory.")
        print("  cd <directory>       - Change directory.")
        print("  pwd                - Print current directory path.")
        print("  cp <src> <dest>      - Copy a file or directory.")
        print("  mv <src> <dest>      - Move or rename a file or directory.")
        print("  rm <name> | <*.ext> - Remove a file, directory, or batch of files.")
        print("  mkdir <name>         - Create a new directory.")
        print("  help               - Show this help message.")
        print("  quit               - Exit the program.\n")
    
    def _handle_quit(self, args: Optional[List[str]] = None) -> None:
        """Exits the program."""
        print("Goodbye!")
        sys.exit(0)

    @staticmethod
    def _confirm_action(prompt: str) -> bool:
        """Gets user confirmation for an action."""
        try:
            resp = input(prompt).strip().lower()
            return resp == 'y'
        except KeyboardInterrupt:
            return False

    @staticmethod
    def _human_readable_size(size: int) -> str:
        """Converts bytes to a human-readable string."""
        if size < 1024:
            return f"{size}B"
        for unit in ['KB', 'MB', 'GB', 'TB']:
            size /= 1024
            if size < 1024:
                return f"{size:.1f}{unit}"
        return f"{size:.1f}PB"

if __name__ == "__main__":
    # The starting folder for the file manager session.
    # Create this directory structure if it doesn't exist.
    start_folder = "module/root_folder"
    pathlib.Path(start_folder).mkdir(parents=True, exist_ok=True)
    
    cli = FileManager(start_dir=start_folder)
    cli.run()