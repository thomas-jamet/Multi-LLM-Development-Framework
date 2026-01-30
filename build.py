#!/usr/bin/env python3
"""
Bootstrap Build Script

Compiles modular source files into a single distributable bootstrap.py file.

This build process:
1. Reads all module files in dependency order
2. Strips internal package imports
3. Preserves external imports and constants
4. Concatenates with proper structure
5. Adds build metadata header
"""

from pathlib import Path
from datetime import datetime, timezone
from typing import List, Tuple


SOURCE_DIR = Path(".")
OUTPUT_FILE = Path("bootstrap.py")
VERSION = "1.0.0"


def read_module(path: Path) -> Tuple[str, List[str], str]:
    """
    Read a module and separate imports from code.

    Returns:
        (imports, external_imports, code) where:
        - imports: All import statements
        - external_imports: List of external library imports
        - code: Module code without imports
    """
    content = path.read_text()
    lines = content.splitlines()

    imports = []
    external_imports = []
    code_lines = []
    in_docstring = False
    docstring_marker = None

    i = 0
    while i < len(lines):
        line = lines[i]

        # Track docstrings/strings
        # We need to handle:
        # 1. Strings that start mid-line (e.g., return f"""...""")
        # 2. Escaped triple quotes inside strings (e.g., \"\"\")
        # 3. Single-line vs multi-line strings

        stripped = line.strip()

        # If we're already in a docstring, check for closing marker
        if in_docstring:
            # Look for the closing marker (unescaped)
            # Simple check: if line contains the marker and previous char isn't backslash
            if docstring_marker in line:
                # Check if it's escaped
                idx = line.find(docstring_marker)
                if idx > 0 and line[idx - 1] == "\\":
                    # It's escaped, not a real closing
                    code_lines.append(line)
                else:
                    # Real closing marker found
                    in_docstring = False
                    docstring_marker = None
                    code_lines.append(line)
            else:
                code_lines.append(line)
            i += 1
            continue

        # Not in a docstring - check if one is starting
        # Look for triple quotes with optional prefix (f, r, b, etc.)
        found_start = False
        for test_marker in ['"""', "'''"]:
            for prefix in ["", "f", "r", "fr", "rf", "b", "br", "rb"]:
                pattern = f"{prefix}{test_marker}"
                if pattern in stripped:
                    # Found a potential start - make sure it's not escaped
                    idx = stripped.find(pattern)
                    if idx == 0 or (idx > 0 and stripped[idx - 1] != "\\"):
                        # Valid string start
                        in_docstring = True
                        docstring_marker = test_marker
                        code_lines.append(line)

                        # Check if it closes on the same line
                        # Look for another occurrence of the marker after this one
                        rest_of_line = stripped[idx + len(pattern) :]
                        if test_marker in rest_of_line:
                            # Check if closing is not escaped
                            close_idx = rest_of_line.find(test_marker)
                            if close_idx > 0 and rest_of_line[close_idx - 1] != "\\":
                                # Single-line string
                                in_docstring = False
                                docstring_marker = None

                        found_start = True
                        break
            if found_start:
                break

        if found_start:
            i += 1
            continue

        if in_docstring:
            code_lines.append(line)
            i += 1
            continue

        # Skip shebang and encoding declarations
        if line.startswith("#!") or line.startswith("# -*-"):
            i += 1
            continue

        # Handle import statements (only when NOT inside a string)
        if line.startswith("import ") or line.startswith("from "):
            # Check if it's an internal import
            is_internal = (
                "from config" in line
                or "from core" in line
                or "from content_generators" in line
                or "from operations" in line
                or "from providers" in line
                or "from bootstrap_src" in line
                or line.startswith("from .")
            )

            # Check if multi-line import
            if "(" in line and ")" not in line:
                # Multi-line import
                if is_internal:
                    # Skip the entire block
                    while i < len(lines) - 1:
                        i += 1
                        if ")" in lines[i]:
                            break
                else:
                    # Keep the entire block
                    import_block = [line]
                    while i < len(lines) - 1 and ")" not in lines[i]:
                        i += 1
                        import_block.append(lines[i])
                    imports.append("\n".join(import_block))

                    # Extract library name
                    first_line = line
                    if first_line.startswith("from "):
                        lib = first_line.split("from ")[1].split()[0].split(".")[0]
                        if lib not in external_imports:
                            external_imports.append(lib)
            elif is_internal:
                # Single-line internal import, skip
                pass
            else:
                # Single-line external import, keep
                imports.append(line)

                # Track external library imports
                if line.startswith("import "):
                    lib = line.replace("import ", "").split()[0].split(".")[0]
                    if lib not in external_imports:
                        external_imports.append(lib)
                elif line.startswith("from "):
                    lib = line.split("from ")[1].split()[0].split(".")[0]
                    if lib not in external_imports:
                        external_imports.append(lib)
        else:
            code_lines.append(line)

        i += 1

    return "\n".join(imports), external_imports, "\n".join(code_lines)


