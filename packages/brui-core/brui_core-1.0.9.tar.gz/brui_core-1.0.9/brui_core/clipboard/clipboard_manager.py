import pyperclip
import asyncio
import logging
import sys

logger = logging.getLogger(__name__)

# Configure pyperclip to use a Linux-compatible clipboard command when running on Linux.
if sys.platform.startswith('linux'):
    try:
        pyperclip.set_clipboard('xclip')
        logger.debug("pyperclip clipboard set to 'xclip' for Linux environment.")
    except Exception as e:
        logger.error(f"Failed to set clipboard to 'xclip': {e}")

async def wait_for_clipboard_content():
    """
    Wait for the clipboard content to change and return the new content.
    
    :return: The new clipboard content as a string.
    """
    initial_clipboard = pyperclip.paste()
    if initial_clipboard != '':
        return initial_clipboard
    while True:
        await asyncio.sleep(0.1)
        new_clipboard = pyperclip.paste()
        if new_clipboard != initial_clipboard:
            pyperclip.copy('')
            return new_clipboard

async def ensure_clipboard_is_empty(max_retries: int = 3, retry_delay: float = 0.5) -> bool:
    """
    Ensures the clipboard is empty by copying an empty string and verifying.
    
    This function attempts to clear the clipboard and then verifies that it's
    actually empty. If verification fails, it retries up to max_retries times.
    
    Parameters:
        max_retries (int): Maximum number of attempts to clear the clipboard.
        retry_delay (float): Delay in seconds between retry attempts.
        
    Returns:
        bool: True if clipboard was successfully cleared, False otherwise.
    """
    logger.debug("Attempting to ensure clipboard is empty")
    
    for attempt in range(max_retries):
        try:
            # Clear the clipboard
            pyperclip.copy("")
            logger.debug(f"Clipboard cleared (attempt {attempt + 1}/{max_retries})")
            
            # Get clipboard content to verify it's empty
            await asyncio.sleep(0.2)  # Small delay to allow clipboard to update
            clipboard_content = pyperclip.paste()
            
            # If clipboard is empty, return success
            if clipboard_content == "":
                logger.debug("Verified clipboard is empty")
                return True
            
            logger.warning(f"Clipboard not empty after clearing attempt {attempt + 1}. "
                           f"Content length: {len(clipboard_content)}")
            
            # Wait before retrying
            if attempt < max_retries - 1:
                await asyncio.sleep(retry_delay)
                
        except Exception as e:
            logger.error(f"Error while clearing clipboard (attempt {attempt + 1}): {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(retry_delay)
    
    logger.warning(f"Failed to clear clipboard after {max_retries} attempts")
    return False
