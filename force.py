from pyrogram.errors import UserNotParticipant
from database import db
import logging

logger = logging.getLogger(__name__)

async def check_user_subscriptions(client, user_id: int, target_channel_id: int):
    """
    Checks membership for the target channel AND all extra fsub channels securely.
    Returns: (is_joined: bool, missing_channels: list of tuples (channel_id, invite_link))
    """
    missing_channels = []

    # Collect all channels to check (Target Channel + Extra FSub Channels)
    channels_to_check = [target_channel_id]
    
    extra_channels = await db.get_fsub_channels()
    for fsub in extra_channels:
        fsub_id = fsub["channel_id"]
        if fsub_id not in channels_to_check:
            channels_to_check.append(fsub_id)

    # Check each channel strictly
    for ch_id in channels_to_check:
        is_member = False
        try:
            member = await client.get_chat_member(ch_id, user_id)
            
            # Safely convert status to lowercase string to handle Pyrogram Enums correctly
            status = str(member.status).lower()
            
            # If status is NOT left, banned, or kicked, it means the user is a valid member
            if any(s in status for s in ["member", "administrator", "creator", "owner"]):
                is_member = True
            elif status not in ["left", "banned", "kicked"]:
                is_member = True
                
        except UserNotParticipant:
            is_member = False
        except Exception as e:
            logger.error(f"Error checking membership for channel {ch_id}: {e}")
            is_member = False

        # If user is truly not a member, generate invite link and add to missing list
        if not is_member:
            try:
                invite = await client.create_chat_invite_link(chat_id=ch_id)
                missing_channels.append((ch_id, invite.invite_link))
            except Exception as e:
                logger.error(f"Failed to create invite link for channel {ch_id}: {e}")

    if missing_channels:
        return False, missing_channels
    return True, []
