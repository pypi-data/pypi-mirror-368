#!/usr/bin/env python3
"""
MareArts ANPR CLI - Command Line Interface for License Plate Detection and Recognition
"""

import argparse
import json
import os
import sys
import re
import getpass
from pathlib import Path
from typing import List, Dict, Any, Optional
import requests

import cv2
import numpy as np
from . import (
    marearts_anpr_from_image_file,
    ma_anpr_detector,
    ma_anpr_ocr,
    validate_user_key
)
from ._version import __version__


# Config files removed for security - use environment variables only

# Environment variable names
ENV_USERNAME = 'MAREARTS_ANPR_USERNAME'
ENV_SERIAL_KEY = 'MAREARTS_ANPR_SERIAL_KEY'

# Input validation patterns
USERNAME_PATTERN = re.compile(r'^[a-zA-Z0-9_\-\.@]+$')
SERIAL_KEY_PATTERN = re.compile(r'^[A-Za-z0-9\-_=+/]+$')
ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}


# Config directory functions removed - use environment variables only


def load_credentials() -> Dict[str, str]:
    """Load credentials from environment variables or .marearts_env file"""
    # First check environment variables
    env_username = os.getenv(ENV_USERNAME)
    env_serial_key = os.getenv(ENV_SERIAL_KEY)
    
    if env_username and env_serial_key:
        return {
            'user_name': env_username,
            'serial_key': env_serial_key,
            'source': 'environment'
        }
    
    # Check for .marearts_env file in current directory
    env_file = Path.cwd() / '.marearts_env'
    if env_file.exists():
        try:
            with open(env_file, 'r') as f:
                lines = f.readlines()
                username = None
                serial_key = None
                for line in lines:
                    if line.startswith(f'export {ENV_USERNAME}='):
                        username = line.split('=', 1)[1].strip().strip('"')
                    elif line.startswith(f'export {ENV_SERIAL_KEY}='):
                        serial_key = line.split('=', 1)[1].strip().strip('"')
                
                if username and serial_key:
                    # Set them in environment for this session
                    os.environ[ENV_USERNAME] = username
                    os.environ[ENV_SERIAL_KEY] = serial_key
                    return {
                        'user_name': username,
                        'serial_key': serial_key,
                        'source': '.marearts_env file'
                    }
        except Exception:
            pass
    
    return {}


# Config file functions removed - use environment variables only


def mask_serial_key(serial_key: str) -> str:
    """Mask serial key for display purposes"""
    if len(serial_key) <= 8:
        return '*' * len(serial_key)
    return serial_key[:4] + '*' * (len(serial_key) - 8) + serial_key[-4:]


# Config file functions removed - use environment variables only


# Duplicate cmd_config function removed - using the full version below


def cmd_gpu_info(args):
    """Display GPU/CUDA information"""
    print("MareArts ANPR GPU Information")
    print("-" * 40)
    
    # Check OpenCV build info
    build_info = cv2.getBuildInformation()
    cuda_enabled = "CUDA" in build_info and "YES" in build_info
    
    print(f"OpenCV: {cv2.__version__} | CUDA: {'Yes' if cuda_enabled else 'No'}")
    
    if cuda_enabled:
        cuda_lines = [line for line in build_info.split('\n') if 'CUDA' in line]
        if cuda_lines:
            print(f"CUDA Details: {cuda_lines[0].strip()}")
    
    try:
        gpu_count = cv2.cuda.getCudaEnabledDeviceCount()
        if gpu_count > 0:
            print(f"GPU Devices: {gpu_count}")
    except:
        pass


