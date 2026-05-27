import discord
from discord import app_commands
from discord.ext import commands
import json
import os

GUILD_ID = 1427156527994765324
DB_FILE = "Fracture_scripts.json"

def load_db():
    if not os.path.exists(DB_FILE): return {}
    with open(DB_FILE, "r", encoding="utf-8") as f: return json.load(f)

def save_db(data):
    with open(DB_FILE, "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False, indent=4)

script_db = load_db()

class ScriptView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.refresh_ui()

    def refresh_ui(self):
        self.clear_items()
        db = load_db()
        if db:
            options = [discord.SelectOption(label=name, description=data['desc'], value=name) for name, data in db.items()]
            select = discord.ui.Select(placeholder="🔍 เลือกสคริปต์", options=options, custom_id="script_select")
            select.callback = self.select_callback
            self.add_item(select)
        
        btn = discord.ui.Button(label="🔄 Refresh", style=discord.ButtonStyle.secondary, custom_id="refresh_btn")
        btn.callback = self.refresh_callback
        self.add_item(btn)

    async def select_callback(self, interaction: discord.Interaction):
        db = load_db()
        name = interaction.data['values'][0]
        await interaction.response.send_message(f"""```lua
{name}
```""", ephemeral=True)

    async def refresh_callback(self, interaction: discord.Interaction):
        self.refresh_ui()
        await interaction.response.edit_message(view=self)

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=discord.Intents.default())

    async def setup_hook(self):
        self.add_view(ScriptView())
        await self.tree.sync(guild=discord.Object(id=GUILD_ID))

bot = MyBot()

script_group = app_commands.Group(name="script", description="จัดการระบบสคริปต์ Fracture Hub")

@script_group.command(name="menu", description="ส่ง Embed เมนูหลัก Fracture Hub")
async def menu(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator: return
    
    em = discord.Embed(
        title="💠 Fracture Hub | Script Store",
        description="""**ยินดีต้อนรับสู่สคริปต์ Fracture Hub**
        
📌 **วิธีใช้งาน:** เลือกสคริปต์ที่ต้องการจากรายการด้านล่างเพื่อเริ่มใช้งาน

━━━━━━━━━━━━━━━━━━
🛠️ **แจ้งปัญหา/บัค:** <#1427156529127362729>
💡 **รีเควสฟังชั่นใหม่:** <#1427156529127362730>
━━━━━━━━━━━━━━━━━━

🙏 *ขอบคุณที่สนับสนุนและเลือกใช้สคริปต์ของค่ายเรา* 🥳""",
        color=0x5865F2
    )    
    em.set_image(url="https://cdn.discordapp.com/attachments/1429933985383059546/1509167766228172911/edd012707f89c049384dd3c600501d11.gif?ex=6a183182&is=6a16e002&hm=91d31bfc36324b8a9b8db1e6822d8fa578885a7ebcf88e8b473d9b2ec5fcd108&")
    # em.set_thumbnail(url="")
    em.set_thumbnail(url=interaction.guild.icon.url if interaction.guild.icon else "")
    em.set_footer(text="Fracture Hub System © 2026", icon_url=bot.user.avatar.url)
    
    await interaction.channel.send(embed=em, view=ScriptView())
    await interaction.response.send_message("✅ ส่งเมนูเรียบร้อย", ephemeral=True)

@script_group.command(name="add", description="เพิ่มสคริปต์ใหม่")
async def add(interaction: discord.Interaction, name: str, description: str, message: str):
    db = load_db()
    db[name] = {"desc": description, "msg": message}
    save_db(db)
    await interaction.response.send_message(f"✅ เพิ่ม '{name}' สำเร็จ!", ephemeral=True)

@script_group.command(name="delete", description="ลบสคริปต์")
async def delete(interaction: discord.Interaction):
    db = load_db()
    if not db: return await interaction.response.send_message("❌ ไม่มีสคริปต์ในคลัง", ephemeral=True)
    
    view = discord.ui.View()
    select = discord.ui.Select(placeholder="เลือกชื่อที่จะลบ...", options=[discord.SelectOption(label=n, value=n) for n in db.keys()])
    async def del_call(i: discord.Interaction):
        new_db = load_db()
        del new_db[i.data['values'][0]]
        save_db(new_db)
        await i.response.send_message("✅ ลบสคริปต์สำเร็จ!", ephemeral=True)
    select.callback = del_call
    view.add_item(select)
    await interaction.response.send_message("เลือกสคริปต์ที่ต้องการลบ:", view=view, ephemeral=True)

bot.tree.add_command(script_group, guild=discord.Object(id=GUILD_ID))
bot.run(os.getenv('DISCORD_TOKEN'))
