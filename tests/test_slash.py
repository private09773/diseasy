from diseasy.ext.slash import slash_command, Interaction


def test_slash_command_to_dict():
    @slash_command(name="greet", description="Greet someone")
    async def greet(interaction):
        return interaction.option_from("name")

    greet.slashoption("name", type="str", required=True, description="Who to greet")
    data = greet.to_dict()
    assert data["name"] == "greet"
    assert data["options"][0]["name"] == "name"


def test_interaction_option_from():
    payload = {"data": {"options": [{"name": "name", "value": "Alex"}]}}
    interaction = Interaction(payload)
    assert interaction.option_from("name") == "Alex"
