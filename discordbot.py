from discord import Intents
from discord.ext import commands  # Bot Commands Framework
from models.setting import Base, ENGINE
import traceback

from config import config
from utils.log_conf import confLogger

logger = confLogger(__name__)

# cog files
INITIAL_EXTENSIONS = [
    'cogs.maincog'
]


class DiscordBot(commands.Bot):

    def __init__(self, command_prefix, intents):
        super().__init__(command_prefix=command_prefix, intents=intents)

        # load cog files into bot.
        for cog in INITIAL_EXTENSIONS:
            try:
                self.load_extension(cog)
            except Exception:
                logger.error(traceback.format_exc())

    async def on_ready(self):
        logger.info('Bot Online.')


if __name__ == '__main__':
    logger.info('Creating database tables...')
    Base.metadata.create_all(bind=ENGINE)
    logger.info('Done!')

    INTENTS = Intents.all()  # need for monitoring user status
    COMMAND_PREFIX = config['DISCORD']['COMMAND_PREFIX']
    bot = DiscordBot(command_prefix=COMMAND_PREFIX, intents=INTENTS)
    
    import os
    TOKEN = os.environ['BOT_TOKEN']
    bot.run(TOKEN)
