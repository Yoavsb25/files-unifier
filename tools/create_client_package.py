#!/usr/bin/env python3
"""
Sales Automation Script
Automates the complete sales process: license generation, app building, and packaging.

Usage:
    # Interactive mode (prompts for all information):
    python tools/create_client_package.py
    
    # Command-line mode (all arguments optional):
    python tools/create_client_package.py --company "Company Name" --expires "2027-12-31" --machines 5 --platform macos
    python tools/create_client_package.py --company "Company Name" --expires "2027-12-31" --machines 5 --platform windows
"""

import argparse
import subprocess
import sys
import shutil
import zipfile
import platform as plat
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from pdf_merger import APP_VERSION
from tools.license_generator import generate_license

# Colors for output
GREEN = '\033[0;32m'
RED = '\033[0;31m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'  # No Color


def print_step(step_num, message):
    """Print a step message."""
    print(f"\n{BLUE}[Step {step_num}]{NC} {message}")


def print_success(message):
    """Print a success message."""
    print(f"{GREEN}✓{NC} {message}")


def print_error(message):
    """Print an error message."""
    print(f"{RED}✗{NC} {message}")


def print_warning(message):
    """Print a warning message."""
    print(f"{YELLOW}⚠{NC} {message}")


def check_prerequisites():
    """Check if all prerequisites are met."""
    print_step(0, "Checking prerequisites...")
    
    # Check PyInstaller
    try:
        subprocess.run(['pyinstaller', '--version'], 
                      capture_output=True, check=True)
        print_success("PyInstaller is installed")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print_error("PyInstaller is not installed")
        print("Install it with: pip install pyinstaller")
        return False
    
    # Check private key
    private_key = Path('tools/private_key.pem')
    if not private_key.exists():
        print_error(f"Private key not found at {private_key}")
        print("Generate keys first with: python tools/license_generator.py generate-keys")
        return False
    print_success("Private key found")
    
    # Check public key
    public_key = Path('pdf_merger/licensing/public_key.pem')
    if not public_key.exists():
        print_warning(f"Public key not found at {public_key}")
        print("Copy public key: cp tools/public_key.pem pdf_merger/licensing/public_key.pem")
        return False
    print_success("Public key found")
    
    return True


def build_application(platform: str) -> bool:
    """Build the application for the specified platform."""
    print_step(2, f"Building application for {platform}...")
    
    project_root = Path(__file__).parent.parent
    current_platform = plat.system()
    
    # Check for cross-platform build issues
    if platform == 'windows' and current_platform != 'Windows':
        print_error("Cannot build Windows executable on macOS/Linux")
        print("Windows builds must be done on a Windows machine.")
        print("\nOptions:")
        print("  1. Build on a Windows machine")
        print("  2. Use --skip-build and provide an existing Windows build")
        return False
    elif platform == 'macos' and current_platform != 'Darwin':
        print_error("Cannot build macOS application on Windows/Linux")
        print("macOS builds must be done on a macOS machine.")
        print("\nOptions:")
        print("  1. Build on a macOS machine")
        print("  2. Use --skip-build and provide an existing macOS build")
        return False
    
    if platform == 'macos':
        build_script = project_root / 'build_config' / 'build.sh'
        if not build_script.exists():
            print_error(f"Build script not found: {build_script}")
            return False
        
        # Make script executable
        build_script.chmod(0o755)
        
        # Run build script
        result = subprocess.run(['bash', str(build_script)], 
                              cwd=project_root, 
                              capture_output=False)
        if result.returncode != 0:
            print_error("Build failed")
            return False
        
        # Check if app was created
        app_path = project_root / 'dist' / 'PDF Batch Merger.app'
        if not app_path.exists():
            print_error("Application bundle not found after build")
            return False
        
        print_success(f"Application built: {app_path}")
        return True
        
    elif platform == 'windows':
        build_script = project_root / 'build_config' / 'build.bat'
        if not build_script.exists():
            print_error(f"Build script not found: {build_script}")
            return False
        
        # Run build script
        result = subprocess.run([str(build_script)], 
                              cwd=project_root, 
                              shell=True,
                              capture_output=False)
        if result.returncode != 0:
            print_error("Build failed")
            return False
        
        # Check if exe was created
        exe_path = project_root / 'dist' / 'PDF Batch Merger.exe'
        if not exe_path.exists():
            print_error("Executable not found after build")
            return False
        
        print_success(f"Application built: {exe_path}")
        return True
    
    else:
        print_error(f"Unknown platform: {platform}")
        return False


