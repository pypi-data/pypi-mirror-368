"""
Copyright (C) 2025, Jabez Winston C

Command-line interface for Docuver - Document Version Control Tool

Author  : Jabez Winston C <jabezwinston@gmail.com>
License : MIT
Date    : 10 Aug 2025

"""

import sys
import argparse
from pathlib import Path
from .core import Docuver, DocuverError
from .completions import install_completions, complete_office_files, complete_office_folders

def check_docuver_initialized():
    """Check if docuver is initialized in the current directory or parent directories"""
    # Try to find .docuver directory by traversing up
    current = Path.cwd().resolve()
    
    while current != current.parent:  # Stop at filesystem root
        docuver_dir = current / '.docuver'
        if docuver_dir.exists() and docuver_dir.is_dir():
            return  # Found .docuver directory
        current = current.parent
    
    # Check the root directory as well
    docuver_dir = current / '.docuver'
    if docuver_dir.exists() and docuver_dir.is_dir():
        return  # Found .docuver directory
    
    # No .docuver directory found
    print("❌ Error: Docuver not initialized in this directory or any parent directory.")
    print("   Run 'docuver init' in the project root to initialize docuver.")
    sys.exit(1)

def main():
    """Main entry point for the docuver command-line interface"""
    parser = argparse.ArgumentParser(
        description="Docuver\n\n"
                     "A meta tool for version control of Office documents (docx, xlsx, pptx, odt, ods, odp).\n"
                     "Converts binary Office files to/from extracted folder representations for proper versioning.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    # Try to enable argcomplete if available
    try:
        import argcomplete
        argcomplete.autocomplete(parser)
    except ImportError:
        pass  # argcomplete not available, continue without it
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Sync command (smart command)
    sync_parser = subparsers.add_parser('sync', help='Sync. file or pack folder (supports wildcards)')
    sync_arg = sync_parser.add_argument('target', nargs='+', help='Office document file(s), extracted folder(s), or wildcard pattern (e.g., *.docx)')
    sync_parser.add_argument('--force', '-f', action='store_true', help='Skip safety checks and force the operation')
    sync_parser.add_argument('--no-format', action='store_true', help='Skip XML formatting for better readability')
    
    # Track command
    track_parser = subparsers.add_parser('track', help='Track Office document(s) for version control (supports wildcards)')
    track_arg = track_parser.add_argument('filename', nargs='+', help='Office document file(s) or wildcard pattern to track (e.g., *.docx)')
    track_parser.add_argument('--force', '-f', action='store_true', help='Skip safety checks and force the operation')
    track_parser.add_argument('--no-format', action='store_true', help='Skip XML formatting for better readability')
    
    # Add completion support if argcomplete is available
    try:
        import argcomplete
        # Smart completion for sync command (both files and folders)
        def complete_sync_targets(prefix, parsed_args, **kwargs):
            files = complete_office_files(prefix, parsed_args, **kwargs)
            folders = complete_office_folders(prefix, parsed_args, **kwargs)
            return files + folders
        
        sync_arg.completer = complete_sync_targets
        track_arg.completer = complete_office_files
    except ImportError:
        pass
    
    # Cleanup command
    cleanup_parser = subparsers.add_parser('cleanup', help='Remove binary Office files (keep folders)')
    cleanup_parser.add_argument('--force', '-f', action='store_true', help='Skip safety checks and force the operation')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show status of Office files and folders')
    
    # Init command
    subparsers.add_parser('init', help='Initialize docuver in current directory')
    
    # Completions command
    subparsers.add_parser('completions', help='Install shell completions for docuver')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        # Commands that require docuver to be initialized
        if args.command in ['sync', 'track', 'cleanup', 'status']:
            check_docuver_initialized()
        
        docuver = Docuver()
        
        if args.command == 'init':
            docuver.init()
        elif args.command == 'sync':
            docuver.sync_multiple(args.target, args.force, not args.no_format)
        elif args.command == 'track':
            if len(args.filename) == 1:
                # Single filename (could be a wildcard pattern)
                docuver.track(args.filename[0], args.force, not args.no_format)
            else:
                # Multiple filenames (shell-expanded wildcards)
                docuver.track_multiple(args.filename, args.force, not args.no_format)
        elif args.command == 'cleanup':
            docuver.cleanup(args.force)
        elif args.command == 'status':
            docuver.status()
        elif args.command == 'completions':
            install_completions()
            
    except DocuverError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
