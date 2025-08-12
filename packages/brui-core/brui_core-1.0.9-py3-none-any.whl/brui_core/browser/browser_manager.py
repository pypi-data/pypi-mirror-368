import asyncio
import logging
from typing import Optional

from playwright.async_api import async_playwright
from playwright.async_api import Browser, BrowserContext

from brui_core.browser.browser_launcher import (
    is_browser_opened_in_debug_mode,
    launch_browser,
    get_browser_config,
    kill_all_chrome_processes
)
from brui_core.singleton_meta import SingletonMeta

logger = logging.getLogger(__name__)

class BrowserManager(metaclass=SingletonMeta):
    def __init__(self):
        self.browser_launch_lock = asyncio.Lock()
        self.playwright: Optional[async_playwright] = None
        self.browser: Optional[Browser] = None

    async def is_browser_running(self) -> bool:
        try:
            return await is_browser_opened_in_debug_mode()
        except Exception as e:
            logger.error(f"Error checking if browser is running: {str(e)}")
            return False

    async def reset_browser_state(self):
        """Reset the browser state and clean up existing connections"""
        try:
            if self.browser is not None:
                await self.browser.close()
                self.browser = None
            if self.playwright is not None:
                await self.playwright.stop()
                self.playwright = None
        except Exception as e:
            logger.error(f"Error resetting browser state: {str(e)}")
            # Still reset the state even if cleanup fails
            self.browser = None
            self.playwright = None

    async def ensure_browser_launched(self):
        """Ensure browser is launched, resetting state if necessary"""
        if not await self.is_browser_running():
            async with self.browser_launch_lock:
                if not await self.is_browser_running():  # Double-check after acquiring lock
                    # Reset state before launching new browser
                    await self.reset_browser_state()
                    try:
                        await launch_browser()
                    except Exception as e:
                        logger.error(f"Failed to launch browser: {str(e)}")
                        raise

    async def get_browser_context(self, browser: Browser) -> BrowserContext:
        """
        Safely access the browser context with recovery for invalid browser states
        
        Args:
            browser: The browser instance to get context from
            
        Returns:
            The browser context
            
        Raises:
            Exception: If unable to access a valid browser context
        """
        logger.info("Accessing browser context...")
        try:
            context = browser.contexts[0]
            logger.info(f"Successfully accessed browser context. Pages in context: {len(context.pages)}")
            return context
        except IndexError:
            logger.warning("No browser contexts available, browser may be in invalid state")
            logger.info("Resetting connection and trying again...")
            
            # Reset the state completely
            await self.reset_browser_state()
            
            # Reconnect with fresh browser instance (this will run ensure_browser_launched)
            await self.connect_browser(reconnect=True)
            
            # Try again with the new browser instance
            try:
                context = self.browser.contexts[0]
                logger.info(f"Successfully accessed browser context after reconnection. Pages: {len(context.pages)}")
                return context
            except IndexError:
                logger.error("Failed to access browser context after reconnection: No contexts available")
                raise
            except Exception as e:
                logger.error(f"Failed to access browser context after reconnection: {str(e)}")
                raise
        except Exception as e:
            logger.error(f"Failed to access browser context: {str(e)}")
            raise

    async def connect_browser(self, reconnect=False) -> Browser:
        """
        Connect to the browser, launching it if necessary
        
        Args:
            reconnect (bool): If True, force reconnection even if a browser instance exists
        
        Returns:
            Connected browser instance
        """
        await self.ensure_browser_launched()
        
        try:
            # If we have a browser already and not forcing reconnection, return it
            if self.browser is not None and not reconnect:
                return self.browser
                
            # Reset browser reference if reconnecting
            if reconnect and self.browser is not None:
                self.browser = None
                
            # If Playwright is None, initialize it
            if self.playwright is None:
                self.playwright = await async_playwright().start()
                
            # Fetch configuration for remote debugging port at runtime
            config = get_browser_config()
            remote_debugging_port = config["browser"].get("remote_debugging_port", 9222)
            endpoint_url = f"http://localhost:{remote_debugging_port}"
            self.browser = await self.playwright.chromium.connect_over_cdp(endpoint_url)
            return self.browser
            
        except Exception as e:
            # If connection fails, clean up resources and re-raise
            logger.error(f"Error connecting to browser: {str(e)}")
            await self.reset_browser_state()
            raise

    async def stop_browser(self):
        """Stop the browser and clean up resources"""
        await self.reset_browser_state()
        try:
            # Run the synchronous kill function in a separate thread to avoid blocking the event loop
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, kill_all_chrome_processes)
            logger.info("Successfully terminated all Chrome processes via BrowserManager.")
        except Exception as e:
            logger.error(f"Error terminating Chrome processes during stop_browser: {e}")
            raise
