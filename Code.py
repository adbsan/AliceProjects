"""
Code Analyzer (高性能バージョン)
AliceProjectの全コードを解析し、品質向上の提案を行います

機能:
- 静的コード解析
- コード品質メトリクス計算
- 潜在的なバグ検出
- パフォーマンス最適化提案
- ベストプラクティスチェック
"""

import ast
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional, Set
import json
from dataclasses import dataclass, asdict
from datetime import datetime
import re


@dataclass
class CodeIssue:
    """コード問題データクラス"""
    file: str
    line: int
    severity: str  # critical/high/medium/low
    category: str
    message: str
    suggestion: str


@dataclass
class CodeMetrics:
    """コードメトリクスデータクラス"""
    file: str
    lines_of_code: int
    comment_lines: int
    blank_lines: int
    functions: int
    classes: int
    complexity: int
    maintainability_index: float
    max_function_length: int
    imports_count: int


class CodeAnalyzer:
    """コード解析クラス（高性能版）"""
    
    # 動的に設定可能なしきい値
    THRESHOLDS = {
        'max_line_length': 120,
        'max_function_length': 50,
        'max_complexity': 20,
        'min_maintainability': 50,
        'max_function_params': 5,
    }
    
    def __init__(self, project_root: Path):
        """
        初期化
        
        Args:
            project_root: プロジェクトルートパス
        """
        self.project_root = project_root
        self.issues: List[CodeIssue] = []
        self.metrics: List[CodeMetrics] = []
        self.analysis_result = {}
        self.output_dir = project_root / "code"
        self.output_dir.mkdir(exist_ok=True)
    
    def analyze_project(self) -> Dict[str, Any]:
        """
        プロジェクト全体を解析
        
        Returns:
            解析結果辞書
        """
        print("=" * 70)
        print("🔍 Alice Project - Code Analyzer (高性能版)")
        print("=" * 70)
        
        # Pythonファイルを取得
        py_files = self._get_python_files()
        
        print(f"\n📁 解析対象: {len(py_files)} ファイル")
        print(f"📂 出力ディレクトリ: {self.output_dir}\n")
        
        for py_file in py_files:
            print(f"  📄 分析中: {py_file.relative_to(self.project_root)}")
            self._analyze_file(py_file)
        
        # 結果をまとめる
        self._generate_report()
        
        return self.analysis_result
    
    def _get_python_files(self) -> List[Path]:
        """
        解析対象のPythonファイルを取得
        
        Returns:
            Pythonファイルのリスト
        """
        py_files = list(self.project_root.rglob("*.py"))
        # 除外パターン
        exclude_patterns = ['venv', '__pycache__', '.git', 'build', 'dist']
        
        filtered_files = []
        for f in py_files:
            if not any(pattern in str(f) for pattern in exclude_patterns):
                filtered_files.append(f)
        
        return sorted(filtered_files)
    
    def _analyze_file(self, file_path: Path):
        """
        単一ファイルを解析
        
        Args:
            file_path: ファイルパス
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # メトリクス計算
            metrics = self._calculate_metrics(file_path, content)
            self.metrics.append(metrics)
            
            # 問題検出
            self._detect_issues(file_path, content)
            
        except Exception as e:
            print(f"    ⚠️  解析エラー: {e}")
    
    def _calculate_metrics(self, file_path: Path, content: str) -> CodeMetrics:
        """
        コードメトリクスを計算
        
        Args:
            file_path: ファイルパス
            content: ファイル内容
            
        Returns:
            CodeMetricsオブジェクト
        """
        lines = content.split('\n')
        
        # 行数カウント
        loc = len([l for l in lines if l.strip() and not l.strip().startswith('#')])
        comment_lines = len([l for l in lines if l.strip().startswith('#')])
        blank_lines = len([l for l in lines if not l.strip()])
        
        # AST解析
        functions = 0
        classes = 0
        complexity = 0
        max_func_length = 0
        imports = 0
        
        try:
            tree = ast.parse(content)
            functions = len([n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)])
            classes = len([n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)])
            complexity = self._calculate_complexity(tree)
            max_func_length = self._get_max_function_length(tree)
            imports = len([n for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom))])
        except SyntaxError:
            pass
        
        # 保守性指標
        maintainability = self._calculate_maintainability(loc, complexity, comment_lines)
        
        return CodeMetrics(
            file=str(file_path.relative_to(self.project_root)),
            lines_of_code=loc,
            comment_lines=comment_lines,
            blank_lines=blank_lines,
            functions=functions,
            classes=classes,
            complexity=complexity,
            maintainability_index=maintainability,
            max_function_length=max_func_length,
            imports_count=imports
        )
    
    def _calculate_complexity(self, tree: ast.AST) -> int:
        """
        循環的複雑度を計算（McCabe複雑度）
        
        Args:
            tree: ASTツリー
            
        Returns:
            複雑度
        """
        complexity = 1
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
            elif isinstance(node, (ast.And, ast.Or)):
                complexity += 1
        
        return complexity
    
    def _get_max_function_length(self, tree: ast.AST) -> int:
        """
        最大関数長を取得
        
        Args:
            tree: ASTツリー
            
        Returns:
            最大関数長
        """
        max_length = 0
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if hasattr(node, 'end_lineno'):
                    length = node.end_lineno - node.lineno
                    max_length = max(max_length, length)
        
        return max_length
    
    def _calculate_maintainability(self, loc: int, complexity: int, comments: int) -> float:
        """
        保守性指標を計算（Maintainability Index）
        
        Args:
            loc: コード行数
            complexity: 複雑度
            comments: コメント行数
            
        Returns:
            保守性指標（0-100）
        """
        if loc == 0:
            return 100.0
        
        # コメント率
        comment_ratio = (comments / loc) if loc > 0 else 0
        
        # 複雑度ペナルティ（正規化）
        complexity_penalty = min(complexity / 50, 1.0)
        
        # コード量ペナルティ（大きすぎるファイル）
        size_penalty = min(loc / 1000, 1.0) * 0.5
        
        # 保守性スコア計算
        score = 100 - (complexity_penalty * 40) - (size_penalty * 20) + (comment_ratio * 15)
        
        return max(0.0, min(100.0, score))
    
    def _detect_issues(self, file_path: Path, content: str):
        """
        コード問題を検出
        
        Args:
            file_path: ファイルパス
            content: ファイル内容
        """
        lines = content.split('\n')
        rel_path = str(file_path.relative_to(self.project_root))
        
        # AST解析による問題検出
        try:
            tree = ast.parse(content)
            self._detect_ast_issues(tree, rel_path)
        except SyntaxError as e:
            self.issues.append(CodeIssue(
                file=rel_path,
                line=e.lineno if e.lineno else 0,
                severity="critical",
                category="syntax",
                message=f"構文エラー: {e.msg}",
                suggestion="構文を修正してください"
            ))
        
        # テキストベースの問題検出
        self._detect_text_issues(lines, rel_path)
    
    def _detect_ast_issues(self, tree: ast.AST, rel_path: str):
        """
        ASTベースの問題検出
        
        Args:
            tree: ASTツリー
            rel_path: 相対パス
        """
        for node in ast.walk(tree):
            # 長い関数
            if isinstance(node, ast.FunctionDef):
                if hasattr(node, 'end_lineno'):
                    func_lines = node.end_lineno - node.lineno
                    if func_lines > self.THRESHOLDS['max_function_length']:
                        self.issues.append(CodeIssue(
                            file=rel_path,
                            line=node.lineno,
                            severity="medium",
                            category="complexity",
                            message=f"関数 '{node.name}' が長すぎます ({func_lines}行 > {self.THRESHOLDS['max_function_length']}行)",
                            suggestion=f"関数を{self.THRESHOLDS['max_function_length']}行以内に分割してください"
                        ))
                
                # 引数が多すぎる関数
                num_args = len(node.args.args)
                if num_args > self.THRESHOLDS['max_function_params']:
                    self.issues.append(CodeIssue(
                        file=rel_path,
                        line=node.lineno,
                        severity="medium",
                        category="design",
                        message=f"関数 '{node.name}' の引数が多すぎます ({num_args}個)",
                        suggestion="引数をオブジェクトにまとめることを検討してください"
                    ))
            
            # 深いネスト
            if isinstance(node, (ast.If, ast.For, ast.While)):
                nest_level = self._get_nesting_level(node)
                if nest_level > 3:
                    self.issues.append(CodeIssue(
                        file=rel_path,
                        line=node.lineno,
                        severity="high",
                        category="complexity",
                        message=f"ネストが深すぎます (レベル {nest_level})",
                        suggestion="早期リターンや関数分割でネストを減らしてください"
                    ))
    
    def _get_nesting_level(self, node: ast.AST, level: int = 0) -> int:
        """
        ネストレベルを計算
        
        Args:
            node: ASTノード
            level: 現在のレベル
            
        Returns:
            最大ネストレベル
        """
        max_level = level
        
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.With)):
                child_level = self._get_nesting_level(child, level + 1)
                max_level = max(max_level, child_level)
        
        return max_level
    
    def _detect_text_issues(self, lines: List[str], rel_path: str):
        """
        テキストベースの問題検出
        
        Args:
            lines: ファイル行リスト
            rel_path: 相対パス
        """
        for i, line in enumerate(lines, 1):
            # 行の長さチェック
            if len(line) > self.THRESHOLDS['max_line_length']:
                self.issues.append(CodeIssue(
                    file=rel_path,
                    line=i,
                    severity="low",
                    category="style",
                    message=f"行が長すぎます ({len(line)}文字 > {self.THRESHOLDS['max_line_length']}文字)",
                    suggestion=f"行を{self.THRESHOLDS['max_line_length']}文字以内に分割してください"
                ))
            
            # TODOコメント
            if re.search(r'\b(TODO|FIXME|HACK|XXX)\b', line):
                self.issues.append(CodeIssue(
                    file=rel_path,
                    line=i,
                    severity="low",
                    category="todo",
                    message="TODO/FIXME/HACK/XXXコメントが残っています",
                    suggestion="対応予定の作業を計画してください"
                ))
            
            # デバッグprint文（ただしロギングは除外）
            stripped = line.strip()
            if stripped.startswith("print(") and "logger" not in line.lower() and "log" not in line.lower():
                # ユーザー向けメッセージは除外
                if not any(keyword in line for keyword in ["===", "---", "✅", "❌", "📊", "💡"]):
                    self.issues.append(CodeIssue(
                        file=rel_path,
                        line=i,
                        severity="low",
                        category="debug",
                        message="デバッグ用のprint文が残っている可能性があります",
                        suggestion="ロガーを使用するか、不要であれば削除してください"
                    ))
    
    def _generate_report(self):
        """解析レポートを生成"""
        print("\n" + "=" * 70)
        print("📊 解析結果サマリー")
        print("=" * 70)
        
        # メトリクスサマリー
        total_loc = sum(m.lines_of_code for m in self.metrics)
        total_functions = sum(m.functions for m in self.metrics)
        total_classes = sum(m.classes for m in self.metrics)
        total_imports = sum(m.imports_count for m in self.metrics)
        avg_maintainability = sum(m.maintainability_index for m in self.metrics) / len(self.metrics) if self.metrics else 0
        max_complexity = max((m.complexity for m in self.metrics), default=0)
        
        print(f"\n📈 コードメトリクス:")
        print(f"  総コード行数: {total_loc:,}")
        print(f"  関数数: {total_functions}")
        print(f"  クラス数: {total_classes}")
        print(f"  Import数: {total_imports}")
        print(f"  平均保守性指標: {avg_maintainability:.1f}/100")
        print(f"  最大複雑度: {max_complexity}")
        
        # 問題サマリー
        severity_counts = {
            "critical": len([i for i in self.issues if i.severity == "critical"]),
            "high": len([i for i in self.issues if i.severity == "high"]),
            "medium": len([i for i in self.issues if i.severity == "medium"]),
            "low": len([i for i in self.issues if i.severity == "low"])
        }
        
        print(f"\n⚠️  検出された問題:")
        print(f"  🔴 Critical: {severity_counts['critical']}")
        print(f"  🟠 High:     {severity_counts['high']}")
        print(f"  🟡 Medium:   {severity_counts['medium']}")
        print(f"  🟢 Low:      {severity_counts['low']}")
        print(f"  📊 合計:     {len(self.issues)}")
        
        # 重要な問題のみ表示
        critical_and_high = [i for i in self.issues if i.severity in ["critical", "high"]]
        medium_issues = [i for i in self.issues if i.severity == "medium"]
        
        if critical_and_high:
            print(f"\n🚨 Critical/High問題:")
            for issue in critical_and_high[:5]:
                print(f"\n  [{issue.severity.upper()}] {issue.file}:{issue.line}")
                print(f"    📝 {issue.message}")
                print(f"    💡 {issue.suggestion}")
        
        if medium_issues and not critical_and_high:
            print(f"\n⚠️  Medium問題（上位5件）:")
            for issue in medium_issues[:5]:
                print(f"\n  [{issue.severity.upper()}] {issue.file}:{issue.line}")
                print(f"    📝 {issue.message}")
                print(f"    💡 {issue.suggestion}")
        
        # 結果を辞書に保存
        self.analysis_result = {
            "timestamp": datetime.now().isoformat(),
            "thresholds": self.THRESHOLDS,
            "summary": {
                "total_loc": total_loc,
                "total_functions": total_functions,
                "total_classes": total_classes,
                "total_imports": total_imports,
                "avg_maintainability": round(avg_maintainability, 2),
                "max_complexity": max_complexity
            },
            "issues": {
                "total": len(self.issues),
                "by_severity": severity_counts
            },
            "metrics": [asdict(m) for m in self.metrics],
            "issues_detail": [asdict(i) for i in self.issues]
        }
    
    def export_report(self, output_path: Optional[Path] = None) -> str:
        """
        レポートをJSONで出力
        
        Args:
            output_path: 出力パス
            
        Returns:
            出力ファイルパス
        """
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = self.output_dir / f"code_analysis_{timestamp}.json"
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.analysis_result, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 レポートを出力しました: {output_path}")
        return str(output_path)
    
    def get_recommendations(self) -> List[str]:
        """
        改善提案を取得
        
        Returns:
            提案リスト
        """
        recommendations = []
        
        # Critical/High問題
        critical_issues = [i for i in self.issues if i.severity == "critical"]
        high_issues = [i for i in self.issues if i.severity == "high"]
        
        if critical_issues:
            recommendations.append(
                f"🚨 Critical問題が{len(critical_issues)}件あります。即座に対応してください"
            )
        
        if high_issues:
            recommendations.append(
                f"🔴 High問題が{len(high_issues)}件あります。優先的に対応してください"
            )
        
        # メトリクスベースの提案
        for metric in self.metrics:
            if metric.maintainability_index < self.THRESHOLDS['min_maintainability']:
                recommendations.append(
                    f"📉 {metric.file}: 保守性が低いです ({metric.maintainability_index:.1f}/100)"
                )
            
            if metric.complexity > self.THRESHOLDS['max_complexity']:
                recommendations.append(
                    f"🔄 {metric.file}: 複雑度が高いです ({metric.complexity} > {self.THRESHOLDS['max_complexity']})"
                )
        
        return recommendations


def main():
    """メイン実行"""
    # プロジェクトルートを取得
    project_root = Path(__file__).parent
    
    # 解析実行
    analyzer = CodeAnalyzer(project_root)
    analyzer.analyze_project()
    
    # レポート出力
    analyzer.export_report()
    
    # 推奨事項
    recommendations = analyzer.get_recommendations()
    if recommendations:
        print("\n" + "=" * 70)
        print("💡 改善提案:")
        print("=" * 70)
        for rec in recommendations:
            print(f"  {rec}")
    else:
        print("\n" + "=" * 70)
        print("✨ コード品質は良好です！")
        print("=" * 70)
    
    print("\n" + "=" * 70)
    print("✅ 解析完了")
    print("=" * 70)


if __name__ == "__main__":
    main()