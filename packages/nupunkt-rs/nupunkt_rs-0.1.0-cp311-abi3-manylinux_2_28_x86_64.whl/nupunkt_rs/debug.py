"""
Debug and analysis utilities for nupunkt-rs

This module provides user-friendly tools for understanding and debugging
tokenization decisions.
"""

import json
from dataclasses import asdict, dataclass
from typing import Any


@dataclass
class TokenDecision:
    """Represents a tokenization decision for a single token"""

    text: str
    position: int
    has_period: bool
    decision: str  # 'Break', 'NoBreak', 'Continue'
    confidence: float
    reason: str
    is_abbreviation: bool = False
    factors: list[dict[str, Any]] | None = None

    def __post_init__(self):
        if self.factors is None:
            self.factors = []


class TokenizationAnalyzer:
    """User-friendly analyzer for tokenization decisions"""

    def __init__(self, tokenizer):
        self.tokenizer = tokenizer

    def analyze_text(self, text: str, verbose: bool = False) -> dict[str, Any]:
        """
        Analyze text and return structured results

        Returns a dictionary with:
        - sentences: List of sentences
        - decisions: List of TokenDecision objects
        - statistics: Summary statistics
        - issues: Potential problems detected
        """
        # Get analysis from tokenizer
        analysis = self.tokenizer.analyze_tokens(text)
        sentences = self.tokenizer.tokenize(text)

        # Convert to user-friendly format
        decisions = []
        for token in analysis.tokens:
            decision = TokenDecision(
                text=token.text,
                position=token.position,
                has_period=token.has_period,
                decision=str(token.decision),
                confidence=token.confidence,
                reason=token.primary_reason,
                is_abbreviation=token.in_abbrev_list,
                factors=[
                    {"type": str(f.factor_type), "weight": f.weight, "description": f.description}
                    for f in token.factors
                ],
            )
            decisions.append(decision)

        # Detect potential issues
        issues = self._detect_issues(decisions, sentences)

        return {
            "text": text,
            "sentences": sentences,
            "decisions": decisions,
            "statistics": {
                "total_tokens": analysis.statistics.total_tokens,
                "total_breaks": analysis.statistics.total_breaks,
                "abbreviations": analysis.statistics.abbreviations_found,
                "avg_confidence": analysis.statistics.average_confidence,
                "low_confidence": analysis.statistics.low_confidence_decisions,
            },
            "issues": issues,
        }

    def _detect_issues(
        self, decisions: list[TokenDecision], sentences: list[str]
    ) -> list[dict[str, Any]]:
        """Detect potential tokenization issues"""
        issues = []

        for _i, decision in enumerate(decisions):
            # Low confidence decisions
            if decision.has_period and decision.confidence < 0.3:
                issues.append(
                    {
                        "type": "low_confidence",
                        "position": decision.position,
                        "token": decision.text,
                        "confidence": decision.confidence,
                        "decision": decision.decision,
                        "severity": "warning",
                    }
                )

            # Abbreviations not in list
            if (
                decision.has_period
                and not decision.is_abbreviation
                and decision.decision == "NoBreak"
            ):
                issues.append(
                    {
                        "type": "unknown_abbreviation",
                        "position": decision.position,
                        "token": decision.text,
                        "severity": "info",
                        "suggestion": f'Consider adding "{decision.text.rstrip(".")}" to abbreviations',
                    }
                )

            # Very short sentences (might be over-segmented)
            for sent in sentences:
                if len(sent.split()) < 3 and not sent.endswith("?") and not sent.endswith("!"):
                    issues.append(
                        {
                            "type": "short_sentence",
                            "sentence": sent,
                            "severity": "info",
                            "suggestion": "Very short sentence - might be incorrectly segmented",
                        }
                    )
                    break  # Only report once

        return issues

    def format_analysis(self, analysis: dict[str, Any], format: str = "text") -> str:
        """
        Format analysis results for display

        Formats:
        - 'text': Human-readable text
        - 'json': JSON format
        - 'html': HTML with highlighting (for Jupyter)
        """
        if format == "json":
            # Convert dataclasses to dicts for JSON serialization
            analysis_copy = analysis.copy()
            analysis_copy["decisions"] = [asdict(d) for d in analysis["decisions"]]
            return json.dumps(analysis_copy, indent=2)

        elif format == "html":
            return self._format_html(analysis)

        else:  # text format
            return self._format_text(analysis)

    def _format_text(self, analysis: dict[str, Any]) -> str:
        """Format as readable text"""
        lines = []
        lines.append("=" * 70)
        lines.append("TOKENIZATION ANALYSIS")
        lines.append("=" * 70)
        lines.append("")

        # Sentences
        lines.append(f"Sentences ({len(analysis['sentences'])}):")
        for i, sent in enumerate(analysis["sentences"], 1):
            lines.append(f"  {i}. {sent}")
        lines.append("")

        # Statistics
        stats = analysis["statistics"]
        lines.append("Statistics:")
        lines.append(f"  Total tokens: {stats['total_tokens']}")
        lines.append(f"  Sentence breaks: {stats['total_breaks']}")
        lines.append(f"  Abbreviations: {stats['abbreviations']}")
        lines.append(f"  Avg confidence: {stats['avg_confidence']:.2f}")
        lines.append(f"  Low confidence decisions: {stats['low_confidence']}")
        lines.append("")

        # Key decisions (periods only)
        lines.append("Key Decisions:")
        for decision in analysis["decisions"]:
            if decision.has_period:
                symbol = "✓" if decision.decision == "Break" else "✗"
                lines.append(
                    f"  {symbol} '{decision.text}' @ pos {decision.position}: "
                    f"{decision.decision} (conf={decision.confidence:.2f}) - {decision.reason}"
                )
        lines.append("")

        # Issues
        if analysis["issues"]:
            lines.append(f"Potential Issues ({len(analysis['issues'])}):")
            for issue in analysis["issues"]:
                if issue["type"] == "low_confidence":
                    lines.append(
                        f"  ⚠ Low confidence at '{issue['token']}': {issue['confidence']:.2f}"
                    )
                elif issue["type"] == "unknown_abbreviation":
                    lines.append(f"  ℹ {issue['suggestion']}")
                elif issue["type"] == "short_sentence":
                    lines.append(f"  ℹ {issue['suggestion']}: '{issue['sentence']}'")

        return "\n".join(lines)

    def _format_html(self, analysis: dict[str, Any]) -> str:
        """Format as HTML with highlighting"""
        html = []
        html.append("""
        <style>
        .tokenization-analysis {
            font-family: 'Courier New', monospace;
            line-height: 1.6;
        }
        .sentence { 
            background: #e8f4f8; 
            padding: 8px; 
            margin: 4px 0;
            border-left: 3px solid #2196F3;
        }
        .break { 
            color: green; 
            font-weight: bold; 
        }
        .no-break { 
            color: orange; 
            font-weight: bold;
        }
        .low-conf { 
            background: #ffe6e6; 
        }
        .stats {
            background: #f5f5f5;
            padding: 10px;
            border-radius: 4px;
        }
        .issue {
            background: #fff3cd;
            padding: 5px;
            margin: 2px 0;
            border-left: 3px solid #ffc107;
        }
        </style>
        """)

        html.append('<div class="tokenization-analysis">')
        html.append("<h3>Tokenization Analysis</h3>")

        # Sentences
        html.append(f"<h4>Sentences ({len(analysis['sentences'])})</h4>")
        for i, sent in enumerate(analysis["sentences"], 1):
            html.append(f'<div class="sentence">{i}. {sent}</div>')

        # Statistics
        stats = analysis["statistics"]
        html.append("<h4>Statistics</h4>")
        html.append('<div class="stats">')
        html.append(f"Tokens: {stats['total_tokens']} | ")
        html.append(f"Breaks: {stats['total_breaks']} | ")
        html.append(f"Abbreviations: {stats['abbreviations']} | ")
        html.append(f"Avg Confidence: {stats['avg_confidence']:.2f} | ")
        html.append(f"Low Confidence: {stats['low_confidence']}")
        html.append("</div>")

        # Visual representation with decisions
        html.append("<h4>Decisions</h4>")
        html.append('<div style="font-size: 14px; line-height: 2;">')

        text = analysis["text"]
        last_pos = 0
        for decision in analysis["decisions"]:
            if decision.has_period:
                # Add text before this token
                if decision.position > last_pos:
                    html.append(text[last_pos : decision.position])

                # Add the token with formatting
                css_class = "break" if decision.decision == "Break" else "no-break"
                if decision.confidence < 0.3:
                    css_class += " low-conf"

                title = f"Confidence: {decision.confidence:.2f} - {decision.reason}"
                html.append(f'<span class="{css_class}" title="{title}">{decision.text}</span>')

                if decision.decision == "Break":
                    html.append(" <b>[BREAK]</b> ")

                last_pos = decision.position + len(decision.text)

        # Add remaining text
        if last_pos < len(text):
            html.append(text[last_pos:])

        html.append("</div>")

        # Issues
        if analysis["issues"]:
            html.append(f"<h4>Issues ({len(analysis['issues'])})</h4>")
            for issue in analysis["issues"]:
                severity_icon = "⚠️" if issue["severity"] == "warning" else "ℹ️"
                html.append(
                    f'<div class="issue">{severity_icon} {issue.get("suggestion", issue["type"])}</div>'
                )

        html.append("</div>")

        return "".join(html)

    def compare_models(
        self, text: str, models: list[tuple[str, Any]], pr_values: list[float] | None = None
    ) -> dict[str, Any]:
        """
        Compare tokenization across different models and settings

        Args:
            text: Text to analyze
            models: List of (name, tokenizer) tuples
            pr_values: Precision/recall values to test

        Returns:
            Dictionary with comparison results
        """
        if pr_values is None:
            pr_values = [0.0, 0.5, 1.0]
        results = {}

        for model_name, tokenizer in models:
            model_results = {}

            for pr in pr_values:
                tokenizer.set_precision_recall_balance(pr)
                sentences = tokenizer.tokenize(text)
                analysis = tokenizer.analyze_tokens(text)

                model_results[f"pr_{pr}"] = {
                    "sentences": sentences,
                    "count": len(sentences),
                    "avg_confidence": analysis.statistics.average_confidence,
                }

            results[model_name] = model_results

        return {"text": text, "models": results, "summary": self._summarize_comparison(results)}

    def _summarize_comparison(self, results: dict[str, Any]) -> dict[str, Any]:
        """Summarize comparison results"""
        summary = {"sentence_counts": {}, "confidence_ranges": {}, "consistency": {}}

        for model_name, model_results in results.items():
            counts = [r["count"] for r in model_results.values()]
            confidences = [r["avg_confidence"] for r in model_results.values()]

            summary["sentence_counts"][model_name] = {
                "min": min(counts),
                "max": max(counts),
                "range": max(counts) - min(counts),
            }

            summary["confidence_ranges"][model_name] = {
                "min": min(confidences),
                "max": max(confidences),
                "avg": sum(confidences) / len(confidences),
            }

        return summary


