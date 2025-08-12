CACHE_WORKDAY_DATA = False

DEFAULT_CHROME_PORT = 9222
DEVELOPER_NAME = "Jeff Goeders"

VERBOSE = False


def set_verbose(verbose: bool):
    """Set the verbosity level for logging."""
    global VERBOSE
    VERBOSE = verbose


def get_verbose():
    """Get the current verbosity level."""
    return VERBOSE


NEW_CHROME_TABS = False


def set_new_chrome_tabs(new_tabs: bool):
    """Set whether to open new Chrome tabs for each operation."""
    global NEW_CHROME_TABS
    NEW_CHROME_TABS = new_tabs


def get_new_chrome_tabs():
    """Get whether to open new Chrome tabs for each operation."""
    return NEW_CHROME_TABS
