import os
import sys
import subprocess
import socket
import asyncio
import time
import logging
import copy
from typing import Set, Optional, NamedTuple

# Static configuration
CONFIG = {
    "browser": {
        "chrome_profile_directory": "Profile 1",
        "remote_debugging_port": 9222
    }
}

logger = logging.getLogger(__name__)

class ChromeProcess(NamedTuple):
    pid: int
    ppid: int
    cmd: str

def get_chrome_startup_path() -> str:
    """
    Returns the Chrome startup path for Linux.
    This path is used to launch Chrome on Linux systems.
    """
    # Linux path for starting Google Chrome
    return '/usr/bin/google-chrome'

def get_chrome_process_path() -> str:
    """
    Returns the path to match against running Chrome processes on Linux.
    This is the actual executable path seen in ps output.
    """
    return '/opt/google/chrome/chrome'

def get_chrome_pids() -> Set[ChromeProcess]:
    """
    Get all Chrome process PIDs using Linux specific commands.
    Returns a set of ChromeProcess objects containing pid, ppid, and command.
    """
    try:
        chrome_path = get_chrome_process_path()
        chrome_processes = set()

        # Linux (GNU) ps syntax
        cmd = ['ps', '-eo', 'pid=,ppid=,cmd=']

        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.error(f"Failed to get process list: {result.stderr}")
            return set()

        # Process each line of output
        for line in result.stdout.splitlines():
            try:
                # Split line but preserve command with all its arguments
                parts = line.strip().split(maxsplit=2)
                if len(parts) == 3:
                    pid, ppid, command = parts
                    # Only include processes that match our Chrome path
                    if chrome_path in command:
                        chrome_processes.add(ChromeProcess(
                            pid=int(pid),
                            ppid=int(ppid),
                            cmd=command
                        ))
            except (ValueError, IndexError) as e:
                logger.debug(f"Error processing process info: {e}")
                continue
                    
        return chrome_processes
    except Exception as e:
        logger.error(f"Error getting Chrome processes: {e}")
        return set()

def find_main_chrome_parent(processes: Set[ChromeProcess]) -> Optional[ChromeProcess]:
    """
    Find the main Chrome parent process that spawned other Chrome processes.
    Returns the ChromeProcess object for the main parent, or None if not found.
    """
    if not processes:
        return None

    # Create mapping of pid to process
    pid_to_process = {p.pid: p for p in processes}
    
    # Find processes whose parent is also a Chrome process
    child_processes = {p for p in processes if p.ppid in pid_to_process}
    
    # The main Chrome process should be a parent but not a child
    parent_candidates = processes - child_processes
    
    if not parent_candidates:
        return None
        
    # If multiple candidates, choose the one with the shortest command
    # (usually the main browser process has fewer arguments)
    return min(parent_candidates, key=lambda p: len(p.cmd))

def wait_for_process_termination(pid: int, timeout: int = 5) -> bool:
    """
    Wait for a process to terminate completely.
    Returns True if process terminated, False if timeout occurred.
    """
    end_time = time.time() + timeout
    while time.time() < end_time:
        try:
            os.kill(pid, 0)
            time.sleep(0.1)
        except ProcessLookupError:
            return True
        except Exception as e:
            logger.error(f"Error checking process {pid}: {e}")
            return False
    return False

def kill_all_chrome_processes():
    """
    Enhanced function to kill Chrome processes by targeting the main parent first.
    """
    try:
        # Get all Chrome processes
        chrome_processes = get_chrome_pids()
        
        if not chrome_processes:
            logger.info("No Chrome processes found to kill")
            return
            
        logger.info(f"Found Chrome processes: {chrome_processes}")
        
        # Find and kill the main parent process first
        main_parent = find_main_chrome_parent(chrome_processes)
        if main_parent:
            logger.info(f"Killing main Chrome parent process: {main_parent}")
            try:
                os.kill(main_parent.pid, 15)  # SIGTERM
                if not wait_for_process_termination(main_parent.pid, timeout=5):
                    os.kill(main_parent.pid, 9)  # SIGKILL
            except ProcessLookupError:
                pass
            
        # Check for remaining processes and force kill them
        remaining_processes = get_chrome_pids()
        if remaining_processes:
            logger.info(f"Killing remaining Chrome processes: {remaining_processes}")
            for process in remaining_processes:
                try:
                    os.kill(process.pid, 9)  # SIGKILL
                except ProcessLookupError:
                    continue
                    
        # Final verification
        final_check = get_chrome_pids()
        if final_check:
            raise Exception(f"Failed to terminate Chrome processes: {final_check}")
            
        logger.info("Successfully terminated all Chrome processes")
    except Exception as e:
        logger.error(f"Error during Chrome process termination: {e}")
        raise

