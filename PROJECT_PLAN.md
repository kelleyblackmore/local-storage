# Project Plan: Local Artifact Storage API RPM Service

## 🎯 Project Name: `artifact-api-local`

## 📋 Goal

Build a local-only web application that accepts and stores uploaded files (artifacts), is installable as an RPM, and runs as a systemd service on RHEL-based systems.

## 📁 Phase 1: Requirements & Setup

### Tasks:

- [x] Define functional requirements:
  - Accept file uploads via `/upload`
  - Store artifacts to `/var/lib/artifact-api`
  - Local-only (no external networking dependencies)
- [x] Choose language/framework (FastAPI)
- [x] Create Git repo structure with:
  - `/api/` - application code
  - `/packaging/` - RPM and systemd service files
  - `/tests/` - basic integration tests

### Deliverables:

- [x] Tech stack decision
- [x] Initial repo scaffolding

## 📦 Phase 2: API Development

### Tasks:

- [ ] Implement basic upload endpoint (`POST /upload`)
- [ ] Save files to local disk
- [ ] Create health check endpoint (`GET /health`)
- [ ] Log uploads and errors
- [ ] Add configurable upload directory via environment variable

### Deliverables:

- [ ] Fully working API in local dev mode
- [ ] Logging to console or file
- [ ] README with local run instructions

## ⚙️ Phase 3: Systemd Integration

### Tasks:

- [ ] Write `artifact-api-local.service` systemd unit
- [ ] Support config via environment variables
- [ ] Allow `ExecStart` to be easily changed
- [ ] Test running as `nobody` or custom service user

### Deliverables:

- [ ] Tested systemd unit file
- [ ] Verified manual startup via `systemctl start`

## 📦 Phase 4: RPM Packaging

### Tasks:

- [ ] Create `artifact-api-local.spec` file
- [ ] Ensure build includes:
  - Application files to `/opt/artifact-api-local`
  - systemd service to `/usr/lib/systemd/system/`
  - Artifact directory at `/var/lib/artifact-api`
- [ ] Add `%post` script for enabling and starting service
- [ ] Test install and uninstall flows

### Deliverables:

- [ ] RPM build script and tree
- [ ] Working `.rpm` file
- [ ] Instructions for building locally (`rpmbuild`)

## 🧪 Phase 5: Testing & Verification

### Tasks:

- [ ] Write automated test script for upload
- [ ] Test service lifecycle:
  - `install`, `start`, `restart`, `stop`, `remove`
- [ ] Verify logs and storage path
- [ ] Test edge cases (large files, unsupported formats)

### Deliverables:

- [ ] Test results
- [ ] Manual QA checklist

## 🧰 Optional: CI/CD & Extras

### Tasks:

- [ ] Add GitHub Actions workflow to build/test RPM
- [ ] Add CLI tool or script to interact with the API
- [ ] Add logging to `/var/log/artifact-api.log`

## 📝 Summary of Artifacts

| File/Folder                          | Purpose                  |
| ------------------------------------ | ------------------------ |
| `/api/main.py`                       | Web API application      |
| `/packaging/artifact-api-local.service` | systemd unit         |
| `/packaging/artifact-api-local.spec` | RPM spec file            |
| `/var/lib/artifact-api/`             | Upload storage location  |
| `/usr/lib/systemd/system/`           | Service file destination |
| `/opt/artifact-api-local/`           | Installed app location   | 