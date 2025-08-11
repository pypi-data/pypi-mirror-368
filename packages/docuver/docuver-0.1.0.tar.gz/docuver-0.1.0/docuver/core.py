"""
Copyright (C) 2025, Jabez Winston C

Core functionality for Docuver - Document Version Control Tool

Author  : Jabez Winston C <jabezwinston@gmail.com>
License : MIT
Date    : 10 Aug 2025

"""

import os
import zipfile
import shutil
from pathlib import Path
from typing import List, Optional, Tuple
import json
import time
import glob
import xml.etree.ElementTree as ET
from xml.dom import minidom
import subprocess

# Supported Office document extensions
OFFICE_EXTENSIONS = {'.docx', '.xlsx', '.pptx', '.odt', '.ods', '.odp'}

class DocuverError(Exception):
    """Custom exception for Docuver operations"""
    pass

class Docuver:
    """Main class for docuver operations"""
    
    def __init__(self, base_path: Optional[str] = None):
        """Initialize Docuver instance
        
        Args:
            base_path: Base directory for operations (defaults to current directory)
        """
        self.current_path = Path(base_path) if base_path else Path.cwd()
        
        # Find the nearest .docuver directory by traversing up the directory tree
        self.base_path = self._find_docuver_root(self.current_path)
        if self.base_path:
            self.docuver_dir = self.base_path / '.docuver'
            self.gitignore_file = self.base_path / '.gitignore'
        else:
            # If no .docuver found, use current directory for init operations
            self.base_path = self.current_path
            self.docuver_dir = self.base_path / '.docuver'
            self.gitignore_file = self.base_path / '.gitignore'
        
        self.config_file = self.docuver_dir / 'config.json'
        self.metadata_file = self.docuver_dir / 'meta.json'
    
    def _find_docuver_root(self, start_path: Path) -> Optional[Path]:
        """Find the nearest .docuver directory by traversing up the directory tree
        
        Args:
            start_path: Directory to start searching from
            
        Returns:
            Path to the directory containing .docuver, or None if not found
        """
        current = start_path.resolve()
        
        # Traverse up the directory tree
        while current != current.parent:  # Stop at filesystem root
            docuver_dir = current / '.docuver'
            if docuver_dir.exists() and docuver_dir.is_dir():
                return current
            current = current.parent
        
        # Check the root directory as well
        docuver_dir = current / '.docuver'
        if docuver_dir.exists() and docuver_dir.is_dir():
            return current
        
        return None
    
    def _load_metadata(self) -> List[dict]:
        """Load centralized metadata from .docuver/meta.json"""
        if not self.metadata_file.exists():
            return []
        
        try:
            with open(self.metadata_file, 'r') as f:
                data = json.load(f)
                # Handle backward compatibility: convert old dict format to array
                if isinstance(data, dict):
                    array_data = []
                    for folder_name, metadata in data.items():
                        metadata['folder_name'] = folder_name
                        array_data.append(metadata)
                    return array_data
                return data if isinstance(data, list) else []
        except (json.JSONDecodeError, OSError):
            return []
    
    def _save_metadata(self, metadata: List[dict]) -> None:
        """Save centralized metadata to .docuver/meta.json"""
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
        except OSError as e:
            raise DocuverError(f"Failed to save metadata: {e}")
    
    def _get_folder_metadata(self, folder_name: str) -> Optional[dict]:
        """Get metadata for a specific folder"""
        all_metadata = self._load_metadata()
        for entry in all_metadata:
            if entry.get('folder_name') == folder_name:
                return entry
        return None
    
    def _set_folder_metadata(self, folder_name: str, metadata: dict) -> None:
        """Set metadata for a specific folder"""
        all_metadata = self._load_metadata()
        metadata['folder_name'] = folder_name
        
        # Remove existing entry if it exists
        all_metadata = [entry for entry in all_metadata if entry.get('folder_name') != folder_name]
        
        # Add new entry
        all_metadata.append(metadata)
        self._save_metadata(all_metadata)
    
    def _remove_folder_metadata(self, folder_name: str) -> None:
        """Remove metadata for a specific folder"""
        all_metadata = self._load_metadata()
        all_metadata = [entry for entry in all_metadata if entry.get('folder_name') != folder_name]
        self._save_metadata(all_metadata)
    
    def _migrate_old_metadata(self) -> None:
        """Migrate old .docuver_meta.json files to centralized metadata"""
        migrated_count = 0
        for item in self.base_path.iterdir():
            if item.is_dir() and any(item.name.endswith(ext + 'f') for ext in OFFICE_EXTENSIONS):
                old_meta_file = item / ".docuver_meta.json"
                if old_meta_file.exists():
                    try:
                        with open(old_meta_file, 'r') as f:
                            metadata = json.load(f)
                        self._set_folder_metadata(item.name, metadata)
                        old_meta_file.unlink()  # Remove old metadata file
                        migrated_count += 1
                    except (json.JSONDecodeError, OSError) as e:
                        print(f"⚠ Warning: Could not migrate metadata for {item.name}: {e}")
        
        if migrated_count > 0:
            print(f"✓ Migrated {migrated_count} metadata file(s) to centralized storage")
    
    def _format_xml_files(self, folder_path: Path) -> int:
        """Format all XML files in the extracted folder for better readability
        
        Args:
            folder_path: Path to the extracted Office document folder
            
        Returns:
            Number of XML files formatted
        """
        formatted_count = 0
        
        # Find all XML files in the folder
        for xml_file in folder_path.rglob('*.xml'):
            try:
                # Read the XML file
                with open(xml_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Parse and format the XML
                try:
                    # Parse the XML
                    root = ET.fromstring(content)
                    
                    # Convert to pretty-printed XML
                    rough_string = ET.tostring(root, encoding='unicode')
                    reparsed = minidom.parseString(rough_string)
                    pretty_xml = reparsed.toprettyxml(indent='  ')
                    
                    # Remove empty lines and fix formatting
                    lines = [line for line in pretty_xml.split('\n') if line.strip()]
                    formatted_content = '\n'.join(lines)
                    
                    # Write back the formatted XML
                    with open(xml_file, 'w', encoding='utf-8') as f:
                        f.write(formatted_content)
                    
                    formatted_count += 1
                    
                except ET.ParseError:
                    # Skip files that aren't valid XML
                    continue
                    
            except (OSError, UnicodeDecodeError):
                # Skip files that can't be read
                continue
        
        return formatted_count
    
    def _is_git_repo(self) -> bool:
        """Check if current directory is a Git repository"""
        try:
            result = subprocess.run(['git', 'rev-parse', '--git-dir'], 
                                  capture_output=True, text=True, cwd=self.base_path)
            return result.returncode == 0
        except FileNotFoundError:
            return False
    
    def _init_git_repo(self) -> bool:
        """Initialize a Git repository in the current directory"""
        try:
            result = subprocess.run(['git', 'init'], 
                                  capture_output=True, text=True, cwd=self.base_path)
            if result.returncode == 0:
                print("✓ Initialized Git repository")
                return True
            else:
                print(f"⚠ Failed to initialize Git repository: {result.stderr.strip()}")
                return False
        except FileNotFoundError:
            print("⚠ Git not found - please install Git to enable version control features")
            return False
    
    def _git_add(self, path: str) -> bool:
        """Add a file or directory to Git staging area"""
        try:
            # Convert path to be relative to the Git repository root
            path_obj = Path(path)
            if not path_obj.is_absolute():
                # If it's a relative path, make it relative to current working directory first
                path_obj = self.current_path / path_obj
            
            # Now make it relative to the Git repository root (base_path)
            try:
                relative_path = path_obj.relative_to(self.base_path)
                git_path = str(relative_path)
            except ValueError:
                # Path is outside the Git repository, use absolute path
                git_path = str(path_obj)
            
            result = subprocess.run(['git', 'add', git_path], 
                                  capture_output=True, text=True, cwd=self.base_path)
            if result.returncode == 0:
                return True
            else:
                print(f"⚠ Failed to add {git_path} to Git: {result.stderr.strip()}")
                return False
        except FileNotFoundError:
            print("⚠ Git not found - skipping Git add")
            return False
        
    def init(self) -> None:
        """Initialize docuver in the current directory"""
        docuver_dir = self.base_path / ".docuver"
        docuver_dir.mkdir(exist_ok=True)
        
        # Create default config
        config = {
            "version": "1.0",
            "auto_extract": True,
            "auto_cleanup": False,
            "supported_extensions": list(OFFICE_EXTENSIONS)
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        # Update .gitignore to exclude binary Office files
        self._update_gitignore()
        
        print(f"✓ Initialized docuver in {self.base_path}")
        print("✓ Updated .gitignore to exclude Office binary files")
        
        # Initialize Git repository if not already initialized
        if not self._is_git_repo():
            self._init_git_repo()
        else:
            print("ℹ️  Git repository already exists")
        
        # Migrate any existing old metadata files
        self._migrate_old_metadata()
    
    def _update_gitignore(self) -> None:
        """Update .gitignore to exclude Office binary files"""
        gitignore_content = []
        
        if self.gitignore_file.exists():
            with open(self.gitignore_file, 'r') as f:
                gitignore_content = f.read().splitlines()
        
        # Add docuver section if not present
        docuver_section = "# Docuver - Office document binaries"
        if docuver_section not in gitignore_content:
            if gitignore_content and gitignore_content[-1] != "":
                gitignore_content.append("")
            
            gitignore_content.extend([
                docuver_section,
                "*.docx",
                "*.xlsx", 
                "*.pptx",
                "*.odt",
                "*.ods",
                "*.odp"
            ])
            
            with open(self.gitignore_file, 'w') as f:
                f.write('\n'.join(gitignore_content) + '\n')
    
    def extract(self, file_path: str, format_xml: bool = True) -> str:
        """Extract an Office document to a folder"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise DocuverError(f"File not found: {file_path}")
        
        if file_path.suffix.lower() not in OFFICE_EXTENSIONS:
            raise DocuverError(f"Unsupported file type: {file_path.suffix}")
        
        # Create folder name by appending 'f' to extension
        folder_name = file_path.name + 'f'
        folder_path = file_path.parent / folder_name
        
        # Remove existing folder if it exists
        if folder_path.exists():
            shutil.rmtree(folder_path)
        
        folder_path.mkdir()
        
        # Extract ZIP contents
        try:
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(folder_path)
        except zipfile.BadZipFile:
            shutil.rmtree(folder_path)
            raise DocuverError(f"Invalid or corrupted Office document: {file_path}")
        
        # Store metadata centrally in .docuver/meta.json
        # Calculate relative path from project root for the original file
        try:
            relative_file_path = file_path.relative_to(self.base_path)
            original_file_path = str(relative_file_path)
        except ValueError:
            # File is outside project root, use absolute path
            original_file_path = str(file_path)
        
        metadata = {
            "original_file": original_file_path,
            "extracted_at": time.time(),
            "file_size": file_path.stat().st_size,
        }
        
        self._set_folder_metadata(folder_name, metadata)
        
        # Format XML files for better readability and version control
        if format_xml:
            formatted_count = self._format_xml_files(folder_path)
            if formatted_count > 0:
                print(f"📝 Formatted {formatted_count} XML file(s) for better readability")
        
        print(f"✓ Extracted {file_path.name} → {folder_name}/")
        return str(folder_path)
    
    def pack(self, folder_path: str) -> str:
        """Pack a folder back into an Office document"""
        folder_path = Path(folder_path)
        
        if not folder_path.exists() or not folder_path.is_dir():
            raise DocuverError(f"Folder not found: {folder_path}")
        
        # Determine original filename from folder name or centralized metadata
        if folder_path.name.endswith('f') and len(folder_path.name) > 1:
            original_name = folder_path.name[:-1]  # Remove trailing 'f'
            output_path = folder_path.parent / original_name
        else:
            # Try to get from centralized metadata
            metadata = self._get_folder_metadata(folder_path.name)
            if metadata and "original_file" in metadata:
                # original_file now contains the full relative path from project root
                original_file_path = self.base_path / metadata["original_file"]
                output_path = original_file_path
            else:
                raise DocuverError(f"Cannot determine original filename for {folder_path}")
        
        # Create ZIP file (no need to skip metadata files since they're now centralized)
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zip_ref:
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(folder_path)
                    zip_ref.write(file_path, arcname)
        
        print(f"✓ Packed {folder_path.name}/ → {original_name}")
        return str(output_path)
    
    def track(self, filename: str, force: bool = False, format_xml: bool = True) -> str:
        """Track Office document(s) for version control with wildcard support and safety checks
        
        Args:
            filename: Office document file or wildcard pattern to track
            force: Skip safety checks and force the operation
            format_xml: Whether to format XML files for better readability
            
        Returns:
            Summary message of tracking results
        """
        # Check for wildcard patterns
        if '*' in filename or '?' in filename or '[' in filename:
            return self._track_wildcard(filename, force, format_xml)
        else:
            return self._track_single_file(filename, force, format_xml)
    
    def _track_single_file(self, filename: str, force: bool = False, format_xml: bool = True) -> str:
        """Track a single Office document for version control with safety checks"""
        file_path = Path(filename)
        
        # Make path absolute if relative (relative to current working directory, not project root)
        if not file_path.is_absolute():
            file_path = self.current_path / file_path
        
        # Check if file exists
        if not file_path.exists():
            raise DocuverError(f"File not found: {filename}")
        
        # Check if it's an Office document
        if not file_path.is_file() or file_path.suffix.lower() not in OFFICE_EXTENSIONS:
            raise DocuverError(f"Not an Office document: {filename}. Supported formats: {', '.join(OFFICE_EXTENSIONS)}")
        
        # Check if corresponding folder already exists
        folder_name = file_path.name + 'f'
        folder_path = file_path.parent / folder_name
        
        if folder_path.exists():
            print(f"ℹ️  Folder {folder_name}/ already exists")
            
            # Safety checks (unless forced)
            if not force:
                # Check for lock files
                is_locked, lock_files = self._is_file_being_edited(file_path)
                if is_locked:
                    raise DocuverError(f"File appears to be open in an editor (lock files found):\n  {', '.join(lock_files)}\nUse --force to override")
                
                # Check modification times
                time_comparison = self._compare_modification_times(file_path, folder_path)
                if time_comparison == "folder_newer":
                    raise DocuverError(f"Folder {folder_name}/ is newer than {file_path.name}. This would overwrite newer changes.\nUse --force to override or check your changes first")
                elif time_comparison == "same":
                    print(f"ℹ️  {file_path.name} and {folder_name}/ have the same modification time")
                elif time_comparison == "file_newer":
                    print(f"📄 {file_path.name} is newer than {folder_name}/ - updating folder")
        else:
            # Safety check for lock files even on first extraction
            if not force:
                is_locked, lock_files = self._is_file_being_edited(file_path)
                if is_locked:
                    raise DocuverError(f"File appears to be open in an editor (lock files found):\n  {', '.join(lock_files)}\nUse --force to override")
        
        # Perform extraction
        try:
            folder_path_str = self.extract(str(file_path), format_xml)
            folder_name = Path(folder_path_str).name
            print(f"✓ Tracking {file_path.name} → {folder_name}/")
            
            # Automatically add extracted folder to Git if in a Git repository
            if self._is_git_repo():
                # Use the full path to the extracted folder for Git add
                folder_full_path = Path(folder_path_str)
                if self._git_add(str(folder_full_path)):
                    print(f"✓ Added {folder_name}/ to Git staging area")
                # Also add .docuver metadata (use absolute path to the actual .docuver directory)
                if self._git_add(str(self.docuver_dir)):
                    print("✓ Added .docuver/ metadata to Git staging area")
            else:
                print("ℹ️  Not in a Git repository - skipping Git add")
            
            return folder_path_str
        except DocuverError as e:
            raise DocuverError(f"Failed to track {file_path.name}: {e}")
    
    def _track_wildcard(self, pattern: str, force: bool = False, format_xml: bool = True) -> str:
        """Track multiple Office documents using wildcard patterns"""
        # Use glob to find matching files
        if Path(pattern).is_absolute():
            matches = list(Path().glob(pattern))
        else:
            matches = list(self.current_path.glob(pattern))
        
        # Filter to only Office documents
        office_files = []
        for match in matches:
            if match.is_file() and match.suffix.lower() in OFFICE_EXTENSIONS:
                office_files.append(match)
        
        if not office_files:
            raise DocuverError(f"No Office documents found matching pattern: {pattern}")
        
        print(f"Found {len(office_files)} Office document(s) matching pattern: {pattern}")
        print("=" * 60)
        
        tracked_count = 0
        skipped_count = 0
        
        # Track each file
        for file_path in sorted(office_files):
            try:
                print(f"\n📄 Tracking {file_path.name}...")
                self._track_single_file(str(file_path), force, format_xml)
                tracked_count += 1
            except DocuverError as e:
                print(f"⚠ Skipped {file_path.name}: {e}")
                skipped_count += 1
        
        # Summary
        print("\n" + "=" * 60)
        print(f"Tracking completed: {tracked_count} successful, {skipped_count} skipped")
        
        if skipped_count > 0 and not force:
            print("💡 Use --force to override safety checks for skipped files")
        
        return f"Tracked {tracked_count} file(s) from pattern: {pattern}"
    
    def track_multiple(self, filenames: List[str], force: bool = False, format_xml: bool = True) -> str:
        """Track multiple Office documents (from shell-expanded wildcards)"""
        # Filter to only Office documents
        office_files = []
        for filename in filenames:
            file_path = Path(filename)
            if not file_path.is_absolute():
                file_path = self.current_path / file_path
            
            if file_path.is_file() and file_path.suffix.lower() in OFFICE_EXTENSIONS:
                office_files.append(file_path)
        
        if not office_files:
            raise DocuverError("No Office documents found in the provided files")
        
        print(f"Found {len(office_files)} Office document(s) to track")
        print("=" * 60)
        
        tracked_count = 0
        skipped_count = 0
        
        # Track each file
        for file_path in sorted(office_files):
            try:
                print(f"\n📄 Tracking {file_path.name}...")
                self._track_single_file(str(file_path), force, format_xml)
                tracked_count += 1
            except DocuverError as e:
                print(f"⚠ Skipped {file_path.name}: {e}")
                skipped_count += 1
        
        # Summary
        print("\n" + "=" * 60)
        print(f"Tracking completed: {tracked_count} successful, {skipped_count} skipped")
        
        if skipped_count > 0 and not force:
            print("💡 Use --force to override safety checks for skipped files")
        
        return f"Tracked {tracked_count} file(s) from {len(filenames)} provided files"
    
    def sync_multiple(self, targets: List[str], force: bool = False, format_xml: bool = True) -> str:
        """Sync multiple Office documents or extracted folders (supports wildcards)"""
        # Expand wildcards and collect all valid targets
        all_targets = []
        for target in targets:
            if any(char in target for char in ['*', '?', '[']):
                # This is a wildcard pattern
                if Path(target).is_absolute():
                    matching_files = glob.glob(target)
                else:
                    matching_files = glob.glob(str(self.base_path / target))
                all_targets.extend(matching_files)
            else:
                # Regular file/folder path
                if Path(target).is_absolute():
                    all_targets.append(target)
                else:
                    all_targets.append(str(self.base_path / target))
        
        if not all_targets:
            raise DocuverError("No files or folders found matching the provided patterns")
        
        # Remove duplicates and sort
        all_targets = sorted(set(all_targets))
        
        # Filter to only valid Office documents or extracted folders
        valid_targets = []
        for target_path_str in all_targets:
            target_path = Path(target_path_str)
            if target_path.exists():
                if (target_path.is_file() and target_path.suffix.lower() in OFFICE_EXTENSIONS) or \
                   (target_path.is_dir() and any(target_path.name.endswith(ext + 'f') for ext in OFFICE_EXTENSIONS)):
                    valid_targets.append(target_path_str)
        
        if not valid_targets:
            raise DocuverError("No valid Office documents or extracted folders found")
        
        print(f"Found {len(valid_targets)} target(s) to sync")
        print("=" * 60)
        
        synced_count = 0
        skipped_count = 0
        
        # Sync each target
        for target in valid_targets:
            try:
                target_path = Path(target)
                print(f"\n📄 Syncing {target_path.name}...")
                result = self.sync(target, force, format_xml)
                print(f"✓ {result}")
                synced_count += 1
            except DocuverError as e:
                print(f"⚠ Skipped {Path(target).name}: {e}")
                skipped_count += 1
        
        # Summary
        print("\n" + "=" * 60)
        print(f"Sync completed: {synced_count} successful, {skipped_count} skipped")
        
        if skipped_count > 0 and not force:
            print("💡 Use --force to override safety checks for skipped files")
        
        return f"Synced {synced_count} target(s) from {len(targets)} provided patterns"
    
    def cleanup(self, force: bool = False) -> List[str]:
        """Remove binary Office files (keep extracted folders) with safety checks
        
        Updates extracted folders with latest content from binary files before removal.
        Uses metadata from meta.json to find tracked Office documents.
        Includes comprehensive safety checks to prevent data loss.
        
        Args:
            force: Skip safety checks and force the operation
        """
        removed = []
        updated = []
        skipped = []
        
        # Load metadata to find all tracked Office documents
        metadata = self._load_metadata()
        if not metadata:
            print("No tracked Office documents found in metadata")
            return removed
        
        print(f"Found {len(metadata)} tracked Office document(s) in metadata")
        
        for entry in metadata:
            original_file = entry.get('original_file')
            folder_name = entry.get('folder_name')
            
            if not original_file or not folder_name:
                print("⚠ Skipped entry with missing file or folder information")
                continue
            
            # Construct paths relative to project root
            file_path = self.base_path / original_file
            folder_path = self.base_path / Path(original_file).parent / folder_name
            
            # Check if binary file exists
            if not file_path.exists():
                print(f"⚠ Skipped {original_file} (binary file not found)")
                skipped.append(str(file_path))
                continue
                
            # Check if corresponding folder exists
            if not folder_path.exists():
                print(f"⚠ Skipped {original_file} (no corresponding folder found)")
                skipped.append(str(file_path))
                continue
                
            # Safety checks (unless forced)
            if not force:
                # Check for lock files
                is_locked, lock_files = self._is_file_being_edited(file_path)
                if is_locked:
                    print(f"🔒 Skipped {file_path.name} (file appears to be open in an editor)")
                    print(f"    Lock files found: {', '.join(lock_files)}")
                    print("    Use --force to override this safety check")
                    skipped.append(str(file_path))
                    continue
                
                # Check modification times
                time_comparison = self._compare_modification_times(file_path, folder_path)
                if "folder is newer" in time_comparison:
                    print(f"⚠ Warning for {original_file}:")
                    print(f"    {time_comparison}")
                    print("    Proceeding will overwrite newer folder content with older file content")
                    print("    Use --force to override this safety check")
                    skipped.append(str(file_path))
                    continue
                elif "file is newer" in time_comparison:
                    print(f"ℹ {original_file}: {time_comparison}")
            
            # Update folder with latest content from binary file
            try:
                print(f"🔄 Updating {folder_name}/ with latest content from {original_file}")
                self.extract(str(file_path))
                updated.append(str(folder_path))
                
                # Automatically add updated folder to Git if in a Git repository
                if self._is_git_repo():
                    if self._git_add(str(folder_path)):
                        print(f"✓ Added updated {folder_name}/ to Git staging area")
                
                # Remove binary file after successful update
                file_path.unlink()
                removed.append(str(file_path))
                print(f"✓ Removed {original_file} (folder {folder_name}/ updated)")
            except DocuverError as e:
                print(f"⚠ Failed to update {folder_name}/ from {original_file}: {e}")
                print(f"⚠ Skipped removal of {original_file}")
                skipped.append(str(file_path))
        
        # Summary
        if updated:
            print(f"\n🔄 Updated {len(updated)} folder(s) with latest content")
        if removed:
            print(f"✓ Cleaned up {len(removed)} binary Office file(s)")
        if skipped:
            print(f"⚠ Skipped {len(skipped)} file(s) due to safety checks or errors")
            if not force:
                print("   Use --force to override safety checks")
        if not removed and not skipped:
            print("No binary Office files to clean up")
        
        return removed
    
    def _check_lock_files(self, base_path: Path) -> List[str]:
        """Check for Office lock files in the directory"""
        lock_patterns = [
            '.~lock.*#',  # LibreOffice/OpenOffice lock files
            '~$*',        # Microsoft Office temporary files
            '.tmp',       # General temporary files
        ]
        
        lock_files = []
        for pattern in lock_patterns:
            lock_files.extend(glob.glob(str(base_path / pattern)))
        
        return lock_files
    
    def _is_file_being_edited(self, file_path: Path) -> Tuple[bool, List[str]]:
        """Check if a file is currently being edited (has lock files)"""
        base_name = file_path.stem
        parent_dir = file_path.parent
        
        # Check for various lock file patterns
        lock_patterns = [
            f'.~lock.{base_name}.*#',  # LibreOffice pattern
            f'~${base_name}*',         # Microsoft Office pattern
            f'{base_name}.tmp',        # General temp pattern
        ]
        
        found_locks = []
        for pattern in lock_patterns:
            matches = list(parent_dir.glob(pattern))
            found_locks.extend([str(m) for m in matches])
        
        return len(found_locks) > 0, found_locks
    
    def _compare_modification_times(self, file_path: Path, folder_path: Path) -> str:
        """Compare modification times between file and folder to determine which is newer"""
        if not file_path.exists() or not folder_path.exists():
            return "unknown"
        
        file_mtime = file_path.stat().st_mtime
        
        # Get the newest modification time from the folder contents
        folder_mtime = folder_path.stat().st_mtime
        for item in folder_path.rglob('*'):
            if item.is_file() and not item.name.startswith('.docuver'):
                item_mtime = item.stat().st_mtime
                folder_mtime = max(folder_mtime, item_mtime)
        
        if file_mtime > folder_mtime + 1:  # 1 second tolerance
            return "file_newer"
        elif folder_mtime > file_mtime + 1:
            return "folder_newer"
        else:
            return "same"
    
    def sync(self, target: str, force: bool = False, format_xml: bool = True) -> str:
        """Smart sync command that automatically extracts or packs based on input and safety checks
        
        Args:
            target: Either an Office document file or extracted folder
            force: Skip safety checks and force the operation
            
        Returns:
            String describing the operation performed
        """
        target_path = Path(target)
        
        # Make path absolute if relative (relative to current working directory)
        if not target_path.is_absolute():
            target_path = self.current_path / target_path
        
        if not target_path.exists():
            raise DocuverError(f"Target not found: {target}")
        
        # Determine operation based on input type
        if target_path.is_file() and target_path.suffix.lower() in OFFICE_EXTENSIONS:
            # Input is an Office file - extract it
            return self._sync_extract(target_path, force, format_xml)
        elif target_path.is_dir() and any(target_path.name.endswith(ext + 'f') for ext in OFFICE_EXTENSIONS):
            # Input is an extracted folder - pack it
            return self._sync_pack(target_path, force)
        else:
            raise DocuverError(f"Invalid target: {target}. Must be an Office document or extracted folder ending with 'f'")
    
    def _sync_extract(self, file_path: Path, force: bool = False, format_xml: bool = True) -> str:
        """Extract an Office file with safety checks"""
        folder_name = file_path.name + 'f'
        folder_path = file_path.parent / folder_name
        
        # Check for lock files
        is_locked, lock_files = self._is_file_being_edited(file_path)
        if is_locked and not force:
            lock_list = '\n  '.join(lock_files)
            raise DocuverError(f"File appears to be open in an editor (lock files found):\n  {lock_list}\nUse --force to override")
        
        # If folder exists, check modification times
        if folder_path.exists():
            time_comparison = self._compare_modification_times(file_path, folder_path)
            
            if time_comparison == "folder_newer" and not force:
                raise DocuverError(f"Folder {folder_name}/ is newer than {file_path.name}. This would overwrite newer changes.\nUse --force to override or check your changes first")
            elif time_comparison == "same":
                print(f"ℹ️  {file_path.name} and {folder_name}/ have the same modification time")
            elif time_comparison == "file_newer":
                print(f"📄 {file_path.name} is newer than {folder_name}/ - updating folder")
        
        # Perform extraction
        result_path = self.extract(str(file_path), format_xml)
        
        # Automatically add extracted folder to Git if in a Git repository
        folder_name = Path(result_path).name
        if self._is_git_repo():
            # Use the full path to the extracted folder for Git add
            folder_full_path = Path(result_path)
            if self._git_add(str(folder_full_path)):
                print(f"✓ Added {folder_name}/ to Git staging area")
            # Also add .docuver metadata (use absolute path to the actual .docuver directory)
            if self._git_add(str(self.docuver_dir)):
                print("✓ Added .docuver/ metadata to Git staging area")
        
        return f"extracted:{result_path}"
    
    def _sync_pack(self, folder_path: Path, force: bool) -> str:
        """Pack a folder with safety checks"""
        if folder_path.name.endswith('f') and len(folder_path.name) > 1:
            original_name = folder_path.name[:-1]
            file_path = folder_path.parent / original_name
        else:
            # Try to get from centralized metadata
            metadata = self._get_folder_metadata(folder_path.name)
            if metadata and "original_file" in metadata:
                # original_file now contains the full relative path from project root
                original_file_path = self.base_path / metadata["original_file"]
                file_path = original_file_path
            else:
                raise DocuverError(f"Cannot determine original filename for {folder_path}")
        
        # Check for lock files that would affect the target file
        if file_path.exists():
            is_locked, lock_files = self._is_file_being_edited(file_path)
            if is_locked and not force:
                lock_list = '\n  '.join(lock_files)
                raise DocuverError(f"Target file appears to be open in an editor (lock files found):\n  {lock_list}\nUse --force to override")
        
        # Check modification times if file exists
        if file_path.exists():
            time_comparison = self._compare_modification_times(file_path, folder_path)
            
            if time_comparison == "file_newer" and not force:
                raise DocuverError(f"File {original_name} is newer than {folder_path.name}/. This would overwrite newer changes.\nUse --force to override or extract the file first")
            elif time_comparison == "same":
                print(f"ℹ️  {folder_path.name}/ and {original_name} have the same modification time")
            elif time_comparison == "folder_newer":
                print(f"📁 {folder_path.name}/ is newer than {original_name} - updating file")
        
        # Perform packing
        result_path = self.pack(str(folder_path))
        return f"packed:{result_path}"
    

    def status(self) -> None:
        """Show status of Office files and folders"""
        files = []
        folders = []
        
        # Find all Office documents and extracted folders in current working directory
        for item in self.current_path.iterdir():
            if item.is_file() and item.suffix.lower() in OFFICE_EXTENSIONS:
                files.append(item)
            elif item.is_dir() and any(item.name.endswith(ext + 'f') for ext in OFFICE_EXTENSIONS):
                folders.append(item)
        
        print("Docuver Status:")
        print("=" * 50)
        
        if files:
            print(f"\nBinary Office Files ({len(files)}):")
            for file_path in sorted(files):
                folder_name = file_path.name + 'f'
                folder_exists = (file_path.parent / folder_name).exists()
                status_icon = "📄" if folder_exists else "❌"
                print(f"  {status_icon} {file_path.name}")
        
        if folders:
            print(f"\nExtracted Folders ({len(folders)}):")
            for folder_path in sorted(folders):
                if folder_path.name.endswith('f'):
                    original_name = folder_path.name[:-1]
                    file_exists = (folder_path.parent / original_name).exists()
                    status_icon = "📁" if file_exists else "✓"
                    print(f"  {status_icon} {folder_path.name}/")
        
        if not files and not folders:
            print("  No Office documents or extracted folders found")
        
        print("\nLegend:")
        print("  📁 = Binary file with extracted folder")
        print("  ❌ = Binary file without extracted folder")
        print("  📄 = Extracted folder with binary file")
        print("  ✓ = Extracted folder only (ready for version control)")
