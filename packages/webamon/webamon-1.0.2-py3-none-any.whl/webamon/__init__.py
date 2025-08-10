"""
Webamon SDK - Brand Protection Placeholder

This package is a placeholder to protect the "webamon" brand name on PyPI.

For the actual Webamon CLI tool and functionality, please use:
    pip install webamon-cli

The webamon-cli package contains the full-featured command-line interface
for Webamon Search - The Google of Threat Intelligence.

Official Links:
- CLI Package: https://pypi.org/project/webamon-cli/
- Website: https://webamon.com
- API Documentation: https://webamon.com/api
- GitHub: https://github.com/webamon-org/webamon-cli
"""

__version__ = "1.0.2"
__author__ = "Webamon Team"
__email__ = "contact@webamon.com"

# Redirect users to the correct package
import warnings

def __getattr__(name):
    """Redirect any attribute access to inform users about webamon-cli."""
    warnings.warn(
        f"This is a placeholder package. Please install 'webamon-cli' for actual functionality: "
        f"pip install webamon-cli",
        DeprecationWarning,
        stacklevel=2
    )
    raise AttributeError(
        f"'{name}' not found. This is a placeholder package. "
        f"Please install 'webamon-cli' for actual Webamon functionality."
    )

def install_cli():
    """Helper function to guide users to install the correct package."""
    print("This is a placeholder package for brand protection.")
    print("For Webamon Search - The Google of Threat Intelligence, install the CLI tool:")
    print("    pip install webamon-cli")
    print("")
    print("Webamon CLI helps you:")
    print("- Search & threat hunt across the web at scale")
    print("- Access millions of scanned domains, IPs, and threat indicators")
    print("- Get unbiased & unfiltered threat intelligence results")
    print("- Search for compromised credentials and infostealers")
    print("")
    print("Quick examples:")
    print("    webamon search example.com")
    print("    webamon scan https://example.com")
    print("    webamon infostealers domain.com")
    print("")
    print("Official resources:")
    print("- PyPI: https://pypi.org/project/webamon-cli/")
    print("- Website: https://webamon.com")
    print("- API Documentation: https://webamon.com/api")
    print("- GitHub: https://github.com/webamon-org/webamon-cli")
    print("- Twitter: https://x.com/webamon_search")
    print("- LinkedIn: https://www.linkedin.com/company/web-a-mon")

# Make the install_cli function available at package level
__all__ = ["install_cli"]