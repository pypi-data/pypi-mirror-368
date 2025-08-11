################################################################################
# ⚠️⚠️⚠️ CRITICAL SECURITY WARNING - MUST READ BEFORE MODIFYING ⚠️⚠️⚠️
################################################################################
#
# This setup.py builds PROPRIETARY Cython extensions for MareArts ANPR
#
# 🚨 SECURITY RULES - VIOLATIONS WILL COMPROMISE THE PRODUCT:
#
# 1. NEVER include .pyx source files in distributions
# 2. NEVER include .c/.cpp generated files in sdist 
# 3. NEVER expose marearts_protect.py source code
# 4. NEVER include debug symbols in production builds
# 5. NEVER include sensitive file paths or credentials
#
# 📦 DISTRIBUTION RULES:
# - Wheels (.whl): Include ONLY compiled .so/.pyd files
# - Source dist (.tar.gz): Include ONLY safe Python wrappers
# - Use MANIFEST.in to strictly control sdist contents
#
# 🔒 The packages= line MUST be:
#    packages=['marearts_anpr']  # NOT find_packages()
#
# ⚠️ find_packages() will include unwanted directories!
#
################################################################################

from setuptools import setup, Extension, find_packages
from setuptools.command.build_ext import build_ext
from Cython.Build import cythonize
import numpy
import platform
import subprocess
import os
import hashlib
import json
from pathlib import Path

# Enhanced security compilation flags for enterprise-grade protection (PRODUCTION MODE)
security_compile_flags = [
    "-O3",                              # Maximum optimization
    "-DNPY_NO_DEPRECATED_API=NPY_1_7_API_VERSION",  # NumPy compatibility
    "-DNDEBUG",                         # Disable debug assertions
    "-fvisibility=hidden",              # Hide symbols by default
    "-fvisibility-inlines-hidden",      # Hide inline functions
    # Selectively export PyInit functions (required for Python import)
    "-Wl,--dynamic-list-data",          # Keep dynamic symbols for module loading
    "-fstack-protector-strong",         # Stack smashing protection
    "-D_FORTIFY_SOURCE=2",              # Runtime buffer overflow detection
    "-fdata-sections",                  # Separate data sections
    "-ffunction-sections",              # Separate function sections
    "-DCYTHON_WITHOUT_ASSERTIONS",      # Remove Cython assertions
    "-fPIC",                            # Position independent code
    
    # PRODUCTION MODE - Remove ALL debug information and runtime strings
    "-DCYTHON_FAST_PYCALL",             # Fast Python calls (less debug info)
    "-DCYTHON_PEP489_MULTI_PHASE_INIT=0", # Disable multi-phase init (less strings)
    "-DCYTHON_USE_PYLONG_INTERNALS=0",  # Don't expose PyLong internals
    "-DCYTHON_USE_PYLIST_INTERNALS=0",  # Don't expose PyList internals
    "-DCYTHON_USE_UNICODE_INTERNALS=0", # Don't expose Unicode internals
    "-DCYTHON_COMPILING_IN_CPYTHON=1",  # Optimize for CPython
    # Note: Symbol table controlled by export_symbols.map instead of -s flag
    "-fomit-frame-pointer",             # Remove frame pointers (less debug info)
    "-DCYTHON_WITHOUT_ASSERTIONS",      # Remove runtime assertions
    "-DCYTHON_TRACE=0",                 # Disable tracing (removes function names)
    "-DCYTHON_TRACE_NOGIL=0",           # Disable nogil tracing
    "-fdata-sections",                  # Separate data sections for better stripping
    "-ffunction-sections",              # Separate function sections for better stripping
    # Note: PyInit functions explicitly exported via export_symbols.map
    
    # AGGRESSIVE STRING HIDING
    "-DCYTHON_HIDE_INTERNALS",          # Hide internal strings
    "-DCYTHON_LIMITED_API=0",           # Don't use limited API (reduces strings)
    "-DCYTHON_FAST_THREAD_STATE",       # Fast thread state (less debug)
    "-DCYTHON_USE_TYPE_SLOTS=0",        # Don't use type slots (reduces strings)
]

