import os
import pymysql
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# ==== CONFIG FROM ENVIRONMENT VARIABLES ====
DB_HOST = os.environ.get('DB_HOST', "auth-db759.hstgr.io")
DB_USER = os.environ.get('DB_USER', "u637884065_Gsm")
DB_PASSWORD = os.environ.get('DB_PASSWORD', "Continental12345*")
DB_NAME = os.environ.get('DB_NAME', "u637884065_Gsm")
DEVICES_TABLE = os.environ.get('DEVICES_TABLE', 'devices')
BOT_TOKEN = os.environ.get('BOT_TOKEN')

def get_db_connection():
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Bienvenido al bot *Continental GSM*.\n\n"
        "Comandos disponibles:\n"
        "`/rsn <serial_number>` – Registrar un nuevo número de serie.\n"
        "`/list` – Ver los últimos 10 registros.\n",
        parse_mode="Markdown"
    )

async def register_serial(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        await update.message.reply_text("❌ Uso correcto: `/rsn <serial>`", parse_mode="Markdown")
        return

    serial_number = context.args[0].strip()
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            sql = f"INSERT INTO {DEVICES_TABLE} (serial_number) VALUES (%s)"
            cursor.execute(sql, (serial_number,))
            conn.commit()
            await update.message.reply_text(f"✅ Serial `{serial_number}` registrado con éxito.", parse_mode="Markdown")
    except pymysql.err.IntegrityError:
        await update.message.reply_text(f"⚠️ El serial `{serial_number}` ya existe.", parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Error al registrar: `{e}`", parse_mode="Markdown")
    finally:
        conn.close()

async def list_serials(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute(f"SELECT serial_number, created_at FROM {DEVICES_TABLE} ORDER BY id DESC LIMIT 10")
            rows = cursor.fetchall()
            if not rows:
                await update.message.reply_text("📭 No hay seriales registrados.")
                return
            msg = "📋 *Últimos 10 seriales registrados:*\n\n"
            for row in rows:
                msg += f"• `{row['serial_number']}` — {row['created_at']}\n"
            await update.message.reply_text(msg, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Error al consultar: `{e}`", parse_mode="Markdown")
    finally:
        conn.close()

def main():
    if not BOT_TOKEN:
        print("❌ ERROR: BOT_TOKEN no configurado")
        return
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("rsn", register_serial))
    application.add_handler(CommandHandler("list", list_serials))
    
    print("🤖 Bot iniciado en Render.com - 24/7 activo!")
    application.run_polling()

if __name__ == "__main__":
    main()