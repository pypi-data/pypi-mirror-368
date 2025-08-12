CORE_COMMAND_NAME = "wex"
WORKDIR_SETUP_DIR = f".{CORE_COMMAND_NAME}"

# Command types
COMMAND_TYPE_SERVICE = "service"
COMMAND_TYPE_ADDON = "addon"

# Command patterns
COMMAND_PATTERN_SERVICE = r"^@([\w_-]+)::([\w_-]+)/([\w_-]+)$"
COMMAND_PATTERN_ADDON = r"^(?:([\w_-]+)::)?([\w_-]+)/([\w_-]+)$"

COMMAND_SEPARATOR_FUNCTION_PARTS = "__"
