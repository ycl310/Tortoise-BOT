from typing import Union
from asyncio import TimeoutError

from discord.ext.commands import Bot
from discord import Embed, Color, Member, User, Status, Message, RawReactionActionEvent, TextChannel, Activity, Game, Spotify

from bot import constants
from bot.cogs.utils.members import get_member_status, get_member_roles_as_mentions, get_member_activity
from bot.cogs.utils.misc import get_badges, get_join_pos, has_verified_role, format_activity, get_device_status, format_date

def simple_embed(message: str, title: str, color: Color) -> Embed:
    embed = Embed(title=title, description=message, color=color)
    return embed


def footer_embed(message: str, title) -> Embed:
    """
    Constructs embed with fixed  green color and fixed footer showing website, privacy url and rules url.
    :param message: embed description
    :param title: title of embed
    :return: Embed object
    """
    content_footer = (
        f"Links: [Website]({constants.website_url}) | "
        f"[Privacy statement]({constants.privacy_url}) | "
        f"[Rules]({constants.rules_url})"
    )
    message = f"{message}\n\n{content_footer}"
    embed = simple_embed(message, title, color=Color.dark_green())
    embed.set_image(url=constants.line_img_url)
    return embed


def welcome(message: str) -> Embed:
    """
    Constructs welcome embed with fixed title 'Welcome' and green color.
    :param message: embed description
    :return: Embed object
    """
    return simple_embed(message, "Welcome!", color=Color.dark_green())


def goodbye(message: str) -> Embed:
    """
    Constructs goodbye embed with fixed title 'Goodbye' and red color.
    :param message: embed description
    :return: Embed object
    """
    return simple_embed(message, "Goodbye", color=Color.dark_red())


def info(message: str, member: Union[Member, User], title: str = "Info") -> Embed:
    """
    Constructs success embed with custom title and description.
    Color depends on passed member top role color.
    :param message: embed description
    :param member: member object to get the color of it's top role from
    :param title: title of embed, defaults to "Info"
    :return: Embed object
    """
    return Embed(title=title, description=message, color=get_top_role_color(member, fallback_color=Color.green()))


def success(message: str, member: Union[Member, User] = None) -> Embed:
    """
    Constructs success embed with fixed title 'Success' and color depending
    on passed member top role color.
    If member is not passed or if it's a User (DMs) green color will be used.
    :param message: embed description
    :param member: member object to get the color of it's top role from,
                   usually our bot member object from the specific guild.
    :return: Embed object
    """
    return simple_embed(message, "Success", get_top_role_color(member, fallback_color=Color.green()))


def warning(message: str) -> Embed:
    """
    Constructs warning embed with fixed title 'Warning' and color gold.
    :param message: embed description
    :return: Embed object
    """
    return simple_embed(message, "Warning", Color.dark_gold())


def failure(message: str) -> Embed:
    """
    Constructs failure embed with fixed title 'Failure' and color red
    :param message: embed description
    :return: Embed object
    """
    return simple_embed(message, "Failure", Color.red())


def authored(message: str, *, author: Union[Member, User]) -> Embed:
    """
    Construct embed and sets its author to passed param author.
    Embed color is based on passed author top role color.
    :param author: to whom the embed will be authored.
    :param message: message to display in embed.
    :return: discord.Embed
    """
    embed = Embed(description=message, color=get_top_role_color(author, fallback_color=Color.green()))
    embed.set_author(name=author.name, icon_url=author.avatar_url)
    return embed


def thumbnail(message: str, member: Union[Member, User], title: str = None) -> Embed:
    """
    Construct embed and sets thumbnail based on passed param member avatar image..
    Embed color is based on passed author top role color.
    :param message: message to display in embed.
    :param member: member from which to get thumbnail from
    :param title: str title of embed
    :return: discord.Embed
    """
    embed = Embed(title=title, description=message, color=get_top_role_color(member, fallback_color=Color.green()))
    embed.set_thumbnail(url=str(member.avatar_url))
    return embed




