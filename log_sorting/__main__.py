

from configs import CONFIG_DIR
from constants import CONFIG_FILES
from config import load_config


def main():
    """Run the main logic of the script."""
    config = load_config(CONFIG_FILES, CONFIG_DIR)
    print(config)


if __name__ == "__main__":
    main()
