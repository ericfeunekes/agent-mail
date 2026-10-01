# Development setup

Agent Mail uses the current development skills from the private
[`ericfeunekes/ai-marketplace`](https://github.com/ericfeunekes/ai-marketplace)
repository. The shared repository is the authoring source; Agent Mail does not
pin or commit imported skill versions.

## Local setup

Git and HTTPS read access to the shared repository are required. Run:

```sh
sh scripts/update-dev-skills.sh
```

The command creates or updates a shallow sparse checkout on `main` under
`.agents/skills/development-source/`. It includes the software-development and
collaboration bundles plus the testing skill. Keeping the bundle directories
intact preserves shared references and scripts that individual skill copies
would omit. Codex discovers the nested `SKILL.md` files and uses the retained
bundle manifests for the `software-development:` and `collaboration:` namespaces.

The lead agent refreshes before development work in each new or resumed chat.
Each refresh uses the source's latest published `main`; already-running agents
may have previously loaded instructions and should finish their current work
before loading a changed workflow. Update skills in the shared source, then
commit and push there. Never edit the generated checkout in Agent Mail.

## Codex Cloud setup

In Settings > Codex Cloud > Environments, create an environment for
`ericfeunekes/agent-mail`. Enable **Allow Codex to access internet**, choose
**Custom domains only**, and allow `github.com`. Git must be able to read the private
`ericfeunekes/ai-marketplace` repository. Selecting the public Agent Mail
repository alone does not establish access to that second repository.

Use the environment's supported GitHub access configuration. If Git needs a
separate credential, use a read-only credential scoped to the shared repository.
The current cloud environment supports **Network secrets**: programs receive a
placeholder and the HTTPS proxy substitutes the credential for allowed hosts
during setup and tasks. Configure Git's authorization to use that supported
mechanism and test it in the environment before publishing.
Keep credentials out of scripts, Git URLs, logs, and this public repository.

Run `sh scripts/update-dev-skills.sh` while preparing the environment, then publish.
The same command in `AGENTS.md` refreshes the source at the start of task work;
the published filesystem snapshot alone would become stale.

In a fresh cloud task, run the refresh and use the repository's code-review
skill for a small review. Confirm its shared references are readable and the
required agent tools are available before relying on the full workflow. Local
proof does not establish cloud authentication or native subagent availability.
Workflows requiring Claude Code and Codex CLI participants also need those
CLIs and their authorized model access; skill discovery does not supply them.

These instructions target the current cloud environment, not Codex Cloud
(Legacy), whose secrets are available only during setup. See the
[official cloud environment guide](https://learn.chatgpt.com/docs/environments/cloud-environments).

## Bootstrap tests

```sh
python3 -m unittest discover -s tests -p 'test_dev_skills.py'
```

The tests exercise the actual refresh command against a local Git remote,
including first installation, a newly published commit, deletions, and an
unreachable source. They do not require access to the private GitHub repository.
