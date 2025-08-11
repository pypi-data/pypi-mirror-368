"""CLI entry point for SimpleBroker."""

import argparse
import os
import sys
from pathlib import Path
from typing import List, NoReturn, Optional

from . import __version__ as VERSION
from . import commands
from ._constants import DEFAULT_DB_NAME, PROG_NAME, TIMESTAMP_EXACT_NUM_DIGITS

# Cache the parser for better startup performance
_PARSER_CACHE = None


class ArgumentParserError(Exception):
    """Custom exception for argument parsing errors."""

    pass


class CustomArgumentParser(argparse.ArgumentParser):
    """Custom ArgumentParser that doesn't exit on error."""

    def error(self, message: str) -> NoReturn:
        raise ArgumentParserError(message)


def add_read_peek_args(parser: argparse.ArgumentParser) -> None:
    """Add shared arguments for read and peek commands."""
    parser.add_argument("queue", help="queue name")
    parser.add_argument("--all", action="store_true", help="read/peek all messages")
    parser.add_argument(
        "--json",
        action="store_true",
        help="output in line-delimited JSON (ndjson) format",
    )
    parser.add_argument(
        "-t",
        "--timestamps",
        action="store_true",
        help="include timestamps in output",
    )
    parser.add_argument(
        "-m",
        "--message",
        type=str,
        metavar="ID",
        dest="message_id",
        help="operate on specific message by timestamp/ID",
    )
    parser.add_argument(
        "--since",
        type=str,
        metavar="TIMESTAMP",
        help="return messages after timestamp (supports: ISO date '2024-01-15', "
        "Unix time '1705329000' or '1705329000s', milliseconds '1705329000000ms', "
        "or native hybrid timestamp)",
    )


def create_parser() -> argparse.ArgumentParser:
    """Create the main parser with global options and subcommands.

    Returns:
        ArgumentParser configured with global options and subcommands
    """
    parser = CustomArgumentParser(
        prog=PROG_NAME,
        description="Simple message broker with SQLite backend",
        allow_abbrev=False,  # Prevent ambiguous abbreviations
    )

    # Add global arguments
    parser.add_argument(
        "-d", "--dir", type=Path, default=Path.cwd(), help="working directory"
    )
    parser.add_argument(
        "-f",
        "--file",
        default=DEFAULT_DB_NAME,
        help=f"database filename or absolute path (default: {DEFAULT_DB_NAME})",
    )
    parser.add_argument(
        "-q", "--quiet", action="store_true", help="suppress diagnostics"
    )
    parser.add_argument("--version", action="store_true", help="show version")
    parser.add_argument(
        "--cleanup", action="store_true", help="delete the database file and exit"
    )
    parser.add_argument(
        "--vacuum", action="store_true", help="remove claimed messages and exit"
    )

    # Create subparsers for commands
    subparsers = parser.add_subparsers(title="commands", dest="command", help=None)

    # Write command
    write_parser = subparsers.add_parser("write", help="write message to queue")
    write_parser.add_argument("queue", help="queue name")
    write_parser.add_argument("message", help="message content ('-' for stdin)")

    # Read command
    read_parser = subparsers.add_parser("read", help="read and remove message")
    add_read_peek_args(read_parser)

    # Peek command
    peek_parser = subparsers.add_parser("peek", help="read without removing")
    add_read_peek_args(peek_parser)

    # List command
    list_parser = subparsers.add_parser("list", help="list all queues")
    list_parser.add_argument(
        "--stats",
        action="store_true",
        help="show statistics including claimed messages",
    )

    # Purge command
    delete_parser = subparsers.add_parser("delete", help="remove messages")
    group = delete_parser.add_mutually_exclusive_group(required=True)
    group.add_argument("queue", nargs="?", help="queue name to delete")
    group.add_argument("--all", action="store_true", help="delete all queues")
    delete_parser.add_argument(
        "-m",
        "--message",
        type=str,
        metavar="ID",
        dest="message_id",
        help="delete specific message by timestamp/ID",
    )

    # Move command
    move_parser = subparsers.add_parser(
        "move", help="atomically transfer messages between queues"
    )
    move_parser.add_argument("source_queue", help="source queue name")
    move_parser.add_argument("dest_queue", help="destination queue name")

    # Create mutually exclusive group for -m and --all
    move_exclusive = move_parser.add_mutually_exclusive_group()
    move_exclusive.add_argument(
        "-m",
        "--message",
        type=str,
        metavar="ID",
        dest="message_id",
        help="move specific message by timestamp/ID",
    )
    move_exclusive.add_argument(
        "--all",
        action="store_true",
        help="move all messages from source to destination",
    )

    # --since can be used with or without --all
    move_parser.add_argument(
        "--since",
        type=str,
        metavar="TIMESTAMP",
        help="only move messages newer than timestamp",
    )
    move_parser.add_argument(
        "--json",
        action="store_true",
        help="output in line-delimited JSON (ndjson) format",
    )
    move_parser.add_argument(
        "-t",
        "--timestamps",
        action="store_true",
        help="include timestamps in output",
    )

    # Broadcast command
    broadcast_parser = subparsers.add_parser(
        "broadcast", help="send message to all queues"
    )
    broadcast_parser.add_argument("message", help="message content ('-' for stdin)")

    # Watch command
    watch_parser = subparsers.add_parser(
        "watch", help="watch queue and consume, peek, or move messages"
    )
    watch_parser.add_argument("queue", help="queue name")

    # Create mutually exclusive group for --peek and --move
    watch_mode_group = watch_parser.add_mutually_exclusive_group()
    watch_mode_group.add_argument(
        "--peek",
        action="store_true",
        help="monitor without consuming messages",
    )
    watch_mode_group.add_argument(
        "--move",
        type=str,
        metavar="QUEUE",
        help="drain ALL messages to another queue (incompatible with --since)",
    )

    watch_parser.add_argument(
        "--json",
        action="store_true",
        help="output in line-delimited JSON (ndjson) format",
    )
    watch_parser.add_argument(
        "-t",
        "--timestamps",
        action="store_true",
        help="include timestamps in output",
    )
    watch_parser.add_argument(
        "--since",
        type=str,
        metavar="TIMESTAMP",
        help="watch for messages after timestamp",
    )

    return parser