def create_feedback_report(
    tokenizer, text: str, expected_sentences: list[str], model_name: str = "unknown"
) -> dict[str, Any]:
    """
    Create a feedback report for incorrect tokenization

    Args:
        tokenizer: The tokenizer used
        text: Original text
        expected_sentences: What the correct sentences should be
        model_name: Name of the model used

    Returns:
        Dictionary with feedback data that can be submitted
    """
    actual_sentences = tokenizer.tokenize(text)
    analysis = tokenizer.analyze_tokens(text)

    # Find differences
    differences = []
    for i, (expected, actual) in enumerate(zip(expected_sentences, actual_sentences, strict=False)):
        if expected != actual:
            differences.append({"index": i, "expected": expected, "actual": actual})

    # If different lengths
    if len(expected_sentences) != len(actual_sentences):
        differences.append(
            {
                "type": "count_mismatch",
                "expected_count": len(expected_sentences),
                "actual_count": len(actual_sentences),
            }
        )

    report = {
        "model": model_name,
        "text": text,
        "expected_sentences": expected_sentences,
        "actual_sentences": actual_sentences,
        "differences": differences,
        "analysis": {
            "total_tokens": analysis.statistics.total_tokens,
            "total_breaks": analysis.statistics.total_breaks,
            "avg_confidence": analysis.statistics.average_confidence,
            "low_confidence_decisions": analysis.statistics.low_confidence_decisions,
        },
        "tokens_with_issues": [],
    }

    # Find problematic tokens
    for token in analysis.tokens:
        if token.has_period and token.confidence < 0.5:
            report["tokens_with_issues"].append(
                {
                    "text": token.text,
                    "position": token.position,
                    "decision": str(token.decision),
                    "confidence": token.confidence,
                    "reason": token.primary_reason,
                }
            )

    return report


def generate_training_data(feedback_reports: list[dict[str, Any]]) -> str:
    """
    Generate training data from feedback reports

    Args:
        feedback_reports: List of feedback reports

    Returns:
        Training data in a format suitable for the trainer
    """
    training_texts = []

    for report in feedback_reports:
        # Reconstruct properly segmented text
        properly_segmented = " ".join(report["expected_sentences"])
        training_texts.append(properly_segmented)

        # Add note about problematic tokens
        if report["tokens_with_issues"]:
            tokens = [t["text"] for t in report["tokens_with_issues"]]
            training_texts.append(f"# Problematic tokens: {', '.join(tokens)}")

    return "\n\n".join(training_texts)
