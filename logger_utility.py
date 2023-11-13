import os
import logging.config
import sys
from ruamel.yaml import YAML

def setup_logging(path='./logger.yml', level=logging.INFO):
    """Setup logging configuration
    """
    yaml = YAML(typ='safe')

    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = yaml.load(f.read())
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=level)

    logger = logging.getLogger(__name__)
    logger.debug('Logger has been initialized')
    logger.info("Running: %s" % sys.argv[0])
    logger.info("Python Version: %s" % sys.version.replace('\n', ' '))
