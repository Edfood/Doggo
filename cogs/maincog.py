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

INF = 1000000

class MainCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.monitor.start()

    @staticmethod
    async def reply(ctx, text):
        """Reply to user in discord."""
        message = f'{ctx.author.mention} {text}'
        await ctx.send(message)

    
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


    @commands.command(name='delete_me')
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
    
    @commands.command()
    async def graph(self, ctx):
        """Show a graph of playtime."""
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

    @commands.command(name='set_alert')
    async def set_alert(self, ctx, limit_time: float):
        """ Set a daily playtime limit. """
        id = str(ctx.author.id)
        await self._update_limit_time(ctx, id, limit_time)

    @commands.command(name='show_alert')
    async def show_alert(self, ctx):
        """ Show playtime limit. """
        try:
            id = str(ctx.author.id)
            user = User.get(id)
        except sqlalchemy.orm.exc.UnmappedInstanceError:
            await MainCog.reply(ctx, 'BOW-WOW! You have not registered.')
        except Exception:
            logger.error(traceback.format_exc())
            await MainCog.reply(ctx, 'BOW-WOW! Error occurred.')
        else:
            limit_time = user.limit_time
            text = f'Limit playtime: {limit_time} minutes'
            await MainCog.reply(ctx, text)
    
    
    @commands.command(name='reset_alert')
    async def reset_alert(self, ctx):
        """ Reset playtime limit. """
        id = str(ctx.author.id)
        
        await self._update_limit_time(ctx, id, INF)
    
    async def _update_limit_time(self, ctx, id: str, limit_time: float):
        try:
            user = User.get(id)
            user.limit_time = limit_time
            session.commit()
        except sqlalchemy.orm.exc.UnmappedInstanceError:
            await MainCog.reply(ctx, 'BOW-WOW! You have not registered.')
        except Exception:
            logger.error(traceback.format_exc())
            await MainCog.reply(ctx, 'BOW-WOW! Error occurred.')
        else:
            if limit_time == INF:
                await MainCog.reply(ctx, 'Alert has deleted.')
            else:
                await MainCog.reply(ctx, 'Alert has updated.')
        

    @tasks.loop(minutes=INTERVAL)
    async def monitor(self):
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
            new_today_playtimes = []
            for user in users:
                id = user.id
                playtimes = user.playtimes
                
                is_playing = id in now_playing_user_dict
                time = INTERVAL if is_playing else 0
                print('playtimes dayo: ')
                print(playtimes)
                if not playtimes or playtimes[-1].date != jst_today:
                    new_today_playtimes.append(Playtime(id, jst_today, time))
                else:
                    today_playtime = playtimes[-1]
                    today_playtime.time_cnt += time
                    if today_playtime.time_cnt > user.limit_time and is_playing:
                        user = now_playing_user_dict[id]
                        await user.send('time is up! Stop playing video games.')

            session.add_all(new_today_playtimes)
            session.commit()

        except Exception:
            session.rollback()
            logger.error(traceback.format_exc())
            logger.error('Failed in cralwling.')
        else:
            logger.info('Finish crawling.')

    @monitor.before_loop
    async def before_crawl(self):
        await self.bot.wait_until_ready()

    @commands.command()
    async def test(self, ctx):
        """ test command. """
        print('\ntest restart.')
        self.monitor.restart()


def setup(bot):
    bot.add_cog(MainCog(bot))
