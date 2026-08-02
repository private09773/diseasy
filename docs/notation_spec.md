# Diseasy Notation Spec

| Symbol | Meaning |
|--------|---------|
| `.`    | Functions |
| `[]`   | Container |
| `()`   | Text, embed, and other responses |
| `<>`   | Variables |
| `{}`   | Cogs container |

## Assets
```
.asset-embed[source="example.jpg"]
.asset-noembed[source="example.jpg"]
.asset-getfrom[internet=true/false, source="example.com"]
```

## Embeds v1
```
.embed[]
.embedtitle()
.embed_descriptor()
.embedinline()
.embedasset.from[<.asset-embed>]
```

## Embeds v2 (Components)
```
.container[]
.containertext[]
.containerseperator
.container_src.image[]
.container_src.thumbnail[]
.containersection[]
.containergallery[]
.containerfile[]
.containeractionrow[]
.containerspoiler[]
```

## Buttons / Selects / Modals
```
.button[style=]
.select[type=]
.modal[]
```

## Events / Commands / Cogs
```
.event[name=](<args>):
.command[name=, description=]:
{cog_name}:
```

## Slash Commands
```
.slashcommand[name=, description=]:
.slashoption[name=, type=, required=]
<option.from"name">
```

## Errors / Views / Tasks / Sharding / Config
```
.error[scope=](<ctx>, <error>):
.view[timeout=]:
.task[seconds=/minutes=/hours=]:
.shard[count=]
.config[source=]
```

Voice is explicitly out of scope for Diseasy.
