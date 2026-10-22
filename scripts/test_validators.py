#!/usr/bin/env python3
"""Regression tests for validator bypasses and publication evidence."""

from __future__ import annotations

import subprocess
import tempfile
import unittest
import os
from pathlib import Path

import evaluation_check
import evolution_check
import repository_check
from quality_check import catalog_selection_warning, check_skill, engine_nesting


class ValidatorRegressionTests(unittest.TestCase):
    def test_quality_markers_inside_fence_do_not_count(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "SKILL.md").write_text(
                """---
name: fenced-only
description: This is a deliberately long trigger description used only to validate fenced Markdown handling in the quality checker.
---
# Fenced Only
```md
## Workflow
## Boundaries
## Quality Standard
```
""",
                encoding="utf-8",
            )
            issues = check_skill(root)
            self.assertTrue(any("workflow/process" in issue for issue in issues))
            self.assertTrue(any("boundaries/anti-patterns" in issue for issue in issues))

    def test_evolution_markers_inside_fence_do_not_count(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for rel, markers in evolution_check.REQUIRED_MARKERS.items():
                path = root / rel
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("```md\n" + "\n".join(markers) + "\n```\n", encoding="utf-8")
            issues = evolution_check.check_markers(root)
            self.assertTrue(issues)

    def test_evaluation_markers_inside_fence_do_not_count(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "references").mkdir()
            (root / "SKILL.md").write_text(
                "```md\n" + "\n".join(evaluation_check.REQUIRED_SKILL_MARKERS) + "\n```\n",
                encoding="utf-8",
            )
            rubric_markers = "\n".join(evaluation_check.REQUIRED_RUBRIC_MARKERS)
            weights = "\n".join(
                f"{name}：0-{maximum}" for name, maximum in evaluation_check.EXPECTED_WEIGHTS.items()
            )
            (root / "references" / "evaluation-rubric.md").write_text(
                f"```md\n{rubric_markers}\n{weights}\n```\n", encoding="utf-8"
            )
            self.assertTrue(evaluation_check.check(root))

    def test_repository_scans_index_blob_not_only_worktree(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            path = root / "README.md"
            staged_secret = "sk-" + "A" * 24
            path.write_text(staged_secret, encoding="utf-8")
            subprocess.run(["git", "add", "README.md"], cwd=root, check=True)
            path.write_text("clean worktree", encoding="utf-8")

            variants = repository_check.content_variants(root, "README.md", cached=True)
            by_origin = {origin: data.decode("utf-8") for origin, data in variants}
            self.assertEqual(by_origin["index"], staged_secret)
            self.assertEqual(by_origin["worktree"], "clean worktree")

    @unittest.skipUnless(
        (Path(__file__).resolve().parents[1] / ".gitignore").is_file(),
        "installed packages do not ship .gitignore",
    )
    def test_gitignore_allowlist_keeps_workspace_out_of_publication(self) -> None:
        gitignore = (Path(__file__).resolve().parents[1] / ".gitignore").read_text(encoding="utf-8")
        public = repository_check.ALLOWED_ROOT_FILES | {
            ".github/workflows/validate.yml",
            "examples/usage-verification.md",
        }
        workspace = {
            "child-skill/SKILL.md",
            "outputs/review/cover.png",
            "assets/article/figure.png",
            "examples/child-skill/SKILL.md",
            "references/drafts/note.md",
            ".dao/skills/child/SKILL.md",
            "scripts/__pycache__/check.cpython-313.pyc",
        }
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            for rel in public | workspace:
                path = root / rel
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("x", encoding="utf-8")
            (root / ".gitignore").write_text(gitignore, encoding="utf-8")

            _, untracked = repository_check.git_file_sets(root)
            self.assertEqual(untracked, public)
            self.assertTrue(all(repository_check.allowed_layout(rel) for rel in untracked))

    def test_child_inside_dao_engine_is_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            for kind, expected in (("source", "warning"), ("installed", "error")):
                engine = Path(tmp) / kind / "dao-skill"
                child = engine / "examples" / "child-skill"
                child.mkdir(parents=True)
                (engine / "SKILL.md").write_text(
                    "---\nname: dao-skill\ndescription: engine\n---\n# Dao\n", encoding="utf-8"
                )
                if kind == "source":
                    (engine / ".git").mkdir()
                result = engine_nesting(child.resolve())
                self.assertIsNotNone(result)
                self.assertEqual(result[0], expected)
                self.assertIsNone(engine_nesting(engine.resolve()))
            self.assertIsNone(engine_nesting(Path(tmp).resolve() / "outside" / "child-skill"))

    def test_formula_catalog_without_selection_rule_is_warned(self) -> None:
        catalog = "".join(f"{n}. 公式 {n}：「XX 模板 {n}」\n" for n in range(1, 21))
        dump = f"## 工作流程\n\n1. 套用下面全部 20 个公式。\n\n## 标题公式\n\n{catalog}"
        self.assertIsNotNone(catalog_selection_warning(dump))
        selected = dump.replace("套用下面全部 20 个公式", "先诊断内容，再按适用信号选用 2-4 个公式")
        self.assertIsNone(catalog_selection_warning(selected))
        fenced = f"## 标题公式\n\n{catalog}```md\n适用信号\n```\n"
        self.assertIsNotNone(catalog_selection_warning(fenced))
        short = "## 模板\n\n1. a\n2. b\n3. c\n"
        self.assertIsNone(catalog_selection_warning(short))

    def test_fake_png_is_rejected(self) -> None:
        self.assertTrue(repository_check.check_png(b"not a png", "assets/dao-skill-banner.png"))

    def test_four_backtick_fence_is_not_closed_by_three(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "SKILL.md").write_text(
                """---
name: four-fence
description: This deliberately long description exists to verify that nested shorter fences cannot expose fake semantic headings.
---
# Four Fence
````md
```
## Workflow
## Boundaries
## Quality Standard
```
````
""",
                encoding="utf-8",
            )
            self.assertTrue(check_skill(root))

    def test_frontmatter_requires_exact_closing_delimiter(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "SKILL.md").write_text(
                "---\nname: false-close\ndescription: A sufficiently long description for validator coverage.\n---not-a-delimiter\n# Body\n",
                encoding="utf-8",
            )
            self.assertIn("SKILL.md frontmatter is not closed", check_skill(root))

    def test_duplicate_and_extra_frontmatter_fields_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            duplicate_root = Path(tmp) / "duplicate"
            duplicate_root.mkdir()
            (duplicate_root / "SKILL.md").write_text(
                "---\nname: duplicate\nname: repeated\ndescription: A sufficiently long description for validator coverage and duplicate detection.\n---\n# Body\n",
                encoding="utf-8",
            )
            self.assertIn("Duplicate frontmatter field: name", check_skill(duplicate_root))

            extra_root = Path(tmp) / "extra"
            extra_root.mkdir()
            (extra_root / "SKILL.md").write_text(
                "---\nname: extra-field\ndescription: A sufficiently long description for validator coverage and extra field detection.\nversion: 1\n---\n# Body\n",
                encoding="utf-8",
            )
            self.assertTrue(
                any("Unexpected frontmatter field(s): version" in issue for issue in check_skill(extra_root))
            )

    def test_invalid_hyphen_placement_in_skill_name_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "SKILL.md").write_text(
                "---\nname: invalid--name\ndescription: A sufficiently long description for validator coverage and invalid name detection.\n---\n# Body\n",
                encoding="utf-8",
            )
            self.assertTrue(
                any("consecutive hyphens" in issue for issue in check_skill(root))
            )

    @unittest.skipIf(os.name == "nt", "creating symlinks may require Windows developer mode")
    def test_staged_symlink_mode_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            (root / "target.txt").write_text("target", encoding="utf-8")
            (root / "link.txt").symlink_to("target.txt")
            subprocess.run(["git", "add", "link.txt"], cwd=root, check=True)
            (root / "link.txt").unlink()
            (root / "link.txt").write_text("ordinary file", encoding="utf-8")
            self.assertEqual(repository_check.git_index_modes(root)["link.txt"], "120000")

    def test_metadata_markers_in_comments_do_not_count(self) -> None:
        fake = """# interface:
#   display_name: "fake"
#   short_description: "fake"
#   default_prompt: "$dao-skill explicitly requests"
# policy:
#   allow_implicit_invocation: true
"""
        self.assertTrue(repository_check.check_metadata(fake))

    def test_metadata_short_description_length_is_enforced(self) -> None:
        metadata = """interface:
  display_name: "Dao"
  short_description: "Too short"
  default_prompt: "Use $dao-skill when the user explicitly requests help."
policy:
  allow_implicit_invocation: true
"""
        self.assertIn(
            "agents/openai.yaml interface.short_description must be 25-64 characters",
            repository_check.check_metadata(metadata),
        )


if __name__ == "__main__":
    unittest.main()