# Platform-specific security flags
security_link_flags = []
if platform.system() == "Linux":
    security_compile_flags.extend([
        "-Wformat",                     # Format string vulnerability protection
        "-Wformat-security",            # Additional format string checks
        "-Werror=format-security",      # Treat format security warnings as errors
    ])
    security_link_flags.extend([
        "-Wl,-z,relro",                 # Read-only relocations
        "-Wl,-z,now",                   # Immediate binding (full RELRO)
        # Use version script to control symbol visibility - only export PyInit functions
        # "-Wl,--version-script=export_symbols.map",  # Removed - clean build without symbol hiding
        "-Wl,--build-id=none",          # Don't add build ID (removes metadata)
    ])
elif platform.system() == "Darwin":  # macOS
    security_link_flags.extend([
        "-Wl,-dead_strip",              # Remove unused code (macOS equivalent)
        "-Wl,-x",                       # Strip local symbols
        "-Wl,-S",                       # Strip debug symbols
    ])
    # macOS-specific compile flags
    security_compile_flags.extend([
        "-mmacosx-version-min=10.9",    # Minimum macOS version
        "-Wno-unused-command-line-argument",  # Suppress warnings
    ])
elif platform.system() == "Windows":
    # Windows-specific flags (MSVC)
    security_compile_flags.extend([
        "/O2",                          # Maximum optimization
        "/GL",                          # Whole program optimization
        "/GS",                          # Buffer security check
        "/DNDEBUG",                     # No debug
    ])
    security_link_flags.extend([
        "/LTCG",                        # Link time code generation
        "/OPT:REF",                     # Remove unreferenced code
        "/OPT:ICF",                     # Identical COMDAT folding
        "/DEF:export_symbols.def",      # Use .def file for symbol export
    ])

extensions = [
    Extension(
        "marearts_anpr.marearts_anpr_d",
        ["marearts_anpr/cython_modules/marearts_anpr_d.pyx"],
        include_dirs=[numpy.get_include()],
        extra_compile_args=security_compile_flags,
        extra_link_args=security_link_flags,
        language="c++"
    ),
    Extension(
        "marearts_anpr.marearts_anpr_r",
        ["marearts_anpr/cython_modules/marearts_anpr_r.pyx"],
        include_dirs=[numpy.get_include()],
        extra_compile_args=security_compile_flags,
        extra_link_args=security_link_flags,
        language="c++"
    ),
    Extension(
        "marearts_anpr.tokenizer",
        ["marearts_anpr/cython_modules/tokenizer.pyx"],
        include_dirs=[numpy.get_include()],
        extra_compile_args=security_compile_flags,
        extra_link_args=security_link_flags,
        language="c++"
    ),
    Extension(
        "marearts_anpr.utils",
        ["marearts_anpr/cython_modules/utils.pyx"],
        include_dirs=[numpy.get_include()],
        extra_compile_args=security_compile_flags,
        extra_link_args=security_link_flags,
        language="c++"
    ),
    Extension(
        "marearts_anpr.image_processor",
        ["marearts_anpr/cython_modules/image_processor.pyx"],
        include_dirs=[numpy.get_include()],
        extra_compile_args=security_compile_flags,
        extra_link_args=security_link_flags,
        language="c++"
    ),
    Extension(
        "marearts_anpr.marearts_anpr_p",
        ["marearts_anpr/cython_modules/marearts_anpr_p.pyx"],
        include_dirs=[numpy.get_include()],
        extra_compile_args=security_compile_flags,
        extra_link_args=security_link_flags,
        language="c++"
    ),
    # DECOY/HONEYPOT Extensions - Fake modules to confuse attackers
    Extension(
        "marearts_anpr.license",
        ["marearts_anpr/cython_modules/license.pyx"],
        include_dirs=[numpy.get_include()],
        extra_compile_args=security_compile_flags,
        extra_link_args=security_link_flags,
        language="c++"
    ),
    Extension(
        "marearts_anpr.secret",
        ["marearts_anpr/cython_modules/secret.pyx"],
        include_dirs=[numpy.get_include()],
        extra_compile_args=security_compile_flags,
        extra_link_args=security_link_flags,
        language="c++"
    ),
]

