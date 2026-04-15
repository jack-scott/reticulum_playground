# Module 09b — NomadNet TUI

NomadNet is a terminal UI application built on RNS + LXMF. It gives you:
- A live **network map** of heard nodes
- A **conversations** view (LXMF messaging)
- A **node browser** — browse pages served by NomadNet nodes on the mesh
- The ability to **host your own pages** that others can browse

## Install

Already in the pixi environment:
```bash
pixi run nomadnet
```

## Key Bindings

| Key | Action |
|---|---|
| `Ctrl+N` | Network map screen |
| `Ctrl+C` | Conversations screen |
| `Ctrl+P` | Node/page browser |
| `Ctrl+H` | Home page |
| `Ctrl+Q` | Quit |
| `Tab` | Switch focus between panels |
| `Arrow keys` | Navigate lists |
| `Enter` | Select / open |

## Exercise 1 — Watch the Network Map

1. Start NomadNet: `pixi run nomadnet`
2. Press `Ctrl+N` to open the network map
3. Run your announcer from another terminal:
   ```bash
   pixi run python experiments/01_hello_rns/announcer.py
   ```
4. Watch your node appear on the map

## Exercise 2 — Send a Message

1. Run the LXMF receiver to get its address:
   ```bash
   pixi run python experiments/06_lxmf/receive_messages.py
   ```
2. In NomadNet press `Ctrl+C` → New Conversation → paste the address
3. Send a message — the receiver terminal should print it

## Exercise 3 — Host a Page

NomadNet can serve `.mu` pages (Micron markup — a simple markup language) over RNS to anyone who browses to your node address.

1. Find your NomadNet config directory:
   ```bash
   ls ~/.nomadnetwork/
   ```
2. Enable node hosting — edit `~/.nomadnetwork/config`:
   ```
   [node]
   enable_node = yes
   node_name = My Playground Node
   ```
3. Create a page at `~/.nomadnetwork/storage/pages/index.mu`:
   ```
   # Hello from my RNS node

   This page is served over Reticulum.

   >Section Header
   Some content here.
   ```
4. Restart NomadNet — your node address is shown in the top bar
5. In another NomadNet instance (or Sideband), browse to your node address

## Exercise 4 — Browse the Testnet

If you have internet connectivity via a backbone interface, you can browse public NomadNet nodes:

- Solar Express node: `<d16df67bff870a8eaa2af6957c5a2d7d>`
  - Has a live messageboard you can post to

Press `Ctrl+P`, enter the address, press Enter.

## Micron Markup (.mu) Basics

Pages are written in Micron — a simple markup for terminal rendering.

| Syntax | Effect |
|---|---|
| `# Heading` | Large heading |
| `## Subheading` | Smaller heading |
| `>Section` | Collapsible section |
| `` `!text` `` | Bold |
| `` `_text` `` | Underline |
| `` `*text` `` | Italic |
| `` `Fxxx` `` | Foreground colour (hex) |
| `` `Bxxx` `` | Background colour (hex) |
| `[link text](address)` | Link to another node |
| `[lxmf@address]` | Link that opens a conversation |
| `-` | Horizontal rule |

See the messageboard example for a full working page:
`sources/nomadnet/examples/messageboard/messageboard.mu`

## How NomadNet Relates to RNS

- NomadNet uses a **shared RNS instance** — it attaches to whatever is running in `~/.reticulum/` (or the default config). It does not use a local `rns_config` like the experiments do.
- Pages are served via the **Resource** mechanism over Links
- Conversations use **LXMF** directly
- The network map is built from **announces** heard by the local RNS instance
