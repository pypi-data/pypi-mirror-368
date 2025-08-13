"""
Google Colab Dependency Installation Template

This module provides a robust installation system for OpenSearch demos in Google Colab.
It includes retry logic, progress indicators, and comprehensive error handling.
"""

import subprocess
import sys
import time
import importlib
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass


@dataclass
class PackageInfo:
    """Information about a package to install."""
    name: str
    version: Optional[str] = None
    import_name: Optional[str] = None
    description: str = ""
    
    @property
    def pip_spec(self) -> str:
        """Get the pip specification for this package."""
        if self.version:
            return f"{self.name}>={self.version}"
        return self.name
    
    @property
    def check_name(self) -> str:
        """Get the name to use for import checking."""
        return self.import_name or self.name.replace('-', '_')


class ColabInstaller:
    """Robust package installer for Google Colab environment."""
    
    # Core packages required for OpenSearch demos
    CORE_PACKAGES = [
        PackageInfo(
            name="opensearch-py",
            version="2.4.0",
            import_name="opensearchpy",
            description="OpenSearch Python client"
        ),
        PackageInfo(
            name="opensearch-demos-utils",
            version="1.0.0",
            description="OpenSearch demo utilities"
        ),
        PackageInfo(
            name="pandas",
            version="1.3.0",
            description="Data manipulation and analysis"
        ),
        PackageInfo(
            name="matplotlib",
            version="3.5.0",
            description="Data visualization"
        ),
        PackageInfo(
            name="seaborn",
            version="0.11.0",
            description="Statistical data visualization"
        ),
        PackageInfo(
            name="requests",
            version="2.25.0",
            description="HTTP library"
        ),
        PackageInfo(
            name="numpy",
            version="1.21.0",
            description="Numerical computing"
        )
    ]
    
    def __init__(self, max_retries: int = 3, retry_delay: float = 2.0):
        """Initialize the installer with retry configuration."""
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.installation_log: List[Dict] = []
    
    def check_package_installed(self, package: PackageInfo) -> bool:
        """Check if a package is already installed and importable."""
        try:
            importlib.import_module(package.check_name)
            return True
        except ImportError:
            return False
    
    def install_package(self, package: PackageInfo) -> Tuple[bool, str]:
        """
        Install a single package with retry logic.
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        for attempt in range(self.max_retries):
            try:
                # Run pip install
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "install", package.pip_spec],
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minute timeout
                )
                
                if result.returncode == 0:
                    # Verify the package can be imported
                    if self.check_package_installed(package):
                        return True, f"Successfully installed {package.name}"
                    else:
                        return False, f"Package {package.name} installed but cannot be imported"
                else:
                    error_msg = result.stderr.strip() or result.stdout.strip()
                    if attempt < self.max_retries - 1:
                        print(f"⚠️  Attempt {attempt + 1}/{self.max_retries} failed for {package.name}")
                        print(f"   Error: {error_msg}")
                        print(f"   Retrying in {self.retry_delay} seconds...")
                        time.sleep(self.retry_delay)
                    else:
                        return False, f"Failed to install {package.name}: {error_msg}"
                        
            except subprocess.TimeoutExpired:
                if attempt < self.max_retries - 1:
                    print(f"⚠️  Installation timeout for {package.name} (attempt {attempt + 1}/{self.max_retries})")
                    print(f"   Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                else:
                    return False, f"Installation timeout for {package.name}"
                    
            except Exception as e:
                if attempt < self.max_retries - 1:
                    print(f"⚠️  Unexpected error installing {package.name} (attempt {attempt + 1}/{self.max_retries})")
                    print(f"   Error: {str(e)}")
                    print(f"   Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                else:
                    return False, f"Unexpected error installing {package.name}: {str(e)}"
        
        return False, f"Failed to install {package.name} after {self.max_retries} attempts"
    
    def install_all_packages(self, packages: Optional[List[PackageInfo]] = None) -> Dict:
        """
        Install all required packages with progress tracking.
        
        Returns:
            Dictionary with installation results and statistics
        """
        if packages is None:
            packages = self.CORE_PACKAGES
        
        print("🚀 Starting OpenSearch demos dependency installation...")
        print(f"📦 Installing {len(packages)} packages with up to {self.max_retries} retries each")
        print("=" * 60)
        
        results = {
            'successful': [],
            'failed': [],
            'skipped': [],
            'total': len(packages),
            'start_time': time.time()
        }
        
        for i, package in enumerate(packages, 1):
            print(f"\n[{i}/{len(packages)}] {package.name}")
            print(f"📝 {package.description}")
            
            # Check if already installed
            if self.check_package_installed(package):
                print(f"✅ Already installed and working")
                results['skipped'].append(package.name)
                continue
            
            # Install the package
            print(f"📥 Installing {package.pip_spec}...")
            success, message = self.install_package(package)
            
            if success:
                print(f"✅ {message}")
                results['successful'].append(package.name)
            else:
                print(f"❌ {message}")
                results['failed'].append(package.name)
                
                # Log detailed error information
                self.installation_log.append({
                    'package': package.name,
                    'error': message,
                    'timestamp': time.time()
                })
        
        # Print summary
        results['end_time'] = time.time()
        results['duration'] = results['end_time'] - results['start_time']
        
        self._print_installation_summary(results)
        return results
    
    def _print_installation_summary(self, results: Dict):
        """Print a comprehensive installation summary."""
        print("\n" + "=" * 60)
        print("📊 INSTALLATION SUMMARY")
        print("=" * 60)
        
        print(f"⏱️  Total time: {results['duration']:.1f} seconds")
        print(f"📦 Total packages: {results['total']}")
        print(f"✅ Successful: {len(results['successful'])}")
        print(f"⏭️  Skipped (already installed): {len(results['skipped'])}")
        print(f"❌ Failed: {len(results['failed'])}")
        
        if results['successful']:
            print(f"\n✅ Successfully installed:")
            for package in results['successful']:
                print(f"   • {package}")
        
        if results['skipped']:
            print(f"\n⏭️  Skipped (already working):")
            for package in results['skipped']:
                print(f"   • {package}")
        
        if results['failed']:
            print(f"\n❌ Failed installations:")
            for package in results['failed']:
                print(f"   • {package}")
            print(f"\n🔧 Troubleshooting tips:")
            print(f"   • Try restarting your Colab runtime")
            print(f"   • Check your internet connection")
            print(f"   • Some packages may require specific Colab configurations")
        
        # Overall status
        if not results['failed']:
            print(f"\n🎉 All dependencies installed successfully!")
            print(f"   You're ready to run OpenSearch demos!")
        else:
            print(f"\n⚠️  Some packages failed to install.")
            print(f"   You may encounter issues running certain demos.")
    
    def verify_installation(self) -> bool:
        """Verify that all core packages are properly installed."""
        print("\n🔍 Verifying installation...")
        
        all_working = True
        for package in self.CORE_PACKAGES:
            try:
                importlib.import_module(package.check_name)
                print(f"✅ {package.name} - OK")
            except ImportError as e:
                print(f"❌ {package.name} - FAILED: {e}")
                all_working = False
        
        if all_working:
            print("\n🎉 All packages verified successfully!")
        else:
            print("\n⚠️  Some packages are not working properly.")
            
        return all_working


def create_colab_installation_cell() -> str:
    """
    Generate the complete installation cell code for Colab notebooks.
    
    Returns:
        String containing the complete installation cell code
    """
    return '''# OpenSearch Demos - Dependency Installation
# Run this cell to install all required packages for OpenSearch demos

import subprocess
import sys
import time
import importlib
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

@dataclass
class PackageInfo:
    """Information about a package to install."""
    name: str
    version: Optional[str] = None
    import_name: Optional[str] = None
    description: str = ""
    
    @property
    def pip_spec(self) -> str:
        if self.version:
            return f"{self.name}>={self.version}"
        return self.name
    
    @property
    def check_name(self) -> str:
        return self.import_name or self.name.replace('-', '_')

class ColabInstaller:
    """Robust package installer for Google Colab."""
    
    CORE_PACKAGES = [
        PackageInfo("opensearch-py", "2.4.0", "opensearchpy", "OpenSearch Python client"),
        PackageInfo("opensearch-demos-utils", "1.0.0", None, "OpenSearch demo utilities"),
        PackageInfo("pandas", "1.3.0", None, "Data manipulation and analysis"),
        PackageInfo("matplotlib", "3.5.0", None, "Data visualization"),
        PackageInfo("seaborn", "0.11.0", None, "Statistical data visualization"),
        PackageInfo("requests", "2.25.0", None, "HTTP library"),
        PackageInfo("numpy", "1.21.0", None, "Numerical computing")
    ]
    
    def __init__(self, max_retries: int = 3, retry_delay: float = 2.0):
        self.max_retries = max_retries
        self.retry_delay = retry_delay
    
    def check_package_installed(self, package: PackageInfo) -> bool:
        try:
            importlib.import_module(package.check_name)
            return True
        except ImportError:
            return False
    
    def install_package(self, package: PackageInfo) -> Tuple[bool, str]:
        for attempt in range(self.max_retries):
            try:
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "install", package.pip_spec],
                    capture_output=True, text=True, timeout=300
                )
                
                if result.returncode == 0:
                    if self.check_package_installed(package):
                        return True, f"Successfully installed {package.name}"
                    else:
                        return False, f"Package {package.name} installed but cannot be imported"
                else:
                    error_msg = result.stderr.strip() or result.stdout.strip()
                    if attempt < self.max_retries - 1:
                        print(f"⚠️  Attempt {attempt + 1}/{self.max_retries} failed for {package.name}")
                        print(f"   Retrying in {self.retry_delay} seconds...")
                        time.sleep(self.retry_delay)
                    else:
                        return False, f"Failed to install {package.name}: {error_msg}"
                        
            except subprocess.TimeoutExpired:
                if attempt < self.max_retries - 1:
                    print(f"⚠️  Installation timeout for {package.name} (attempt {attempt + 1}/{self.max_retries})")
                    time.sleep(self.retry_delay)
                else:
                    return False, f"Installation timeout for {package.name}"
            except Exception as e:
                if attempt < self.max_retries - 1:
                    print(f"⚠️  Unexpected error installing {package.name}")
                    time.sleep(self.retry_delay)
                else:
                    return False, f"Unexpected error: {str(e)}"
        
        return False, f"Failed after {self.max_retries} attempts"
    
    def install_all_packages(self) -> Dict:
        print("🚀 Starting OpenSearch demos dependency installation...")
        print(f"📦 Installing {len(self.CORE_PACKAGES)} packages with up to {self.max_retries} retries each")
        print("=" * 60)
        
        results = {'successful': [], 'failed': [], 'skipped': [], 'total': len(self.CORE_PACKAGES)}
        
        for i, package in enumerate(self.CORE_PACKAGES, 1):
            print(f"\\n[{i}/{len(self.CORE_PACKAGES)}] {package.name}")
            print(f"📝 {package.description}")
            
            if self.check_package_installed(package):
                print(f"✅ Already installed and working")
                results['skipped'].append(package.name)
                continue
            
            print(f"📥 Installing {package.pip_spec}...")
            success, message = self.install_package(package)
            
            if success:
                print(f"✅ {message}")
                results['successful'].append(package.name)
            else:
                print(f"❌ {message}")
                results['failed'].append(package.name)
        
        # Print summary
        print("\\n" + "=" * 60)
        print("📊 INSTALLATION SUMMARY")
        print("=" * 60)
        print(f"📦 Total packages: {results['total']}")
        print(f"✅ Successful: {len(results['successful'])}")
        print(f"⏭️  Skipped: {len(results['skipped'])}")
        print(f"❌ Failed: {len(results['failed'])}")
        
        if results['failed']:
            print(f"\\n❌ Failed installations: {', '.join(results['failed'])}")
            print(f"🔧 Try restarting your runtime if you encounter issues")
        else:
            print(f"\\n🎉 All dependencies installed successfully!")
            print(f"   You're ready to run OpenSearch demos!")
        
        return results

# Run the installation
installer = ColabInstaller()
installation_results = installer.install_all_packages()

# Verify core imports work
print("\\n🔍 Verifying core imports...")
try:
    import opensearchpy
    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sns
    import numpy as np
    import requests
    print("✅ All core packages imported successfully!")
except ImportError as e:
    print(f"❌ Import verification failed: {e}")
    print("🔧 You may need to restart your runtime")

print("\\n" + "=" * 60)
print("🎯 READY TO START!")
print("You can now run the OpenSearch demo notebooks.")
print("=" * 60)
'''


# Example usage for testing
if __name__ == "__main__":
    installer = ColabInstaller()
    results = installer.install_all_packages()
    installer.verify_installation()