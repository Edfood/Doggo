import discord
import io
from discord.ext import commands, tasks
from models.setting import session
from models.user import User
from models.playtime import Playtime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import sqlalchemy
from datetime import datetime, timedelta, timezone
import traceback

from config import config
from utils.log_conf import confLogger

logger = confLogger(__name__)

# generate timezone
JST = timezone(timedelta(hours=+9), 'JST')


class MainCog(commands.Cog):
    # Monitoring interval
    INTERVAL = float(config['TIME']['INTERVAL'])
    # default number of days to draw on the graph
    DAYS = int(config['TIME']['DAYS'])

    def __init__(self, bot):
        self.bot = bot
        # self.crawl.start()

    @staticmethod
    async def reply(ctx, text):
        """Reply to user in discord."""
        message = f'{ctx.author.mention} {text}'
        await ctx.send(message)
    

    @commands.command()
    async def show(self, ctx):
        """Show playtime graph"""
        user_id = str(ctx.author.id)
        ios = self._create_playtime_graph(user_id, MainCog.DAYS)
        filename = ctx.author.name + '\'s stats.png'
        file = discord.File(fp=ios, filename=filename)
        await ctx.send(file=file)
    

    @staticmethod
    def _create_playtime_graph(user_id, days):
        """return binary stream for a playtime graph."""

        # Get a data to make a graph from DB
        try:
            playtimes = Playtime.get_x_days(user_id, days)
        except Exception:
            logger.error(traceback.format_exc())
        
        # today = datetime.date.today()

        jst_today = datetime.now(JST).date()

        x = pd.date_range(end=jst_today, periods=days, freq='d')[::-1]
        y = [0] * days
        for i, playtime in enumerate(playtimes):
            date = playtime.date
            time = playtime.time_cnt * MainCog.INTERVAL / 60  # On an hourly basis
            if (jst_today - date).days < days:
                y[i] = time
        ave = sum(y) / days


        def create_graph(x, y, ave):
            fig = plt.figure()
            ax = fig.add_subplot(111)
            rects = ax.bar(x, y, color='darkturquoise', label='playtime')
            ax.set_xlabel('date')
            ax.set_ylabel('playtime[hour]')
            ax.set_ylim(bottom=0)
            plt.axhline(y=ave, xmin=0, xmax=days, color='orange', label='average')
            ax.legend()

            # Display the value above bars.
            for rect in rects:
                height = rect.get_height()
                ax.annotate(f'{height}', 
                            xy=(rect.get_x() + rect.get_width() / 2, height),
                            xytext=(0, 1),
                            textcoords="offset points",
                            ha='center', va='bottom')

            # Setting the x-axis scale
            dayLoc = mdates.DayLocator()
            dayFmt = mdates.DateFormatter('%m-%d')
            ax.xaxis.set_major_locator(dayLoc)
            ax.xaxis.set_major_formatter(dayFmt)

            # image to binary stream of data
            format = "png"
            ios = io.BytesIO()
            plt.savefig(ios, format=format)
            ios.seek(0)
            return ios

        ios = create_graph(x, y, ave)
        return ios


    @commands.command()
    async def register(self, ctx):
        """Register a user in database."""
        user_id = str(ctx.author.id)
        print('registered id: ' + str(user_id))
        user = User(user_id)

        try:
            User.save(user)
            session.commit()
        except sqlalchemy.exc.IntegrityError:
            session.rollback()
            await MainCog.reply(ctx, 'BOW-WOW! You are already registered.')
        except Exception:
            logger.error(traceback.format_exc())
            await MainCog.reply(ctx, 'BOW-WOW! Error occurred.')
        else:
            await MainCog.reply(ctx, 'You has been registered. :guide_dog:')


    @commands.command()
    async def delete(self, ctx):
        """Delete a registered user from DB."""
        user_id = str(ctx.author.id)
        try:
            User.delete(user_id)
            session.commit()
        except sqlalchemy.orm.exc.UnmappedInstanceError:
            await MainCog.reply(ctx, 'BOW-WOW! You have not registered.')
        except Exception:
            logger.error(traceback.format_exc())
            await MainCog.reply(ctx, 'BOW-WOW! Error occurred.')
        else:
            text = 'You\'ve deleted from database.\n'\
                   'You\'ll not be tracked from now on. :service_dog:'
            await MainCog.reply(ctx, text)

    # @tasks.loop(seconds=30)
    # async def crawl(self):
    #     print('||||||||||||||||||||||||||||||||||||||||')
    #     logger.info('Start crawling.')
        
    #     # Get members info from discord.
    #     now_playing_user_ids = set()   # IDs of users who are playing game.
    #     for member in self.bot.get_all_members():
    #         print('yap: ' + str(member.id) + ' : ' + str(member.name))
    #         if (member.activity is not None and
    #                 member.activity.type == discord.ActivityType.playing):
    #             print('koko: ' + str(member.id))
    #             now_playing_user_ids.add(str(member.id))

    #     # Increase time_cnt of playtime in database.
    #     try:
    #         users = User.get_all()

    #         for user in users:
    #             id = user.id
    #             playtime = Playtime.get(id, datetime.date.today())
    #             print('this is the playtime !!!: ' + str(playtime))

    #             if playtime is None and id in now_playing_user_ids:
    #                 continue    # This is for reduce queries.
    #             if playtime is None:
    #                 playtime = Playtime(id, datetime.date.today())
    #             if id in now_playing_user_ids:
    #                 playtime.time_cnt += MainCog.INTERVAL

                
    #             Playtime.merge(playtime)

    #         session.commit()

    #     except Exception:
    #         session.rollback()
    #         logger.error(traceback.format_exc())
    #         logger.error('Failed in cralwling.')
    #     else:
    #         logger.info('Finish crawling.')
    
    @commands.command()
    async def test(self, ctx):
        
        print('||||||||||||||||||||||||||||||||||||||||')
        logger.info('Start crawling.')
        
        # Get members info from discord.
        now_playing_user_ids = set()   # IDs of users who are playing game.
        for member in self.bot.get_all_members():
            if (member.activity is not None and
                    member.activity.type == discord.ActivityType.playing):
                print('hakken: ' + str(member.id))
                now_playing_user_ids.add(str(member.id))

        jst_today = datetime.now(JST).date()

        # Increase time_cnt of playtime in database.
        try:
            users = User.get_all()

            for user in users:
                id = user.id
                playtime = Playtime.get(id, jst_today)
                print('id dayo : ' + str(id))
                print(playtime)
                if playtime is None and id in now_playing_user_ids:
                    continue    # This is for reduce queries.
                if playtime is None:
                    playtime = Playtime(id, jst_today)
                if id in now_playing_user_ids:
                    playtime.time_cnt += MainCog.INTERVAL

                print('this is the playtime !!!: ' + str(playtime))
                
                Playtime.merge(playtime)

            session.commit()

        except Exception:
            session.rollback()
            logger.error(traceback.format_exc())
            logger.error('Failed in cralwling.')
        else:
            logger.info('Finish crawling.')


def setup(bot):
    bot.add_cog(MainCog(bot))
