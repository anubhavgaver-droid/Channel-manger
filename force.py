from pyrogram.errors import UserNotParticipant
from database import db
import logging

logger = logging.getLogger(__name__)

async def check_user_subscriptions(client, user_id: int, target_channel_id: int):
    """
    Checks if user has joined the target channel 
    AND any extra force-subscribe channels added via admin.
    """
    # 1. Check Target Channel First
    try:
        await client.get_chat_member(target_channel_id, user_id)
    except UserNotParticipant:
        try:
            invite = await client.create_chat_invite_link(chat_id=target_channel_id)
            return False, invite.invite_link
        except Exception as e:
            logger.error(f"Failed to create invite for target {target_channel_id}: {e}")
            return False, None
    except Exception:
        return False, None

    # 2. Check Extra Force-Subscribe Channels from Database
    extra_channels = await db.get_fsub_channels()
    for fsub in extra_channels:
        fsub_id = fsub["channel_id"]
        if fsub_id == target_channel_id:
            continue
        try:
            await client.get_chat_member(fsub_id, user_id)
        except UserNotParticipant:
            try:
                invite = await client.create_chat_invite_link(chat_id=fsub_id)
                return False, invite.invite_link
            except Exception:
                return False, None
        except Exception:
            pass

    return True, None
