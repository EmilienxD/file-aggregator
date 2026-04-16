import os
import time

def get_file_states(source_paths):
    """Returns a dictionary mapping file paths to their current modification times."""
    return {src: os.path.getmtime(src) if os.path.exists(src) else None for src in source_paths}

def concatenate_file(target_path, source_paths):
    """Concatenates existing source files into the target file with file safety."""
    # Check if any source file actually exists
    valid_sources = [src for src in source_paths if os.path.exists(src) and os.path.isfile(src)]
    
    if not valid_sources:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Skipping: No valid source files exist for {target_path}")
        return False

    with open(target_path, 'w', encoding='utf-8') as f_out:
        for src in valid_sources:
            with open(src, 'r', encoding='utf-8') as f_in:
                content = f_in.read()
                f_out.write(content)
                if content and not content.endswith('\n'):
                    f_out.write('\n')
    
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Built/Updated: {target_path}")
    return True
