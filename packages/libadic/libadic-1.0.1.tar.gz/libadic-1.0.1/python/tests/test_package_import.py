"""
Test package installation and import functionality.
These tests ensure the package can be properly installed and imported.
"""

import pytest
import sys
import importlib


class TestPackageImport:
    """Test basic package import functionality."""
    
    def test_basic_import(self):
        """Test that libadic can be imported."""
        try:
            import libadic
            assert libadic.__version__ is not None
            assert libadic.__author__ is not None
        except ImportError as e:
            pytest.fail(f"Failed to import libadic: {e}")
    
    def test_version_info(self):
        """Test that version information is available."""
        import libadic
        
        # Check version string format
        version = libadic.__version__
        assert isinstance(version, str)
        assert len(version.split('.')) >= 2  # At least major.minor
        
        # Test show_versions function
        try:
            libadic.show_versions()
        except Exception as e:
            pytest.fail(f"show_versions() failed: {e}")
    
    def test_core_classes_available(self):
        """Test that core mathematical classes can be imported."""
        import libadic
        
        # Test basic p-adic classes
        required_classes = ['Zp', 'Qp', 'BigInt']
        for cls_name in required_classes:
            assert hasattr(libadic, cls_name), f"Missing class: {cls_name}"
    
    def test_mathematical_functions_available(self):
        """Test that core mathematical functions are available."""
        import libadic
        
        # Test mathematical functions
        required_functions = ['gamma_p', 'log_p', 'bernoulli']
        for func_name in required_functions:
            assert hasattr(libadic, func_name), f"Missing function: {func_name}"
    
    def test_crypto_import(self):
        """Test that crypto components can be imported."""
        try:
            from libadic.crypto import PadicLattice, SecurityLevel, PadicPRNG
            
            # Test that classes are available
            assert PadicLattice is not None
            assert SecurityLevel is not None
            assert PadicPRNG is not None
            
        except ImportError as e:
            pytest.fail(f"Failed to import crypto components: {e}")
    
    def test_security_levels_enum(self):
        """Test that SecurityLevel enum works correctly."""
        from libadic.crypto import SecurityLevel
        
        # Test enum values
        assert hasattr(SecurityLevel, 'DEMO')
        assert hasattr(SecurityLevel, 'LEVEL_1') 
        assert hasattr(SecurityLevel, 'LEVEL_3')
        assert hasattr(SecurityLevel, 'LEVEL_5')


class TestBasicFunctionality:
    """Test basic functionality to ensure library is working."""
    
    def test_basic_padic_arithmetic(self):
        """Test basic p-adic arithmetic operations."""
        import libadic
        
        try:
            # Create a simple p-adic integer
            x = libadic.Zp(7, 10, 42)
            
            # Basic operations
            y = x + x
            z = x * libadic.Zp(7, 10, 2)
            
            assert y is not None
            assert z is not None
            
        except Exception as e:
            pytest.fail(f"Basic p-adic arithmetic failed: {e}")
    
    def test_crypto_basic_functionality(self):
        """Test basic crypto functionality."""
        from libadic.crypto import PadicLattice, SecurityLevel
        
        try:
            # Create a demo lattice (fastest for testing)
            lattice = PadicLattice(SecurityLevel.DEMO)
            
            # Generate keys
            lattice.generate_keys()
            
            # Test encryption/decryption  
            message = [1, 2, 3, 4]
            ciphertext = lattice.encrypt(message)
            decrypted = lattice.decrypt(ciphertext)
            
            assert ciphertext is not None
            assert decrypted is not None
            assert len(decrypted) >= len(message)
            
        except Exception as e:
            pytest.fail(f"Basic crypto functionality failed: {e}")
    
    def test_bigint_functionality(self):
        """Test BigInt operations."""
        import libadic
        
        try:
            # Create BigInt instances
            a = libadic.BigInt(123456789)
            b = libadic.BigInt(987654321)
            
            # Basic operations
            c = a + b
            d = a * b
            
            assert c is not None
            assert d is not None
            
        except Exception as e:
            pytest.fail(f"BigInt functionality failed: {e}")


class TestPackageStructure:
    """Test package structure and organization."""
    
    def test_submodules_structure(self):
        """Test that expected submodules are available."""
        import libadic
        
        # Check that crypto submodule is available
        try:
            from libadic import crypto
            assert crypto is not None
        except ImportError:
            pytest.fail("crypto submodule not available")
    
    def test_no_missing_dependencies(self):
        """Test that all required dependencies are available."""
        try:
            import numpy
            assert numpy.__version__ is not None
        except ImportError:
            pytest.fail("NumPy dependency not available")
    
    def test_c_extension_loaded(self):
        """Test that the C++ extension module is loaded."""
        import libadic
        
        # The _libadic module should be loaded
        assert hasattr(libadic, '_libadic')
        assert libadic._libadic is not None


if __name__ == "__main__":
    # Allow running tests directly
    pytest.main([__file__, "-v"])