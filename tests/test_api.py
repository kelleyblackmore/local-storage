#!/usr/bin/env python3

import os
import requests
import time
from datetime import datetime
from pathlib import Path

# API configuration
API_BASE_URL = "http://127.0.0.1:54321"
PROD_API_BASE_URL = "http://0.0.0.0:8000"  # Changed to http since we're not using SSL in CI

def check_api_availability(url):
    """Check if an API endpoint is available."""
    try:
        response = requests.get(f"{url}/health", timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def get_available_api_url():
    """Get the first available API URL."""
    urls = [API_BASE_URL, PROD_API_BASE_URL]
    for url in urls:
        print(f"Checking API availability at {url}...")
        if check_api_availability(url):
            print(f"✓ API is available at {url}")
            return url
    raise ConnectionError("No API endpoints are available")

# Get the first available API URL
API_BASE_URL = get_available_api_url()

def test_health():
    """Test the health check endpoint."""
    print("\nTesting health check endpoint...")
    response = requests.get(f"{API_BASE_URL}/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    print("✓ Health check passed")

def test_upload(filename, content):
    """Test file upload."""
    print(f"\nTesting file upload for {filename}...")
    files = {"file": (filename, content)}
    response = requests.post(f"{API_BASE_URL}/upload", files=files)
    assert response.status_code == 200
    result = response.json()
    assert result["message"] == "File uploaded successfully"
    assert result["filename"] == filename
    print(f"✓ Upload successful: {result['storage_path']}")
    return result

def test_download(filename):
    """Test file download."""
    print(f"\nTesting file download for {filename}...")
    response = requests.get(f"{API_BASE_URL}/download/{filename}")
    assert response.status_code == 200
    
    # Create downloads directory if it doesn't exist
    downloads_dir = Path("downloads")
    downloads_dir.mkdir(exist_ok=True)
    
    # Save the file
    download_path = downloads_dir / filename
    with open(download_path, "wb") as f:
        f.write(response.content)
    
    print(f"✓ Download successful: {len(response.content)} bytes (saved to {download_path})")
    return response.content

def test_list_files():
    """Test listing all files."""
    print("\nTesting file list endpoint...")
    response = requests.get(f"{API_BASE_URL}/files")
    assert response.status_code == 200
    files = response.json()["files"]
    print(f"✓ Found {len(files)} files:")
    for file in files:
        print(f"  - {file['filename']} ({file['metadata']['size']} bytes)")
    return files

def test_delete(filename):
    """Test file deletion."""
    print(f"\nTesting file deletion for {filename}...")
    response = requests.delete(f"{API_BASE_URL}/files/{filename}")
    assert response.status_code == 200
    result = response.json()
    assert result["message"] == "File deleted successfully"
    assert result["filename"] == filename
    print(f"✓ Delete successful: {filename}")

def main():
    """Run all tests."""
    print("Starting API tests...")
    
    # Test health check
    test_health()
    
    # Create and upload test files
    test_files = [
        ("test1.txt", f"Test file 1 created at {datetime.now()}"),
        ("test2.txt", f"Test file 2 created at {datetime.now()}"),
    ]
    
    uploaded_files = []
    for filename, content in test_files:
        result = test_upload(filename, content)
        uploaded_files.append((filename, content))
    
    # List all files
    files = test_list_files()
    initial_file_count = len(files)
    assert len(files) >= len(test_files)
    
    # Download and verify files
    for filename, original_content in uploaded_files:
        downloaded_content = test_download(filename)
        assert downloaded_content.decode() == original_content
        print(f"✓ Content verification passed for {filename}")
    
    # Test delete functionality
    for filename, _ in uploaded_files:
        test_delete(filename)
    
    # Verify files are deleted
    files = test_list_files()
    assert len(files) == initial_file_count - len(test_files), "Files were not properly deleted"
    
    print("\nAll tests completed successfully!")

if __name__ == "__main__":
    try:
        main()
    except AssertionError as e:
        print(f"\n❌ Test failed: {str(e)}")
        exit(1)
    except requests.exceptions.ConnectionError:
        print("\n❌ Could not connect to the API. Is the service running?")
        exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        exit(1) 