def prompt_for_input(prompt: str, default: str = None, validator=None) -> str:
    """Prompt user for input with optional default and validator."""
    if default:
        full_prompt = f"{prompt} [{default}]: "
    else:
        full_prompt = f"{prompt}: "
    
    while True:
        value = input(full_prompt).strip()
        
        # Use default if empty
        if not value and default:
            value = default
        
        # Validate if validator provided
        if validator:
            error = validator(value)
            if error:
                print_error(error)
                continue
        
        if value:
            return value
        else:
            print_error("This field is required. Please enter a value.")


def validate_date(date_str: str) -> str:
    """Validate date format (YYYY-MM-DD)."""
    if not date_str:
        return "Date is required"
    
    try:
        expiry_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        today = datetime.now().date()
        if expiry_date <= today:
            return "Expiration date must be in the future"
        return None
    except ValueError:
        return "Invalid date format. Use YYYY-MM-DD (e.g., 2027-12-31)"


def validate_platform(platform: str) -> str:
    """Validate platform choice."""
    if not platform:
        return "Platform is required"
    platform_lower = platform.lower()
    if platform_lower not in ['macos', 'windows', '1', '2']:
        return "Please enter 'macos' or 'windows' (or 1/2)"
    return None


def validate_machines(machines_str: str) -> str:
    """Validate number of machines."""
    if not machines_str:
        return None  # Optional field
    try:
        machines = int(machines_str)
        if machines < 1:
            return "Number of machines must be at least 1"
        return None
    except ValueError:
        return "Please enter a valid number"


def get_customer_info():
    """Interactively get customer information."""
    print(f"\n{GREEN}{'='*60}{NC}")
    print(f"{GREEN}PDF Batch Merger - Sales Automation{NC}")
    print(f"{GREEN}{'='*60}{NC}\n")
    print("Please provide the following information:\n")
    
    # Company name
    company = prompt_for_input("Customer company name")
    
    # Expiration date
    default_expires = (datetime.now().replace(year=datetime.now().year + 1)).strftime('%Y-%m-%d')
    expires = prompt_for_input(
        "License expiration date (YYYY-MM-DD)",
        default=default_expires,
        validator=validate_date
    )
    
    # Number of machines
    machines_str = prompt_for_input(
        "Number of allowed machines",
        default="1",
        validator=validate_machines
    )
    machines = int(machines_str) if machines_str else 1
    
    # Platform
    print(f"\n{YELLOW}Select target platform:{NC}")
    print("  1. macOS")
    print("  2. Windows")
    platform_input = prompt_for_input(
        "Platform (1/2 or macos/windows)",
        validator=validate_platform
    )
    platform_lower = platform_input.lower()
    if platform_lower in ['1', 'macos']:
        platform = 'macos'
    else:
        platform = 'windows'
    
    # Skip build option
    skip_build_input = prompt_for_input(
        "Skip building? Use existing build if available (y/n)",
        default="n"
    )
    skip_build = skip_build_input.lower() in ['y', 'yes']
    
    return {
        'company': company,
        'expires': expires,
        'machines': machines,
        'platform': platform,
        'skip_build': skip_build
    }


