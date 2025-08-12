from asyncio import sleep
from re import search
from typing import Union

from discord import MISSING, PermissionOverwrite, Member, Role, Message
from discord.utils import _MissingSentinel

__all__ = [
    'dshell_create_text_channel',
    'dshell_delete_channel',
    'dshell_delete_channels',
    'dshell_create_voice_channel',
    'dshell_edit_text_channel',
    'dshell_edit_voice_channel'
]


async def dshell_create_text_channel(ctx: Message,
                                     name,
                                     category=None,
                                     position=MISSING,
                                     slowmode=MISSING,
                                     topic=MISSING,
                                     nsfw=MISSING,
                                     permission: dict[Union[Member, Role], PermissionOverwrite] = MISSING,
                                     reason=None):
    """
    Creates a text channel on the server
    """

    if not isinstance(position, _MissingSentinel) and not isinstance(position, int):
        raise Exception(f"Position must be an integer, not {type(position)} !")

    if not isinstance(slowmode, _MissingSentinel) and not isinstance(slowmode, int):
        raise Exception(f"Slowmode must be an integer, not {type(slowmode)} !")

    if not isinstance(topic, _MissingSentinel) and not isinstance(topic, str):
        raise Exception(f"Topic must be a string, not {type(topic)} !")

    if not isinstance(nsfw, _MissingSentinel) and not isinstance(nsfw, bool):
        raise Exception(f"NSFW must be a boolean, not {type(nsfw)} !")

    channel_category = ctx.channel.category if category is None else ctx.channel.guild.get_channel(category)

    created_channel = await ctx.guild.create_text_channel(str(name),
                                                          category=channel_category,
                                                          position=position,
                                                          slowmode_delay=slowmode,
                                                          topic=topic,
                                                          nsfw=nsfw,
                                                          overwrites=permission,
                                                          reason=reason)

    return created_channel.id


async def dshell_create_voice_channel(ctx: Message,
                                      name,
                                      category=None,
                                      position=MISSING,
                                      bitrate=MISSING,
                                      permission: dict[Union[Member, Role], PermissionOverwrite] = MISSING,
                                      reason=None):
    """
    Creates a voice channel on the server
    """
    if not isinstance(position, _MissingSentinel) and not isinstance(position, int):
        raise Exception(f"Position must be an integer, not {type(position)} !")

    if not isinstance(bitrate, _MissingSentinel) and not isinstance(bitrate, int):
        raise Exception(f"Bitrate must be an integer, not {type(bitrate)} !")

    channel_category = ctx.channel.category if category is None else ctx.channel.guild.get_channel(category)

    created_channel = await ctx.guild.create_voice_channel(str(name),
                                                           category=channel_category,
                                                           position=position,
                                                           bitrate=bitrate,
                                                           overwrites=permission,
                                                           reason=reason)

    return created_channel.id


async def dshell_delete_channel(ctx: Message, channel=None, reason=None, timeout=0):
    """
    Deletes a channel.
    You can add a waiting time before it is deleted (in seconds)
    """
    if not isinstance(timeout, int):
        raise Exception(f'Timeout must be an integer, not {type(timeout)} !')

    channel_to_delete = ctx.channel if channel is None else ctx.channel.guild.get_channel(channel)

    if channel_to_delete is None:
        raise Exception(f"Channel {channel} not found !")

    await sleep(timeout)

    await channel_to_delete.delete(reason=reason)

    return channel_to_delete.id


async def dshell_delete_channels(ctx: Message, name=None, regex=None, reason=None):
    """
    Deletes all channels with the same name and/or matching the same regex.
    If neither is set, it will delete all channels with the same name as the one where the command was executed.
    """
    if name is not None and not isinstance(name, str):
        raise Exception(f"Name must be a string, not {type(name)} !")

    if regex is not None and not isinstance(regex, str):
        raise Exception(f"Regex must be a string, not {type(regex)} !")

    for channel in ctx.channel.guild.channels:

        if name is not None and channel.name == str(name):
            await channel.delete(reason=reason)

        elif regex is not None and search(regex, channel.name):
            await channel.delete(reason=reason)


async def dshell_edit_text_channel(ctx: Message,
                                   channel=None,
                                   name=None,
                                   position=MISSING,
                                   slowmode=MISSING,
                                   topic=MISSING,
                                   nsfw=MISSING,
                                   permission: dict[Union[Member, Role], PermissionOverwrite] = MISSING,
                                   reason=None):
    """
    Edits a text channel on the server
    """

    if not isinstance(position, _MissingSentinel) and not isinstance(position, int):
        raise Exception(f"Position must be an integer, not {type(position)} !")

    if not isinstance(slowmode, _MissingSentinel) and not isinstance(slowmode, int):
        raise Exception(f"Slowmode must be an integer, not {type(slowmode)} !")

    if not isinstance(topic, _MissingSentinel) and not isinstance(topic, str):
        raise Exception(f"Topic must be a string, not {type(topic)} !")

    if not isinstance(nsfw, _MissingSentinel) and not isinstance(nsfw, bool):
        raise Exception(f"NSFW must be a boolean, not {type(nsfw)} !")

    channel_to_edit = ctx.channel if channel is None else ctx.channel.guild.get_channel(channel)

    if channel_to_edit is None:
        raise Exception(f"Channel {channel} not found !")

    await channel_to_edit.edit(name=name if name is not None else channel_to_edit.name,
                               position=position if position is not MISSING else channel_to_edit.position,
                               slowmode_delay=slowmode if slowmode is not MISSING else channel_to_edit.slowmode_delay,
                               topic=topic if topic is not MISSING else channel_to_edit.topic,
                               nsfw=nsfw if nsfw is not MISSING else channel_to_edit.nsfw,
                               overwrites=permission if permission is not MISSING else channel_to_edit.overwrites,
                               reason=reason)

    return channel_to_edit.id


async def dshell_edit_voice_channel(ctx: Message,
                                    channel=None,
                                    name=None,
                                    position=MISSING,
                                    bitrate=MISSING,
                                    permission: dict[Union[Member, Role], PermissionOverwrite] = MISSING,
                                    reason=None):
    """
    Edits a voice channel on the server
    """
    if not isinstance(position, _MissingSentinel) and not isinstance(position, int):
        raise Exception(f"Position must be an integer, not {type(position)} !")

    if not isinstance(bitrate, _MissingSentinel) and not isinstance(bitrate, int):
        raise Exception(f"Bitrate must be an integer, not {type(bitrate)} !")

    channel_to_edit = ctx.channel if channel is None else ctx.channel.guild.get_channel(channel)

    if channel_to_edit is None:
        raise Exception(f"Channel {channel} not found !")

    await channel_to_edit.edit(name=name if name is not None else channel_to_edit.name,
                               position=position if position is not MISSING else channel_to_edit.position,
                               bitrate=bitrate if bitrate is not MISSING else channel_to_edit.bitrate,
                               overwrites=permission if permission is not MISSING else channel_to_edit.overwrites,
                               reason=reason)

    return channel_to_edit.id