def rearrange_args(argv: List[str]) -> List[str]:
    """Rearrange arguments to put global options before subcommand.

    This allows global options to appear anywhere on the command line,
    including after the subcommand.

    Args:
        argv: List of command line arguments (without program name)

    Returns:
        List of rearranged arguments

    Raises:
        ArgumentParserError: If a global option that requires a value is missing its value
    """
    if not argv:
        return argv

    processor = ArgumentProcessor()
    return processor.process(argv)


class ArgumentProcessor:
    """Helper class to process and rearrange command line arguments."""

    def __init__(self) -> None:
        # Define global option flags
        self.global_options = {
            "-d",
            "--dir",
            "-f",
            "--file",
            "-q",
            "--quiet",
            "--version",
            "--cleanup",
            "--vacuum",
        }

        # Options that require values
        self.options_with_values = {"-d", "--dir", "-f", "--file"}

        # Find subcommands
        self.subcommands = {
            "write",
            "read",
            "peek",
            "list",
            "delete",
            "move",
            "broadcast",
            "watch",
        }

        self.global_args: List[str] = []
        self.command_args: List[str] = []
        self.found_command = False
        self.expecting_value_for: Optional[str] = None

    def process(self, argv: List[str]) -> List[str]:
        """Process and rearrange arguments."""
        i = 0
        while i < len(argv):
            self._process_argument(argv[i])
            i += 1

        # Check if we're still expecting a value at the end
        if self.expecting_value_for:
            raise ArgumentParserError(
                f"option {self.expecting_value_for} requires an argument"
            )

        # Combine: global options first, then command and its arguments
        return self.global_args + self.command_args

    def _process_argument(self, arg: str) -> None:
        """Process a single argument."""
        if self.expecting_value_for:
            self._handle_expected_value(arg)
        elif self._is_option_with_equals(arg):
            self._handle_option_with_equals(arg)
        elif arg in self.global_options:
            self._handle_global_option(arg)
        elif arg in self.subcommands and not self.found_command:
            self._handle_subcommand(arg)
        else:
            self.command_args.append(arg)

    def _handle_expected_value(self, arg: str) -> None:
        """Handle an argument when we're expecting a value for a previous option."""
        if arg.startswith("-"):
            # This is likely another flag, not a value
            raise ArgumentParserError(
                f"option {self.expecting_value_for} requires an argument"
            )
        self.global_args.append(arg)
        self.expecting_value_for = None

    def _is_option_with_equals(self, arg: str) -> bool:
        """Check if argument is a global option with equals form."""
        return "=" in arg and arg.split("=")[0] in self.global_options

    def _handle_option_with_equals(self, arg: str) -> None:
        """Handle --option=value format."""
        option_name = arg.split("=")[0]
        if option_name in self.options_with_values:
            # Check if value is provided after =
            if arg.endswith("="):
                # Ends with = but no value
                raise ArgumentParserError(f"option {option_name} requires an argument")
        self.global_args.append(arg)

    def _handle_global_option(self, arg: str) -> None:
        """Handle a global option."""
        self.global_args.append(arg)
        # Check if this option takes a value
        if arg in self.options_with_values:
            # Mark that we're expecting a value next
            self.expecting_value_for = arg

    def _handle_subcommand(self, arg: str) -> None:
        """Handle a subcommand."""
        self.found_command = True
        self.command_args.append(arg)


