"""
Copyright (C) 2025, Jabez Winston C

Command completion support for Docuver CLI

Author  : Jabez Winston C <jabezwinston@gmail.com>
License : MIT
Date    : 10 Aug 2025

"""

from pathlib import Path
from typing import List
from .core import OFFICE_EXTENSIONS

def complete_office_files(prefix: str, parsed_args, **kwargs) -> List[str]:
    """Complete Office document filenames"""
    current_dir = Path('.')
    matches = []
    
    for file_path in current_dir.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in OFFICE_EXTENSIONS:
            if file_path.name.startswith(prefix):
                matches.append(file_path.name)
    
    return matches

def complete_office_folders(prefix: str, parsed_args, **kwargs) -> List[str]:
    """Complete Office document folder names (ending with 'f')"""
    current_dir = Path('.')
    matches = []
    
    for item in current_dir.iterdir():
        if item.is_dir() and any(item.name.endswith(ext + 'f') for ext in OFFICE_EXTENSIONS):
            if item.name.startswith(prefix):
                matches.append(item.name)
    
    return matches

def generate_bash_completion() -> str:
    """Generate bash completion script"""
    return '''#!/bin/bash
# Bash completion for docuver

_docuver_completions() {
    local cur prev words cword
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    words=("${COMP_WORDS[@]}")
    cword=$COMP_CWORD

    # Main commands
    local commands="init sync track cleanup status completions"
    
    # If we're completing the first argument (command)
    if [[ $cword -eq 1 ]]; then
        COMPREPLY=($(compgen -W "$commands" -- "$cur"))
        return 0
    fi

    # Command-specific completions
    case "${words[1]}" in
        sync)
            # Complete with both Office document files and folders
            local office_files=$(find . -maxdepth 1 -type f \\( -name "*.docx" -o -name "*.xlsx" -o -name "*.pptx" -o -name "*.odt" -o -name "*.ods" -o -name "*.odp" \\) -printf "%f\\n" 2>/dev/null)
            COMPREPLY=($(compgen -W "$office_files" -- "$cur"))
            ;;
        track)
            # Complete with Office document files
            local office_files=$(find . -maxdepth 1 -type f \\( -name "*.docx" -o -name "*.xlsx" -o -name "*.pptx" -o -name "*.odt" -o -name "*.ods" -o -name "*.odp" \\) -printf "%f\\n" 2>/dev/null)
            COMPREPLY=($(compgen -W "$office_files" -- "$cur"))
            ;;
        init|cleanup|status|completions)
            # These commands don't take arguments
            COMPREPLY=()
            ;;
        *)
            # Default file completion
            COMPREPLY=($(compgen -f -- "$cur"))
            ;;
    esac
}

# Register the completion function
complete -F _docuver_completions docuver
'''

def generate_zsh_completion() -> str:
    """Generate zsh completion script"""
    return '''#compdef docuver

# Zsh completion for docuver

_docuver() {
    local context state line
    typeset -A opt_args

    _arguments -C \\
        '1: :_docuver_commands' \\
        '*: :_docuver_args' && return 0

    case $state in
        (args)
            case $words[2] in
                (sync)
                    _docuver_office_files
                    ;;
                (init|prepare|cleanup|status)
                    # No arguments for these commands
                    ;;
            esac
            ;;
    esac
}

_docuver_commands() {
    local commands
    commands=(
        'init:Initialize docuver in current directory'
        'sync:Smart sync - extract file or pack folder with safety checks'
        'track:Track a specific Office document for version control'
        'cleanup:Remove binary Office files (keep folders)'
        'status:Show status of Office files and folders'
        'completions:Install shell completions'
    )
    _describe 'commands' commands
}

_docuver_office_files() {
    local office_files
    office_files=($(find . -maxdepth 1 -type f \\( -name "*.docx" -o -name "*.xlsx" -o -name "*.pptx" -o -name "*.odt" -o -name "*.ods" -o -name "*.odp" \\) -printf "%f\\n" 2>/dev/null))
    _describe 'office files' office_files
}

_docuver_office_folders() {
    local office_folders
    office_folders=($(find . -maxdepth 1 -type d \\( -name "*.docxf" -o -name "*.xlsxf" -o -name "*.pptxf" -o -name "*.odtf" -o -name "*.odsf" -o -name "*.odpf" \\) | sed 's|^\\./||' 2>/dev/null))
    _describe 'office folders' office_folders
}

_docuver_args() {
    case $words[2] in
        (sync)
            # Complete with both files and folders for sync
            local office_files
            local office_folders
            office_files=($(find . -maxdepth 1 -type f \\( -name "*.docx" -o -name "*.xlsx" -o -name "*.pptx" -o -name "*.odt" -o -name "*.ods" -o -name "*.odp" \\) -printf "%f\\n" 2>/dev/null))
            office_folders=($(find . -maxdepth 1 -type d \\( -name "*.docxf" -o -name "*.xlsxf" -o -name "*.pptxf" -o -name "*.odtf" -o -name "*.odsf" -o -name "*.odpf" \\) | sed 's|^\\./||' 2>/dev/null))
            _describe 'targets' office_files office_folders
            ;;
        (track)
            _docuver_office_files
            ;;
    esac
}

_docuver "$@"
'''