def cmd_models(args):
    """List available models"""
    print("\n📍 DETECTOR MODELS:")
    
    print("\nv10 Series:")
    v10_models = [
        ("v10_nano", "Fastest, lowest accuracy"),
        ("v10_small", "Fast, lower accuracy"),
        ("v10_middle", "Balanced performance"),
        ("v10_large", "High accuracy, slower"),
        ("v10_xlarge", "Highest accuracy, slowest")
    ]
    for model, desc in v10_models:
        print(f"  - {model:<12} {desc}")
    
    print("\nv11 Series:")
    v11_models = [
        ("v11_nano", "Fastest v11 variant"),
        ("v11_small", "Fast v11 variant"),
        ("v11_middle", "Balanced v11 variant"),
        ("v11_large", "High accuracy v11 variant")
    ]
    for model, desc in v11_models:
        print(f"  - {model:<12} {desc}")
    
    print("\nv13 Series (Latest):")
    v13_models = [
        ("v13_nano", "Fastest v13 variant"),
        ("v13_small", "Fast v13 variant"),
        ("v13_middle", "Balanced v13 variant"),
        ("v13_large", "High accuracy v13 variant")
    ]
    for model, desc in v13_models:
        print(f"  - {model:<12} {desc}")
    
    print("\n🔤 OCR MODELS:")
    
    print("\nBase Models:")
    base_ocr = [
        ("eu", "European license plates (40+ countries)"),
        ("kr", "Korean license plates"),
        ("euplus", "Enhanced European model"),
        ("univ", "Universal model")
    ]
    for model, desc in base_ocr:
        print(f"  - {model:<12} {desc}")
    
    print("\nv11 Series:")
    v11_ocr = [
        ("v11_eu", "v11 European model"),
        ("v11_kr", "v11 Korean model"),
        ("v11_euplus", "v11 Enhanced European model"),
        ("v11_univ", "v11 Universal model"),
        ("v11_cn", "v11 Chinese model")
    ]
    for model, desc in v11_ocr:
        print(f"  - {model:<12} {desc}")
    
    print("\nv13 Series (Latest):")
    v13_ocr = [
        ("v13_univ", "v13 Universal model"),
        ("v13_euplus", "v13 Enhanced European model"),
        ("v13_eu", "v13 European model"),
        ("v13_kr", "v13 Korean model"),
        ("v13_cn", "v13 Chinese model")
    ]
    for model, desc in v13_ocr:
        print(f"  - {model:<12} {desc}")
    
    print(f"\n💡 Recommended: v13_middle + v13_euplus (balanced)")


def cmd_validate(args):
    """Validate license"""
    config = load_credentials()
    if not config:
        print("No credentials. Run: ma-anpr config")
        sys.exit(1)
    
    user_name = config.get('user_name')
    serial_key = config.get('serial_key')
    source = config.get('source', 'environment')
    
    print(f"Validating: {user_name} | {mask_serial_key(serial_key)}")
    
    # Use the secure validation utility
    is_valid = validate_user_key(user_name, serial_key)
    error_message = "Invalid credentials" if not is_valid else None
    
    if is_valid:
        print("✓ License valid")
    else:
        print(f"✗ {error_message}")
        print(f"Set: {ENV_USERNAME} and {ENV_SERIAL_KEY}")


def validate_file_path(path: str) -> Optional[Path]:
    """Validate and sanitize file paths"""
    try:
        # Resolve to absolute path
        abs_path = Path(path).resolve()
        
        # Check if path exists
        if not abs_path.exists():
            return None
        
        # For files, check extension
        if abs_path.is_file():
            if abs_path.suffix.lower() not in ALLOWED_IMAGE_EXTENSIONS:
                return None
        
        return abs_path
    except Exception:
        return None