def main() -> int:
    """Main CLI entry point.

    Returns:
        Exit code (0 for success, 1 for error)
    """
    # Use cached parser for better startup performance
    global _PARSER_CACHE
    if _PARSER_CACHE is None:
        _PARSER_CACHE = create_parser()
    parser = _PARSER_CACHE

    # Parse arguments, rearranging to put global options first
    try:
        if len(sys.argv) == 1:
            parser.print_help()
            return 0

        # Rearrange arguments to put global options before subcommand
        rearranged_args = rearrange_args(sys.argv[1:])

        # Use regular parse_args with rearranged arguments
        args = parser.parse_args(rearranged_args)
    except ArgumentParserError as e:
        print(f"{PROG_NAME}: error: {e}", file=sys.stderr)
        return 1
    except SystemExit as e:  # e.code: Union[int, str, None]
        # Handle argparse's default exit behavior
        # Help exits with 0, errors exit with 2
        if e.code is None:
            return 1
        try:
            return int(e.code)
        except (ValueError, TypeError):
            # If code can't be converted to int, return error code 1
            return 1

    # Handle --version flag
    if args.version:
        print(f"{PROG_NAME} {VERSION}")
        return 0

    # Handle absolute paths in -f flag
    file_path = Path(args.file)
    absolute_path_provided = file_path.is_absolute()

    if absolute_path_provided:
        # Extract directory and filename from absolute path
        extracted_dir = file_path.parent
        extracted_file = file_path.name

        # Check if user also specified -d with a different directory
        if args.dir != Path.cwd() and args.dir != extracted_dir:
            print(
                f"{PROG_NAME}: error: Inconsistent paths - "
                f"absolute path '{args.file}' conflicts with directory '{args.dir}'",
                file=sys.stderr,
            )
            return 1

        # Update args to use extracted components
        args.dir = extracted_dir
        args.file = extracted_file

    # Handle cleanup flag
    if args.cleanup:
        try:
            db_path = args.dir / args.file
            # Check if file existed before deletion for messaging purposes
            file_existed = db_path.exists()

            try:
                # Use missing_ok=True to handle TOCTOU race condition atomically
                # This will succeed whether the file exists or not
                db_path.unlink(missing_ok=True)

                if file_existed and not args.quiet:
                    print(f"Database cleaned up: {db_path}")
                elif not file_existed and not args.quiet:
                    print(f"Database not found, nothing to clean up: {db_path}")
            except PermissionError:
                print(
                    f"{PROG_NAME}: error: Permission denied: {db_path}",
                    file=sys.stderr,
                )
                return 1
            return 0
        except Exception as e:
            print(f"{PROG_NAME}: error: {e}", file=sys.stderr)
            return 1

    # Handle vacuum flag
    if args.vacuum:
        try:
            db_path = args.dir / args.file
            if not db_path.exists():
                if not args.quiet:
                    print(f"Database not found: {db_path}")
                return 0

            return commands.cmd_vacuum(str(db_path))
        except Exception as e:
            print(f"{PROG_NAME}: error: {e}", file=sys.stderr)
            return 1

    # Show help if no command given
    if not args.command:
        parser.print_help()
        return 0

    # Validate and construct database path
    try:
        working_dir = args.dir
        if not working_dir.exists():
            raise ValueError(f"Directory not found: {working_dir}")
        if not working_dir.is_dir():
            # Provide more helpful error message for common mistake
            if working_dir.is_file():
                raise ValueError(f"Path is a file, not a directory: {working_dir}")
            else:
                raise ValueError(f"Not a directory: {working_dir}")

        db_path = working_dir / args.file

        # Prevent path traversal attacks - ensure db_path stays within working_dir
        from pathlib import PurePath

        # Check for path traversal attempts
        file_path_pure = PurePath(args.file)

        # Check for parent directory references
        for part in file_path_pure.parts:
            if part == "..":
                raise ValueError(
                    f"Database filename must not contain parent directory references: {args.file}"
                )

        # Resolve symlinks BEFORE validation and use resolved path throughout
        # This prevents symlink-based path traversal attacks
        try:
            # Always resolve the database path to handle symlinks
            resolved_db_path = db_path.resolve()
            resolved_working_dir = working_dir.resolve()

            # On Windows, resolve() might not fully resolve symlink chains
            # Keep resolving until we reach a non-symlink or hit an error
            max_symlink_depth = 40  # Prevent infinite loops
            depth = 0
            while resolved_db_path.is_symlink() and depth < max_symlink_depth:
                try:
                    # Read the symlink target and resolve it
                    if hasattr(resolved_db_path, "readlink"):
                        # Python 3.9+
                        target = resolved_db_path.readlink()
                    else:
                        # Python 3.8 and older
                        target = Path(os.readlink(str(resolved_db_path)))

                    if target.is_absolute():
                        resolved_db_path = target.resolve()
                    else:
                        # Relative symlink - resolve relative to parent
                        resolved_db_path = (resolved_db_path.parent / target).resolve()
                    depth += 1
                except (OSError, RuntimeError):
                    # If we can't read/resolve the symlink, use what we have
                    break

            # For non-absolute paths, ensure the resolved path is within working directory
            if not absolute_path_provided:
                # Check if the database path is within the working directory
                # Use is_relative_to() if available (Python 3.9+), otherwise use relative_to()
                if hasattr(resolved_db_path, "is_relative_to"):
                    if not resolved_db_path.is_relative_to(resolved_working_dir):
                        raise ValueError(
                            "Database file must be within the working directory"
                        )
                else:
                    # Fallback for older Python versions - try relative_to and catch exception
                    try:
                        resolved_db_path.relative_to(resolved_working_dir)
                    except ValueError:
                        raise ValueError(
                            "Database file must be within the working directory"
                        ) from None

            # Use the resolved path from now on to prevent symlink attacks
            db_path = resolved_db_path

        except (RuntimeError, OSError):
            # resolve() can fail if parent directories don't exist yet
            # In this case, we create a resolved path based on resolved working dir
            if not absolute_path_provided:
                try:
                    resolved_working_dir = working_dir.resolve()
                    # Manually construct the resolved path
                    db_path = resolved_working_dir / args.file
                except (RuntimeError, OSError):
                    # If we can't resolve even the working directory, keep original
                    pass

        # 1) Check if parent directory exists
        if not db_path.parent.exists():
            raise ValueError(f"Parent directory not found: {db_path.parent}")

        # 2) Check if parent directory is accessible (executable/writable)
        if not os.access(db_path.parent, os.X_OK):
            raise ValueError(f"Parent directory is not accessible: {db_path.parent}")

        if not os.access(db_path.parent, os.W_OK):
            raise ValueError(f"Parent directory is not writable: {db_path.parent}")

        # 3) Check if file exists and permissions
        if db_path.exists():
            # Check if it's a regular file
            if not db_path.is_file():
                raise ValueError(f"Path exists but is not a regular file: {db_path}")

            # Check if file is readable/writable
            if not os.access(db_path, os.R_OK):
                raise ValueError(f"Database file is not readable: {db_path}")

            if not os.access(db_path, os.W_OK):
                raise ValueError(f"Database file is not writable: {db_path}")

    except ValueError as e:
        print(f"{PROG_NAME}: error: {e}", file=sys.stderr)
        return 1

    # Execute command
    try:
        db_path_str = str(db_path)

        # Dispatch to appropriate command handler
        if args.command == "write":
            return commands.cmd_write(db_path_str, args.queue, args.message)
        elif args.command == "read":
            since_str = getattr(args, "since", None)
            message_id_str = getattr(args, "message_id", None)

            # Validate message_id format early (fail fast)
            if message_id_str is not None:
                if (
                    len(message_id_str) != TIMESTAMP_EXACT_NUM_DIGITS
                    or not message_id_str.isdigit()
                ):
                    return commands.EXIT_QUEUE_EMPTY  # Return 2 for invalid format

                # Check mutual exclusivity
                if args.all or since_str:
                    parser.error("--message cannot be used with --all or --since")

            return commands.cmd_read(
                db_path_str,
                args.queue,
                args.all,
                args.json,
                args.timestamps,
                since_str,
                message_id_str,
            )
        elif args.command == "peek":
            since_str = getattr(args, "since", None)
            message_id_str = getattr(args, "message_id", None)

            # Validate message_id format early (fail fast)
            if message_id_str is not None:
                if (
                    len(message_id_str) != TIMESTAMP_EXACT_NUM_DIGITS
                    or not message_id_str.isdigit()
                ):
                    return commands.EXIT_QUEUE_EMPTY  # Return 2 for invalid format

                # Check mutual exclusivity
                if args.all or since_str:
                    parser.error("--message cannot be used with --all or --since")

            return commands.cmd_peek(
                db_path_str,
                args.queue,
                args.all,
                args.json,
                args.timestamps,
                since_str,
                message_id_str,
            )
        elif args.command == "list":
            show_stats = getattr(args, "stats", False)
            return commands.cmd_list(db_path_str, show_stats)
        elif args.command == "delete":
            # argparse mutual exclusion ensures exactly one of queue or --all is provided
            queue = None if args.all else args.queue
            message_id_str = getattr(args, "message_id", None)

            # Validate message_id format early (fail fast)
            if message_id_str is not None:
                if (
                    len(message_id_str) != TIMESTAMP_EXACT_NUM_DIGITS
                    or not message_id_str.isdigit()
                ):
                    return commands.EXIT_QUEUE_EMPTY  # Return 2 for invalid format

                # Require queue when using --message
                if queue is None:
                    parser.error("--message requires a queue name")

            return commands.cmd_delete(db_path_str, queue, message_id_str)
        elif args.command == "move":
            # Get arguments
            all_messages = getattr(args, "all", False)
            json_output = getattr(args, "json", False)
            show_timestamps = getattr(args, "timestamps", False)
            message_id_str = getattr(args, "message_id", None)
            since_str = getattr(args, "since", None)

            # Validate message_id format early (fail fast)
            if message_id_str is not None:
                if (
                    len(message_id_str) != TIMESTAMP_EXACT_NUM_DIGITS
                    or not message_id_str.isdigit()
                ):
                    return commands.EXIT_QUEUE_EMPTY  # Return 2 for invalid format

                # Check mutual exclusivity
                if since_str:
                    parser.error("--message cannot be used with --since")

            return commands.cmd_move(
                db_path_str,
                args.source_queue,
                args.dest_queue,
                all_messages=all_messages,
                json_output=json_output,
                show_timestamps=show_timestamps,
                message_id_str=message_id_str,
                since_str=since_str,
            )
        elif args.command == "broadcast":
            return commands.cmd_broadcast(db_path_str, args.message)
        elif args.command == "watch":
            since_str = getattr(args, "since", None)
            move_to = getattr(args, "move", None)
            return commands.cmd_watch(
                db_path_str,
                args.queue,
                args.peek,
                args.json,
                args.timestamps,
                since_str,
                args.quiet,
                move_to,
            )

        return 0

    except ValueError as e:
        print(f"{PROG_NAME}: error: {e}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        # Handle Ctrl-C gracefully
        print(f"\n{PROG_NAME}: interrupted", file=sys.stderr)
        return 0
    except Exception as e:
        if not args.quiet:
            print(f"{PROG_NAME}: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
