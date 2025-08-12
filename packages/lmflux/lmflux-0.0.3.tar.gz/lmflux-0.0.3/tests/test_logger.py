import unittest
from lmflux.logger import PipelinesLogger

class TestPipelinesLogger(unittest.TestCase):
    def test_singleton_instance(self):
        logger1 = PipelinesLogger.get_instance()
        logger2 = PipelinesLogger.get_instance()
        self.assertEqual(logger1, logger2)

    def test_logger_init(self):
        logger = PipelinesLogger.get_instance()
        self.assertIsNotNone(logger.logger)

    def test_info(self):
        logger = PipelinesLogger.get_instance()
        logger.info("Test info message")

    def test_warn(self):
        logger = PipelinesLogger.get_instance()
        logger.warn("Test warning message")

    def test_error(self):
        logger = PipelinesLogger.get_instance()
        logger.error("Test error message")

if __name__ == '__main__':
    unittest.main()