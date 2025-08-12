"""
libadic version information.
"""

__version__ = "1.0.0"
__version_info__ = (1, 0, 0)

# Build and release information
__build_date__ = "2025-08-11"
__git_revision__ = None  # Will be populated by CI/CD

# Feature flags
__has_crypto__ = True
__has_elliptic__ = True  
__has_bigint__ = True

def get_version():
    """Get the libadic version string."""
    return __version__

def get_version_info():
    """Get the libadic version as a tuple."""
    return __version_info__

def show_versions():
    """Print version information for libadic and dependencies."""
    print(f"libadic: {__version__}")
    print(f"Build date: {__build_date__}")
    
    try:
        import numpy
        print(f"NumPy: {numpy.__version__}")
    except ImportError:
        print("NumPy: not available")
    
    # Show feature availability
    features = []
    if __has_crypto__:
        features.append("cryptography")
    if __has_elliptic__:
        features.append("elliptic curves") 
    if __has_bigint__:
        features.append("big integers")
    
    if features:
        print(f"Features: {', '.join(features)}")
    else:
        print("Features: core only")

# Export for backward compatibility
version = __version__
version_info = __version_info__