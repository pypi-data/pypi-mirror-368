import logging

class PipelinesLogger:
    _instance = None
    
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PipelinesLogger, cls).__new__(cls)
            cls._instance.init_logger()
        return cls._instance

    @classmethod
    def get_instance(cls):
        return cls()

    def init_logger(self):
        self.logger = logging.getLogger('pipelines_logger')
        self.logger.setLevel(logging.INFO)


    def info(self, message):
        self.logger.info(f"{self.GREEN}{message}{self.ENDC}")

    def warn(self, message):
        self.logger.warning(f"{self.YELLOW}{message}{self.ENDC}")

    def error(self, message):
        self.logger.error(f"{self.RED}{message}{self.ENDC}")
    