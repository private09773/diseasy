import diseasy


def test_embed_to_dict():
    embed = diseasy.Embed(color=0x00FF00)
    embed.embedtitle("Title").embed_descriptor("Desc").embedinline("Field", "Value")
    data = embed.to_dict()
    assert data["title"] == "Title"
    assert data["description"] == "Desc"
    assert data["color"] == 0x00FF00
    assert data["fields"] == [{"name": "Field", "value": "Value", "inline": True}]


def test_button_to_dict():
    button = diseasy.Button(style="danger").buttonlabel("Delete").buttoncustomid("del_1")
    data = button.to_dict()
    assert data["style"] == "danger"
    assert data["label"] == "Delete"
    assert data["custom_id"] == "del_1"


def test_container_v2():
    container = diseasy.Container()
    container.add(diseasy.ContainerText("Hello world"))
    container.add(diseasy.ContainerSeparator())
    data = container.to_dict()
    assert data["type"] == "container"
    assert data["items"][0] == {"type": "text", "content": "Hello world"}
    assert data["items"][1] == {"type": "separator"}


def test_view_persistent_requires_custom_id():
    view = diseasy.View(timeout=None)
    view.view_persistent(True)
    button = diseasy.Button(style="primary").buttonlabel("No id")
    try:
        view.view_item(button)
        assert False, "expected ValueError for missing custom_id"
    except ValueError:
        pass
