"""A persistent view with a button, matching .view_persistent[true] rules
(timeout must be None, every item needs a custom_id)."""
import diseasy

confirm_button = diseasy.Button(style="success") \
    .buttonlabel("Confirm") \
    .buttoncustomid("confirm_action")


@confirm_button.button_callback
async def on_confirm(interaction):
    await interaction.send("Confirmed!")


view = diseasy.View(timeout=None)
view.view_persistent(True)
view.view_item(confirm_button)