def create_delivery_package(company: str, platform: str, license_path: Path) -> Path:
    """Create a delivery package with app, license, and user guide."""
    print_step(3, "Creating delivery package...")
    
    project_root = Path(__file__).parent.parent
    
    # Create delivery directory
    safe_company = "".join(c for c in company if c.isalnum() or c in (' ', '-', '_')).strip()
    delivery_name = f"PDF_Batch_Merger_{safe_company}_{datetime.now().strftime('%Y%m%d')}"
    delivery_dir = project_root / 'deliveries' / delivery_name
    delivery_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy application
    if platform == 'macos':
        app_source = project_root / 'dist' / 'PDF Batch Merger.app'
        app_dest = delivery_dir / 'PDF Batch Merger.app'
        if app_source.exists():
            shutil.copytree(app_source, app_dest, dirs_exist_ok=True)
            print_success("Application copied")
        else:
            print_error("Application not found")
            return None
    else:  # windows
        exe_source = project_root / 'dist' / 'PDF Batch Merger.exe'
        exe_dest = delivery_dir / 'PDF Batch Merger.exe'
        if exe_source.exists():
            shutil.copy2(exe_source, exe_dest)
            print_success("Application copied")
        else:
            print_error("Application not found")
            return None
    
    # Copy license
    license_dest = delivery_dir / 'license.json'
    shutil.copy2(license_path, license_dest)
    print_success("License copied")
    
    # Copy user guide
    user_guide_source = project_root / 'docs' / 'README_USER.md'
    if user_guide_source.exists():
        user_guide_dest = delivery_dir / 'User_Guide.md'
        shutil.copy2(user_guide_source, user_guide_dest)
        print_success("User guide copied")
    
    # Create installation instructions
    instructions = delivery_dir / 'INSTALLATION_INSTRUCTIONS.txt'
    with open(instructions, 'w') as f:
        f.write("PDF Batch Merger - Installation Instructions\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Company: {company}\n")
        f.write(f"Version: {APP_VERSION}\n")
        f.write(f"Platform: {platform.upper()}\n\n")
        f.write("INSTALLATION:\n")
        f.write("-" * 50 + "\n\n")
        if platform == 'macos':
            f.write("1. Copy 'PDF Batch Merger.app' to your Applications folder\n")
            f.write("2. Copy 'license.json' to the same folder as the app\n")
            f.write("   (or to ~/.pdf_merger/ directory)\n")
            f.write("3. Double-click 'PDF Batch Merger.app' to launch\n\n")
        else:
            f.write("1. Copy 'PDF Batch Merger.exe' to your desired location\n")
            f.write("2. Copy 'license.json' to the same folder as the .exe\n")
            f.write("   (or to %USERPROFILE%\\.pdf_merger\\ directory)\n")
            f.write("3. Double-click 'PDF Batch Merger.exe' to launch\n\n")
        f.write("SUPPORT:\n")
        f.write("-" * 50 + "\n")
        f.write("For technical support or license renewal, contact your software provider.\n")
    
    # Copy getting started guides
    copy_guide_files(platform, delivery_dir)

    print_success(f"Delivery package created: {delivery_dir}")
    return delivery_dir


def copy_guide_files(platform: str, dest_dir: Path, project_root: Path = None) -> bool:
    """Copy Getting_Started guide files for the given platform into dest_dir.

    Returns True if at least one file was copied, False if none were found.
    Accepts an optional project_root for testing with temp directories.
    """
    if project_root is None:
        project_root = Path(__file__).parent.parent
    guide_dir = project_root / "docs" / "guides" / platform
    copied = False
    for fmt in ("txt", "pdf", "html"):
        src = guide_dir / f"Getting_Started.{fmt}"
        if src.exists():
            shutil.copy2(src, dest_dir / f"Getting_Started.{fmt}")
            copied = True
        else:
            print_warning(f"Guide file not found: {src}")
    if copied:
        print_success("Getting Started guides copied")
    return copied


def get_desktop_path() -> Path:
    """Get the desktop path for the current platform."""
    if plat.system() == 'Windows':
        # Windows desktop path
        desktop = Path.home() / 'Desktop'
    elif plat.system() == 'Darwin':  # macOS
        # macOS desktop path
        desktop = Path.home() / 'Desktop'
    else:  # Linux
        # Linux desktop path
        desktop = Path.home() / 'Desktop'
    
    return desktop


