#!/usr/bin/env python3
"""
Bootstrap CLI Entry Point

Handles command-line argument parsing and main() function.

NOTE: This module contains forward references to symbols from other modules
(TIERS, TEMPLATES, ValidationError, error(), etc.) that are resolved during
the build process when all modules are concatenated. Lint errors for these
are expected and suppressed with # noqa: F821 comments.
"""
# ruff: noqa: F821  # Forward references resolved at build time

import sys
import argparse
import json
from pathlib import Path

# Version constant (imported from config in final build)
VERSION = "2026.26"
DEFAULT_PYTHON_VERSION = "3.11"

# Exit codes
EXIT_SUCCESS = 0
EXIT_VALIDATION_ERROR = 1
EXIT_CREATION_ERROR = 2
EXIT_UPGRADE_ERROR = 3
EXIT_ROLLBACK_ERROR = 4
EXIT_CONFIG_ERROR = 5
EXIT_WORKSPACE_ERROR = 6
EXIT_INTERRUPT = 130
EXIT_UNEXPECTED_ERROR = 255


# Global USE_COLOR flag (imported from core in final build)
USE_COLOR = True


def run_self_tests():
    """Run internal self-tests for the bootstrap script.

    Tests core functionality without external dependencies.
    Returns exit code 0 on success, 1 on failure.
    """
    print("🧪 Running Bootstrap Self-Tests...\n")

    passed = 0
    failed = 0

    def test(name, condition):
        nonlocal passed, failed
        if condition:
            print(f"  ✅ {name}")
            passed += 1
        else:
            print(f"  ❌ {name}")
            failed += 1

    # Test 1: Version format
    test(
        "VERSION format (YYYY.NN)",
        len(VERSION.split(".")) == 2 and VERSION.split(".")[0].isdigit(),
    )

    # Test 2: Tier definitions exist
    test(
        "TIERS defined with 3 tiers",
        len(TIERS) == 3 and all(k in TIERS for k in ["1", "2", "3"]),
    )  # noqa: F821 - TIERS imported from config in build

    # Test 3: Each tier has required keys
    for tier_id, tier_data in TIERS.items():  # noqa: F821
        test(f"Tier {tier_id} has 'name' key", "name" in tier_data)

    # Test 4: Exit codes defined
    test("EXIT_SUCCESS is 0", EXIT_SUCCESS == 0)
    test("EXIT_VALIDATION_ERROR is non-zero", EXIT_VALIDATION_ERROR != 0)

    # Test 5: Project name validation (if available)
    try:
        # Valid names should pass
        validate_project_name("my-project")
        test("validate_project_name accepts valid name", True)
    except NameError:
        test("validate_project_name available", False)
    except ValidationError:  # noqa: F821 - ValidationError imported from core in build
        test("validate_project_name accepts valid name", False)

    try:
        # Invalid names should fail
        validate_project_name("123-invalid")
        test("validate_project_name rejects invalid name", False)
    except NameError:
        pass  # Already reported above
    except ValidationError:  # noqa: F821
        test("validate_project_name rejects invalid name", True)

    # Test 6: Template consistency
    for tmpl_name, tmpl_config in TEMPLATES.items():  # noqa: F821 - TEMPLATES imported from config in build
        test(f"Template '{tmpl_name}' has tier", "tier" in tmpl_config)

    # Summary
    print(f"\n{'=' * 50}")
    print(f"Results: {passed} passed, {failed} failed")

    if failed > 0:
        print("\n❌ Self-tests FAILED")
        sys.exit(1)
    else:
        print("\n✅ All self-tests passed")
        sys.exit(0)


def main():
    try:
        _main_impl()
    except ValidationError as e:  # noqa: F821
        error(f"Validation failed: {e}")
        sys.exit(EXIT_VALIDATION_ERROR)
    except CreationError as e:  # noqa: F821
        error(f"Workspace creation failed: {e}")
        sys.exit(EXIT_CREATION_ERROR)
    except UpgradeError as e:  # noqa: F821
        error(f"Upgrade failed: {e}")
        sys.exit(EXIT_UPGRADE_ERROR)
    except RollbackError as e:  # noqa: F821
        error(f"Rollback failed: {e}")
        sys.exit(EXIT_ROLLBACK_ERROR)
    except ConfigurationError as e:  # noqa: F821
        error(f"Configuration error: {e}")
        sys.exit(EXIT_CONFIG_ERROR)
    except WorkspaceError as e:  # noqa: F821
        error(f"Workspace operation failed: {e}")
        sys.exit(EXIT_WORKSPACE_ERROR)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(EXIT_INTERRUPT)
    except Exception as e:
        import traceback

        traceback.print_exc()
        error(f"Unexpected error: {e}")
        sys.exit(EXIT_UNEXPECTED_ERROR)


