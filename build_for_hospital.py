"""
============================================================
  HOSPITAL APP - BUILD SCRIPT
  Run this every time you make code changes
  Usage: python build_for_hospital.py
============================================================
"""

import os
import sys
import shutil
import py_compile
import compileall
from pathlib import Path

# Ensure console handles UTF-8 for emojis
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')


# ── Configuration ──
PROJECT_DIR = Path(__file__).resolve().parent
BUILD_DIR = PROJECT_DIR / "hospital_build"

# Folders to compile and copy (your Django app code)
CODE_FOLDERS = ["hospApp", "HospProject"]

# Folders to copy as-is (no compilation needed)
STATIC_FOLDERS = ["static", "staticfiles", "media"]

# Individual files to copy
INDIVIDUAL_FILES = ["manage.py", "hospital_db.sql", "run_on_startup.bat", "setup_autorun.bat", "UPDATE_GUIDE.md", "DEPLOYMENT_GUIDE.md", "serve.py"]

# File extensions to SKIP (source code - never copy these)
SKIP_EXTENSIONS = {".py"}

# File extensions to ALWAYS copy
COPY_EXTENSIONS = {".html", ".css", ".js", ".json", ".txt", ".png", ".jpg", 
                   ".jpeg", ".gif", ".svg", ".webp", ".woff", ".woff2", 
                   ".ttf", ".eot", ".ico", ".pdf", ".pyc"}

# Folders to skip
SKIP_FOLDERS = {"__pycache__", "venv", ".git", "node_modules", "hospital_build"}


def clean_pyc_in_build(build_dir):
    """Remove old .pyc files from build directory"""
    for root, dirs, files in os.walk(build_dir):
        for f in files:
            if f.endswith(".pyc"):
                os.remove(os.path.join(root, f))


def compile_and_copy_code(folder_name):
    """Compile .py files to .pyc and copy to build directory along with non-.py files"""
    src = PROJECT_DIR / folder_name
    dst = BUILD_DIR / folder_name
    
    if not src.exists():
        print(f"  ⚠️  Folder not found: {folder_name}")
        return
    
    # Remove old folder in build
    if dst.exists():
        shutil.rmtree(dst)
    
    file_count = 0
    compiled_count = 0
    
    for root, dirs, files in os.walk(src):
        # Skip __pycache__ and other unwanted folders
        dirs[:] = [d for d in dirs if d not in SKIP_FOLDERS]
        
        rel_path = Path(root).relative_to(src)
        dst_folder = dst / rel_path
        dst_folder.mkdir(parents=True, exist_ok=True)
        
        for filename in files:
            src_file = Path(root) / filename
            ext = src_file.suffix.lower()
            
            if filename == "__init__.py":
                # __init__.py: compile to .pyc AND keep original .py
                # Django needs __init__.py files to recognize packages
                dst_file = dst_folder / filename
                shutil.copy2(src_file, dst_file)
                
                # Also compile it
                pyc_file = dst_folder / (filename + "c")  # __init__.pyc
                try:
                    py_compile.compile(str(src_file), cfile=str(dst_folder / filename.replace('.py', '.pyc')), doraise=True)
                    compiled_count += 1
                except py_compile.PyCompileError as e:
                    print(f"  ❌ Compile error: {src_file} → {e}")
                file_count += 1
                
            elif ext == ".py":
                # Regular .py files: compile to .pyc only (NO .py copied)
                pyc_filename = filename.replace(".py", ".pyc")
                pyc_dst = dst_folder / pyc_filename
                try:
                    py_compile.compile(str(src_file), cfile=str(pyc_dst), doraise=True)
                    compiled_count += 1
                    file_count += 1
                except py_compile.PyCompileError as e:
                    print(f"  ❌ Compile error: {src_file} → {e}")
                    
            else:
                # Non-.py files (HTML templates, etc): copy as-is
                dst_file = dst_folder / filename
                shutil.copy2(src_file, dst_file)
                file_count += 1
    
    print(f"  ✅ {folder_name}/ → {file_count} files copied, {compiled_count} compiled to .pyc")


def copy_static_folder(folder_name):
    """Copy static/media folders as-is"""
    src = PROJECT_DIR / folder_name
    dst = BUILD_DIR / folder_name
    
    if not src.exists():
        print(f"  ⚠️  Folder not found: {folder_name}")
        return
    
    if dst.exists():
        shutil.rmtree(dst)
    
    shutil.copytree(src, dst)
    
    # Count files
    count = sum(1 for _ in dst.rglob("*") if _.is_file())
    print(f"  ✅ {folder_name}/ → {count} files copied")


