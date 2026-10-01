import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


PROJECT = Path(__file__).resolve().parents[1]
SOURCE_URL = "https://github.com/ericfeunekes/ai-marketplace.git"


class DevelopmentSkillsTest(unittest.TestCase):
    def setUp(self):
        scratch = PROJECT / ".scratch"
        scratch.mkdir(exist_ok=True)
        self.workspace = tempfile.TemporaryDirectory(dir=scratch)
        self.addCleanup(self.workspace.cleanup)
        self.root = Path(self.workspace.name)
        self.remote = self.root / "remote.git"
        self.author = self.root / "author"
        self.consumer = self.root / "consumer"
        self.consumer.mkdir()
        (self.consumer / "scripts").mkdir()
        shutil.copy2(PROJECT / "scripts/update-dev-skills.sh", self.consumer / "scripts")
        self.git("init", "--bare", "--initial-branch=main", str(self.remote))
        self.git("clone", str(self.remote), str(self.author))
        self.git("config", "user.name", "Bootstrap Test", cwd=self.author)
        self.git("config", "user.email", "bootstrap@example.invalid", cwd=self.author)
        self.write("plugins/software-development/skills/github/SKILL.md", "version one")
        self.write("plugins/software-development/references/artifact-routing.md", "shared reference")
        self.write("plugins/collaboration/skills/brainstorm/SKILL.md", "brainstorm")
        self.write("plugins/collaboration/references/native-subagents.md", "native reference")
        self.write("plugins/collaboration/scripts/runtime.py", "print('shared runtime')\n")
        self.write("skills/testing/SKILL.md", "testing")
        self.write("skills/personal-only/SKILL.md", "not selected")
        self.publish("Initial skill source")

        # Redirect the production GitHub URL to a real local remote for tests.
        config = self.root / "gitconfig"
        config.write_text(
            f'[url "{self.remote.as_uri()}"]\n'
            f'    insteadOf = {SOURCE_URL}\n'
            '[protocol "file"]\n    allow = always\n'
        )
        self.env = dict(os.environ, GIT_CONFIG_GLOBAL=str(config), GIT_TERMINAL_PROMPT="0")
        self.checkout = self.consumer / ".agents/skills/development-source"

    def git(self, *args, cwd=None):
        return subprocess.run(
            ["git", *args], cwd=cwd, check=True, capture_output=True, text=True
        )

    def write(self, path, content):
        destination = self.author / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(content)

    def publish(self, message):
        self.git("add", ".", cwd=self.author)
        self.git("commit", "-m", message, cwd=self.author)
        self.git("push", "origin", "main", cwd=self.author)

    def refresh(self):
        # Invoke from a different directory to prove the script owns its target.
        return subprocess.run(
            ["sh", str(self.consumer / "scripts/update-dev-skills.sh")],
            cwd=self.root,
            env=self.env,
            capture_output=True,
            text=True,
        )

    def assertRefreshSucceeds(self):
        result = self.refresh()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_clean_install_preserves_bundle_references_and_unrelated_skills(self):
        unrelated = self.consumer / ".agents/skills/project-specific/SKILL.md"
        unrelated.parent.mkdir(parents=True)
        unrelated.write_text("owned by this project")
        self.assertRefreshSucceeds()
        self.assertEqual(unrelated.read_text(), "owned by this project")
        github = self.checkout / "plugins/software-development/skills/github"
        self.assertEqual((github / "../../references/artifact-routing.md").read_text(), "shared reference")
        brainstorm = self.checkout / "plugins/collaboration/skills/brainstorm"
        self.assertEqual((brainstorm / "../../references/native-subagents.md").read_text(), "native reference")
        runner = brainstorm / "../../scripts/runtime.py"
        result = subprocess.run(["python3", str(runner)], check=True, capture_output=True, text=True)
        self.assertEqual(result.stdout, "shared runtime\n")
        self.assertTrue((self.checkout / "skills/testing/SKILL.md").is_file())
        self.assertFalse((self.checkout / "skills/personal-only").exists())

    def test_refresh_reads_new_published_commit_and_removes_deleted_files(self):
        self.assertRefreshSucceeds()
        self.write("plugins/software-development/skills/github/SKILL.md", "version two")
        (self.author / "plugins/software-development/references/artifact-routing.md").unlink()
        self.write("plugins/software-development/skills/new-workflow/SKILL.md", "new workflow")
        self.publish("Update shared workflows")
        self.assertRefreshSucceeds()
        self.assertEqual(
            (self.checkout / "plugins/software-development/skills/github/SKILL.md").read_text(),
            "version two",
        )
        self.assertTrue((self.checkout / "plugins/software-development/skills/new-workflow/SKILL.md").is_file())
        self.assertFalse((self.checkout / "plugins/software-development/references/artifact-routing.md").exists())

    def test_unreachable_source_fails_even_with_an_existing_checkout(self):
        self.remote.rename(self.root / "unavailable.git")
        self.assertNotEqual(self.refresh().returncode, 0)
        (self.root / "unavailable.git").rename(self.remote)
        self.assertRefreshSucceeds()
        self.remote.rename(self.root / "unavailable.git")
        self.assertNotEqual(self.refresh().returncode, 0)


if __name__ == "__main__":
    unittest.main()