def draw_results(image: np.ndarray, results: List[Dict[str, Any]]) -> np.ndarray:
    """Draw detection results on image"""
    output = image.copy()
    
    for result in results:
        bbox = result['bbox']
        x1, y1, x2, y2 = int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])
        
        # Draw bounding box
        cv2.rectangle(output, (x1, y1), (x2, y2), (0, 255, 0), 2)
        
        # Prepare label
        ocr_text = result.get('ocr_text', 'N/A')
        ocr_conf = result.get('ocr_conf', 0.0)
        label = f"{ocr_text} ({ocr_conf:.2f})"
        
        # Draw label background
        label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
        label_y = y1 - 10 if y1 - 10 > label_size[1] else y1 + label_size[1] + 10
        cv2.rectangle(output, 
                     (x1, label_y - label_size[1] - 5),
                     (x1 + label_size[0], label_y + 5),
                     (0, 255, 0), -1)
        
        # Draw label text
        cv2.putText(output, label,
                   (x1, label_y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
    
    return output


def process_image(image_path: str, args) -> List[Dict[str, Any]]:
    """Process single image with secure credential handling"""
    config = load_credentials()
    if not config:
        raise ValueError("No configuration found. Run 'marearts-anpr config' first.")
    
    user_name = config.get('user_name')
    serial_key = config.get('serial_key')
    
    if not user_name or not serial_key:
        raise ValueError("Invalid credentials found. Please reconfigure.")
    
    try:
        # Get model versions from args with available fallbacks
        detector_model = getattr(args, 'detector_model', 'v11_middle')  # Fallback to available model
        ocr_model = getattr(args, 'ocr_model', 'euplus')  # Fallback to available model
        
        # Create detector object with correct parameters
        detector = ma_anpr_detector(detector_model, user_name, serial_key)
        
        # Create OCR object with correct parameters  
        ocr = ma_anpr_ocr(ocr_model, user_name, serial_key)
        
        # Use the correct API with initialized objects
        api_result = marearts_anpr_from_image_file(detector, ocr, image_path)
        
        # Convert API format to expected CLI format
        if api_result and 'results' in api_result:
            results = []
            for result in api_result['results']:
                # Convert to expected format
                plate_result = {
                    'ocr_text': result.get('ocr', ''),
                    'ocr_conf': result.get('ocr_conf', 0) / 100.0 if result.get('ocr_conf', 0) > 1 else result.get('ocr_conf', 0),  # Convert percentage to decimal
                    'bbox': result.get('ltrb', []),
                    'bbox_conf': result.get('ltrb_conf', 0) / 100.0 if result.get('ltrb_conf', 0) > 1 else result.get('ltrb_conf', 0)
                }
                results.append(plate_result)
            return results
        else:
            return []
        
    except Exception as e:
        # Generic error message to avoid credential leakage
        raise ValueError("Failed to process image. Please check your configuration and license.")
    finally:
        # Clear sensitive variables from memory
        user_name = None
        serial_key = None


def cmd_read(args):
    """Read license plates from images"""
    # Check configuration
    config = load_credentials()
    if not config:
        print("No configuration. Run: ma-anpr config")
        sys.exit(1)
    
    # Get list of input files with validation
    input_files = []
    for input_path in args.input:
        path = validate_file_path(input_path)
        if path is None:
            print(f"Skip: {input_path}")
            continue
            
        if path.is_file():
            input_files.append(path)
        elif path.is_dir():
            # Find all image files in directory
            for ext in ALLOWED_IMAGE_EXTENSIONS:
                input_files.extend(path.glob(f'*{ext}'))
                input_files.extend(path.glob(f'*{ext.upper()}'))
    
    if not input_files:
        print("No valid files")
        sys.exit(1)
    
    print(f"Processing {len(input_files)} images | {args.detector_model}/{args.ocr_model} | Conf: {args.confidence}")
    
    all_results = []
    
    for img_path in input_files:
        try:
            print(f"{img_path.name}:", end=' ')
            
            # Process image
            results = process_image(str(img_path), args)
            
            # Filter by confidence
            filtered_results = [r for r in results if r.get('ocr_conf', 0) >= args.confidence]
            
            # Store results with filename
            for result in filtered_results:
                result['filename'] = str(img_path)
            
            all_results.extend(filtered_results)
            
            # Display results
            if filtered_results:
                plates = ', '.join([f"{r.get('ocr_text', 'N/A')} ({r.get('ocr_conf', 0):.2f})" for r in filtered_results])
                print(f"{len(filtered_results)} plates: {plates}")
            else:
                print("No plates")
            
            # Save annotated image if requested
            if args.output:
                image = cv2.imread(str(img_path))
                annotated = draw_results(image, filtered_results)
                
                if len(input_files) == 1:
                    output_path = args.output
                else:
                    # Multiple files - create unique output names
                    output_path = Path(args.output)
                    if output_path.is_dir():
                        output_path = output_path / f"detected_{img_path.name}"
                    else:
                        output_path = output_path.parent / f"detected_{img_path.stem}{output_path.suffix}"
                
                cv2.imwrite(str(output_path), annotated)
                print(f"  → Saved: {output_path.name}")
                
        except Exception as e:
            print(f"Error: {str(e)}")
            continue
    
    # Save results to JSON if requested
    if args.json:
        try:
            json_path = Path(args.json).resolve()
            with open(json_path, 'w') as f:
                json.dump(all_results, f, indent=2)
            print(f"\nResults saved to: {json_path}")
        except Exception:
            print("\nError: Failed to save JSON results")
    
    print(f"\nTotal: {len(all_results)} plates from {len(input_files)} images")


def cmd_test_api(args):
    """Test API functionality using public credentials"""
    # Public test credentials
    PUBLIC_API_KEY = "J4K9L2Wory34@G7T1Y8rt-PP83uSSvkV3Z6ioSTR!"
    PUBLIC_USER_ID = "marearts@public"
    API_URL = "https://we303v9ck8.execute-api.eu-west-1.amazonaws.com/Prod/marearts_anpr"
    
    # List models option
    if hasattr(args, 'list_models') and args.list_models:
        print("Available Test API Models:")
        print("\nDetector Models:")
        print("  - v10_nano, v10_small, v10_middle, v10_large")
        print("  - v11_small, v11_middle, v11_large")
        print("  - v13_nano, v13_small, v13_middle, v13_large")
        print("\nOCR Models:")
        print("  - eu, euplus, kr, cn, univ")
        print("  - v11_eu, v11_euplus, v11_kr, v11_univ")
        print("  - v13_eu, v13_euplus, v13_kr, v13_cn, v13_univ")
        print("\nNote: Daily limit is 1000 requests")
        return
    
    # Check if input files are provided
    if not args.input:
        print("Error: No input files specified.")
        print("Usage: ma-anpr test-api image.jpg [--detector MODEL] [--ocr MODEL]")
        print("       ma-anpr test-api --list-models")
        return
    
    # Process images
    for input_file in args.input:
        file_path = validate_file_path(input_file)
        if file_path is None or not file_path.is_file():
            print(f"Error: {input_file} is not a valid image file")
            continue
        
        print(f"{file_path.name}:", end=' ')
        
        try:
            # Read image file with size validation
            file_size = file_path.stat().st_size
            if file_size > 5 * 1024 * 1024:  # 5MB limit
                print(f"Error: File {file_path.name} is too large ({file_size/1024/1024:.1f}MB). Maximum size is 5MB.")
                continue
                
            with open(file_path, 'rb') as f:
                image_data = f.read()
            
            # Prepare headers
            headers = {
                'Content-Type': 'image/jpeg',
                'x-api-key': PUBLIC_API_KEY,
                'user-id': PUBLIC_USER_ID,
                'detector_model_version': args.detector,
                'ocr_model_version': args.ocr
            }
            
            # Make API request with security settings
            response = requests.post(
                API_URL, 
                headers=headers, 
                data=image_data, 
                timeout=30,
                verify=True,  # Always verify SSL certificates
                allow_redirects=False  # Don't follow redirects for security
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Format output similar to local processing
                if 'results' in result:
                    for plate in result['results']:
                        ocr_text = plate.get('ocr', 'N/A')
                        ocr_conf = plate.get('ocr_conf', 0)
                        ltrb = plate.get('ltrb', [])
                        ltrb_conf = plate.get('ltrb_conf', 0)
                        
                        print(f"{ocr_text} ({ocr_conf}%)", end=' ')
                
                if not result.get('results'):
                    print("")
                # Show processing times if available
                if 'ltrb_proc_sec' in result and 'ocr_proc_sec' in result:
                    total_time = result['ltrb_proc_sec'] + result['ocr_proc_sec']
                    print(f"[{total_time:.2f}s]")
                
                # Show usage information if available
                if 'usage' in result and 'day_max' in result:
                    usage = int(result['usage']) + 1
                    day_max = int(result['day_max'])
                    print(f"  API: {usage}/{day_max}")
                    
                # Save JSON if requested
                if args.json:
                    json_results = {
                        'file': str(file_path),
                        'detector_model': args.detector,
                        'ocr_model': args.ocr,
                        'result': result
                    }
                    json_path = Path(args.json).resolve()
                    with open(json_path, 'w') as f:
                        json.dump(json_results, f, indent=2)
                    
            else:
                print(f"Error: {response.status_code}")
                
                if response.status_code == 403 and "Usage limit exceeded" in response.text:
                    print(" (Daily limit reached)")
                
                # Try to show usage info even for error responses (if available)
                try:
                    error_result = response.json()
                    if isinstance(error_result, dict) and 'usage' in error_result and 'day_max' in error_result:
                        usage = int(error_result['usage'])
                        day_max = int(error_result['day_max'])
                        remaining = day_max - usage
                        print(f"\nAPI Usage: {usage}/{day_max} requests today ({remaining} remaining)")
                except:
                    # If we can't parse JSON or extract usage info, just continue
                    pass
                
        except requests.exceptions.Timeout:
            print("Error: Request timed out")
        except requests.exceptions.ConnectionError:
            print("Error: Failed to connect to API")
        except Exception as e:
            print(f"Error: {str(e)}")


def cmd_version(args):
    """Show version information"""
    print(f"MareArts ANPR CLI v{__version__}")


def cmd_config(args):
    """Interactive credential configuration"""
    print("🔧 Configure MareArts ANPR")
    
    # Get username with validation
    while True:
        username = input("Enter your MareArts username/email: ").strip()
        if not username:
            print("❌ Empty username")
            continue
        
        if not USERNAME_PATTERN.match(username):
            print("❌ Invalid format")
            continue
            
        break
    
    # Get serial key securely with validation
    while True:
        serial_key = getpass.getpass("Enter your serial key: ").strip()
        if not serial_key:
            print("❌ Empty key")
            continue
            
        if not SERIAL_KEY_PATTERN.match(serial_key):
            print("❌ Invalid format")
            continue
            
        break
    
    # Set the credentials in the current process environment
    os.environ[ENV_USERNAME] = username
    os.environ[ENV_SERIAL_KEY] = serial_key
    
    # Save to .env file for easy sourcing
    env_file = Path.cwd() / '.marearts_env'
    try:
        with open(env_file, 'w') as f:
            f.write(f'# MareArts ANPR Credentials\n')
            f.write(f'export {ENV_USERNAME}="{username}"\n')
            f.write(f'export {ENV_SERIAL_KEY}="{serial_key}"\n')
        os.chmod(env_file, 0o600)  # Secure permissions
        
        print("✅ Saved to .marearts_env")
        print("Run: source .marearts_env")
    except Exception as e:
        print("✅ Session configured")
        print(f"Export: {ENV_USERNAME} and {ENV_SERIAL_KEY}")
    
    print("Testing...", end=' ')
    
    # Test the credentials
    is_valid = validate_user_key(username, serial_key)
    
    if is_valid:
        print("✅ Valid")
        print("Ready to use: ma-anpr image.jpg")
    else:
        print("❌ Invalid")
        return 1
    
    return 0


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        prog='marearts-anpr',
        description='MareArts ANPR CLI - License Plate Detection and Recognition'
    )
    
    # Add --version flag support
    parser.add_argument('--version', action='version', version=f'MareArts ANPR CLI v{__version__}')
    
    # Add direct file support - if first arg looks like a file, treat as read command
    if len(sys.argv) > 1 and not sys.argv[1].startswith('-') and sys.argv[1] not in ['config', 'gpu-info', 'models', 'validate', 'read', 'version']:
        # Check if it could be a file path, glob pattern, or directory
        potential_file = sys.argv[1]
        # Accept any path-like argument (files, directories, glob patterns)
        if '.' in potential_file or '/' in potential_file or '\\' in potential_file or '*' in potential_file or Path(potential_file).exists():
            # Insert 'read' command
            sys.argv.insert(1, 'read')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Config command
    config_parser = subparsers.add_parser('config', help='Interactive credential configuration')
    
    # GPU info command
    gpu_parser = subparsers.add_parser('gpu-info', help='Display GPU/CUDA information')
    
    # Models command
    models_parser = subparsers.add_parser('models', help='List available models')
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate license')
    
    # Version command
    version_parser = subparsers.add_parser('version', help='Show version information')
    
    # Test API command
    test_api_parser = subparsers.add_parser('test-api', help='Test ANPR using public API (no credentials required)')
    test_api_parser.add_argument('input', nargs='*', help='Input image file(s)')
    test_api_parser.add_argument('--detector', default='v13_middle',
                                 help='Detector model (default: v13_middle)')
    test_api_parser.add_argument('--ocr', default='v13_euplus',
                                 help='OCR model (default: v13_euplus)')
    test_api_parser.add_argument('--list-models', action='store_true',
                                 help='List available models for test API')
    test_api_parser.add_argument('--json', help='Save results to JSON file')
    
    # Read command
    read_parser = subparsers.add_parser('read', help='Read license plates from images')
    read_parser.add_argument('input', nargs='+', help='Input image file(s) or directory')
    read_parser.add_argument('--detector-model', default='v13_middle',
                              choices=['v10_nano', 'v10_small', 'v10_middle', 'v10_large', 'v10_xlarge',
                                       'v11_nano', 'v11_small', 'v11_middle', 'v11_large',
                                       'v13_nano', 'v13_small', 'v13_middle', 'v13_large'],
                              help='Detector model version (default: v13_middle)')
    read_parser.add_argument('--ocr-model', default='v13_euplus',
                              choices=['eu', 'kr', 'euplus', 'univ',
                                       'v11_eu', 'v11_kr', 'v11_euplus', 'v11_univ', 'v11_cn',
                                       'v13_univ', 'v13_euplus', 'v13_eu', 'v13_kr', 'v13_cn'],
                              help='OCR model version (default: v13_euplus)')
    read_parser.add_argument('--confidence', type=float, default=0.5,
                              help='Minimum confidence threshold (default: 0.5)')
    read_parser.add_argument('--output', help='Output path for annotated image(s)')
    read_parser.add_argument('--json', help='Save results to JSON file')
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Execute command
    try:
        if args.command == 'config':
            cmd_config(args)
        elif args.command == 'gpu-info':
            cmd_gpu_info(args)
        elif args.command == 'models':
            cmd_models(args)
        elif args.command == 'validate':
            cmd_validate(args)
        elif args.command == 'version':
            cmd_version(args)
        elif args.command == 'test-api':
            cmd_test_api(args)
        elif args.command == 'read':
            # Set defaults for direct invocation if not set
            if not hasattr(args, 'detector_model'):
                args.detector_model = 'v13_middle'
            if not hasattr(args, 'ocr_model'):
                args.ocr_model = 'v13_euplus'
            if not hasattr(args, 'confidence'):
                args.confidence = 0.5
            if not hasattr(args, 'output'):
                args.output = None
            if not hasattr(args, 'json'):
                args.json = None
            cmd_read(args)
    except KeyboardInterrupt:
        print("\nOperation cancelled.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()