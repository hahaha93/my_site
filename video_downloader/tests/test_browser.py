import pytest
from playwright.sync_api import Page, expect
import subprocess
import time
import requests
import os
import signal
import sys

# Global process handles
backend_process = None
frontend_process = None

@pytest.fixture(scope="session", autouse=True)
def start_servers():
    global backend_process, frontend_process
    
    os.makedirs("logs", exist_ok=True)
    backend_log = open("logs/backend.log", "w")
    frontend_log = open("logs/frontend.log", "w")
    
    # Start Backend
    print("Starting Backend...")
    backend_env = os.environ.copy()
    backend_process = subprocess.Popen(
        ["uvicorn", "backend.main:app", "--port", "8001"],
        cwd="/home/robertlo/Desktop/personal/Tool/video_downloader",
        env=backend_env,
        stdout=backend_log,
        stderr=backend_log
    )
    
    # Start Frontend
    print("Starting Frontend...")
    frontend_env = os.environ.copy()
    frontend_env["BACKEND_URL"] = "http://127.0.0.1:8001"
    frontend_process = subprocess.Popen(
        ["python3", "frontend/app.py"],
        cwd="/home/robertlo/Desktop/personal/Tool/video_downloader",
        env=frontend_env,
        stdout=frontend_log,
        stderr=frontend_log
    )

    # Wait for servers to start
    max_retries = 30
    backend_ready = False
    frontend_ready = False
    
    for i in range(max_retries):
        try:
            if not backend_ready:
                requests.get("http://127.0.0.1:8001/docs") 
                backend_ready = True
                print("Backend Ready")
            if not frontend_ready:
                requests.get("http://127.0.0.1:5000/")
                frontend_ready = True
                print("Frontend Ready")
            
            if backend_ready and frontend_ready:
                break
        except Exception:
            pass
        time.sleep(1)
        
    if not (backend_ready and frontend_ready):
        print("Servers failed to start.")
        if backend_process: os.kill(backend_process.pid, signal.SIGTERM)
        if frontend_process: os.kill(frontend_process.pid, signal.SIGTERM)
        pytest.fail("Servers failed to start")

    yield

    print("Stopping servers...")
    if backend_process:
        os.kill(backend_process.pid, signal.SIGTERM)
    if frontend_process:
        os.kill(frontend_process.pid, signal.SIGTERM)

def test_homepage_loads(page: Page):
    page.goto("http://127.0.0.1:5000/")
    expect(page).to_have_title("Premium Video Downloader")
    expect(page.locator("h1")).to_contain_text("Video Downloader")

def test_playlist_option_removed(page: Page):
    page.goto("http://127.0.0.1:5000/")
    # Radio buttons for "video" vs "playlist" should be gone
    expect(page.locator("input[name='type']")).to_have_count(0)
    expect(page.locator("text=Playlist")).to_have_count(0)

def test_download_button_updated(page: Page):
    page.goto("http://127.0.0.1:5000/")
    expect(page.locator("#submitBtn span")).to_have_text("Download File")
