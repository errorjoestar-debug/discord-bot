import discord
from discord import ui
from discord.ext import commands
from utils.favorites import add_favorite, remove_favorite


class PaginationView(ui.View):
    """Pagination view for navigating through multiple pages."""
    
    def __init__(self, pages: list[str], title: str, color: int, timeout: float = 180, retry_callback=None):
        super().__init__(timeout=timeout)
        self.pages = pages
        self.current_page = 0
        self.title = title
        self.color = color
        self.message = None
        self.retry_callback = retry_callback

    async def send(self, interaction: discord.Interaction):
        """Send the first page with pagination buttons."""
        embed = self._get_embed()
        self.message = await interaction.followup.send(embed=embed, view=self)
        return self.message

    def _get_embed(self) -> discord.Embed:
        """Get the embed for the current page."""
        embed = discord.Embed(
            title=self.title,
            description=self.pages[self.current_page],
            color=self.color,
        )
        embed.set_footer(text=f"الصفحة {self.current_page + 1}/{len(self.pages)}")
        return embed

    @ui.button(label="◀️ السابق", style=discord.ButtonStyle.secondary, emoji="◀️")
    async def previous_page(self, interaction: discord.Interaction, button: ui.Button):
        """Go to previous page."""
        if self.current_page > 0:
            self.current_page -= 1
            await interaction.response.edit_message(embed=self._get_embed(), view=self)
        else:
            await interaction.response.defer()

    @ui.button(label="التالي ▶️", style=discord.ButtonStyle.secondary, emoji="▶️")
    async def next_page(self, interaction: discord.Interaction, button: ui.Button):
        """Go to next page."""
        if self.current_page < len(self.pages) - 1:
            self.current_page += 1
            await interaction.response.edit_message(embed=self._get_embed(), view=self)
        else:
            await interaction.response.defer()

    @ui.button(label="🗑️ حذف", style=discord.ButtonStyle.danger, emoji="🗑️")
    async def delete_message(self, interaction: discord.Interaction, button: ui.Button):
        """Delete the message."""
        await interaction.response.edit_message(view=None)
        await self.message.delete()

    @ui.button(label="🔄 إعادة المحاولة", style=discord.ButtonStyle.secondary, emoji="🔄", row=1)
    async def retry_action(self, interaction: discord.Interaction, button: ui.Button):
        """Retry the action."""
        if self.retry_callback:
            await interaction.response.defer()
            await self.retry_callback(interaction)
        else:
            await interaction.response.defer()


class AzkarCounterView(ui.View):
    """Quick counter view for azkar."""
    
    def __init__(self, user_id: int, initial_count: int = 0, timeout: float = 600):
        super().__init__(timeout=timeout)
        self.user_id = user_id
        self.count = initial_count
        self.message = None

    async def send(self, interaction: discord.Interaction):
        """Send the counter view."""
        embed = self._get_embed()
        self.message = await interaction.followup.send(embed=embed, view=self)
        return self.message

    def _get_embed(self) -> discord.Embed:
        """Get the embed for the counter."""
        embed = discord.Embed(
            title="🔢 عداد الذكر",
            description=f"عدد ذكرك الحالي: **{self.count}**",
            color=0x3498DB,
        )
        embed.set_footer(text="اضغط على الأزرار لزيادة أو تصفير العداد")
        return embed

    @ui.button(label="+1", style=discord.ButtonStyle.primary, emoji="➕")
    async def increment_one(self, interaction: discord.Interaction, button: ui.Button):
        """Increment counter by 1."""
        from utils.azkar_counter import increment_counter
        self.count = increment_counter(self.user_id)
        await interaction.response.edit_message(embed=self._get_embed(), view=self)

    @ui.button(label="+10", style=discord.ButtonStyle.primary, emoji="🔟")
    async def increment_ten(self, interaction: discord.Interaction, button: ui.Button):
        """Increment counter by 10."""
        from utils.azkar_counter import increment_counter
        for _ in range(10):
            self.count = increment_counter(self.user_id)
        await interaction.response.edit_message(embed=self._get_embed(), view=self)

    @ui.button(label="+33", style=discord.ButtonStyle.primary, emoji="📿")
    async def increment_33(self, interaction: discord.Interaction, button: ui.Button):
        """Increment counter by 33 (for subhanAllah, etc)."""
        from utils.azkar_counter import increment_counter
        for _ in range(33):
            self.count = increment_counter(self.user_id)
        await interaction.response.edit_message(embed=self._get_embed(), view=self)

    @ui.button(label="🔄 تصفير", style=discord.ButtonStyle.danger, emoji="🔄")
    async def reset_counter(self, interaction: discord.Interaction, button: ui.Button):
        """Reset counter."""
        from utils.azkar_counter import reset_counter
        self.count = reset_counter(self.user_id)
        await interaction.response.edit_message(embed=self._get_embed(), view=self)


class SurahSelectView(ui.View):
    """Select menu for choosing a surah."""
    
    def __init__(self, callback, timeout: float = 180):
        super().__init__(timeout=timeout)
        self.callback = callback

    @ui.select(
        placeholder="اختر سورة...",
        min_values=1,
        max_values=1,
        custom_id="surah_select"
    )
    async def select_surah(self, interaction: discord.Interaction, select: ui.Select):
        """Handle surah selection."""
        await self.callback(interaction, int(select.values[0]))


class AyahHadithView(ui.View):
    """View for ayah/hadith with save button."""
    
    def __init__(self, user_id: int, item_type: str, item_id: str, content: str, metadata: dict = None, timeout: float = 600, refresh_callback=None):
        super().__init__(timeout=timeout)
        self.user_id = user_id
        self.item_type = item_type
        self.item_id = item_id
        self.content = content
        self.metadata = metadata or {}
        self.is_saved = False
        self.refresh_callback = refresh_callback

    @ui.button(label="⭐ حفظ", style=discord.ButtonStyle.primary, emoji="⭐")
    async def save_item(self, interaction: discord.Interaction, button: ui.Button):
        """Save item to favorites."""
        if self.is_saved:
            # Remove from favorites
            success = remove_favorite(self.user_id, self.item_type, self.item_id)
            if success:
                self.is_saved = False
                button.label = "⭐ حفظ"
                button.style = discord.ButtonStyle.primary
                await interaction.response.edit_message(view=self)
            else:
                await interaction.response.defer()
        else:
            # Add to favorites
            success = add_favorite(self.user_id, self.item_type, self.item_id, self.content, self.metadata)
            if success:
                self.is_saved = True
                button.label = "✅ محفوظ"
                button.style = discord.ButtonStyle.success
                await interaction.response.edit_message(view=self)
            else:
                await interaction.response.defer()

    @ui.button(label="📋 نسخ", style=discord.ButtonStyle.secondary, emoji="📋")
    async def copy_text(self, interaction: discord.Interaction, button: ui.Button):
        """Copy text to clipboard (send as ephemeral)."""
        await interaction.response.send_message(
            f"```\n{self.content}\n```",
            ephemeral=True
        )

    @ui.button(label="🔄 تحديث", style=discord.ButtonStyle.secondary, emoji="🔄")
    async def refresh_item(self, interaction: discord.Interaction, button: ui.Button):
        """Refresh the item content."""
        if self.refresh_callback:
            await interaction.response.defer()
            await self.refresh_callback(interaction)
        else:
            await interaction.response.defer()
