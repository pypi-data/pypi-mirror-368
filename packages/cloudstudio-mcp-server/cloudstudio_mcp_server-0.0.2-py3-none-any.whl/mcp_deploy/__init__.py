from . import server
from . import mcp_handlers
from . import models

__version__ = "0.1.0"


def main():
    """Main entry point for the package."""
    server.main()


__all__ = ["main", "server", "mcp_handlers", "models", "__version__"]

if __name__ == "__main__":
    main()