import logging

def setup_logger(verbose: bool = False) -> logging.Logger:
    logger = logging.getLogger('common_ai_core')
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)
    
    formatter = logging.Formatter('%(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s - %(message)s')
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    
    return logger 