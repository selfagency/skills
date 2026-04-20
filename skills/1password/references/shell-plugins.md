# Shell Plugins

Use shell plugins when CLI auth should be biometric and centrally managed.

## Setup pattern

1. Initialize plugin:
   - `op plugin init aws`
   - `op plugin init gh`
2. Add generated `eval $(...)` snippet to shell rc (`.zshrc`, `.bashrc`, etc.).
3. Open a new shell.
4. Verify CLI command that requires auth.

## Notes

- Keep plugin init output exactly as generated.
- Use plugin-specific docs for command nuances.
- If plugin auth appears stale, re-run init and restart shell.
