import logging 

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        filenam='ml_pipeline.log',
        filemode='a'
    )
    