def create_zip_file(delivery_dir: Path, company: str) -> Path:
    """Create a zip file of the delivery package on the desktop."""
    print_step(4, "Creating zip file on desktop...")
    
    desktop = get_desktop_path()
    
    # Create zip filename
    zip_name = f"{delivery_dir.name}.zip"
    zip_path = desktop / zip_name
    
    # Remove existing zip if it exists
    if zip_path.exists():
        zip_path.unlink()
        print_warning(f"Removed existing zip file: {zip_path}")
    
    # Create zip file
    try:
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add all files and directories from delivery package
            # This ensures the zip contains the folder structure
            for item in delivery_dir.rglob('*'):
                if item.is_file():
                    # Calculate relative path for archive (includes folder name)
                    arcname = item.relative_to(delivery_dir.parent)
                    zipf.write(item, arcname)
        
        # Get zip file size for display
        zip_size_mb = zip_path.stat().st_size / (1024 * 1024)
        print_success(f"Zip file created: {zip_path}")
        print(f"  Size: {zip_size_mb:.2f} MB")
        return zip_path
    except Exception as e:
        print_error(f"Failed to create zip file: {e}")
        return None


def prompt_for_input(prompt: str, default: str = None, validator=None) -> str:
    """Prompt user for input with optional default and validator."""
    if default:
        full_prompt = f"{prompt} [{default}]: "
    else:
        full_prompt = f"{prompt}: "
    
    while True:
        value = input(full_prompt).strip()
        
        # Use default if empty
        if not value and default:
            value = default
        
        # Validate if validator provided
        if validator:
            error = validator(value)
            if error:
                print_error(error)
                continue
        
        if value:
            return value
        else:
            print_error("This field is required. Please enter a value.")


def validate_date(date_str: str) -> str:
    """Validate date format (YYYY-MM-DD)."""
    if not date_str:
        return "Date is required"
    
    try:
        expiry_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        today = datetime.now().date()
        if expiry_date <= today:
            return "Expiration date must be in the future"
        return None
    except ValueError:
        return "Invalid date format. Use YYYY-MM-DD (e.g., 2027-12-31)"


def validate_platform(platform: str) -> str:
    """Validate platform choice."""
    if not platform:
        return "Platform is required"
    platform_lower = platform.lower()
    if platform_lower not in ['macos', 'windows', '1', '2']:
        return "Please enter 'macos' or 'windows' (or 1/2)"
    return None


def validate_machines(machines_str: str) -> str:
    """Validate number of machines."""
    if not machines_str:
        return None  # Optional field
    try:
        machines = int(machines_str)
        if machines < 1:
            return "Number of machines must be at least 1"
        return None
    except ValueError:
        return "Please enter a valid number"


