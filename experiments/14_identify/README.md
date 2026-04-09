# Module 14 — Remote Identity Verification

## Goal

Prove who you are to a remote peer over an established link. Understand when RNS gives you
confidentiality vs when it gives you authenticated identity.

## Key concepts

- After link establishment: you have an **encrypted channel** to *someone* — but you don't know who
- After `link.identify()`: the remote side has cryptographically proven their Ed25519 identity
- This is opt-in — many applications don't need it (the channel is still encrypted either way)
- `set_remote_identified_callback` — fires when the remote peer identifies themselves

## Trust model

```
Link established          → encrypted, but anonymous peer
link.identify() called    → peer's identity proven (Ed25519 signature over a link-specific nonce)
server checks recalled identity → can compare against known/trusted hashes
```

## Source to study

`sources/Reticulum/Examples/Identify.py`

## Exercises

1. Run the example — server prints the identity hash of the client after identification
2. Modify the server to maintain a whitelist of trusted hashes — reject unknown identities
3. What happens if you don't call `identify()`? Does the link still work?
4. Save a trusted identity hash to a file and recall it across restarts