def status_embed(ctx,member: Member) -> Embed:
    """
    Construct status embed for certain member.
    Status will have info such as member device, online status, activity, roles etc.
    :param member: member to get data from
    :param description: optional, description to use as embed description
    :return: discord.Embed
    """

    color_dict = {
        Status.online: Color.green(),
        Status.offline: 0x000000,
        Status.idle: Color.orange(),
        Status.dnd: Color.red()
    }


    embed = Embed(title=str(member),color= color_dict[member.status])
    embed.description = get_badges(member)
    embed.set_thumbnail(url=member.avatar_url)

    bot = constants.tick_no
    nick = member.nick
    verified = constants.tick_no
    join_pos = get_join_pos(ctx, member)
    activities = ""

    if member.bot:
        bot = constants.tick_yes

    if has_verified_role(ctx, member):
        verified = constants.tick_yes

    if not nick:
        nick = constants.tick_no

    for activity in member.activities:

        clean_activity = format_activity(activity)
        activities += f"{clean_activity}\n"

    embed.add_field(name=f"{constants.pin_emoji} General info",
                    value=f"**Nick** : {nick}\n**Bot** : {bot}\n**Verified** : {verified}\n**Join position** : {join_pos}")
    embed.add_field(name=f"{constants.user_emoji} Status", value=get_device_status(member), inline=False)
    embed.add_field(name="\📆 Dates",
                    value=f"**Join date** : {format_date(member.joined_at)}\n **Creation Date** : {format_date(member.created_at)}",
                    inline=False)

    if not activities == "":
        embed.add_field(name='Activities', value=activities, inline=False)


    return embed


def infraction_embed(
        ctx,
        infracted_member: Union[Member, User],
        infraction_type: constants.Infraction,
        reason: str
) -> Embed:
    """
    :param ctx: context to get mod member from (the one who issued this infraction) and
                bot so we can get it's image.
    :param infracted_member: member who got the infraction
    :param infraction_type: infraction type
    :param reason: str reason for infraction
    :return: discord Embed
    """

    embed = Embed(title="**Infraction information**", color=infraction_type.value)
    embed.set_author(name="Tortoise Community", icon_url=ctx.me.avatar_url)

    embed.add_field(name="**Member**", value=f"{infracted_member}", inline=False)
    embed.add_field(name="**Type**", value=infraction_type.name, inline=False)
    embed.add_field(name="**Reason**", value=reason, inline=False)
    return embed


def get_top_role_color(member: Union[Member, User], *, fallback_color) -> Color:
    """
    Tries to get member top role color and if fails returns fallback_color - This makes it work in DMs.
    Also if the top role has default role color then returns fallback_color.
    :param member: Member to get top role color from. If it's a User then default discord color will be returned.
    :param fallback_color: Color to use if the top role of param member is default color or if param member is
                           discord.User (DMs)
    :return: discord.Color
    """
    try:
        color = member.top_role.color
    except AttributeError:
        # Fix for DMs
        return fallback_color

    if color == Color.default():
        return fallback_color
    else:
        return color


class RemovableMessage:
    emoji_remove = "❌"

    @classmethod
    async def create_instance(cls, bot: Bot,  message: Message, action_member: Member, *, timeout: int = 120):
        self = RemovableMessage()

        self.bot = bot
        self.message = message
        self.action_member = action_member
        self.timeout = timeout

        await self.message.add_reaction(cls.emoji_remove)
        await self._listen()

    def __init__(self):
        self.bot = None
        self.message = None
        self.action_member = None
        self.timeout = None

    def _check(self, payload: RawReactionActionEvent):
        return (
            str(payload.emoji) == self.emoji_remove and
            payload.message_id == self.message.id and
            payload.user_id == self.action_member.id and
            payload.user_id != self.bot.user.id
        )

    async def _listen(self):
        try:
            await self.bot.wait_for("raw_reaction_add", check=self._check, timeout=self.timeout)
            await self.message.delete()
        except TimeoutError:
            await self.message.remove_reaction(self.emoji_remove, self.bot.user)


def suggestion_embed(author: User, suggestion: str, status: constants.SuggestionStatus) -> Embed:
    """
    Creates suggestion embed message with author thumbnail and suggestion status.
    :param author: User discord user from which to get name and avatar
    :param suggestion: str actual suggestion text
    :param status: constants.SuggestionStatus status for suggestion
    :return: discord.Embed
    """
    embed = Embed(
        title=f"{author}'s suggestion",
        description=suggestion,
        color=Color.gold()
    )
    embed.set_thumbnail(url=str(author.avatar_url))
    embed.add_field(name="Status", value=status.value)
    embed.set_footer(text="Powered by Tortoise Community.")
    return embed


async def create_suggestion_msg(channel: TextChannel, author: User, suggestion: str) -> Message:
    """
    Creates suggestion embed with up-vote and down-vote reactions.
    :param channel: TextChannel channel where to sent created suggestion embed
    :param author: User discord user from which to get name and avatar
    :param suggestion: str actual suggestion text
    :return: discord.Message
    """
    thumbs_up_reaction = "\U0001F44D"
    thumbs_down_reaction = "\U0001F44E"

    embed = suggestion_embed(author, suggestion, constants.SuggestionStatus.under_review)

    suggestion_msg = await channel.send(embed=embed)
    await suggestion_msg.add_reaction(thumbs_up_reaction)
    await suggestion_msg.add_reaction(thumbs_down_reaction)

    return suggestion_msg
