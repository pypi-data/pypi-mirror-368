#!/usr/bin/env python3
"""
Nedo Vision Worker Service Doctor

This module provides diagnostic capabilities to check system requirements
and dependencies for the Nedo Vision Worker Service.
"""

import subprocess
import sys
import platform
import shutil
import os
from pathlib import Path


def check_python_version():
    """Check if Python version meets requirements."""
    print("🐍 Checking Python version...")
    
    version = sys.version_info
    min_version = (3, 8)
    
    if version >= min_version:
        print(f"   ✅ Python {version.major}.{version.minor}.{version.micro} (meets requirement >= {min_version[0]}.{min_version[1]})")
        return True
    else:
        print(f"   ❌ Python {version.major}.{version.minor}.{version.micro} (requires >= {min_version[0]}.{min_version[1]})")
        return False


def check_ffmpeg():
    """Check if FFmpeg is installed and accessible."""
    print("🎬 Checking FFmpeg...")
    
    try:
        # Check if ffmpeg is in PATH
        ffmpeg_path = shutil.which("ffmpeg")
        if not ffmpeg_path:
            print("   ❌ FFmpeg not found in PATH")
            return False
        
        # Check ffmpeg version
        result = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            # Extract version from output
            version_line = result.stdout.split('\n')[0]
            print(f"   ✅ {version_line}")
            print(f"   📍 Location: {ffmpeg_path}")
            return True
        else:
            print("   ❌ FFmpeg found but failed to get version")
            return False
            
    except subprocess.TimeoutExpired:
        print("   ❌ FFmpeg check timed out")
        return False
    except Exception as e:
        print(f"   ❌ Error checking FFmpeg: {e}")
        return False


def check_opencv():
    """Check if OpenCV is properly installed."""
    print("👁️ Checking OpenCV...")
    
    try:
        import cv2
        version = cv2.__version__
        build_info = cv2.getBuildInformation()
        
        print(f"   ✅ OpenCV {version} installed")
        
        # Check OpenCV build configuration
        if "CUDA" in build_info:
            print("   🚀 OpenCV built with CUDA support")
        if "OpenMP" in build_info:
            print("   ⚡ OpenCV built with OpenMP support")
        
        # Check for platform-specific optimizations
        machine = platform.machine()
        if machine in ["aarch64", "armv7l", "arm64"]:
            if "NEON" in build_info:
                print("   🎯 OpenCV built with ARM NEON optimizations")
            else:
                print("   ⚠️ OpenCV may not have ARM optimizations")
        
        # Test basic functionality
        import numpy as np
        test_img = np.zeros((100, 100, 3), dtype=np.uint8)
        
        # Test encoding/decoding
        _, encoded = cv2.imencode('.jpg', test_img)
        decoded = cv2.imdecode(encoded, cv2.IMREAD_COLOR)
        
        if decoded is not None:
            print("   ✅ OpenCV basic functionality working")
            return True
        else:
            print("   ❌ OpenCV encoding/decoding test failed")
            return False
            
    except ImportError:
        print("   ❌ OpenCV not installed")
        return False
    except Exception as e:
        print(f"   ❌ OpenCV test failed: {e}")
        return False


def check_grpc():
    """Check if gRPC is properly installed."""
    print("🌐 Checking gRPC...")
    
    try:
        import grpc
        print(f"   ✅ gRPC installed")
        
        # Test basic gRPC functionality
        from grpc import StatusCode
        print("   ✅ gRPC basic imports working")
        return True
        
    except ImportError:
        print("   ❌ gRPC not installed")
        return False
    except Exception as e:
        print(f"   ❌ gRPC test failed: {e}")
        return False


