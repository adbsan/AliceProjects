import subprocess
import json
import ast
import re
from pathlib import Path
from typing import List, Dict, Any
from radon.complexity import cc_visit
from radon.metrics import mi_visit


FLAKE8_PATTERN = re.compile(
    r"^(?P<file>.*?):(?P<line>\d+):(?P<col>\d+):\s(?P<code>\w+)\s(?P<msg>.*)$"
)


class EnterpriseCodeAnalyzer:
    def __init__(self, root: str = ".") -> None:
        self.root = Path(root).resolve()
        self.issues: List[Dict[str, Any]] = []
        self.complexity_score = 0.0
        self.maintainability_index = 0.0

    # ===============================
    # Public
    # ===============================
    def run(self) -> None:
        print("=== Enterprise Code Quality Analyzer ===")
        self._run_external_tools()
        self._run_ast_analysis()
        self._compute_scores()
        self._export_report()

    # ===============================
    # External Tools
    # ===============================
    def _run_external_tools(self) -> None:
        self._capture_tool("flake8", ["flake8", str(self.root)])
        self._capture_tool(
            "pylint",
            ["pylint", str(self.root), "--output-format=json"],
            is_json=True,
        )
        self._capture_tool("mypy", ["mypy", str(self.root)])
        self._run_radon()

    def _capture_tool(
        self, name: str, command: List[str], is_json: bool = False
    ) -> None:
        print(f"Running {name}...")

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
        )

        if is_json:
            if result.stdout.strip():
                try:
                    data = json.loads(result.stdout)
                    for item in data:
                        self.issues.append(
                            {
                                "tool": "pylint",
                                "file": item.get("path"),
                                "line": item.get("line"),
                                "column": item.get("column"),
                                "code": item.get("symbol"),
                                "message": item.get("message"),
                                "severity": self._map_pylint_severity(
                                    item.get("type", "")
                                ),
                            }
                        )
                except json.JSONDecodeError:
                    pass
        else:
            for line in result.stdout.splitlines():
                self._parse_tool_output(name, line)

    # ===============================
    # Parsing
    # ===============================
    def _parse_tool_output(self, tool_name: str, raw_line: str) -> None:
        raw_line = raw_line.strip()
        if not raw_line:
            return

        if tool_name == "flake8":
            match = FLAKE8_PATTERN.match(raw_line)
            if not match:
                return

            self.issues.append(
                {
                    "tool": "flake8",
                    "file": match.group("file"),
                    "line": int(match.group("line")),
                    "column": int(match.group("col")),
                    "code": match.group("code"),
                    "message": match.group("msg"),
                    "severity": self._map_flake8_severity(
                        match.group("code")
                    ),
                }
            )

        elif tool_name == "mypy":
            # Example:
            # file.py:10: error: Something wrong
            parts = raw_line.split(":", 3)
            if len(parts) >= 3 and parts[1].isdigit():
                self.issues.append(
                    {
                        "tool": "mypy",
                        "file": parts[0],
                        "line": int(parts[1]),
                        "column": 0,
                        "code": "mypy",
                        "message": parts[-1].strip(),
                        "severity": "HIGH",
                    }
                )

    # ===============================
    # Severity Mapping
    # ===============================
    def _map_flake8_severity(self, code: str) -> str:
        if code.startswith(("E", "F")):
            return "HIGH"
        if code.startswith("W"):
            return "MEDIUM"
        return "LOW"

    def _map_pylint_severity(self, pylint_type: str) -> str:
        mapping = {
            "error": "HIGH",
            "fatal": "HIGH",
            "warning": "MEDIUM",
            "convention": "LOW",
            "refactor": "LOW",
        }
        return mapping.get(pylint_type, "LOW")

    # ===============================
    # Radon
    # ===============================
    def _run_radon(self) -> None:
        print("Running radon...")

        for py_file in self.root.rglob("*.py"):
            try:
                code = py_file.read_text(encoding="utf-8")
                blocks = cc_visit(code)
                for block in blocks:
                    self.complexity_score += block.complexity

                self.maintainability_index += mi_visit(code, True)
            except Exception:
                continue

    # ===============================
    # AST Analysis
    # ===============================
    def _run_ast_analysis(self) -> None:
        print("Running AST analysis...")

        for py_file in self.root.rglob("*.py"):
            try:
                tree = ast.parse(py_file.read_text(encoding="utf-8"))
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        if len(node.body) > 50:
                            self.issues.append(
                                {
                                    "tool": "AST",
                                    "file": str(py_file),
                                    "line": node.lineno,
                                    "column": 0,
                                    "code": "LONG_FUNCTION",
                                    "message": f"Function '{node.name}' too long",
                                    "severity": "MEDIUM",
                                }
                            )
            except Exception:
                continue

    # ===============================
    # Scoring
    # ===============================
    def _compute_scores(self) -> None:
        critical = sum(1 for i in self.issues if i["severity"] == "HIGH")
        medium = sum(1 for i in self.issues if i["severity"] == "MEDIUM")

        self.debt_score = (
            self.complexity_score * 2
            + critical * 5
            + medium * 3
        )

    # ===============================
    # Report
    # ===============================
    def _export_report(self) -> None:
        report = {
            "total_issues": len(self.issues),
            "complexity_score": self.complexity_score,
            "maintainability_index": self.maintainability_index,
            "debt_score": self.debt_score,
            "issues": self.issues,
        }

        with open("quality_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, indent=4)

        print("\n=== Summary ===")
        print(f"Issues: {len(self.issues)}")
        print(f"Complexity Score: {self.complexity_score:.2f}")
        print(f"Maintainability Index: {self.maintainability_index:.2f}")
        print(f"Debt Score: {self.debt_score:.2f}")
        print("Report saved to quality_report.json")


# ===============================
# Entry
# ===============================
def main() -> None:
    analyzer = EnterpriseCodeAnalyzer(".")
    analyzer.run()


if __name__ == "__main__":
    main()
