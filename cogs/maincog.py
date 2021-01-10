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

# Monitoring interval
INTERVAL = float(config['TIME']['INTERVAL'])
# default number of days to draw on the graph
DAYS = int(config['TIME']['DAYS'])


class MainCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.crawl.start()

    @staticmethod
    async def reply(ctx, text):
        """Reply to user in discord."""
        message = f'{ctx.author.mention} {text}'
        await ctx.send(message)
    
    @commands.command()
    async def show(self, ctx):
        """Show playtime graph"""
        user_id = str(ctx.author.id)
        ios = self._create_playtime_graph(user_id, DAYS)
        filename = ctx.author.name + '\'s_stats.png'
        file = discord.File(fp=ios, filename=filename)
        await ctx.send(file=file)
    
    @staticmethod
    def _create_playtime_graph(user_id, days):
        """return binary stream for a playtime graph."""

        # Get playtimes to make a graph from DB
        try:
            playtimes = Playtime.get_x_days(user_id, days)
        except Exception:
            logger.error(traceback.format_exc())
        
        jst_today = datetime.now(JST).date()
        print(playtimes)
        # x: date   e.g. x = [11-29, ..., 12-06, 12-07, 12-08]
        x = pd.date_range(end=jst_today, periods=days, freq='d')[::-1]
        # y: playtime
        y = [0] * days

        for i, playtime in enumerate(playtimes):
            date = playtime.date
            time = round(playtime.time_cnt / 60, 1)  # On an hourly basis
            if (jst_today - date).days < days:
                y[i] = time
        average = sum(y) / days


        def create_graph(x, y, average):
            fig = plt.figure()
            ax = fig.add_subplot(111)
            rects = ax.bar(x, y, color='darkturquoise', label='Playtime')
            ax.set_xlabel('date')
            ax.set_ylabel('playtime[hour]')
            ax.set_ylim(bottom=0)
            plt.axhline(y=average, xmin=0, xmax=days, color='orange', label='Average')
            ax.legend()

            # Display a playtime value above bars.
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

        ios = create_graph(x, y, average)
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

    @tasks.loop(minutes=INTERVAL)
    async def crawl(self):
        print('||||||||||||||||||||||||||||||||||||||||')
        logger.info('Start crawling.')
        
        now_playing_user_dict = {}   # key: user ID, value: member(user)

        # Get members info from discord.
        for member in self.bot.get_all_members():
            if (member.activity is not None and
                    member.activity.type == discord.ActivityType.playing):
                id = str(member.id)
                now_playing_user_dict[id] = member

        jst_today = datetime.now(JST).date()

        # Increase time_cnt of playtime in database.
        try:
            users = User.get_all()

            for user in users:
                id = user.id
                playtime = Playtime.get(id, jst_today)
                if playtime is None:
                    playtime = Playtime(id, jst_today)
                is_playing = id in now_playing_user_dict
                if is_playing:
                    playtime.time_cnt += INTERVAL
                    Playtime.merge(playtime)

                # check if time limit exceeded
                if playtime.time_cnt > user.limit_time:
                    user = now_playing_user_dict[id]
                    user.send('time is up! Stop playing video games.')

            session.commit()

        except Exception:
            session.rollback()
            logger.error(traceback.format_exc())
            logger.error('Failed in cralwling.')
        else:
            logger.info('Finish crawling.')


    @commands.command()
    async def test(self, ctx):
        print('||||||||||||||||||||||||||||||||||||||||')
        logger.info('Start crawling.')
        
        now_playing_user_dict = {}   # key: user ID, value: member(user)

        # Get members info from discord.
        for member in self.bot.get_all_members():
            if (member.activity is not None and
                    member.activity.type == discord.ActivityType.playing):
                id = str(member.id)
                now_playing_user_dict[id] = member

        jst_today = datetime.now(JST).date()

        # Increase time_cnt of playtime in database.
        try:
            users = User.get_all()

            for user in users:
                id = user.id
                playtime = Playtime.get(id, jst_today)
                if playtime is None:
                    playtime = Playtime(id, jst_today)
                is_playing = id in now_playing_user_dict
                if is_playing:
                    playtime.time_cnt += INTERVAL
                    Playtime.merge(playtime)

                # check if time limit exceeded
                if playtime.time_cnt > user.limit_time:
                    user = now_playing_user_dict[id]
                    user.send('time is up! Stop playing video games.')

            session.commit()

        except Exception:
            session.rollback()
            logger.error(traceback.format_exc())
            logger.error('Failed in cralwling.')
        else:
            logger.info('Finish crawling.')

    
    # @commands.command(name='set')
    # async def setAlarm(self, ctx):
    
    # @commands.command(name='del')
    # async def deleteAlarm(self, ctx):

    # @commands.command(name='ca')
    # async def showAlarm(self, ctx):

    
    

def setup(bot):
    bot.add_cog(MainCog(bot))