def check_pynvml():
    """Check if pynvml (NVIDIA management) is available."""
    print("🎮 Checking NVIDIA GPU support...")
    
    try:
        import pynvml
        pynvml.nvmlInit()
        
        device_count = pynvml.nvmlDeviceGetCount()
        if device_count > 0:
            for i in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                name = pynvml.nvmlDeviceGetName(handle)
                # Handle both string and bytes return types for compatibility
                if isinstance(name, bytes):
                    name = name.decode('utf-8')
                
                # Get additional GPU information
                try:
                    memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                    memory_total_gb = memory_info.total / (1024**3)
                    print(f"   ✅ GPU {i}: {name}")
                    print(f"      💾 Memory: {memory_total_gb:.1f} GB")
                    
                    # Check for Jetson-specific GPUs
                    if "tegra" in name.lower() or "jetson" in name.lower():
                        print("      🚀 Jetson GPU detected")
                    
                    # Check compute capability for deep learning
                    try:
                        major, minor = pynvml.nvmlDeviceGetCudaComputeCapability(handle)
                        print(f"      🔢 Compute Capability: {major}.{minor}")
                        if major >= 6:  # Pascal architecture or newer
                            print("      ✅ GPU supports modern deep learning frameworks")
                        else:
                            print("      ⚠️ GPU may have limited deep learning support")
                    except:
                        pass
                        
                except Exception as e:
                    print(f"   ✅ GPU {i}: {name} (limited info: {e})")
            
            return True
        else:
            print("   ⚠️ pynvml installed but no NVIDIA GPUs detected")
            # Check if we're on ARM and might have integrated GPU
            if platform.machine() in ["aarch64", "armv7l", "arm64"]:
                print("   💡 ARM device may use integrated GPU (Mali, Adreno, etc.)")
            return True  # Not an error, just no NVIDIA GPU
            
    except ImportError:
        print("   ❌ pynvml not installed")
        print("   💡 Install with: pip install pynvml")
        return False
    except Exception as e:
        print(f"   ⚠️ GPU check failed: {e}")
        # More helpful error messages for common issues
        if "driver" in str(e).lower():
            print("   💡 NVIDIA drivers may not be installed")
        elif "nvml" in str(e).lower():
            print("   💡 NVIDIA Management Library not available")
        return True  # Not critical for service operation


def check_storage_permissions():
    """Check if we can create storage directories."""
    print("💾 Checking storage permissions...")
    
    try:
        # Test default storage path
        test_path = Path("data") / "test_permissions"
        test_path.mkdir(parents=True, exist_ok=True)
        
        # Test file creation
        test_file = test_path / "test.txt"
        test_file.write_text("test")
        
        # Test file reading
        content = test_file.read_text()
        
        # Cleanup
        test_file.unlink()
        test_path.rmdir()
        
        if content == "test":
            print("   ✅ Storage read/write permissions OK")
            return True
        else:
            print("   ❌ Storage read/write test failed")
            return False
            
    except Exception as e:
        print(f"   ❌ Storage permission check failed: {e}")
        return False


def check_network_connectivity():
    """Check basic network connectivity."""
    print("🌐 Checking network connectivity...")
    
    try:
        import socket
        
        # Test DNS resolution
        socket.gethostbyname("be.vision.sindika.co.id")
        print("   ✅ DNS resolution working (be.vision.sindika.co.id)")
        
        # Test basic socket connectivity
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex(("be.vision.sindika.co.id", 50051))
        sock.close()
        
        if result == 0:
            print("   ✅ Network connectivity to be.vision.sindika.co.id:50051 OK")
            return True
        else:
            print("   ⚠️ Cannot connect to be.vision.sindika.co.id:50051 (may be normal if service is down)")
            return True  # Not critical for initial setup
            
    except Exception as e:
        print(f"   ⚠️ Network check failed: {e}")
        return True  # Not critical for service installation


def check_platform_compatibility():
    """Check platform-specific compatibility."""
    print("🔧 Checking platform compatibility...")
    
    system = platform.system()
    machine = platform.machine()
    
    # Check for known compatible platforms
    compatible_platforms = {
        "Linux": ["x86_64", "aarch64", "armv7l", "arm64"],
        "Windows": ["AMD64", "x86_64"],
        "Darwin": ["x86_64", "arm64"]  # macOS Intel and Apple Silicon
    }
    
    if system in compatible_platforms:
        if machine in compatible_platforms[system]:
            print(f"   ✅ Platform {system}/{machine} is supported")
            
            # Special handling for ARM devices
            if machine in ["aarch64", "armv7l", "arm64"]:
                print("   📱 ARM-based device detected")
                if "tegra" in platform.platform().lower():
                    print("   🚀 NVIDIA Jetson device detected")
                elif "raspberry" in platform.platform().lower():
                    print("   🍓 Raspberry Pi device detected")
            
            return True
        else:
            print(f"   ⚠️ Architecture {machine} may have limited support on {system}")
            return True  # Still allow execution
    else:
        print(f"   ⚠️ Platform {system} may have limited support")
        return True  # Still allow execution


def print_system_info():
    """Print basic system information."""
    print("💻 System Information:")
    print(f"   🖥️ OS: {platform.system()} {platform.release()}")
    print(f"   🏗️ Architecture: {platform.machine()}")
    print(f"   🐍 Python: {platform.python_version()}")
    print(f"   📍 Python executable: {sys.executable}")
    
    # Additional platform details
    try:
        import os
        if hasattr(os, 'uname'):
            uname = os.uname()
            print(f"   🔧 Kernel: {uname.sysname} {uname.release}")
    except:
        pass
    
    # Check for containerized environment
    if Path("/.dockerenv").exists():
        print("   🐳 Running in Docker container")
    elif os.environ.get("KUBERNETES_SERVICE_HOST"):
        print("   ☸️ Running in Kubernetes pod")


