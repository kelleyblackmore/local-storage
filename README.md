# Local Artifact Storage API

A local-only FastAPI-based service for storing, listing, downloading, and deleting files (artifacts) on your server. Includes a web UI for easy file management.

[![CI/CD Pipeline](https://github.com/kelleyblackmore/local-storage/actions/workflows/ci.yml/badge.svg)](https://github.com/kelleyblackmore/local-storage/actions/workflows/ci.yml)
## Features
- Upload, download, and delete files via API or web UI
- List all uploaded files with metadata
- Simple, local storage (no cloud dependencies)

## Building the RPM

To build the RPM package, run:

```sh
./build.sh
```

This will generate an RPM file at:

```
~/rpmbuild/RPMS/noarch/artifact-api-local-1.0.0-1.el10.noarch.rpm
```

## Installing the RPM

To install (or upgrade) the service, use:

```sh
sudo rpm -ivh ~/rpmbuild/RPMS/noarch/artifact-api-local-1.0.0-1.el10.noarch.rpm --force
```

This will:
- Install the service files to `/opt/artifact-api-local/`
- Set up a systemd service `artifact-api-local`
- Create a storage directory at `/var/lib/artifact-api/`

## Starting the Service

Enable and start the service with:

```sh
sudo systemctl enable artifact-api-local
sudo systemctl start artifact-api-local
```

Check status and logs:

```sh
sudo systemctl status artifact-api-local
sudo journalctl -u artifact-api-local -n 50
```

## Accessing the Service

After installation and starting the service, you can access it at:

- Web UI: http://127.0.0.1:54321
- API Base URL: http://127.0.0.1:54321
- Prod URL: http:0.0.0.0:8000


To verify the service is running:
```sh
# Check service status
sudo systemctl status artifact-api-local

# Test the health endpoint
curl http://0.0.0.0:8000/health
```

### Troubleshooting

If you can't access the service:

1. Check if the service is running:
   ```sh
   sudo systemctl status artifact-api-local
   ```

2. Check the service logs for errors:
   ```sh
   sudo journalctl -u artifact-api-local -n 50
   ```

3. Verify the port is not in use:
   ```sh
   sudo lsof -i :54321
   ```

4. If the port is in use, stop any existing instances:
   ```sh
   sudo pkill -f "uvicorn main:app"
   ```

5. Restart the service:
   ```sh
   sudo systemctl restart artifact-api-local
   ```

## API Endpoints
- `POST /upload` — Upload a file
- `GET /files` — List all files
- `GET /download/{filename}` — Download a file
- `DELETE /files/{filename}` — Delete a file
- `GET /health` — Health check

## Development & Testing

To run the API in development mode:

```sh
cd api
python3 -m uvicorn main:app --reload --host 127.0.0.1 --port 54321
```

To run the test script:

```sh
python3 test_api.py
```

---

For more details, see the code and comments in `api/main.py` and `test_api.py`.

## 🎯 Project Overview

This service provides a simple HTTP API for storing and retrieving artifacts locally. It's designed to be:
- Local-only (no external networking dependencies)
- Easy to install via RPM
- Managed via systemd
- Secure and configurable

## 📋 Features

- File upload endpoint (`POST /upload`)
- Health check endpoint (`GET /health`)
- Configurable storage location
- Logging to system journal
- Runs as a dedicated service user

## 🛠️ Installation

### From RPM

```bash
# Install the RPM
sudo rpm -ivh artifact-api-local-1.0.0-1.el8.x86_64.rpm

# Start the service
sudo systemctl start artifact-api-local

# Enable on boot
sudo systemctl enable artifact-api-local
```

### Manual Build

```bash
# Build the RPM
rpmbuild -bb packaging/artifact-api-local.spec

# Install dependencies
sudo dnf install python3-fastapi python3-uvicorn
```

## 🔧 Configuration

The service can be configured via environment variables:

- `ARTIFACT_STORAGE_PATH`: Storage location
  - Development default: `./storage` (relative to application directory)
  - Production default: `/var/lib/artifact-api`
- `ARTIFACT_API_PORT`: API port (default: 54321)
- `ARTIFACT_API_HOST`: Bind address (default: 127.0.0.1)

### Storage Locations

- **Development**: Files are stored in `./storage` relative to where you run the application
- **Production**: Files are stored in `/var/lib/artifact-api` when installed via RPM
- **Custom**: You can override the storage location using `ARTIFACT_STORAGE_PATH`

#### Storage Directory Structure

```
storage/
├── 2024/                    # Year directory
│   ├── 01/                 # Month directory (January)
│   │   ├── file1.txt      # Uploaded file
│   │   ├── file2.pdf      # Uploaded file
│   │   └── metadata.json  # File metadata
│   └── 02/                 # Month directory (February)
│       ├── file3.txt
│       └── metadata.json
└── 2025/                    # Next year's directory
    └── ...
```

Each month's directory contains:
- Uploaded files
- A `metadata.json` file tracking:
  - Original filename
  - Upload timestamp
  - File size
  - Content type
  - Storage path

## 📁 Project Structure

```
.
├── api/                    # Application code
│   ├── main.py            # FastAPI application
│   └── requirements.txt    # Python dependencies
├── packaging/             # RPM and systemd files
│   ├── artifact-api-local.spec
│   └── artifact-api-local.service
├── tests/                 # Integration tests
└── README.md             # This file
```

## 🧪 Testing

```bash
# Run tests
python3 -m pytest tests/

# Manual test
curl -X POST -F "file=@test.txt" http://localhost:54321/upload
```

## 📝 License

MIT License

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## 🔍 Project Plan

See the detailed project plan in [PROJECT_PLAN.md](PROJECT_PLAN.md) 