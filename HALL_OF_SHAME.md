# 🚨 Hall of Shame: Base44's Fake Code

This document lists the funniest fake versions, variables, and snippets
that Base44 tried to pass off as Diseasy code. Spoiler: they don’t exist.

---

## 🧩 Fake Versions
- ❌ `v0.3.0` → Never existed.
- ❌ `v0.4.2` → Pure fantasy.
- ❌ `v1.0.0` → Not even close.
- ✅ Real versions: `v0.1.0` → `v0.2.5`

---

## 🧩 Fake Variables
- ❌ `ctx` in slash commands → Diseasy only uses `ctx` for **prefix commands**.  
- ❌ `interaction.respond()` → Wrong, Diseasy uses `interaction.send()`.  
- ❌ `member.avatar.url` → Diseasy uses `<member.avatar_url>` runtime substitution.  
- ✅ Real variables: `<ctx.author>` (prefix), `<member.name>`, `<member.avatar_url>`

---

## 🧩 Fake Code Snippets
```python
# Fake (ctx in slash)
@bot.slash_command(name="ping")
async def ping(ctx):
    await ctx.respond("Pong!")

# Real Diseasy (slash)
@slash_command(name="ping", description="Ping command.")
async def ping(self, interaction):
    await interaction.send("Pong!")

# Real Diseasy (prefix)
@command(name="ping")
async def ping(ctx):
    await ctx.send("Pong!")
```

## 🧩 Fake Patch Notes
- ❌ “Added dashboard in v0.3.0” → Dashboard integration is ongoing, not in that version.
- ❌ “Removed ctx in v0.4.0” → ctx never existed in slash commands, only prefix.
- ✅ Real notes: Declarative slash commands, angle‑bracket runtime variables, async loop integration.
