import pytest
import asyncio
from brui_core.browser.browser_manager import BrowserManager
from brui_core.browser.browser_launcher import get_chrome_pids, kill_all_chrome_processes

@pytest.fixture(autouse=True)
def clean_chrome_state():
    """Ensure a clean state by killing all Chrome processes before and after each test."""
    kill_all_chrome_processes()
    yield
    kill_all_chrome_processes()

@pytest.fixture
def browser_manager(event_loop):
    """
    Provide a clean BrowserManager instance for each test.
    This fixture ensures a fresh, isolated manager for each test and handles teardown.
    """
    # Clear the singleton cache to ensure a fresh instance for each test.
    BrowserManager._instances = {}
    manager = BrowserManager()

    yield manager
    
    # Run async cleanup in the event loop.
    event_loop.run_until_complete(manager.stop_browser())

@pytest.mark.asyncio
async def test_initial_state(browser_manager):
    """Test that a new BrowserManager instance starts in the correct state."""
    assert not await browser_manager.is_browser_running()
    assert browser_manager.browser is None
    assert browser_manager.playwright is None

def test_singleton_behavior():
    """Verify that BrowserManager is a singleton."""
    # Ensure a clean state for this specific test.
    BrowserManager._instances = {}
    manager1 = BrowserManager()
    manager2 = BrowserManager()
    assert manager1 is manager2

@pytest.mark.asyncio
async def test_launch_and_connect(browser_manager):
    """Test the browser can be launched and connected to."""
    await browser_manager.ensure_browser_launched()
    assert await browser_manager.is_browser_running()
    assert get_chrome_pids()

    browser = await browser_manager.connect_browser()
    assert browser is not None
    assert browser.is_connected()
    assert browser_manager.browser is browser
    assert browser_manager.playwright is not None

@pytest.mark.asyncio
async def test_stop_browser(browser_manager):
    """Test that stop_browser correctly terminates the browser process."""
    # First, launch the browser
    await browser_manager.ensure_browser_launched()
    assert await browser_manager.is_browser_running()

    # Now, stop it
    await browser_manager.stop_browser()
    
    # Wait for the browser to fully shut down and release the port.
    for _ in range(50):  # Wait up to 5 seconds (25 * 0.2s)
        if not await browser_manager.is_browser_running():
            break
        await asyncio.sleep(0.2)
    else:
        pytest.fail("Browser did not shut down and release port in time.")

    assert not get_chrome_pids()
    assert browser_manager.browser is None
    assert browser_manager.playwright is None

@pytest.mark.asyncio
async def test_reconnect_reuses_instance(browser_manager):
    """Verify that subsequent calls to connect_browser return the same instance."""
    browser1 = await browser_manager.connect_browser()
    initial_processes = get_chrome_pids()
    assert initial_processes

    browser2 = await browser_manager.connect_browser()
    assert browser1 is browser2
    assert len(get_chrome_pids()) == len(initial_processes)

@pytest.mark.asyncio
async def test_restart_after_stop(browser_manager):
    """Test that a new browser can be started after a full stop."""
    # Launch and stop the first instance
    browser1 = await browser_manager.connect_browser()
    await browser_manager.stop_browser()

    # Wait for shutdown to complete
    for _ in range(25):
        if not await browser_manager.is_browser_running():
            break
        await asyncio.sleep(0.2)
    else:
        pytest.fail("Browser did not shut down in time for restart test.")
    
    # Launch again and connect
    browser2 = await browser_manager.connect_browser()
    assert browser2 is not None
    assert browser2.is_connected()
    assert browser1 is not browser2  # Must be a new instance

@pytest.mark.asyncio
async def test_connection_recovery_after_disconnect(browser_manager):
    """Test recovery from a disconnected state without killing the process."""
    # Establish initial connection
    browser = await browser_manager.connect_browser()
    assert browser.is_connected()
    
    # Simulate a client-side disconnect without killing the browser process
    await browser_manager.browser.close()
    assert not browser.is_connected()
    assert await browser_manager.is_browser_running() # Process should still be alive

    # Attempt to reconnect
    recovered_browser = await browser_manager.connect_browser(reconnect=True)
    assert recovered_browser is not None
    assert recovered_browser.is_connected()
    assert recovered_browser is not browser