def build_bootstrap():
    """Main build process."""
    print("🔨 Building bootstrap.py from modular source...")

    # Module order (determines concatenation order, respecting dependencies)
    module_order = [
        "config.py",
        "core.py",
        "providers/base.py",
        "core/makefile.py",
        "core/templates/__init__.py",
        "core/templates/gemini_md.py",
        "core/templates/github_workflow.py",
        "core/templates/scripts_core.py",
        "core/templates/scripts_snapshot.py",
        "core/templates/scripts_skills.py",
        "core/templates/schemas.py",
        "core/templates/configs.py",
        "content_generators.py",
        "operations/create.py",
        "__main__.py",
    ]

    # Check all modules exist
    for module_path_str in module_order:
        module_path = Path(module_path_str)
        if not module_path.exists():
            print(f"❌ Missing module: {module_path}")
            return 1

    # Collect all imports and code
    all_imports = []
    all_external_libs = set()
    all_code = []
    build_log = []  # Initialize build_log

    print("\n📦 Processing modules:")
    for idx, module_str in enumerate(module_order, 1):
        module_path = Path(module_str)

        print(f"   - {module_path}")
        imports, ext_libs, code = read_module(module_path)

        if imports:
            all_imports.append(imports)

        # Track external libraries
        all_external_libs.update(ext_libs)

        # Add module separator comment
        module_name = str(module_path)
        all_code.append(f"\n# {'=' * 78}")
        all_code.append(f"# Module: {module_name}")
        all_code.append(f"# {'=' * 78}\n")

        # Add code to collection
        all_code.append(code)

        # Print status
        stats_path = module_path.relative_to(SOURCE_DIR)
        size = module_path.stat().st_size
        lines = len(code.splitlines())
        build_log.append(f"   {idx}. {stats_path}: {lines} lines ({size} bytes)")

    # Build final file
    build_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    header = f'''#!/usr/bin/env python3
"""
Gemini Native Workspace Bootstrap Script v{VERSION}

Creates, validates, and upgrades self-contained Gemini workspaces.

Usage:
    python bootstrap.py                           # Interactive mode
    python bootstrap.py -t 2 -n myproject        # Create Standard workspace
    python bootstrap.py --validate ./myproject   # Validate workspace
    python bootstrap.py --upgrade ./myproject    # Upgrade to next tier

Features:
    - Tiered workspace system (Lite, Standard, Enterprise)
    - LLM-agnostic design (Gemini, Claude, ChatGPT)
    - Built-in validation and health monitoring
    - Tier upgrades with backup/rollback support
    - Template system for custom workspace types

Build Information:
    Version: {VERSION}
    Built: {build_time}
    Source: Modular architecture (bootstrap_src/)

This file is AUTO-GENERATED from modular source.
DO NOT EDIT THIS FILE DIRECTLY.
Edit files in bootstrap_src/ and rebuild with: python bootstrap_src/build.py
"""

'''

    # Combine everything
    final_content = header

    # Add unique imports
    unique_imports = []
    seen = set()
    for import_block in all_imports:
        for line in import_block.splitlines():
            if line and line not in seen:
                unique_imports.append(line)
                seen.add(line)

    if unique_imports:
        final_content += "\n".join(unique_imports) + "\n\n"

    # Add all code
    final_content += "\n".join(all_code)

    # Write output
    OUTPUT_FILE.write_text(final_content)

    # Make executable
    OUTPUT_FILE.chmod(0o755)

    print(f"\n✅ Created {OUTPUT_FILE}")
    print(
        f"   Total size: {len(final_content)} chars ({len(final_content.splitlines())} lines)"
    )
    print(
        f"   External libraries: {', '.join(sorted(all_external_libs)) if all_external_libs else 'none'}"
    )

    # Summary
    print("\n📊 Build Summary:")
    for idx, module_str in enumerate(module_order, 1):
        module_path = Path(module_str)
        stats_path = module_path.relative_to(SOURCE_DIR)
        size = module_path.stat().st_size
        lines = len(module_path.read_text().splitlines())
        print(f"   {idx}. {stats_path}: {lines} lines ({size} bytes)")

    print(f"\n🎉 Build complete! Run with: python {OUTPUT_FILE}")
    return 0


if __name__ == "__main__":
    exit(build_bootstrap())