def get_customer_info():
    """Interactively get customer information."""
    print(f"\n{GREEN}{'='*60}{NC}")
    print(f"{GREEN}PDF Batch Merger - Sales Automation{NC}")
    print(f"{GREEN}{'='*60}{NC}\n")
    print("Please provide the following information:\n")
    
    # Company name
    company = prompt_for_input("Customer company name")
    
    # Expiration date
    default_expires = (datetime.now().replace(year=datetime.now().year + 1)).strftime('%Y-%m-%d')
    expires = prompt_for_input(
        "License expiration date (YYYY-MM-DD)",
        default=default_expires,
        validator=validate_date
    )
    
    # Number of machines
    machines_str = prompt_for_input(
        "Number of allowed machines",
        default="1",
        validator=validate_machines
    )
    machines = int(machines_str) if machines_str else 1
    
    # Platform
    print(f"\n{YELLOW}Select target platform:{NC}")
    print("  1. macOS")
    print("  2. Windows")
    platform_input = prompt_for_input(
        "Platform (1/2 or macos/windows)",
        validator=validate_platform
    )
    platform_lower = platform_input.lower()
    if platform_lower in ['1', 'macos']:
        platform = 'macos'
    else:
        platform = 'windows'
    
    # Skip build option
    skip_build_input = prompt_for_input(
        "Skip building? Use existing build if available (y/n)",
        default="n"
    )
    skip_build = skip_build_input.lower() in ['y', 'yes']
    
    return {
        'company': company,
        'expires': expires,
        'machines': machines,
        'platform': platform,
        'skip_build': skip_build
    }


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Automate sales process: generate license, build app, and package for delivery"
    )
    
    parser.add_argument(
        '--company',
        help='Customer company name'
    )
    parser.add_argument(
        '--expires',
        help='License expiration date (YYYY-MM-DD)'
    )
    parser.add_argument(
        '--machines',
        type=int,
        help='Number of allowed machines (default: 1)'
    )
    parser.add_argument(
        '--platform',
        choices=['macos', 'windows'],
        help='Target platform (macos or windows)'
    )
    parser.add_argument(
        '--private-key',
        type=Path,
        default=Path('tools/private_key.pem'),
        help='Path to private key (default: tools/private_key.pem)'
    )
    parser.add_argument(
        '--skip-build',
        action='store_true',
        help='Skip building the application (use existing build)'
    )
    
    args = parser.parse_args()
    
    # If any required argument is missing, use interactive mode
    if not all([args.company, args.expires, args.platform]):
        customer_info = get_customer_info()
        company = customer_info['company']
        expires = customer_info['expires']
        machines = customer_info['machines']
        platform = customer_info['platform']
        skip_build = customer_info['skip_build']
    else:
        company = args.company
        expires = args.expires
        machines = args.machines if args.machines else 1
        platform = args.platform
        skip_build = args.skip_build
    
    print(f"\n{GREEN}{'='*60}{NC}")
    print(f"{GREEN}PDF Batch Merger - Sales Automation{NC}")
    print(f"{GREEN}{'='*60}{NC}\n")
    print(f"Company: {company}")
    print(f"Expires: {expires}")
    print(f"Machines: {machines}")
    print(f"Platform: {platform}")
    print(f"Version: {APP_VERSION}\n")
    
    # Check prerequisites
    if not check_prerequisites():
        sys.exit(1)
    
    # Generate license
    print_step(1, "Generating license...")
    license_path = Path('deliveries') / f"license_{company.replace(' ', '_')}.json"
    license_path.parent.mkdir(parents=True, exist_ok=True)
    
    if not generate_license(
        company=company,
        expires=expires,
        allowed_machines=machines,
        version=APP_VERSION,
        private_key_path=args.private_key,
        output_path=license_path
    ):
        print_error("License generation failed")
        sys.exit(1)
    
    # Build application
    if not skip_build:
        if not build_application(platform):
            print_error("Build failed")
            sys.exit(1)
    else:
        print_warning("Skipping build (using existing build)")
    
    # Create delivery package
    delivery_dir = create_delivery_package(company, platform, license_path)
    if not delivery_dir:
        print_error("Failed to create delivery package")
        sys.exit(1)
    
    # Create zip file on desktop
    zip_path = create_zip_file(delivery_dir, company)
    
    # Summary
    print(f"\n{GREEN}{'='*60}{NC}")
    print(f"{GREEN}✓ Sales package created successfully!{NC}")
    print(f"{GREEN}{'='*60}{NC}\n")
    print(f"Delivery package location: {delivery_dir}")
    if zip_path:
        print(f"Zip file location: {zip_path}")
    print(f"\nPackage contents:")
    print(f"  - Application ({platform})")
    print(f"  - license.json")
    print(f"  - User_Guide.md")
    print(f"  - Getting_Started.txt / .pdf / .html")
    print(f"\nReady to deliver to: {company}")
    if zip_path:
        print(f"\n{YELLOW}💡 Tip: Send the zip file to your client: {zip_path.name}{NC}\n")
    else:
        print()


if __name__ == '__main__':
    main()
