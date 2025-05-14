Name:           artifact-api-local
Version:        1.0.0
Release:        1%{?dist}
Summary:        Local Artifact Storage API

License:        MIT
URL:            https://github.com/yourusername/artifact-api-local
BuildArch:      noarch

Requires:       python3

%description
A local-only web application that accepts and stores uploaded files (artifacts),
running as a systemd service on RHEL-based systems.

%prep
# No prep needed as we're not building from source

%build
# No build needed as we're packaging Python files

%install
# Create directories
mkdir -p %{buildroot}/opt/artifact-api-local
mkdir -p %{buildroot}/usr/lib/systemd/system
mkdir -p %{buildroot}/var/lib/artifact-api

# Copy application files
cp -r api/* %{buildroot}/opt/artifact-api-local/

# Copy systemd service file
cp artifact-api-local.service %{buildroot}/usr/lib/systemd/system/

# Set permissions
chmod 755 %{buildroot}/opt/artifact-api-local
chmod 644 %{buildroot}/usr/lib/systemd/system/artifact-api-local.service

%post
# Create artifact-api-local user and group if they don't exist
getent group artifact-api-local >/dev/null || groupadd -r artifact-api-local
getent passwd artifact-api-local >/dev/null || useradd -r -g artifact-api-local -d /var/lib/artifact-api -s /sbin/nologin -c "Artifact API Service" artifact-api-local

# Set ownership of the data directory
chown -R artifact-api-local:artifact-api-local /var/lib/artifact-api

# Create a virtual environment for the service
python3 -m venv /opt/artifact-api-local/venv

# Install Python dependencies into the venv
/opt/artifact-api-local/venv/bin/pip install --upgrade pip
/opt/artifact-api-local/venv/bin/pip install -r /opt/artifact-api-local/requirements.txt

# Enable and start the service
systemctl daemon-reload
systemctl enable artifact-api-local
systemctl start artifact-api-local

%preun
# Stop the service before uninstalling
systemctl stop artifact-api-local
systemctl disable artifact-api-local

%files
%defattr(-,artifact-api-local,artifact-api-local,-)
/opt/artifact-api-local/
/usr/lib/systemd/system/artifact-api-local.service
/var/lib/artifact-api/

%changelog
* Wed Nov 15 2023 Your Name <your.email@example.com> - 1.0.0-1
- Initial release 