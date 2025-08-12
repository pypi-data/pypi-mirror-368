import pytest
import asyncio
import os
import socket
import time
from pathlib import Path

from brui_core.browser.browser_launcher import (
    launch_browser,
    kill_all_chrome_processes,
    is_browser_opened_in_debug_mode,
    get_browser_config,
    get_chrome_pids,
)


@pytest.fixture(autouse=True)
def setup_and_cleanup():
    """Ensure clean state before and after tests by killing all Chrome processes"""
    kill_all_chrome_processes()
    yield
    kill_all_chrome_processes()


def is_port_in_use(port):
    """Check if a port is actually in use"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0


@pytest.mark.asyncio
async def test_launch_and_kill_browser_flow():
    """Test the complete flow of launching and killing Chrome"""
    # Verify no Chrome processes at start
    assert not get_chrome_pids(), "Chrome processes found before test"
    assert not await is_browser_opened_in_debug_mode(), "Debug port should not be open"

    # Launch browser
    await launch_browser()

    # Verify Chrome is running
    chrome_processes = get_chrome_pids()
    assert chrome_processes, "No Chrome processes found after launch"

    # Verify debug port is listening
    port = get_browser_config()["browser"]["remote_debugging_port"]
    assert await is_browser_opened_in_debug_mode(), "Debug port not open after launch"
    assert is_port_in_use(port), "Debug port not actually listening"

    # Kill browser
    kill_all_chrome_processes()

    # Verify cleanup
    assert not get_chrome_pids(), "Chrome processes still running after kill"
    assert not await is_browser_opened_in_debug_mode(), "Debug port still open after kill"
    assert not is_port_in_use(port), "Debug port still in use"


@pytest.mark.asyncio
async def test_multiple_launch_attempts():
    """Test launching browser multiple times"""
    # First launch
    await launch_browser()

    # Allow some time for Chrome to start
    await asyncio.sleep(5)

    initial_processes = get_chrome_pids()
    assert initial_processes, "First launch failed"

    # Capture the number of Chrome processes
    initial_count = len(initial_processes)

    # Try second launch without killing
    await launch_browser()

    # Allow some time for potential additional processes
    await asyncio.sleep(5)

    new_processes = get_chrome_pids()
    new_count = len(new_processes)

    # Should not create additional processes
    assert new_count == initial_count, "Multiple launches created extra processes"

    # Debug port should still be accessible
    assert await is_browser_opened_in_debug_mode(), "Debug mode not accessible after second launch"

    # Cleanup
    kill_all_chrome_processes()
    await asyncio.sleep(5)


@pytest.fixture
def temp_config(tmp_path):
    """Fixture to create a temporary config file"""
    config_dir = tmp_path / "test_config"
    config_dir.mkdir()
    config_file = config_dir / "config.toml"
    config_content = """
[browser]
chrome_profile_directory = "Integration Test Profile"
remote_debugging_port = 9222
download_directory = "/tmp/downloads"
"""
    config_file.write_text(config_content)
    return config_file


def test_config_loading(temp_config):
    """Test loading real and overridden configuration files"""
    # Set environment variable to use the temporary config file
    os.environ['BROWSER_CONFIG_PATH'] = str(temp_config)

    config = get_browser_config()
    assert config['browser']['chrome_profile_directory'] == "Integration Test Profile"
    assert config['browser']['remote_debugging_port'] == 9222
    assert config['browser']['download_directory'] == "/tmp/downloads"

    # Override chrome_profile_directory using environment variable
    os.environ['CHROME_PROFILE_DIRECTORY'] = "Override Profile"
    config = get_browser_config()
    assert config['browser']['chrome_profile_directory'] == "Override Profile"

    # Override download_directory using environment variable
    os.environ['CHROME_DOWNLOAD_DIRECTORY'] = "/override/downloads"
    config = get_browser_config()
    assert config['browser']['download_directory'] == "/override/downloads"

    # Cleanup environment variables
    del os.environ['BROWSER_CONFIG_PATH']
    del os.environ['CHROME_PROFILE_DIRECTORY']
    del os.environ['CHROME_DOWNLOAD_DIRECTORY']


@pytest.mark.asyncio
async def test_browser_startup_timeout():
    """Test browser startup with actual timeout"""
    # First, kill all Chrome processes to ensure a clean state
    kill_all_chrome_processes()
    await asyncio.sleep(2)

    # Temporarily set remote_debugging_port to an unused port to simulate timeout
    unused_port = 9999
    try:
        os.environ['CHROME_REMOTE_DEBUGGING_PORT'] = str(unused_port)
        with pytest.raises(TimeoutError):
            # launch_browser doesn't take a timeout, it uses the default.
            # We expect this to time out because we're launching on a port
            # that we're not listening to.
            await launch_browser()
    finally:
        # Clean up environment variable to not affect other tests
        if 'CHROME_REMOTE_DEBUGGING_PORT' in os.environ:
            del os.environ['CHROME_REMOTE_DEBUGGING_PORT']
        kill_all_chrome_processes()
        await asyncio.sleep(2)


def test_kill_nonexistent_browser():
    """Test killing Chrome when no processes exist"""
    # Ensure no Chrome is running
    kill_all_chrome_processes()
    assert not get_chrome_pids(), "Chrome processes found before test"

    # Attempt to kill Chrome processes when none exist
    try:
        kill_all_chrome_processes()
    except Exception as e:
        pytest.fail(f"kill_all_chrome_processes raised an exception when no processes exist: {e}")


@pytest.mark.asyncio
async def test_debug_mode_check():
    """Test debug mode detection with actual browser"""
    # Initial state
    assert not await is_browser_opened_in_debug_mode(), "Debug mode active before browser launch"

    # Launch browser
    await launch_browser()

    # Allow some time for Chrome to start and listen on the debug port
    await asyncio.sleep(5)

    # Verify debug mode
    port = get_browser_config()["browser"]["remote_debugging_port"]
    assert await is_browser_opened_in_debug_mode(), "Debug mode not detected after launch"
    assert is_port_in_use(port), "Debug port not actually listening after launch"

    # Kill browser
    kill_all_chrome_processes()

    # Allow processes time to fully terminate
    await asyncio.sleep(5)

    # Verify debug mode inactive
    assert not await is_browser_opened_in_debug_mode(), "Debug mode still active after kill"
    assert not is_port_in_use(port), "Debug port still in use after kill"
