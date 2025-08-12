
"""
Script to switch active dbt Cloud project or host in dbt_cloud.yml.
Usage:
  # Switch to a specific project and host
  python switch_dbt_proj.py --proj proj_2_dev --host staging

  # Switch only the project (host stays the same)
  python switch_dbt_proj.py --proj proj_1_staging

  # Switch only the host (project stays the same)
  python switch_dbt_proj.py --host dev

  # See all available options
  python switch_dbt_proj.py --list
"""

import argparse
import re
import sys
from pathlib import Path


def switch_active_property(file_path, property_name, target_value):
    """
    Switch the active property in dbt_cloud.yml by commenting/uncommenting lines.
    
    Args:
        file_path (Path): Path to the dbt_cloud.yml file.
        property_name (str): The property to switch (e.g., 'active-project', 'active-host').
        target_value (str): The identifier for the property value to activate.
    """
    try:
        with open(file_path, 'r') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.", file=sys.stderr)
        return False
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        return False

    # Regex to match lines for the given property (commented or uncommented)
    # e.g., active-project: "123456" # proj_1
    # or # active-host: "dev.getdbt.com" # dev
    pattern = re.compile(r'^(\s*)(#\s*)?(' + re.escape(property_name) + r':\s*"[^"]+")(\s*#\s*(.+))?$')
    
    lines = content.split('\n')
    modified = False
    found_target = False
    
    for i, line in enumerate(lines):
        match = pattern.match(line)
        if match:
            indent, comment_prefix, prop_part, _, value_name = match.groups()
            indent = indent or ''
            comment_prefix = comment_prefix or ''
            value_name = value_name.strip() if value_name else ''

            if value_name == target_value:
                # This is our target - make sure it's uncommented
                if comment_prefix:
                    lines[i] = f"{indent}{prop_part.strip()}{' # ' + value_name if value_name else ''}"
                    modified = True
                    print(f"✓ Activated {property_name}: {target_value}")
                found_target = True
            else:
                # This is not our target - make sure it's commented
                if not comment_prefix:
                    lines[i] = f"{indent}# {prop_part.strip()}{' # ' + value_name if value_name else ''}"
                    modified = True
                    print(f"✓ Deactivated {property_name}: {value_name or 'unnamed'}")

    if not found_target:
        print(f"Error: {property_name} '{target_value}' not found in {file_path}", file=sys.stderr)
        return False

    if modified:
        try:
            with open(file_path, 'w') as f:
                f.write('\n'.join(lines))
            print(f"✅ Successfully updated {file_path}")
            return True
        except Exception as e:
            print(f"Error writing file: {e}", file=sys.stderr)
            return False
    else:
        print(f"ℹ️  {property_name} '{target_value}' was already active.")
        return True


def list_available_options(file_path):
    """
    Lists all available projects and hosts from the dbt_cloud.yml file.
    """
    try:
        with open(file_path, 'r') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Available options in {file_path}:\n")
    
    for prop_name in ['active-host', 'active-project']:
        pattern = re.compile(r'^(\s*)(#\s*)?(' + re.escape(prop_name) + r':\s*"[^"]+")(\s*#\s*(.+))?$')
        lines = content.split('\n')
        
        print(f"{prop_name}s:")
        for line in lines:
            match = pattern.match(line)
            if match and match.group(5):
                status = "active" if not match.group(2) else "inactive"
                value_name = match.group(5).strip()
                print(f"  - {value_name} ({status})")
        print("")


def main():
    parser = argparse.ArgumentParser(
        description="Switch active dbt Cloud project or host in dbt_cloud.yml.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "--proj",
        help="Project identifier to activate (e.g., proj_1_dev, proj_2_staging)."
    )
    parser.add_argument(
        "--host",
        help="Host identifier to activate (e.g., prod, dev, staging)."
    )
    parser.add_argument(
        "--file",
        default="dbt_cloud.yml",
        help="Path to dbt_cloud.yml file (default: dbt_cloud.yml in the current directory)."
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available projects and hosts without making changes."
    )

    args = parser.parse_args()
    file_path = Path(args.file).expanduser()

    if args.list:
        list_available_options(file_path)
        return

    if not args.proj and not args.host:
        parser.print_help()
        print("\nError: At least one of --proj or --host must be provided.", file=sys.stderr)
        sys.exit(1)

    success = True
    if args.proj:
        if not switch_active_property(file_path, 'active-project', args.proj):
            success = False
    
    if args.host:
        if not switch_active_property(file_path, 'active-host', args.host):
            success = False

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
