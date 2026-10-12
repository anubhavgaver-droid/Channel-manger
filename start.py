import re
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import db
from force import check_user_subscriptions

def register_start_handlers(app):
    
    @app.on_message(filters.command("start") & filters.private)
    async def start_handler(client, message):
        user_id = message.from_user.id
        first_name = message.from_user.first_name or "User"
        
        await db.add_user(user_id, first_name)
        text_args = message.text.split()

        if len(text_args) > 1 and text_args[1].startswith("c"):
            payload_id = text_args[1]

            payload_data = await db.get_payload(payload_id)
            if not payload_data:
                pattern = r"c(?P<channel_id>\d+)_m(?P<msg_id>\d+)"
                match = re.match(pattern, payload_id)
                if not match:
                    await message.reply_text("Invalid or Expired Link.")
                    return
                clean_c_id = match.group("channel_id")
                channel_id = int(f"-100{clean_c_id}")
                msg_id = int(match.group("msg_id"))
            else:
                channel_id = payload_data["channel_id"]
                msg_id = payload_data["message_id"]
                clean_c_id = str(channel_id).replace("-100", "")

            # Check Subscriptions across all channels
            is_joined, missing_channels = await check_user_subscriptions(client, user_id, channel_id)

            if is_joined:
                # All channels joined -> Direct Content Link Button
                direct_msg_link = f"https://t.me/c/{clean_c_id}/{msg_id}"
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("👉 Click Here To View Content", url=direct_msg_link)]
                ])
                await message.reply_text(
                    "Verification Successful!\n\n"
                    "You have successfully joined all required channels. Click the button below to view your content directly:",
                    reply_markup=keyboard
                )
            else:
                bot_info = await client.get_me()
                
                # Build dynamic buttons for all missing channels together
                keyboard_buttons = []
                for idx, (ch_id, invite_url) in enumerate(missing_channels, start=1):
                    keyboard_buttons.append([InlineKeyboardButton(f"📢 Join Channel {idx}", url=invite_url)])

                # Add Try Again button at the bottom
                keyboard_buttons.append([InlineKeyboardButton("🔄 Try Again & Access Content", url=f"https://t.me/{bot_info.username}?start={payload_id}")])

                keyboard = InlineKeyboardMarkup(keyboard_buttons)

                await message.reply_text(
                    "Access Restricted!\n\n"
                    "To access this protected content, you must join all our required channels listed below:\n\n"
                    "1. Click the join buttons above.\n"
                    "2. Once joined, tap **'Try Again & Access Content'** to verify.",
                    reply_markup=keyboard
                )
        else:
            await message.reply_text(
                f"Hello {first_name}!\n\n"
                "Welcome to the Content Protection & Access Bot.\n"
                "Please open a designated share link to access target channel content."
            )