def generate_fish_completion() -> str:
    """Generate fish completion script"""
    return '''# Fish completion for docuver

# Main commands
complete -c docuver -f
complete -c docuver -n '__fish_use_subcommand' -a 'init' -d 'Initialize docuver in current directory'
complete -c docuver -n '__fish_use_subcommand' -a 'sync' -d 'Smart sync - extract file or pack folder with safety checks'
complete -c docuver -n '__fish_use_subcommand' -a 'track' -d 'Track a specific Office document for version control'
complete -c docuver -n '__fish_use_subcommand' -a 'cleanup' -d 'Remove binary Office files (keep folders)'
complete -c docuver -n '__fish_use_subcommand' -a 'status' -d 'Show status of Office files and folders'
complete -c docuver -n '__fish_use_subcommand' -a 'completions' -d 'Install shell completions'

# Command-specific completions
complete -c docuver -n '__fish_seen_subcommand_from sync' -a '(__fish_complete_suffix .docx .xlsx .pptx .odt .ods .odp)' -d 'Office document'
complete -c docuver -n '__fish_seen_subcommand_from sync' -a '(find . -maxdepth 1 -type d \\( -name "*.docxf" -o -name "*.xlsxf" -o -name "*.pptxf" -o -name "*.odtf" -o -name "*.odsf" -o -name "*.odpf" \\) | sed "s|^\\./||" 2>/dev/null)' -d 'Office folder'
complete -c docuver -n '__fish_seen_subcommand_from track' -a '(__fish_complete_suffix .docx .xlsx .pptx .odt .ods .odp)' -d 'Office document'
'''

def _update_shell_config(config_file: Path, source_line: str, marker: str) -> bool:
    """Update shell configuration file to source completion script"""
    try:
        # Read existing config
        if config_file.exists():
            with open(config_file, 'r') as f:
                content = f.read()
        else:
            content = ""
        
        # Check if already configured
        if marker in content:
            return False  # Already configured
        
        # Add completion source line
        if content and not content.endswith('\n'):
            content += '\n'
        
        content += f'\n# {marker}\n{source_line}\n'
        
        # Write back to config file
        with open(config_file, 'w') as f:
            f.write(content)
        
        return True
    except Exception as e:
        print(f" Warning: Could not update {config_file}: {e}")
        return False

def install_completions() -> None:
    home = Path.home()
    installed_shells = []
    
    # Bash completion
    bash_completion_dir = home / '.bash_completion.d'
    bash_completion_dir.mkdir(exist_ok=True)
    
    bash_script = bash_completion_dir / 'docuver'
    with open(bash_script, 'w') as f:
        f.write(generate_bash_completion())
    
    print(f"✓ Installed bash completion: {bash_script}")
    
    # Update bash configuration files
    bash_configs = [home / '.bashrc', home / '.bash_profile']
    source_line = f'source "{bash_script}"'
    marker = "Docuver completion"
    
    for config_file in bash_configs:
        if config_file.exists():
            if _update_shell_config(config_file, source_line, marker):
                print(f"✓ Updated {config_file} to load completions automatically")
                installed_shells.append("bash")
            break
    else:
        # If no config file exists, create .bashrc
        if _update_shell_config(home / '.bashrc', source_line, marker):
            print("✓ Created ~/.bashrc with completion loading")
            installed_shells.append("bash")
    
    # Zsh completion
    zsh_completion_dir = home / '.zsh' / 'completions'
    zsh_completion_dir.mkdir(parents=True, exist_ok=True)
    
    zsh_script = zsh_completion_dir / '_docuver'
    with open(zsh_script, 'w') as f:
        f.write(generate_zsh_completion())
    
    print(f"✓ Installed zsh completion: {zsh_script}")
    
    # Update zsh configuration
    zsh_config = home / '.zshrc'
    fpath_line = f'fpath=("{zsh_completion_dir}" $fpath)'
    autoload_line = 'autoload -U compinit && compinit'
    
    if _update_shell_config(zsh_config, f'{fpath_line}\n{autoload_line}', "Docuver completion"):
        print("✓ Updated ~/.zshrc to load completions automatically")
        installed_shells.append("zsh")
    
    # Fish completion
    fish_completion_dir = home / '.config' / 'fish' / 'completions'
    if fish_completion_dir.parent.exists() or (home / '.config' / 'fish').exists():
        fish_completion_dir.mkdir(parents=True, exist_ok=True)
        
        fish_script = fish_completion_dir / 'docuver.fish'
        with open(fish_script, 'w') as f:
            f.write(generate_fish_completion())
        
        print(f"✓ Installed fish completion: {fish_script}")
        print("✓ Fish completions are automatically loaded")
        installed_shells.append("fish")
    
    # Summary
    if installed_shells:
        print(f"\n🎉 Completions installed and configured for: {', '.join(installed_shells)}")
        print("📝 Completions will be available in new shell sessions")
        print("💡 To use in current session: restart your shell or run 'exec $SHELL'")
    else:
        print("\n⚠ No shell configurations were updated")
        print("💡 You may need to manually source the completion scripts")

if __name__ == '__main__':
    install_completions()
