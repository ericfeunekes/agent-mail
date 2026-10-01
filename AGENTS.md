# Agent Mail

The product contract is [README.md](README.md). Keep implementation within its
accepted scope.

## Development skills

Before planning, implementing, testing, or reviewing development work in a new
or resumed chat, the lead agent runs:

```sh
sh scripts/update-dev-skills.sh
```

This fetches the latest development workflows from Eric's shared GitHub source.
If the refresh fails, resolve the reported access or Git error before using the
development skills. Delegated agents use the refreshed checkout; they do not
run another refresh.

Use the repository's skills under `.agents/skills/development-source/` for this
project, including when a globally installed skill has the same name:

- `plugins/software-development/skills/`: investigation, code review,
  simplification, closeout, GitHub work management, landing, and release.
- `plugins/collaboration/skills/`: grounding, research, discovery, and independent
  review.
- `skills/testing/`: test strategy and proof at realistic boundaries.

After refreshing, read the relevant `SKILL.md` and its referenced files from
this checkout, even if this chat previously loaded an older copy. The
bundle manifests retain the `software-development:` and `collaboration:` skill
namespaces. Keep the generated
checkout out of commits; author skill changes in the shared source repository.
Skills provide instructions, not missing runtime tools. Report a required tool
or agent capability that the current environment cannot provide.

Setup and cloud access are documented in [docs/development-setup.md](docs/development-setup.md).
