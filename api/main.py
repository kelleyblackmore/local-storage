import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.requests import Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Local Artifact Storage API",
    description="A local-only API for storing and retrieving artifacts",
    version="1.0.0",
)

# Determine if we're running in production (installed via RPM) or development
is_production = (
    Path(__file__).parent.parent.name == "opt"
    and Path(__file__).parent.name == "artifact-api-local"
)

if is_production:
    storage_path = Path("/var/lib/artifact-api")
    logger.info("Running in production mode with system storage")
else:
    storage_path = Path(__file__).parent / "storage"
    logger.info("Running in development mode with local storage")

logger.info(f"Storage directory: {storage_path}")

# Ensure storage directory exists
storage_path.mkdir(parents=True, exist_ok=True)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


def get_metadata(file_path: Path) -> Optional[Dict[str, Any]]:
    """Get metadata for a file."""
    try:
        metadata_path = file_path.parent / "metadata.json"
        if metadata_path.exists():
            with open(metadata_path, "r") as f:
                metadata = json.load(f)
                if file_path.name in metadata:
                    return metadata[file_path.name]
        return None
    except Exception as e:
        logger.error(f"Error reading metadata for {file_path}: {str(e)}")
        return None


def update_metadata(file_path: Path, metadata: Dict[str, Any]) -> None:
    """Update metadata for a file."""
    try:
        metadata_path = file_path.parent / "metadata.json"
        existing_metadata = {}
        if metadata_path.exists():
            with open(metadata_path, "r") as f:
                existing_metadata = json.load(f)

        existing_metadata[file_path.name] = metadata
        with open(metadata_path, "w") as f:
            json.dump(existing_metadata, f, indent=2)
    except Exception as e:
        logger.error(f"Error updating metadata for {file_path}: {str(e)}")


def find_file(filename: str) -> Optional[Path]:
    """Find a file in the storage directory."""
    # Search in all year/month directories
    for year_dir in storage_path.iterdir():
        if not year_dir.is_dir():
            continue
        for month_dir in year_dir.iterdir():
            if not month_dir.is_dir():
                continue
            file_path = month_dir / filename
            if file_path.exists() and file_path.is_file():
                return file_path

            # Check metadata for the file
            metadata_path = month_dir / "metadata.json"
            if metadata_path.exists():
                try:
                    with open(metadata_path, "r") as f:
                        metadata = json.load(f)
                        if filename in metadata:
                            # Verify the file actually exists
                            if file_path.exists() and file_path.is_file():
                                return file_path
                except json.JSONDecodeError:
                    logger.warning(f"Invalid metadata file at {metadata_path}")
                    continue
    return None


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Serve the web UI."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload a file."""
    try:
        # Create year/month directory structure
        now = datetime.now()
        year_dir = storage_path / str(now.year)
        month_dir = year_dir / f"{now.month:02d}"
        month_dir.mkdir(parents=True, exist_ok=True)

        # Save the file
        file_path = month_dir / file.filename
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # Update metadata
        metadata = {
            "filename": file.filename,
            "size": len(content),
            "content_type": file.content_type,
            "uploaded_at": now.isoformat(),
            "storage_path": str(file_path.relative_to(storage_path)),
        }
        update_metadata(file_path, metadata)

        logger.info(f"File uploaded successfully: {file.filename}")
        return {
            "filename": file.filename,
            "size": len(content),
            "storage_path": str(file_path.relative_to(storage_path)),
        }
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/files")
async def list_files():
    """List all available files with their metadata."""
    try:
        files = []
        logger.info(f"Listing files from storage directory: {storage_path}")

        # Check if storage directory exists
        if not storage_path.exists():
            logger.warning(f"Storage directory {storage_path} does not exist")
            return {"files": []}

        # Walk through all year/month directories
        for year_dir in storage_path.iterdir():
            if not year_dir.is_dir():
                logger.debug(f"Skipping non-directory: {year_dir}")
                continue
            logger.info(f"Scanning year directory: {year_dir}")

            for month_dir in year_dir.iterdir():
                if not month_dir.is_dir():
                    logger.debug(f"Skipping non-directory: {month_dir}")
                    continue
                logger.info(f"Scanning month directory: {month_dir}")

                # Check if we can read the directory
                try:
                    for file_path in month_dir.iterdir():
                        if file_path.name != "metadata.json" and file_path.is_file():
                            try:
                                metadata = get_metadata(file_path)
                                if metadata:
                                    files.append(
                                        {
                                            "filename": file_path.name,
                                            "storage_path": str(
                                                file_path.relative_to(storage_path)
                                            ),
                                            "metadata": metadata,
                                        }
                                    )
                                    logger.info(f"Added file to list: {file_path.name}")
                                else:
                                    logger.warning(
                                        f"No metadata found for file: {file_path}"
                                    )
                            except Exception as e:
                                logger.error(
                                    f"Error processing file {file_path}: {str(e)}"
                                )
                                continue
                except PermissionError:
                    logger.error(f"Permission denied accessing directory: {month_dir}")
                    continue
                except Exception as e:
                    logger.error(f"Error reading directory {month_dir}: {str(e)}")
                    continue

        # Sort files by upload date (newest first)
        files.sort(key=lambda x: x["metadata"]["uploaded_at"], reverse=True)

        logger.info(f"Found {len(files)} files")
        return {"files": files}
    except Exception as e:
        logger.error(f"Error listing files: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/download/{filename}")
async def download_file(filename: str):
    """Download a file."""
    try:
        file_path = find_file(filename)
        if not file_path:
            raise HTTPException(status_code=404, detail="File not found")

        return FileResponse(
            file_path, filename=filename, media_type="application/octet-stream"
        )
    except Exception as e:
        logger.error(f"Error downloading file {filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/files/{filename}")
async def delete_file(filename: str):
    """Delete a file."""
    try:
        file_path = find_file(filename)
        if not file_path:
            raise HTTPException(status_code=404, detail="File not found")

        # Delete the file
        file_path.unlink()

        # Update metadata
        metadata_path = file_path.parent / "metadata.json"
        if metadata_path.exists():
            try:
                with open(metadata_path, "r") as f:
                    metadata = json.load(f)
                if filename in metadata:
                    del metadata[filename]
                    with open(metadata_path, "w") as f:
                        json.dump(metadata, f, indent=2)
            except Exception as e:
                logger.error(f"Error updating metadata after deletion: {str(e)}")

        logger.info(f"File deleted successfully: {filename}")
        return {"message": f"File {filename} deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting file {filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


def start():
    """Start the FastAPI application."""
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    start()
