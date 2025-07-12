import os
import pathlib
from collections import defaultdict

def count_lines_in_file(file_path):
    """Count lines in a single file, handling encoding issues."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return len(file.readlines())
    except UnicodeDecodeError:
        # Try with different encoding for binary-like files
        try:
            with open(file_path, 'r', encoding='latin-1') as file:
                return len(file.readlines())
        except:
            return 0
    except Exception:
        return 0

def get_code_files_recursive(directory):
    """Get all code files recursively in the directory and subdirectories."""
    # Define code file extensions
    code_extensions = {
        '.py', '.js', '.jsx', '.ts', '.tsx', '.html', '.htm', '.css', '.scss',
        '.less', '.json', '.xml', '.yaml', '.yml', '.md', '.txt', '.sql',
        '.sh', '.bat', '.ps1', '.cpp', '.c', '.h', '.java', '.php', '.rb',
        '.go', '.rs', '.swift', '.kt', '.dart', '.vue', '.svelte', '.r', '.m',
        '.pl', '.scala', '.clj', '.hs', '.lua', '.vim', '.dockerfile'
    }
    
    # Directories to skip (common build/dependency folders)
    skip_dirs = {
        'node_modules', '__pycache__', '.git', '.vscode', '.idea', 'venv', 
        'env', 'build', 'dist', 'target', '.pytest_cache', 'coverage',
        '.next', '.nuxt', 'vendor', 'bower_components'
    }
    
    code_files = []
    base_path = pathlib.Path(directory)
    
    # Use rglob to recursively find all files
    for file_path in base_path.rglob('*'):
        # Skip if file is in a directory we want to ignore
        if any(skip_dir in file_path.parts for skip_dir in skip_dirs):
            continue
            
        if file_path.is_file() and file_path.suffix.lower() in code_extensions:
            code_files.append(file_path)
    
    return code_files

def main():
    # Get the directory where this script is located
    script_dir = pathlib.Path(__file__).parent.absolute()
    
    print(f"Analyzing code files recursively in: {script_dir}")
    print("=" * 80)
    
    # Get all code files recursively
    code_files = get_code_files_recursive(script_dir)
    
    if not code_files:
        print("No code files found in the project.")
        return
    
    # Count lines by file type and directory
    file_stats = defaultdict(lambda: {'files': 0, 'lines': 0})
    dir_stats = defaultdict(lambda: {'files': 0, 'lines': 0})
    total_lines = 0
    total_files = 0
    
    # Process each file
    print("**Files Found:**")
    current_dir = None
    
    for file_path in sorted(code_files):
        line_count = count_lines_in_file(file_path)
        extension = file_path.suffix.lower()
        relative_path = file_path.relative_to(script_dir)
        file_dir = str(relative_path.parent) if relative_path.parent != pathlib.Path('.') else 'root'
        
        # Print directory header when we enter a new directory
        if file_dir != current_dir:
            if current_dir is not None:
                print()  # Add spacing between directories
            print(f"\n**{file_dir}/**")
            current_dir = file_dir
        
        # Update statistics
        file_stats[extension]['files'] += 1
        file_stats[extension]['lines'] += line_count
        dir_stats[file_dir]['files'] += 1
        dir_stats[file_dir]['lines'] += line_count
        total_lines += line_count
        total_files += 1
        
        print(f"  {file_path.name:<35} {line_count:>6} lines")
    
    print("\n" + "=" * 80)
    
    # Print summary by directory
    print("\n**Summary by Directory:**")
    for dir_name, stats in sorted(dir_stats.items()):
        print(f"{dir_name:<30} {stats['files']:>3} files, {stats['lines']:>8} lines")
    
    print("\n**Summary by File Type:**")
    for ext, stats in sorted(file_stats.items()):
        print(f"{ext:<8} {stats['files']:>3} files, {stats['lines']:>8} lines")
    
    print("=" * 80)
    print(f"**TOTAL PROJECT: {total_files} files, {total_lines:,} lines of code**")
    
    # Show average lines per file
    avg_lines = total_lines / total_files if total_files > 0 else 0
    print(f"**Average lines per file: {avg_lines:.1f}**")

if __name__ == "__main__":
    main()
