from discord.ui import *
from discord.ext import commands
import discord
import random
class giveaway_view(View):
    def __init__(self, duration_giveaway: int, template_embed: discord.Embed) -> None:
        self.embed = template_embed
        
        super().__init__(timeout=duration_giveaway)
        self.joined = []
        self.duration = duration_giveaway
    async def on_timeout(self) -> None:
        self.stop()
    @discord.ui.button(label="join", disabled=False, custom_id="join", style=discord.ButtonStyle.green)
    async def on_join_callback(self, buton: discord.Button, interaction: discord.Interaction) -> None:
        if interaction.user.id in self.joined:
            await interaction.response.send_message(content="You are in the giveaway!", ephemeral=True)
            
            return
        else:
            self.joined.append(interaction.user.id)
            await interaction.response.send_message("Joined", ephemeral=True)
            to_d = self.embed.to_dict()

            new_embed = discord.Embed(title=self.embed.title, description=self.embed.description, colour=discord.Color.green())
            current_count = int(to_d["fields"][3]["value"])
            current_count += 1
            del to_d["fields"][3]
            for field in to_d["fields"]:
                new_embed.add_field(name=field.get("name"), value=field.get("value"), inline=field.get("inline"))
            new_embed.add_field(name="participants joined", value=f"{current_count}", inline=True)
            self.embed = new_embed
            await interaction.message.edit(embed=self.embed)           
    @discord.ui.button(label="leave", custom_id="leave", style=discord.ButtonStyle.red)
    async def on_leave_callback(self, btn: Button, interaction: discord.Interaction):
        if interaction.user.id in self.joined:
            del self.joined[self.joined.index(interaction.user.id)]
            to_d = self.embed.to_dict()
            to_d["fields"][-1]["value"] = str(int(to_d["fields"][-1]["value"]) - 1)
            self.embed = discord.Embed.from_dict(to_d)
            await interaction.response.send_message("You left the giveaway", ephemeral=True)
            await interaction.message.edit(embed=self.embed)
            
        else:
            await interaction.response.send_message("You are not in the giveaway!", ephemeral=True)
            