def copy_individual_file(filename):
    """Copy individual files"""
    src = PROJECT_DIR / filename
    dst = BUILD_DIR / filename
    
    if not src.exists():
        print(f"  ⚠️  File not found: {filename}")
        return
    
    # For manage.py, compile it
    if filename.endswith(".py"):
        shutil.copy2(src, dst)
        print(f"  ✅ {filename} → copied (needed as .py for Django)")
    else:
        shutil.copy2(src, dst)
        print(f"  ✅ {filename} → copied")


def verify_no_source_code():
    """Verify that no .py source code leaked into the build (except allowed files)"""
    allowed_py = {"manage.py", "__init__.py", "serve.py"}
    leaked = []
    
    for py_file in BUILD_DIR.rglob("*.py"):
        if py_file.name not in allowed_py:
            leaked.append(py_file.relative_to(BUILD_DIR))
    
    if leaked:
        print(f"\n  ⚠️  WARNING: {len(leaked)} source .py files found in build!")
        for f in leaked[:10]:
            print(f"      - {f}")
        return False
    else:
        print(f"\n  ✅ VERIFIED: No source code (.py) leaked into build!")
        return True


def count_build_size():
    """Count total build size"""
    total = 0
    file_count = 0
    for f in BUILD_DIR.rglob("*"):
        if f.is_file():
            total += f.stat().st_size
            file_count += 1
    
    size_mb = total / (1024 * 1024)
    print(f"  📦 Total build: {file_count} files, {size_mb:.1f} MB")


def main():
    print("=" * 60)
    print("  🏥 HOSPITAL APP — BUILD SCRIPT")
    print("=" * 60)
    print(f"  Source: {PROJECT_DIR}")
    print(f"  Output: {BUILD_DIR}")
    print("=" * 60)
    
    # Create build directory if not exists
    BUILD_DIR.mkdir(exist_ok=True)
    
    # Step 1: Compile and copy code folders
    print("\n📝 Step 1: Compiling Python code to .pyc...")
    for folder in CODE_FOLDERS:
        compile_and_copy_code(folder)
    
    # Step 2: Copy static folders
    print("\n📁 Step 2: Copying static files, media...")
    for folder in STATIC_FOLDERS:
        copy_static_folder(folder)
    
    # Step 3: Copy individual files
    print("\n📄 Step 3: Copying individual files...")
    for filename in INDIVIDUAL_FILES:
        copy_individual_file(filename)
    
    # Step 4: Make sure serve.py exists
    serve_py = BUILD_DIR / "serve.py"
    if not serve_py.exists():
        print("  ⚠️  serve.py not found in build!")
    else:
        print("  ✅ serve.py → already exists")
    
    # Step 5: Make sure .env.template exists
    env_template = BUILD_DIR / ".env.template"
    if not env_template.exists():
        print("  ⚠️  .env.template not found in build!")
    else:
        print("  ✅ .env.template → already exists")
    
    # Step 6: Make sure requirements.txt exists
    req = BUILD_DIR / "requirements.txt"
    if not req.exists():
        # Copy from project
        src_req = PROJECT_DIR / "requirements.txt"
        if src_req.exists():
            shutil.copy2(src_req, req)
            print("  ✅ requirements.txt → copied from project")
    else:
        print("  ✅ requirements.txt → already exists")
    
    # Verification
    print("\n🔍 Step 4: Verifying build...")
    verify_no_source_code()
    count_build_size()

    # Packaging ZIP
    print("\n📦 Step 5: Packaging build into ZIP archive...")
    zip_base = PROJECT_DIR / "hospital_build"
    try:
        # Create ZIP where the root of the archive is the project folder and base_dir is 'hospital_build'
        shutil.make_archive(str(zip_base), 'zip', root_dir=str(PROJECT_DIR), base_dir="hospital_build")
        print(f"  ✅ ZIP archive created: {zip_base}.zip")
    except Exception as e:
        print(f"  ❌ Failed to create ZIP archive: {e}")
    
    print("\n" + "=" * 60)
    print("  ✅ BUILD COMPLETE & PUBLISHED!")
    print("=" * 60)
    print("  📂 Your deployment folder is ready at:")
    print(f"     {BUILD_DIR}")
    print("  📦 Your published package is ready at:")
    print(f"     {zip_base}.zip")
    print("")
    print("  📋 Next steps:")
    print("     1. Copy 'hospital_build.zip' and 'hospital_db.sql' to USB drive")
    print("     2. Take USB to hospital server")
    print("     3. Follow the hospital setup / deployment guides")
    print("=" * 60)


if __name__ == "__main__":
    main()
