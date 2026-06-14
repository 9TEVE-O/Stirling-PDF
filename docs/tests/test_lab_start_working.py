"""Tests for docs/lab-start-working.md.

Validates the structure, content, and consistency of the LAB setup note
against the repository's Taskfile.yml and project conventions.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
DOC_PATH = REPO_ROOT / "docs" / "lab-start-working.md"
TASKFILE_PATH = REPO_ROOT / "Taskfile.yml"

REQUIRED_H2_SECTIONS = [
    "Repository baseline",
    "Observed project shape",
    "Setup commands",
    "First working slice",
    "Guardrails for future work",
    "Next action",
]

# All `task <name>` commands referenced in the doc's bash code blocks.
DOCUMENTED_TASK_COMMANDS = [
    "install",
    "check",
    "backend:check",
    "frontend:check",
    "engine:check",
    "dev",
    "dev:all",
]

EXPECTED_REPO_REFERENCE = "9TEVE-O/Stirling-PDF"
EXPECTED_DEFAULT_BRANCH = "main"
EXPECTED_WORKING_BRANCH = "lab/setup-start-working"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def doc_text() -> str:
    return DOC_PATH.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def taskfile_text() -> str:
    return TASKFILE_PATH.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def doc_lines(doc_text: str) -> list[str]:
    return doc_text.splitlines()


# ---------------------------------------------------------------------------
# File existence and basic health
# ---------------------------------------------------------------------------


class TestFileExists:
    def test_doc_file_exists(self) -> None:
        assert DOC_PATH.exists(), f"Expected file not found: {DOC_PATH}"

    def test_doc_file_is_not_empty(self, doc_text: str) -> None:
        assert len(doc_text.strip()) > 0, "docs/lab-start-working.md must not be empty"

    def test_doc_file_ends_with_newline(self, doc_text: str) -> None:
        assert doc_text.endswith("\n"), "File must end with a trailing newline"

    def test_taskfile_exists(self) -> None:
        assert TASKFILE_PATH.exists(), f"Taskfile not found: {TASKFILE_PATH}"


# ---------------------------------------------------------------------------
# Document structure: headings
# ---------------------------------------------------------------------------


class TestHeadings:
    def test_h1_title(self, doc_lines: list[str]) -> None:
        h1_lines = [line for line in doc_lines if line.startswith("# ")]
        assert len(h1_lines) == 1, "Document must have exactly one H1 heading"
        assert h1_lines[0] == "# LAB start-working note"

    @pytest.mark.parametrize("section", REQUIRED_H2_SECTIONS)
    def test_required_h2_section_present(
        self, doc_lines: list[str], section: str
    ) -> None:
        heading = f"## {section}"
        assert any(
            line.strip() == heading for line in doc_lines
        ), f"Required section missing: '{heading}'"

    def test_h2_section_count(self, doc_lines: list[str]) -> None:
        h2_lines = [line for line in doc_lines if re.match(r"^## ", line)]
        assert len(h2_lines) == len(
            REQUIRED_H2_SECTIONS
        ), f"Expected {len(REQUIRED_H2_SECTIONS)} H2 sections, found {len(h2_lines)}: {h2_lines}"

    def test_no_h3_or_deeper_headings(self, doc_lines: list[str]) -> None:
        deep = [line for line in doc_lines if re.match(r"^#{3,}", line)]
        assert deep == [], f"Unexpected sub-headings found: {deep}"


# ---------------------------------------------------------------------------
# Document content: repository metadata
# ---------------------------------------------------------------------------


class TestRepositoryMetadata:
    def test_repo_name_mentioned(self, doc_text: str) -> None:
        assert EXPECTED_REPO_REFERENCE in doc_text, (
            f"Expected repository reference '{EXPECTED_REPO_REFERENCE}' not found"
        )

    def test_default_branch_mentioned(self, doc_text: str) -> None:
        assert EXPECTED_DEFAULT_BRANCH in doc_text, (
            f"Expected default branch '{EXPECTED_DEFAULT_BRANCH}' not found"
        )

    def test_working_branch_mentioned(self, doc_text: str) -> None:
        assert EXPECTED_WORKING_BRANCH in doc_text, (
            f"Expected working branch '{EXPECTED_WORKING_BRANCH}' not found"
        )

    def test_access_levels_mentioned(self, doc_text: str) -> None:
        """The doc lists five repository access permissions."""
        access_levels = ["admin", "maintain", "push", "triage", "pull"]
        for level in access_levels:
            assert level in doc_text, f"Expected access level '{level}' not found"


# ---------------------------------------------------------------------------
# Setup commands: bash code blocks
# ---------------------------------------------------------------------------


def _extract_bash_blocks(text: str) -> list[list[str]]:
    """Return a list of blocks; each block is a list of non-empty lines."""
    blocks: list[list[str]] = []
    in_block = False
    current: list[str] = []
    for line in text.splitlines():
        if line.strip() == "```bash":
            in_block = True
            current = []
        elif line.strip() == "```" and in_block:
            in_block = False
            blocks.append([l for l in current if l.strip()])
        elif in_block:
            current.append(line)
    return blocks


class TestSetupCommands:
    @pytest.mark.parametrize("task_name", DOCUMENTED_TASK_COMMANDS)
    def test_documented_task_exists_in_taskfile(
        self, task_name: str, taskfile_text: str
    ) -> None:
        """Every `task <name>` mentioned in bash blocks must be defined or delegated in Taskfile.yml."""
        # Tasks can appear as top-level entries or as namespace includes (e.g. backend:check)
        if ":" in task_name:
            namespace, subtask = task_name.split(":", 1)
            # The namespace must be included in Taskfile.yml
            assert f"taskfile: .taskfiles/{namespace}.yml" in taskfile_text, (
                f"Namespace '{namespace}' not included in Taskfile.yml "
                f"(needed for documented task '{task_name}')"
            )
        else:
            # Top-level task: look for `<name>:` at start of a line (with optional spaces)
            pattern = rf"^\s+{re.escape(task_name)}:\s*$"
            assert re.search(pattern, taskfile_text, re.MULTILINE), (
                f"Task '{task_name}' not found as a top-level task in Taskfile.yml"
            )

    def test_bash_blocks_contain_only_task_invocations(self, doc_text: str) -> None:
        """All commands in bash code blocks must be `task ...` invocations."""
        blocks = _extract_bash_blocks(doc_text)
        assert len(blocks) > 0, "Expected at least one bash code block in the document"
        for block in blocks:
            for line in block:
                stripped = line.strip()
                assert stripped.startswith("task "), (
                    f"Non-task command found in bash block: '{stripped}'. "
                    "All bash examples must use the task runner."
                )

    def test_four_bash_code_blocks_present(self, doc_text: str) -> None:
        """The Setup commands section should contain exactly four bash blocks."""
        blocks = _extract_bash_blocks(doc_text)
        assert len(blocks) == 4, (
            f"Expected 4 bash code blocks (root, narrow checks, dev, dev:all), found {len(blocks)}"
        )

    def test_install_and_check_in_first_block(self, doc_text: str) -> None:
        blocks = _extract_bash_blocks(doc_text)
        first = [line.strip() for line in blocks[0]]
        assert "task install" in first
        assert "task check" in first

    def test_narrow_checks_block_has_three_commands(self, doc_text: str) -> None:
        blocks = _extract_bash_blocks(doc_text)
        second = [line.strip() for line in blocks[1]]
        assert len(second) == 3, (
            f"Expected 3 narrow check commands, found {len(second)}: {second}"
        )
        assert "task backend:check" in second
        assert "task frontend:check" in second
        assert "task engine:check" in second

    def test_dev_block_has_single_command(self, doc_text: str) -> None:
        blocks = _extract_bash_blocks(doc_text)
        third = [line.strip() for line in blocks[2]]
        assert third == ["task dev"]

    def test_dev_all_block_has_single_command(self, doc_text: str) -> None:
        blocks = _extract_bash_blocks(doc_text)
        fourth = [line.strip() for line in blocks[3]]
        assert fourth == ["task dev:all"]


# ---------------------------------------------------------------------------
# First working slice
# ---------------------------------------------------------------------------


class TestFirstWorkingSlice:
    def _get_section_lines(
        self, doc_lines: list[str], section_heading: str
    ) -> list[str]:
        """Return lines belonging to a section (until the next H2 or end of file)."""
        start = None
        result: list[str] = []
        for i, line in enumerate(doc_lines):
            if line.strip() == f"## {section_heading}":
                start = i + 1
            elif start is not None and re.match(r"^## ", line):
                break
            elif start is not None:
                result.append(line)
        return result

    def test_five_numbered_steps(self, doc_lines: list[str]) -> None:
        section = self._get_section_lines(doc_lines, "First working slice")
        numbered = [
            line.strip()
            for line in section
            if re.match(r"^\d+\.", line.strip())
        ]
        assert len(numbered) == 5, (
            f"Expected 5 numbered steps in 'First working slice', found {len(numbered)}"
        )

    def test_steps_are_consecutively_numbered(self, doc_lines: list[str]) -> None:
        section = self._get_section_lines(doc_lines, "First working slice")
        numbered = [
            line.strip()
            for line in section
            if re.match(r"^\d+\.", line.strip())
        ]
        for expected, item in enumerate(numbered, start=1):
            actual_num = int(item.split(".")[0])
            assert actual_num == expected, (
                f"Step {expected} is out of sequence: '{item}'"
            )

    def test_tests_before_behaviour_step_present(self, doc_lines: list[str]) -> None:
        """Step 4 must mention tests."""
        section = self._get_section_lines(doc_lines, "First working slice")
        numbered = [
            line.strip()
            for line in section
            if re.match(r"^\d+\.", line.strip())
        ]
        step_4 = numbered[3]
        assert "test" in step_4.lower(), (
            f"Step 4 should mention tests but got: '{step_4}'"
        )


# ---------------------------------------------------------------------------
# Guardrails
# ---------------------------------------------------------------------------


class TestGuardrails:
    def _get_guardrails_lines(self, doc_lines: list[str]) -> list[str]:
        start = None
        result: list[str] = []
        for line in doc_lines:
            if line.strip() == "## Guardrails for future work":
                start = True
            elif start and re.match(r"^## ", line):
                break
            elif start:
                result.append(line)
        return result

    def test_five_guardrail_bullets(self, doc_lines: list[str]) -> None:
        section = self._get_guardrails_lines(doc_lines)
        bullets = [
            line.strip() for line in section if line.strip().startswith("- ")
        ]
        assert len(bullets) == 5, (
            f"Expected 5 guardrail bullets, found {len(bullets)}: {bullets}"
        )

    def test_security_guardrail_present(self, doc_lines: list[str]) -> None:
        section = self._get_guardrails_lines(doc_lines)
        text = "\n".join(section)
        assert "PDF security" in text or "security" in text.lower(), (
            "Guardrails must address PDF security concerns"
        )

    def test_licensing_guardrail_present(self, doc_lines: list[str]) -> None:
        section = self._get_guardrails_lines(doc_lines)
        text = "\n".join(section)
        assert "licensing" in text.lower() or "attribution" in text.lower(), (
            "Guardrails must mention licensing or upstream attribution"
        )

    def test_ai_behaviour_guardrail_present(self, doc_lines: list[str]) -> None:
        section = self._get_guardrails_lines(doc_lines)
        text = "\n".join(section)
        assert "AI" in text or "ai" in text.lower(), (
            "Guardrails must address AI behaviour"
        )

    def test_reversibility_guardrail_present(self, doc_lines: list[str]) -> None:
        section = self._get_guardrails_lines(doc_lines)
        text = "\n".join(section)
        assert "reversible" in text.lower() or "small" in text.lower(), (
            "Guardrails must mention keeping changes small and reversible"
        )

    def test_no_guardrail_mentions_weakening_security(
        self, doc_lines: list[str]
    ) -> None:
        """The security guardrail must be phrased as a prohibition (starts with 'Do not')."""
        section = self._get_guardrails_lines(doc_lines)
        security_bullets = [
            line.strip()
            for line in section
            if "security" in line.lower() and line.strip().startswith("- ")
        ]
        assert len(security_bullets) >= 1
        for bullet in security_bullets:
            assert bullet.startswith("- Do not"), (
                f"Security guardrail should be a prohibition: '{bullet}'"
            )


# ---------------------------------------------------------------------------
# Whitespace and formatting
# ---------------------------------------------------------------------------


class TestFormatting:
    def test_no_trailing_whitespace(self, doc_lines: list[str]) -> None:
        offending = [
            (i + 1, repr(line))
            for i, line in enumerate(doc_lines)
            if line != line.rstrip()
        ]
        assert offending == [], (
            f"Trailing whitespace found on lines: {offending}"
        )

    def test_no_windows_line_endings(self, doc_text: str) -> None:
        assert "\r\n" not in doc_text, "File must not contain Windows (CRLF) line endings"

    def test_no_tab_characters(self, doc_text: str) -> None:
        assert "\t" not in doc_text, "File must not contain tab characters"

    def test_line_count_is_reasonable(self, doc_lines: list[str]) -> None:
        """The document should be concise — between 50 and 200 lines."""
        assert 50 <= len(doc_lines) <= 200, (
            f"Unexpected line count {len(doc_lines)}; expected between 50 and 200"
        )


# ---------------------------------------------------------------------------
# Regression / boundary tests
# ---------------------------------------------------------------------------


class TestRegressionAndBoundary:
    def test_no_placeholder_text(self, doc_text: str) -> None:
        """Common placeholder strings must not appear in the document."""
        placeholders = ["TODO", "FIXME", "PLACEHOLDER", "TBD", "lorem ipsum"]
        for placeholder in placeholders:
            assert placeholder not in doc_text, (
                f"Placeholder text '{placeholder}' found in document"
            )

    def test_no_duplicate_h2_sections(self, doc_lines: list[str]) -> None:
        h2_lines = [line.strip() for line in doc_lines if re.match(r"^## ", line)]
        assert len(h2_lines) == len(set(h2_lines)), (
            f"Duplicate H2 headings found: {h2_lines}"
        )

    def test_project_components_listed(self, doc_text: str) -> None:
        """The 'Observed project shape' section must list all seven components."""
        components = [
            "Spring Boot",
            "React",
            "TypeScript",
            "Python",
            "Tauri",
            "Docker",
            "Gradle",
        ]
        for component in components:
            assert component in doc_text, (
                f"Expected project component '{component}' not mentioned"
            )

    def test_taskfile_runner_mentioned(self, doc_text: str) -> None:
        assert "Taskfile" in doc_text, (
            "Document must reference the Taskfile-based developer command runner"
        )

    def test_next_action_section_is_non_empty(self, doc_lines: list[str]) -> None:
        """The 'Next action' section must contain at least one non-blank line of guidance."""
        start = None
        content_lines: list[str] = []
        for line in doc_lines:
            if line.strip() == "## Next action":
                start = True
            elif start and re.match(r"^## ", line):
                break
            elif start and line.strip():
                content_lines.append(line)
        assert len(content_lines) >= 1, (
            "The 'Next action' section must contain at least one line of content"
        )

    def test_pull_request_mentioned_in_next_action(self, doc_lines: list[str]) -> None:
        """The next action must reference a pull request."""
        in_section = False
        section_text = ""
        for line in doc_lines:
            if line.strip() == "## Next action":
                in_section = True
            elif in_section and re.match(r"^## ", line):
                break
            elif in_section:
                section_text += line + "\n"
        assert "pull request" in section_text.lower() or "PR" in section_text, (
            "The 'Next action' section must reference a pull request"
        )
