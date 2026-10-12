from pyrogram import filters
import config
from database import db

def register_admin_handlers(app):
    
    @app.on_message(filters.command("share") & filters.private)
    async def generate_share_link(client, message):
        if message.from_user.id not in config.ADMIN_IDS:
            await message.reply_text("Access Denied: Unauthorized user.")
            return

        try:
            args = message.text.split()
            if len(args) < 3:
                await message.reply_text(
                    "Invalid Syntax!\n\n"
                    "Usage: /share <Channel_ID> <Message_ID>\n"
                    "Example: /share -1001234567890 145"
                )
                return

            raw_channel_id = int(args[1])
            msg_id = int(args[2])

            clean_channel_id = str(raw_channel_id).replace("-100", "")
            payload_id = f"c{clean_channel_id}_m{msg_id}"

            await db.store_payload(payload_id, raw_channel_id, msg_id)

            bot_info = await client.get_me()
            deep_link = f"https://t.me/{bot_info.username}?start={payload_id}"

            response_text = (
                "Secure Content Link Generated Successfully!\n\n"
                f"Shareable Deep Link:\n{deep_link}\n\n"
                f"Channel ID: {raw_channel_id}\n"
                f"Message ID: {msg_id}"
            )
            await message.reply_text(response_text)

        except ValueError:
            await message.reply_text("Channel ID and Message ID must be valid integers.")
        except Exception as e:
            await message.reply_text(f"Error: {str(e)}")

    @app.on_message(filters.command("addfsub") & filters.private)
    async def add_fsub(client, message):
        if message.from_user.id not in config.ADMIN_IDS:
            await message.reply_text("Unauthorized.")
            return
        try:
            args = message.text.split()
            if len(args) < 2:
                await message.reply_text("Usage: /addfsub <Channel_ID>\nExample: /addfsub -1001234567890")
                return
            c_id = int(args[1])
            await db.add_fsub_channel(c_id)
            await message.reply_text(f"Extra Force-Subscribe channel {c_id} added successfully!")
        except ValueError:
            await message.reply_text("Channel ID must be a valid number.")
        except Exception as e:
            await message.reply_text(f"Error: {e}")

    @app.on_message(filters.command("remfsub") & filters.private)
    async def remove_fsub(client, message):
        if message.from_user.id not in config.ADMIN_IDS:
            await message.reply_text("Unauthorized.")
            return
        try:
            args = message.text.split()
            if len(args) < 2:
                await message.reply_text("Usage: /remfsub <Channel_ID>\nExample: /remfsub -1001234567890")
                return
            c_id = int(args[1])
            await db.remove_fsub_channel(c_id)
            await message.reply_text(f"Force-Subscribe channel {c_id} removed successfully!")
        except ValueError:
            await message.reply_text("Channel ID must be a valid number.")
        except Exception as e:
            await message.reply_text(f"Error: {e}")