# Enhanced Cython compiler directives for maximum security (PRODUCTION MODE)
security_compiler_directives = {
    'language_level': "3",              # Python 3 syntax
    'embedsignature': False,            # Remove function signatures from compiled code
    'linetrace': False,                 # Disable line tracing for security
    'profile': False,                   # Disable profiling hooks
    'emit_code_comments': False,        # Remove code comments from output
    'annotation_typing': False,         # Disable type annotation processing
    'boundscheck': False,               # Disable bounds checking for performance
    'wraparound': False,                # Disable negative indexing
    'initializedcheck': False,          # Disable initialized variable checks
    'cdivision': True,                  # Use C division semantics
    
    # AGGRESSIVE STRING REDUCTION
    'binding': False,                   # Don't bind Python functions (reduces metadata)
    'embedsignature.format': 'c',       # Minimal signature format
    'c_string_type': 'bytes',           # Use bytes instead of unicode where possible
    'c_string_encoding': 'ascii',       # Use ASCII encoding (smaller)
    'optimize.use_switch': True,        # Use switch statements (less strings)
    'optimize.unpack_method_calls': True, # Optimize method calls
    
    # PRODUCTION MODE - Remove all debug information  
    'unraisable_tracebacks': False,     # Disable traceback generation
    'old_style_globals': True,          # Use faster global access
    
    # CRITICAL: Remove module paths and function names from errors
    # 'error_on_unknown_names': False,    # Not a valid Cython directive
    'warn.undeclared': False,           # No warnings about undeclared names
    'warn.unused': False,               # No warnings about unused vars
    'warn.unused_arg': False,           # No warnings about unused args
    'warn.unused_result': False,        # No warnings about unused results
    
    # HIDE CLASS INTERNALS - Remove attribute name strings
    'auto_pickle': False,               # Disable pickling support (removes attribute names)
    'auto_cpdef': False,                # Don't auto-generate Python wrappers
    
    # AGGRESSIVE OPTIMIZATION - Minimize string generation
    'optimize.use_switch': True,        # Use switch statements instead of if/else chains
    'optimize.unpack_method_calls': True,  # Optimize method calls
    'always_allow_keywords': False,     # Don't allow keyword arguments (reduces strings)
    'remove_unreachable': True,         # Remove unreachable code
}

