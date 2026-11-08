import discord
from discord.ui import Button, View, Select
import os

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

client = discord.Client(intents=intents)

ROLE_ID = 1562309878695985272  # إيدي الرتبة المطلوبة للـ منشن
VOUCHES_CHANNEL_ID = 1555521230419922974  # إيدي روم التقييم

class TicketSelect(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="بيت هالويين ماب النط", description="طلب فك لون للهالويين", emoji="🎃"),
            discord.SelectOption(label="بيت البارتي ماب النط", description="طلب فك لون للبارتي", emoji="🎉")
        ]
        super().__init__(placeholder="Make a selection", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        category = interaction.channel.category
        role = guild.get_role(ROLE_ID)
        
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_messages=True),
            role: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_messages=True) if role else None
        }

        # إنشاء روم التكت
        ticket_channel = await guild.create_text_channel(
            name=f"تكت-{self.values[0]}",
            category=category,
            overwrites=overwrites
        )

        embed = discord.Embed(
            title=f"تفاصيل تذكرة: {self.values[0]}",
            description=f"صاحب الطلب: {interaction.user.mention}\n\nالضمان:\n|\nالمقابل:\n|\nاسم اللاعب:\n|",
            color=discord.Color.orange()
        )

        view = TicketControlView(interaction.user.id)
        await ticket_channel.send(content=f"مرحباً {interaction.user.mention} | {role.mention if role else ''}", embed=embed, view=view)
        await interaction.response.send_message(f"تم فتح تذكرتك: {ticket_channel.mention}", ephemeral=True)

class TicketControlView(View):
    def __init__(self, user_id):
        super().__init__(timeout=None)
        self.user_id = user_id

    @discord.ui.button(label="استلام التكت", style=discord.ButtonStyle.green, emoji="🙋‍♂️")
    async def claim_ticket(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message(f"تم استلام التذكره بواسطة {interaction.user.mention}")

    @discord.ui.button(label="قفل التكت", style=discord.ButtonStyle.red, emoji="🔒")
    async def close_ticket(self, interaction: discord.Interaction, button: Button):
        await interaction.channel.delete()

class TicketSetupView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author.bot:
        return

    # أمر فتح رسالة التيشيت (مثلاً تكتب !ticket لإرسال القائمة)
    if message.content == "!ticket":
        embed = discord.Embed(
            title="🎨 | طلب فك لون",
            description="طلب فك لون بيت\n\nاختر لون و افتح على لون الي تبي\nالرجاء قراءة القوانين قبل فتح التذكره",
            color=discord.Color.green()
        )
        await message.channel.send(embed=embed, view=TicketSetupView())

    # أمر الحذف (+) داخل التكت
    if message.content.startswith("+"):
        try:
            await message.delete()
        except:
            pass
        
        vouche_channel = message.guild.get_channel(VOUCHES_CHANNEL_ID)
        vouche_mention = vouche_channel.mention if vouche_channel else "#VOUCHES"
        
        response_text = f"🎨 كان معك من فريق الرسامين: {message.author.mention}\n\nشكراً لتعاملكم معنا! نرجو منكم كتابة تقييمكم للخدمة في روم التقييمات: {vouche_mention}\n\nنتمنى لكم يوماً سعيداً! ❤️"
        await message.channel.send(response_text)

# ضع توكن بوتك هنا
client.run(os.environ.get("TOKEN") or "YOUR_BOT_TOKEN")
