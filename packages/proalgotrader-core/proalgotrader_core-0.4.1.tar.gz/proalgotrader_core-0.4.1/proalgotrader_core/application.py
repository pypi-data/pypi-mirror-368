from proalgotrader_core.algorithm import Algorithm
from logzero import logger


class Application:
    def __init__(self) -> None:
        self.algorithm = Algorithm()

    async def start(self) -> None:
        logger.debug("booting application")
        await self.algorithm.boot()

        logger.debug("running application")
        await self.algorithm.run()