def preprocess_cython_file(pyx_file):
    """Remove any remaining docstrings and comments from Cython files before compilation"""
    try:
        with open(pyx_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remove triple-quoted docstrings more aggressively
        import re
        
        # Remove docstrings patterns
        patterns_to_remove = [
            r'"""[^"]*"""',  # Triple double quotes
            r"'''[^']*'''",  # Triple single quotes
            r'r"""[^"]*"""', # Raw docstrings
            r"r'''[^']*'''", # Raw docstrings
        ]
        
        for pattern in patterns_to_remove:
            content = re.sub(pattern, '', content, flags=re.DOTALL)
        
        # Write cleaned content to temp file
        temp_file = pyx_file + '.tmp'
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Replace original with cleaned version
        import shutil
        shutil.move(temp_file, pyx_file)
        
    except Exception as e:
        print(f"⚠️ Failed to preprocess {pyx_file}: {e}")

# Preprocess all .pyx files to remove any remaining docstrings
for ext in extensions:
    for source_file in ext.sources:
        if source_file.endswith('.pyx'):
            preprocess_cython_file(source_file)

class SecurityHardenedBuildExt(build_ext):
    """Custom build_ext class that adds binary security hardening"""
    
    def run(self):
        """Run the standard build process then add security hardening"""
        # Run standard build
        super().run()
        
        # SECURITY: Clean debug strings from compiled binaries
        self.clean_debug_strings()
        
        # SECURITY: Patch PyInit visibility in generated C files
        self.patch_pyinit_visibility()
        
        # Add binary security hardening
        self.add_binary_security_headers()
    
    def patch_pyinit_visibility(self):
        """Add visibility attributes to PyInit functions for secure module loading"""
        try:
            import glob
            import re
            
            # Find all generated .c/.cpp files
            c_files = glob.glob("marearts_anpr/cython_modules/*.c") + glob.glob("marearts_anpr/cython_modules/*.cpp")
            
            for c_file in c_files:
                try:
                    with open(c_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Simple line-by-line approach to add visibility to PyInit functions
                    lines = content.split('\n')
                    new_lines = []
                    patches_applied = 0
                    
                    for line in lines:
                        # Look for PyInit function definitions
                        if 'PyInit_' in line and ('__Pyx_PyMODINIT_FUNC' in line or 'PyMODINIT_FUNC' in line):
                            # Check if it's a function definition (not a prototype)
                            if line.strip().endswith(')') and not line.strip().endswith(';'):
                                # Add visibility attribute
                                new_line = '__attribute__((visibility("default"))) ' + line
                                new_lines.append(new_line)
                                patches_applied += 1
                                print(f"  📌 Added visibility to: {line.strip()[:60]}...")
                            else:
                                new_lines.append(line)
                        else:
                            new_lines.append(line)
                    
                    new_content = '\n'.join(new_lines)
                    
                    if new_content != content:
                        with open(c_file, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        print(f"🔓 Patched PyInit visibility: {os.path.basename(c_file)} ({patches_applied} patterns matched)")
                    else:
                        print(f"ℹ️ No PyInit patterns found in: {os.path.basename(c_file)}")
                        
                except Exception as e:
                    print(f"⚠️ PyInit patch failed for {c_file}: {e}")
                    
        except Exception as e:
            print(f"⚠️ PyInit patching failed: {e}")
    
    def clean_debug_strings(self):
        """Remove debug and error strings from compiled binaries"""
        import glob
        
        print("\n🧹 CLEANING DEBUG STRINGS FROM BINARIES...")
        
        # Strings to completely remove (replace with spaces)
        strings_to_remove = [
            # Python runtime errors (keep minimal for functionality)
            b"cannot import name",
            b"name '%U' is not defined",
            b"got multiple values for keyword argument",
            b"keywords must be strings",
            b"__int__ returned non-int",
            b"has incorrect type (expected",
            b"'NoneType' object has no attribute",
            b"too many values to unpack",
            b"local variable '%s' referenced before assignment",
            
            # CRITICAL: Remove module paths and function names
            b"marearts_anpr.marearts_anpr_p.validate_license_state",
            # b"marearts_anpr.marearts_anpr_p.validate_user_key",  # Keep this for CLI
            b"marearts_anpr.marearts_anpr_p.grant_license_access",
            b"marearts_anpr.marearts_anpr_p.revoke_license_access",
            b"marearts_anpr.marearts_anpr_p.needs_revalidation",
            b"marearts_anpr.marearts_anpr_p.secure_license_check",
            # b"marearts_anpr.marearts_anpr_p.decrypt_file",  # Keep for internal use
            b"marearts_anpr.marearts_anpr_p.download_file",
            b"marearts_anpr.marearts_anpr_p.",
            b"marearts_anpr/cython_modules/",
            # b"marearts_anpr.",  # DISABLED - corrupts imports like marearts_anpr.utils
            
            # Remove function/method names
            b"validate_license_state",
            # b"validate_user_key",  # Keep for CLI
            b"grant_license_access",
            b"secure_license_check",
            # b"decrypt_file",  # Keep for internal module use
            b"encode",
            
            # Development artifacts
            b"compile time Python version",
            b"Note that Cython is deliberately stricter",
            b"cline_in_traceback",
            b"_getframe",
            b"co_firstlineno",
            b"co_name",
            b"__builtins__",
            b"__qualname__",
            b"__module__",
            b"__spec__",
            b"__test__",
            b"__main__",
        ]
        
        # Find all .so files
        so_files = glob.glob('marearts_anpr/*.so')
        so_files.extend(glob.glob('marearts_anpr/*.pyd'))  # Windows
        
        for so_file in so_files:
            try:
                # Read binary
                with open(so_file, 'rb') as f:
                    data = f.read()
                
                original_size = len(data)
                cleaned = False
                
                # Remove debug strings
                for string in strings_to_remove:
                    if string in data:
                        # Replace with spaces to maintain binary structure
                        replacement = b' ' * len(string)
                        data = data.replace(string, replacement)
                        cleaned = True
                
                if cleaned:
                    # Write cleaned binary
                    with open(so_file, 'wb') as f:
                        f.write(data)
                    
                    new_size = len(data)
                    reduction = ((original_size - new_size) / original_size) * 100
                    print(f"  ✅ Cleaned {os.path.basename(so_file)}")
                
            except Exception as e:
                print(f"  ⚠️ Could not clean {so_file}: {e}")
    
    def add_binary_security_headers(self):
        """Add security headers and integrity checks to compiled binaries"""
        print("\n🛡️ Adding binary security hardening...")
        
        # Find all built .so files
        built_files = []
        if hasattr(self, 'get_outputs'):
            built_files = self.get_outputs()
        
        # Also check build directory
        for root, dirs, files in os.walk(self.build_lib if hasattr(self, 'build_lib') else '.'):
            for file in files:
                if file.endswith('.so'):
                    built_files.append(os.path.join(root, file))
        
        # Process each binary
        for binary_path in built_files:
            if os.path.exists(binary_path):
                self.harden_binary_only(binary_path)
    
    def harden_binary_only(self, binary_path):
        """Clean build - no obfuscation, everything should work"""
        try:
            # CLEAN BUILD v0.0.99 - No obfuscation, no stripping
            print(f"✅ CLEAN BUILD: {os.path.basename(binary_path)}")
            
            # Just verify PyInit symbols are present
            self.verify_pyinit_symbols(binary_path)
            
            # Set secure permissions
            os.chmod(binary_path, 0o755)
            
            print(f"✅ CLEAN BUILD COMPLETE: {os.path.basename(binary_path)}")
            return
            
            if platform.system() == "Darwin":
                # macOS: Use strip with specific flags
                if os.path.exists('/usr/bin/strip'):
                    subprocess.run(['strip', '-x', '-S', binary_path], 
                                 check=False, capture_output=True)
            elif platform.system() == "Windows":
                # Windows: Limited stripping options, rely on link flags
                pass
            
            # ULTIMATE OBFUSCATION: UPX compression (if available)
            if os.path.exists('/usr/bin/upx'):
                # Use UPX to compress and obfuscate the binary
                # This makes strings much harder to extract
                try:
                    result = subprocess.run(['upx', '--best', '--lzma', binary_path], 
                                          check=False, capture_output=True, text=True)
                    if result.returncode == 0:
                        print(f"🔒 UPX COMPRESSED: {os.path.basename(binary_path)} (maximum obfuscation)")
                        # Show compression ratio
                        for line in result.stdout.split('\n'):
                            if '%' in line and os.path.basename(binary_path) in line:
                                print(f"   📊 Compression: {line.strip()}")
                    else:
                        print(f"⚠️ UPX compression failed: {result.stderr}")
                except Exception as e:
                    print(f"⚠️ UPX error: {e}")
            else:
                # Try alternative UPX locations
                upx_paths = ['/usr/local/bin/upx', 'upx']
                upx_found = False
                for upx_path in upx_paths:
                    try:
                        result = subprocess.run([upx_path, '--version'], 
                                              capture_output=True, check=False)
                        if result.returncode == 0:
                            # Found UPX, use it
                            result = subprocess.run([upx_path, '--best', '--lzma', binary_path], 
                                                  check=False, capture_output=True, text=True)
                            if result.returncode == 0:
                                print(f"🔒 UPX COMPRESSED: {os.path.basename(binary_path)} (maximum obfuscation)")
                                upx_found = True
                                break
                    except:
                        continue
                
                if not upx_found:
                    print(f"ℹ️ UPX not found - install with: sudo apt install upx-ucl")
            
            # Set secure permissions
            os.chmod(binary_path, 0o755)
            
            print(f"✅ PRODUCTION HARDENED: {os.path.basename(binary_path)} (debug info stripped, PyInit preserved)")
            
        except Exception as e:
            # Don't fail build if hardening fails
            print(f"⚠️ Hardening failed for {os.path.basename(binary_path)}: {e}")
    
    def obfuscate_internal_strings(self, binary_path):
        """Remove internal class attribute name strings from binary"""
        try:
            # Read binary content
            with open(binary_path, 'rb') as f:
                content = f.read()
            
            # Define patterns to obfuscate - COMPREHENSIVE LIST
            obfuscation_patterns = [
                # CRITICAL: DO NOT OBFUSCATE THESE - They are needed for imports!
                # b'validate_user_key',      # NEEDED FOR IMPORTS
                # b'secure_license_check',   # NEEDED FOR IMPORTS  
                # b'grant_license_access',   # NEEDED FOR IMPORTS
                # b'revoke_license_access',  # MIGHT BE NEEDED
                # b'needs_revalidation',     # MIGHT BE NEEDED
                # b'validate_license_state', # NEEDED FOR IMPORTS
                # b'decrypt_file',           # NEEDED FOR IMPORTS
                # b'download_file',          # INTERNAL - can obfuscate
                b'_check_rate_limit',        # INTERNAL - can obfuscate
                # b'download_anpr_detector_model', # NEEDED FOR IMPORTS
                # b'download_anpr_ocr_model',      # NEEDED FOR IMPORTS
                
                # Full module paths - BE CAREFUL, these can break imports
                # Only obfuscate the function part, not the module path
                # b'marearts_anpr.marearts_anpr_p.validate_user_key',
                # b'marearts_anpr.marearts_anpr_p.secure_license_check',
                # b'marearts_anpr.marearts_anpr_p.grant_license_access',
                # b'marearts_anpr.marearts_anpr_p.revoke_license_access',
                # b'marearts_anpr.marearts_anpr_p.validate_license_state',
                # b'marearts_anpr.marearts_anpr_p.needs_revalidation',
                # b'marearts_anpr.marearts_anpr_p.decrypt_file',
                # b'marearts_anpr.marearts_anpr_p.download_file',
                # b'marearts_anpr.marearts_anpr_p._check_rate_limit',
                # b'marearts_anpr.marearts_anpr_p.download_anpr_detector_model',
                # b'marearts_anpr.marearts_anpr_p.download_anpr_ocr_model',
                
                # Class internals - CAREFUL with module paths
                # b'marearts_anpr.marearts_anpr_d.ma_anpr_d._license_session_valid.__set_',
                # b'marearts_anpr.marearts_anpr_d.ma_anpr_d._license_session_valid',
                # b'marearts_anpr.marearts_anpr_r.ma_anpr_r._license_session_valid',
                b'_license_session_valid.__set_',
                b'_license_session_valid.__get_',
                b'_license_session_valid',
                # These might be needed for imports - commenting out to be safe
                # b'ma_anpr_d.',
                # b'ma_anpr_r.',
                
                # Error messages that reveal internals
                b'Authentication failed',
                b'Resource unavailable',
                b'Access denied',
                b'Invalid request',
                b'Download failed',
                b'Processing failed',
                b'Operation failed',
                b'validate_serial_key',
                
                # File names that reveal structure
                b'_preprocessor_config.dat',
                b'_encoder_model.dat',
                b'_decoder_model.dat',
                b'_configure.dat',
                b'.last_modified',
                
                # Cython internals
                b'cline_in_traceback',
                b'__pyx_',
                b'__Pyx_',
                
                # Additional module paths - REMOVED to prevent import breakage
                # These should NOT be obfuscated as they're needed for imports
                # b'marearts_anpr.marearts_anpr_p',
                # b'marearts_anpr.marearts_anpr_d',
                # b'marearts_anpr.marearts_anpr_r',
                # b'marearts_anpr.utils',
                # b'marearts_anpr.tokenizer',
                # b'marearts_anpr.image_processor',
                
                # Variable names
                b'serial_key',
                b'user_name',
                b'username',
                b'dat_file_path',
                b'encrypted_content',
                b'marearts_anpr_data',
                b'marearts_crystal',
                b'ma_crystal',
            ]
            
            modified = False
            replacements = 0
            
            for pattern in obfuscation_patterns:
                count = content.count(pattern)
                if count > 0:
                    # Replace with random bytes of same length
                    replacement = b'X' * len(pattern)
                    content = content.replace(pattern, replacement)
                    modified = True
                    replacements += count
                    print(f"🔒 Obfuscated {count}x: {pattern.decode('utf-8', errors='ignore')[:50]}...")
            
            if modified:
                # Write back the obfuscated content
                with open(binary_path, 'wb') as f:
                    f.write(content)
                print(f"🎭 STRING OBFUSCATION: {os.path.basename(binary_path)} ({replacements} strings masked)")
            else:
                print(f"ℹ️ No sensitive strings found in {os.path.basename(binary_path)}")
            
        except Exception as e:
            print(f"⚠️ String obfuscation failed for {os.path.basename(binary_path)}: {e}")
    
    def verify_pyinit_symbols(self, binary_path):
        """Verify that PyInit functions are still present after stripping"""
        try:
            result = subprocess.run(['nm', '-D', binary_path], capture_output=True, text=True, check=False)
            if result.returncode == 0 and 'PyInit' in result.stdout:
                print(f"✅ PyInit symbols verified in {os.path.basename(binary_path)}")
            else:
                print(f"⚠️ PyInit symbols may be missing in {os.path.basename(binary_path)}")
        except Exception:
            pass  # Don't fail build if verification fails
    
    def harden_binary(self, binary_path):
        """Apply security hardening to a single binary (legacy method with integrity files)"""
        try:
            # Strip debug information
            if os.path.exists('/usr/bin/strip'):
                subprocess.run(['strip', '--strip-debug', '--strip-unneeded', binary_path], 
                             check=False, capture_output=True)
            
            # Set secure permissions
            os.chmod(binary_path, 0o755)
            
            # Create integrity file
            self.create_integrity_file(binary_path)
            
            print(f"✅ Hardened: {os.path.basename(binary_path)}")
            
        except Exception as e:
            # Don't fail build if hardening fails
            print(f"⚠️ Hardening failed for {os.path.basename(binary_path)}: {e}")
    
    def create_integrity_file(self, binary_path):
        """Create integrity check file for binary (not distributed)"""
        try:
            with open(binary_path, 'rb') as f:
                content = f.read()
            
            integrity_info = {
                'file_size': len(content),
                'sha256': hashlib.sha256(content).hexdigest(),
                'sha1': hashlib.sha1(content).hexdigest(),
                'build_flags': security_compile_flags,
                'security_features': ['RELRO', 'stack_canary', 'NX_bit']
            }
            
            # Create integrity file in build directory only (not distributed)
            build_dir = os.path.dirname(binary_path)
            integrity_file = os.path.join(build_dir, 'build_integrity_' + os.path.basename(binary_path) + '.json')
            with open(integrity_file, 'w') as f:
                json.dump(integrity_info, f, indent=2)
                
        except Exception:
            pass  # Don't fail build if integrity file creation fails

setup(
    name="marearts_anpr",
    # ⚠️ CRITICAL: MUST use explicit package list, NOT find_packages()
    # find_packages() would include test/, claude/, etc. with source code!
    packages=['marearts_anpr'],  # Only include the main package, not subpackages
    ext_modules=cythonize(
        extensions, 
        compiler_directives=security_compiler_directives,
        force=True,                     # Force rebuild for security updates
        quiet=True                      # Suppress verbose output
    ),
    package_data={
        'marearts_anpr': ['*.so', '*.pyd'],
    },
    exclude_package_data={
        'marearts_anpr': ['*.pyx', '*.cpp', '*.c'],
    },
    zip_safe=False,
    cmdclass={'build_ext': SecurityHardenedBuildExt},
    install_requires=[
        'numpy>=1.21.6,<2.0; python_version=="3.9"',
        'numpy>=1.23.0,<2.0; python_version=="3.10"', 
        'numpy>=1.23.0,<2.0; python_version=="3.11"',
        'numpy>=1.26.0,<2.0; python_version>="3.12"',
        'opencv-python==4.10.0.84',
        'requests==2.32.3',
        'imageio==2.34.2',
        'pillow==10.4.0',
        'onnxruntime==1.15.1; python_version=="3.9" and platform_machine=="aarch64"',
        'onnxruntime==1.16.3; python_version>="3.10" and platform_machine=="aarch64"',
        'onnxruntime==1.18.1; python_version=="3.9" and platform_machine!="aarch64"',
        'onnxruntime==1.22.1; python_version>="3.10" and platform_machine!="aarch64"',
        'PyYAML==6.0.1',
        'dotmap==1.3.30',
        'marearts-crystal',
        'tqdm==4.66.4'
    ],
    entry_points={
        'console_scripts': [
            'marearts-anpr=marearts_anpr.cli:main',
            'ma-anpr=marearts_anpr.cli:main',
        ],
    },
)