def print_installation_help():
    """Print installation help for missing dependencies."""
    print("\n📋 Installation Help:")
    print("=" * 50)
    
    system = platform.system()
    machine = platform.machine()
    
    print("\n🎬 FFmpeg Installation:")
    if system == "Windows":
        print("   • Using Chocolatey: choco install ffmpeg")
        print("   • Using winget: winget install FFmpeg")
        print("   • Manual: Download from https://ffmpeg.org/download.html")
    elif system == "Darwin":  # macOS
        print("   • Using Homebrew: brew install ffmpeg")
        print("   • Using MacPorts: sudo port install ffmpeg")
    else:  # Linux
        print("   • Ubuntu/Debian: sudo apt update && sudo apt install ffmpeg")
        print("   • CentOS/RHEL: sudo yum install ffmpeg")
        print("   • Fedora: sudo dnf install ffmpeg")
        print("   • Alpine: apk add ffmpeg")
        
        # ARM-specific guidance
        if machine in ["aarch64", "armv7l", "arm64"]:
            print("   • For ARM devices:")
            print("     - Jetson: Usually pre-installed with JetPack")
            print("     - Raspberry Pi: sudo apt install ffmpeg")
            print("     - Build from source for optimal performance")
    
    print("\n🐍 Python Dependencies:")
    print("   • Install all: pip install -r requirements.txt")
    print("   • Or install individually:")
    print("     - pip install opencv-python")
    print("     - pip install grpcio")
    print("     - pip install pynvml")
    
    # Platform-specific OpenCV guidance
    if machine in ["aarch64", "armv7l", "arm64"]:
        print("\n🔧 ARM-Specific Notes:")
        print("   • OpenCV: Consider opencv-python-headless for servers")
        print("   • Jetson: Use opencv built with JetPack for GPU acceleration")
        print("   • Build from source for optimal ARM performance")
        print("   • For Jetson: Install with 'sudo apt install python3-opencv'")
    
    print("\n🎮 GPU Support:")
    if system == "Linux" and machine in ["aarch64", "armv7l"]:
        print("   • Jetson devices:")
        print("     - Install JetPack SDK from NVIDIA")
        print("     - Verify with: sudo /usr/bin/tegrastats")
        print("     - Check CUDA: nvcc --version")
    else:
        print("   • NVIDIA GPU (Optional):")
        print("     - Install NVIDIA drivers from https://www.nvidia.com/drivers/")
        print("     - Install CUDA toolkit if needed")
        print("     - pynvml should work automatically if drivers are installed")
    
    print("\n☁️ Cloud/Container Deployment:")
    print("   • Docker: Use nvidia/cuda base images for GPU support")
    print("   • Cloud: Ensure GPU instances have proper drivers")
    print("   • Kubernetes: Use nvidia.com/gpu resource limits")
    print("   • AWS: Use Deep Learning AMI or ECS GPU instances")
    print("   • GCP: Use AI Platform or GPU-enabled Compute instances")
    
    print("\n📦 Package Installation Tips:")
    print("   • Use virtual environments: python -m venv venv")
    print("   • Update pip: pip install --upgrade pip")
    print("   • For ARM: pip install --extra-index-url https://www.piwheels.org/simple/")
    print("   • Build tools: sudo apt install build-essential python3-dev")


def main():
    """Run all diagnostic checks."""
    print("🏥 Nedo Vision Worker Service Doctor")
    print("=" * 50)
    
    # Print system info
    print_system_info()
    print()
    
    # Run all checks
    checks = [
        ("Platform Compatibility", check_platform_compatibility),
        ("Python Version", check_python_version),
        ("FFmpeg", check_ffmpeg),
        ("OpenCV", check_opencv),
        ("gRPC", check_grpc),
        ("NVIDIA GPU Support", check_pynvml),
        ("Storage Permissions", check_storage_permissions),
        ("Network Connectivity", check_network_connectivity),
    ]
    
    results = []
    print("🔍 Running Diagnostic Checks:")
    print("-" * 30)
    
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"   ❌ {name} check failed with exception: {e}")
            results.append((name, False))
        print()
    
    # Summary
    print("📊 Summary:")
    print("-" * 20)
    
    passed = 0
    failed = 0
    
    for name, result in results:
        if result:
            print(f"   ✅ {name}")
            passed += 1
        else:
            print(f"   ❌ {name}")
            failed += 1
    
    print(f"\n🎯 Results: {passed} passed, {failed} failed")
    
    if failed > 0:
        print("\n⚠️ Some checks failed. See installation help below:")
        print_installation_help()
        return 1
    else:
        print("\n🎉 All checks passed! Your system is ready for Nedo Vision Worker Service.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
