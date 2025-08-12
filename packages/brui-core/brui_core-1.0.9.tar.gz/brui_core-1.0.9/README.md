# BRUI Core (Browser UI Automation Core)

A flexible and robust browser UI automation framework that provides essential functionality for browser-based UI automation projects.

## Features

- **Browser Management**: Automated browser launching and control across different operating systems
- **Configuration Handling**: Flexible configuration management with TOML and environment variable support
- **Clipboard Integration**: Easy clipboard monitoring and manipulation
- **UI Integration Base**: Extensible base classes for UI automation
- **Cross-Platform Support**: Works on Linux and macOS

## Installation

```bash
pip install brui_core
```

## Quick Start

```python
from brui_core.ui_integrator import UIIntegrator

async def main():
    # Initialize the UI integrator
    ui = UIIntegrator()
    await ui.initialize()
    
    try:
        # Your automation code here
        pass
    finally:
        # Clean up
        await ui.close()

# Run with asyncio
import asyncio
asyncio.run(main())
```

## Requirements

- Python 3.8+
- Playwright
- Chrome/Chromium browser installed
- Additional dependencies listed in requirements.txt

## Configuration

The framework supports configuration via TOML files or environment variables:

```toml
[browser]
chrome_profile_directory = "Profile 1"
remote_debugging_port = 9222
remote_host = "localhost"
```

Environment variables:
- BROWSER_CONFIG_PATH: Path to custom browser configuration
- CHROME_PROFILE_DIRECTORY: Override chrome profile directory
- CHROME_DOWNLOAD_DIRECTORY: Override download directory

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please open an issue in the GitHub repository.

## Acknowledgments

- Built with Playwright
- Developed by AutoByteus