async def is_browser_opened_in_debug_mode():
    """
    Check if the browser is opened in debug mode by attempting to connect to the debug port.
    """
    try:
        config = get_browser_config()
        remote_host = "localhost"
        remote_debugging_port = config["browser"].get("remote_debugging_port", 9222)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1)
            result = sock.connect_ex((remote_host, remote_debugging_port))
            return result == 0
    except (ConnectionRefusedError, OSError) as error:
        logger.error(f"Debug mode check error: {error}")
        return False

async def wait_for_browser_start(timeout=20, retry_interval=1):
    """
    Wait for the browser to start and listen on the debug port.
    
    Args:
        timeout (int): Maximum time to wait in seconds
        retry_interval (int): Time between retry attempts in seconds
    
    Raises:
        TimeoutError: If browser doesn't start within timeout period
    """
    start_time = asyncio.get_event_loop().time()
    while not await is_browser_opened_in_debug_mode():
        if asyncio.get_event_loop().time() - start_time > timeout:
            config = get_browser_config()
            remote_debugging_port = config["browser"].get("remote_debugging_port", 9222)
            raise TimeoutError(f"Timed out waiting for port {remote_debugging_port} to listen")
        await asyncio.sleep(retry_interval)

async def launch_browser():
    """
    Launches a new instance of Chrome in debug mode.
    Before launching, it assumes that any necessary cleanup (like killing existing Chrome processes)
    has already been performed if needed.
    """
    # Fetch current configuration values when needed
    config = get_browser_config()
    chrome_profile_directory = config["browser"].get("chrome_profile_directory", "Default")
    remote_debugging_port = config["browser"].get("remote_debugging_port", 9222)

    executable_path = get_chrome_startup_path()

    # Browser launch arguments
    args = [
        "--no-first-run",
        "--flag-switches-begin",
        "--flag-switches-end",
        f"--remote-debugging-port={remote_debugging_port}",
        f"--profile-directory={chrome_profile_directory}"
    ]

    subprocess.Popen([executable_path] + args)
    await wait_for_browser_start()

def get_browser_config():
    """
    Get browser configuration with environment variable overrides.
    """
    # Use deepcopy to prevent side-effects from modifying the config dict
    browser_config = copy.deepcopy(CONFIG)
    
    # Override chrome_profile_directory if CHROME_PROFILE_DIRECTORY environment variable is set
    if "CHROME_PROFILE_DIRECTORY" in os.environ:
        browser_config["browser"]["chrome_profile_directory"] = os.environ["CHROME_PROFILE_DIRECTORY"]
        logger.debug(f"Overriding chrome_profile_directory from environment: {browser_config['browser']['chrome_profile_directory']}")
    
    # Override remote_debugging_port if CHROME_REMOTE_DEBUGGING_PORT environment variable is set
    if "CHROME_REMOTE_DEBUGGING_PORT" in os.environ:
        try:
            port = int(os.environ["CHROME_REMOTE_DEBUGGING_PORT"])
            browser_config["browser"]["remote_debugging_port"] = port
            logger.debug(f"Overriding remote_debugging_port from environment: {port}")
        except ValueError:
            logger.error(f"Invalid port number in CHROME_REMOTE_DEBUGGING_PORT: {os.environ['CHROME_REMOTE_DEBUGGING_PORT']}")
    
    # Override download_directory if CHROME_DOWNLOAD_DIRECTORY is set
    if "CHROME_DOWNLOAD_DIRECTORY" in os.environ:
        browser_config["browser"]["download_directory"] = os.environ["CHROME_DOWNLOAD_DIRECTORY"]
        logger.debug(f"Overriding download_directory from environment: {browser_config['browser']['download_directory']}")

    return browser_config
