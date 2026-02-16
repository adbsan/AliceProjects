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
from typing import List, Dict, Any, Optional
import json
from dataclasses import dataclass, asdict
from datetime import datetime


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


class CodeAnalyzer:
    """コード解析クラス（高性能版）"""
    
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
        py_files = list(self.project_root.rglob("*.py"))
        py_files = [f for f in py_files if "venv" not in str(f) and "__pycache__" not in str(f)]
        
        print(f"\n📁 解析対象: {len(py_files)} ファイル\n")
        
        for py_file in py_files:
            print(f"  分析中: {py_file.relative_to(self.project_root)}")
            self._analyze_file(py_file)
        
        # 結果をまとめる
        self._generate_report()
        
        return self.analysis_result
    
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
        try:
            tree = ast.parse(content)
            functions = len([n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)])
            classes = len([n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)])
            complexity = self._calculate_complexity(tree)
        except:
            functions = 0
            classes = 0
            complexity = 0
        
        # 保守性指標（簡易版）
        maintainability = self._calculate_maintainability(loc, complexity, comment_lines)
        
        return CodeMetrics(
            file=str(file_path.relative_to(self.project_root)),
            lines_of_code=loc,
            comment_lines=comment_lines,
            blank_lines=blank_lines,
            functions=functions,
            classes=classes,
            complexity=complexity,
            maintainability_index=maintainability
        )
    
    def _calculate_complexity(self, tree: ast.AST) -> int:
        """
        循環的複雑度を計算（簡易版）
        
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
        
        return complexity
    
    def _calculate_maintainability(self, loc: int, complexity: int, comments: int) -> float:
        """
        保守性指標を計算
        
        Args:
            loc: コード行数
            complexity: 複雑度
            comments: コメント行数
            
        Returns:
            保守性指標（0-100）
        """
        if loc == 0:
            return 100.0
        
        # 簡易的な計算式
        comment_ratio = comments / loc if loc > 0 else 0
        complexity_penalty = min(complexity / 10, 1.0)
        
        score = 100 - (complexity_penalty * 30) + (comment_ratio * 10)
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
        
        # 長い関数の検出
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_lines = node.end_lineno - node.lineno if hasattr(node, 'end_lineno') else 0
                    if func_lines > 50:
                        self.issues.append(CodeIssue(
                            file=rel_path,
                            line=node.lineno,
                            severity="medium",
                            category="complexity",
                            message=f"関数 '{node.name}' が長すぎます ({func_lines}行)",
                            suggestion="関数を小さな関数に分割することを検討してください"
                        ))
        except:
            pass
        
        # 行の長さチェック
        for i, line in enumerate(lines, 1):
            if len(line) > 120:
                self.issues.append(CodeIssue(
                    file=rel_path,
                    line=i,
                    severity="low",
                    category="style",
                    message=f"行が長すぎます ({len(line)}文字)",
                    suggestion="行を120文字以内に収めることを推奨します"
                ))
        
        # TODO コメントの検出
        for i, line in enumerate(lines, 1):
            if "TODO" in line or "FIXME" in line or "HACK" in line:
                self.issues.append(CodeIssue(
                    file=rel_path,
                    line=i,
                    severity="low",
                    category="todo",
                    message="TODO/FIXME/HACKコメントが残っています",
                    suggestion="対応予定の作業を計画してください"
                ))
        
        # print文の検出（デバッグ用）
        for i, line in enumerate(lines, 1):
            if line.strip().startswith("print(") and "# debug" not in line.lower():
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
        avg_maintainability = sum(m.maintainability_index for m in self.metrics) / len(self.metrics) if self.metrics else 0
        
        print(f"\n📈 コードメトリクス:")
        print(f"  総コード行数: {total_loc:,}")
        print(f"  関数数: {total_functions}")
        print(f"  クラス数: {total_classes}")
        print(f"  平均保守性指標: {avg_maintainability:.1f}/100")
        
        # 問題サマリー
        severity_counts = {
            "critical": len([i for i in self.issues if i.severity == "critical"]),
            "high": len([i for i in self.issues if i.severity == "high"]),
            "medium": len([i for i in self.issues if i.severity == "medium"]),
            "low": len([i for i in self.issues if i.severity == "low"])
        }
        
        print(f"\n⚠️  検出された問題:")
        print(f"  Critical: {severity_counts['critical']}")
        print(f"  High:     {severity_counts['high']}")
        print(f"  Medium:   {severity_counts['medium']}")
        print(f"  Low:      {severity_counts['low']}")
        print(f"  合計:     {len(self.issues)}")
        
        # 詳細な問題リスト
        if self.issues:
            print(f"\n📋 問題詳細（上位10件）:")
            for issue in sorted(self.issues, key=lambda x: ["low", "medium", "high", "critical"].index(x.severity), reverse=True)[:10]:
                print(f"\n  [{issue.severity.upper()}] {issue.file}:{issue.line}")
                print(f"    {issue.message}")
                print(f"    💡 {issue.suggestion}")
        
        # 結果を辞書に保存
        self.analysis_result = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_loc": total_loc,
                "total_functions": total_functions,
                "total_classes": total_classes,
                "avg_maintainability": avg_maintainability
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
            output_path = self.project_root / "code_analysis_report.json"
        
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
        
        # メトリクスベースの提案
        for metric in self.metrics:
            if metric.maintainability_index < 50:
                recommendations.append(
                    f"📉 {metric.file}: 保守性が低いです。リファクタリングを検討してください"
                )
            
            if metric.complexity > 20:
                recommendations.append(
                    f"🔄 {metric.file}: 複雑度が高いです。関数を分割してください"
                )
        
        # 問題ベースの提案
        critical_issues = [i for i in self.issues if i.severity == "critical"]
        if critical_issues:
            recommendations.append(
                f"🚨 Critical問題が{len(critical_issues)}件あります。最優先で対応してください"
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
    
    print("\n" + "=" * 70)
    print("✅ 解析完了")
    print("=" * 70)


if __name__ == "__main__":
    main()