def _main_impl():
    parser = argparse.ArgumentParser(
        description=f"Gemini Native Workspace Bootstrap (Grand Unified v{VERSION})",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  python bootstrap.py                            Interactive mode
  python bootstrap.py -t 2 -n myapp              Create Standard workspace
  python bootstrap.py -t 3 -n platform --git     Create with git init
  python bootstrap.py -t 2 -n myapp --force -v   Overwrite with verbose output
  python bootstrap.py --from-template fastapi -n myapi  Use template
  python bootstrap.py --list-templates           Show available templates
  python bootstrap.py --validate ./myapp         Validate existing workspace
  python bootstrap.py --upgrade ./myapp          Upgrade workspace tier
  python bootstrap.py --update-scripts ./myapp   Update scripts only
  python bootstrap.py --dry-run -t 2 -n myapp    Preview without creating
  python bootstrap.py -t 2 -n child --parent ..  Create child in monorepo
  python bootstrap.py --config ./my-config.json  Use custom config file

After creation:
  cd myapp && make onboard                       First-run experience
        """,
    )

    # Create mode
    parser.add_argument(
        "-t",
        "--tier",
        choices=["1", "2", "3"],
        help="Tier: 1=Lite, 2=Standard, 3=Enterprise",
    )
    parser.add_argument(
        "-V", "--version", action="version", version=f"Gemini Bootstrap v{VERSION}"
    )
    parser.add_argument("-n", "--name", help="Project name")
    parser.add_argument(
        "--dry-run", action="store_true", help="Preview without creating files"
    )
    parser.add_argument(
        "--force", action="store_true", help="Overwrite existing directory"
    )
    parser.add_argument("--git", action="store_true", help="Initialize git repository")
    parser.add_argument("-q", "--quiet", action="store_true", help="Minimal output")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable colored output (for CI/logging)",
    )
    parser.add_argument(
        "--shared-agent", help="Path to shared .agent/ directory (symlink)"
    )
    parser.add_argument("--parent", help="Parent workspace path (for monorepos)")

    # Validate/Upgrade/Update mode
    parser.add_argument(
        "--validate", metavar="PATH", help="Validate existing workspace"
    )
    parser.add_argument(
        "--upgrade", metavar="PATH", help="Upgrade workspace to next tier"
    )
    parser.add_argument(
        "-y",
        "--yes",
        action="store_true",
        help="Skip confirmation prompts (for CI/CD automation)",
    )
    parser.add_argument(
        "--update-scripts",
        metavar="PATH",
        help="Update management scripts without full upgrade",
    )
    parser.add_argument(
        "--rollback", metavar="PATH", help="Rollback workspace from upgrade backup"
    )
    parser.add_argument(
        "--backup",
        metavar="NAME",
        help="Specific backup to restore (use with --rollback)",
    )
    parser.add_argument(
        "--export-template",
        metavar="PATH",
        help="Export an existing workspace as a template",
    )
    parser.add_argument(
        "--template-name",
        metavar="NAME",
        help="Name for exported template (use with --export-template)",
    )

    parser.add_argument(
        "--config",
        metavar="PATH",
        help="Path to config file (default: .gemini-bootstrap.json)",
    )
    parser.add_argument(
        "--validate-schemas",
        metavar="PATH",
        help="Validate workspace JSON files against schemas",
    )
    parser.add_argument(
        "--python-version",
        metavar="VERSION",
        default=None,
        help="Python version for CI workflows (default: 3.11)",
    )

    # Template mode
    parser.add_argument(
        "--from-template",
        metavar="NAME",
        help=f"Use template: {', '.join(TEMPLATES.keys())}",
    )
    parser.add_argument(
        "--list-templates", action="store_true", help="List available templates"
    )
    parser.add_argument(
        "--show-telemetry-info",
        action="store_true",
        help="Show what data is collected by telemetry (transparency)",
    )
    parser.add_argument(
        "--run-self-tests",
        action="store_true",
        help="Run internal unit tests for the bootstrap script",
    )

    args = parser.parse_args()

    # Handle --no-color flag
    global USE_COLOR
    if args.no_color:
        USE_COLOR = False

    # Load config file (from --config flag or default location)
    if args.config:
        config_path = Path(args.config)
        if config_path.exists():
            try:
                with open(config_path) as f:
                    config = json.load(f)
                info(f"Using config: {args.config}")
            except (json.JSONDecodeError, PermissionError) as e:
                warning(f"Failed to load config: {e}")
                config = {}
        else:
            error(f"Config file not found: {args.config}")
            sys.exit(1)
    else:
        config = load_config()

    # Handle list-templates
    if args.list_templates:
        header("Available Templates")
        for name, tmpl in TEMPLATES.items():
            print(f"  {name:12} - Tier {tmpl['tier']}, deps: {', '.join(tmpl['deps'])}")
        return

    # Handle show-telemetry-info
    if args.show_telemetry_info:
        show_telemetry_info()  # noqa: F821 - Function defined in operations module
        return

    # Handle self-tests
    if args.run_self_tests:
        run_self_tests()
        return

    # Handle validate mode
    if args.validate:
        validate_workspace(args.validate)
        return

    # Handle upgrade mode
    if args.upgrade:
        upgrade_workspace(args.upgrade, target_tier=args.tier, yes=args.yes)
        return

    # Handle update-scripts mode
    if args.update_scripts:
        update_scripts(args.update_scripts)
        return

    # Handle standalone snapshot creation (--backup NAME --parent PATH)
    if args.backup and args.parent and not args.rollback:
        create_snapshot(args.parent, args.backup)
        return

    # Handle rollback mode
    if args.rollback:
        backup_name = args.backup if hasattr(args, "backup") and args.backup else None
        rollback_workspace(args.rollback, backup_name, yes=args.yes)
        return

    # Handle export-template mode
    if args.export_template:
        if not args.template_name:
            error("Please specify a template name with --template-name")
            sys.exit(1)
        export_workspace_as_template(args.export_template, args.template_name)
        return

    # Handle validate-schemas mode
    if args.validate_schemas:
        validate_schemas(args.validate_schemas)
        return

    # Handle template mode
    template_files = None
    template_deps = None
    if args.from_template:
        # Validation now raises ValidationError
        validate_template_name(args.from_template)
        tmpl = TEMPLATES[args.from_template]
        args.tier = tmpl["tier"]
        template_files = tmpl["files"]
        template_deps = tmpl.get("deps", [])
        info(f"Using template '{args.from_template}' (Tier {args.tier})")

    # Interactive mode for create
    if args.tier is None:
        header(f"GEMINI GRAND UNIFIED BOOTSTRAP (v{VERSION})")
        print("\nSelect Tier:")
        for k, v in TIERS.items():
            print(f"  [{k}] {v['name']}")

        while True:
            default_tier = config.get("default_tier", "")
            prompt = (
                "\nChoice (1-3)" + (f" [{default_tier}]" if default_tier else "") + ": "
            )
            choice = input(prompt).strip() or default_tier
            if choice in TIERS:
                args.tier = choice
                break
            error("Invalid choice. Please enter 1, 2, or 3.")

    if args.name is None:
        while True:
            args.name = input("Project Name: ").strip() or "gemini_workspace"
            try:
                validate_project_name(args.name)
                break
            except ValidationError as e:  # noqa: F821
                error(str(e))

    # Apply config defaults
    if not args.shared_agent and config.get("shared_agent_path"):
        args.shared_agent = config["shared_agent_path"]

    # Get python_version from args or config and validate
    py_version = args.python_version or config.get(
        "python_version", DEFAULT_PYTHON_VERSION
    )
    validate_python_version(py_version)

    create_workspace(
        args.tier,
        args.name,
        args.dry_run,
        args.git,
        args.shared_agent,
        args.parent,
        template_files,
        template_deps,
        args.force,
        args.quiet,
        args.verbose,
        py_version,
    )


if __name__ == "__main__":
    main()
