"""Batch Error Aggregation and Reporting for TestAPIX

This module provides comprehensive error aggregation and reporting capabilities
for batch operations, helping users understand patterns and prioritize fixes.
"""

import json
import time
from collections import Counter
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

from testapix.core.exceptions import ResponseValidationError
from testapix.core.logging_utils import ErrorSuggestion, get_logger


class BatchErrorSeverity(str, Enum):
    """Severity levels for batch errors"""

    CRITICAL = "critical"  # Blocking all operations
    HIGH = "high"  # Major functionality broken
    MEDIUM = "medium"  # Some functionality impaired
    LOW = "low"  # Minor issues, warnings
    INFO = "info"  # Informational, not errors


@dataclass
class BatchErrorItem:
    """Individual error item in a batch operation"""

    error: Exception
    context: dict[str, Any]
    timestamp: float
    operation_id: str
    operation_type: str
    severity: BatchErrorSeverity = BatchErrorSeverity.HIGH

    def __post_init__(self) -> None:
        """Set severity based on error type if not explicitly provided"""
        if isinstance(self.error, ResponseValidationError):
            # Status code errors are often more critical
            if hasattr(self.error, "actual") and isinstance(self.error.actual, int):
                status = self.error.actual
                if status >= 500:
                    self.severity = BatchErrorSeverity.CRITICAL
                elif status in (401, 403, 404):
                    self.severity = BatchErrorSeverity.HIGH
                else:
                    self.severity = BatchErrorSeverity.MEDIUM
        elif "timeout" in str(self.error).lower():
            self.severity = BatchErrorSeverity.HIGH
        elif "network" in str(self.error).lower():
            self.severity = BatchErrorSeverity.CRITICAL


@dataclass
class BatchErrorPattern:
    """Represents a pattern of similar errors"""

    error_type: str
    message_pattern: str
    occurrences: int
    first_seen: float
    last_seen: float
    operation_types: set[str] = field(default_factory=set)
    contexts: list[dict[str, Any]] = field(default_factory=list)
    severity: BatchErrorSeverity = BatchErrorSeverity.MEDIUM
    suggested_fixes: list[ErrorSuggestion] = field(default_factory=list)

    def add_occurrence(self, error_item: BatchErrorItem) -> None:
        """Add another occurrence of this pattern"""
        self.occurrences += 1
        self.last_seen = error_item.timestamp
        self.operation_types.add(error_item.operation_type)
        self.contexts.append(error_item.context)

        # Update severity to the highest seen
        severities = [
            BatchErrorSeverity.INFO,
            BatchErrorSeverity.LOW,
            BatchErrorSeverity.MEDIUM,
            BatchErrorSeverity.HIGH,
            BatchErrorSeverity.CRITICAL,
        ]
        if severities.index(error_item.severity) > severities.index(self.severity):
            self.severity = error_item.severity


@dataclass
class BatchOperationReport:
    """Comprehensive report for a batch operation"""

    operation_name: str
    start_time: float
    end_time: float | None = None
    total_operations: int = 0
    successful_operations: int = 0
    failed_operations: int = 0
    errors: list[BatchErrorItem] = field(default_factory=list)
    patterns: list[BatchErrorPattern] = field(default_factory=list)
    performance_stats: dict[str, Any] = field(default_factory=dict)
    suggestions: list[ErrorSuggestion] = field(default_factory=list)

    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage"""
        if self.total_operations == 0:
            return 0.0
        return (self.successful_operations / self.total_operations) * 100

    @property
    def duration(self) -> float:
        """Calculate total duration in seconds"""
        if self.end_time is None:
            return time.time() - self.start_time
        return self.end_time - self.start_time

    def add_error(
        self,
        error: Exception,
        context: dict[str, Any],
        operation_id: str,
        operation_type: str,
    ) -> None:
        """Add an error to the batch report"""
        error_item = BatchErrorItem(
            error=error,
            context=context,
            timestamp=time.time(),
            operation_id=operation_id,
            operation_type=operation_type,
        )

        self.errors.append(error_item)
        self.failed_operations += 1

        # Update patterns
        self._update_patterns(error_item)

    def add_success(self, context: dict[str, Any]) -> None:
        """Add a successful operation to the report"""
        self.successful_operations += 1

    def _update_patterns(self, error_item: BatchErrorItem) -> None:
        """Update error patterns with new error"""
        error_type = type(error_item.error).__name__
        message = str(error_item.error)

        # Simple pattern matching - could be enhanced with more sophisticated algorithms
        message_pattern = self._extract_pattern(message)

        # Look for existing pattern
        for pattern in self.patterns:
            if (
                pattern.error_type == error_type
                and pattern.message_pattern == message_pattern
            ):
                pattern.add_occurrence(error_item)
                return

        # Create new pattern
        new_pattern = BatchErrorPattern(
            error_type=error_type,
            message_pattern=message_pattern,
            occurrences=1,
            first_seen=error_item.timestamp,
            last_seen=error_item.timestamp,
            severity=error_item.severity,
        )
        new_pattern.add_occurrence(error_item)
        self.patterns.append(new_pattern)

    def _extract_pattern(self, message: str) -> str:
        """Extract a pattern from error message for grouping"""
        # Replace numbers, IDs, and other variable parts with placeholders
        import re

        # Replace UUIDs
        pattern = re.sub(
            r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b",
            "<UUID>",
            message,
            flags=re.IGNORECASE,
        )

        # Replace numbers
        pattern = re.sub(r"\b\d+\b", "<NUMBER>", pattern)

        # Replace URLs
        pattern = re.sub(r"https?://[^\s]+", "<URL>", pattern)

        # Replace file paths
        pattern = re.sub(r"/[^/\s]+(?:/[^/\s]+)*", "<PATH>", pattern)

        # Replace quoted strings
        pattern = re.sub(r'"[^"]*"', "<STRING>", pattern)
        pattern = re.sub(r"'[^']*'", "<STRING>", pattern)

        return pattern

    def finalize(self) -> None:
        """Finalize the report and generate insights"""
        self.end_time = time.time()
        self.total_operations = self.successful_operations + self.failed_operations

        # Generate performance stats
        self.performance_stats = {
            "duration": self.duration,
            "operations_per_second": (
                self.total_operations / self.duration if self.duration > 0 else 0
            ),
            "average_response_time": self._calculate_avg_response_time(),
            "error_rate": (
                (self.failed_operations / self.total_operations * 100)
                if self.total_operations > 0
                else 0
            ),
        }

        # Generate suggestions based on patterns
        self._generate_suggestions()

        # Sort patterns by severity and occurrence count
        self.patterns.sort(
            key=lambda p: (
                ["info", "low", "medium", "high", "critical"].index(p.severity),
                p.occurrences,
            ),
            reverse=True,
        )

    def _calculate_avg_response_time(self) -> float:
        """Calculate average response time from error contexts"""
        response_times = []
        for error in self.errors:
            if "response_time" in error.context:
                response_times.append(error.context["response_time"])

        return sum(response_times) / len(response_times) if response_times else 0

    def _generate_suggestions(self) -> None:
        """Generate suggestions based on error patterns"""
        self.suggestions = []

        # Pattern-based suggestions
        error_types = Counter(p.error_type for p in self.patterns)

        if error_types.get("ResponseValidationError", 0) > 0:
            self.suggestions.append(
                ErrorSuggestion(
                    "Review API response validation",
                    "Multiple validation errors suggest API schema changes or test expectations need updating",
                    1,
                )
            )

        if error_types.get("TimeoutError", 0) > 0:
            self.suggestions.append(
                ErrorSuggestion(
                    "Investigate timeout issues",
                    "Consider increasing timeouts or optimizing API performance",
                    1,
                )
            )

        if self.success_rate < 50:
            self.suggestions.append(
                ErrorSuggestion(
                    "Critical batch failure",
                    f"Only {self.success_rate:.1f}% success rate indicates systematic issues",
                    1,
                )
            )
        elif self.success_rate < 90:
            self.suggestions.append(
                ErrorSuggestion(
                    "Review failing operations",
                    f"{self.success_rate:.1f}% success rate suggests some operations need attention",
                    2,
                )
            )

        # Performance suggestions
        if self.performance_stats.get("operations_per_second", 0) < 1:
            self.suggestions.append(
                ErrorSuggestion(
                    "Optimize batch performance",
                    "Low throughput suggests potential for parallelization or optimization",
                    3,
                )
            )


class BatchErrorAggregator:
    """Aggregates and analyzes errors from batch operations"""

    def __init__(self, name: str = "BatchOperations"):
        self.name = name
        self.logger = get_logger(f"{__name__}.{name}")
        self.active_reports: dict[str, BatchOperationReport] = {}
        self.completed_reports: list[BatchOperationReport] = []
        self.global_patterns: dict[str, BatchErrorPattern] = {}

    def start_batch(self, batch_id: str, operation_name: str) -> BatchOperationReport:
        """Start tracking a new batch operation"""
        report = BatchOperationReport(
            operation_name=operation_name, start_time=time.time()
        )

        self.active_reports[batch_id] = report
        self.logger.info(f"Started batch operation: {operation_name} (ID: {batch_id})")

        return report

    def record_error(
        self,
        batch_id: str,
        error: Exception,
        operation_id: str,
        operation_type: str,
        context: dict[str, Any] | None = None,
    ) -> None:
        """Record an error for a batch operation"""
        if batch_id not in self.active_reports:
            self.logger.warning(f"Recording error for unknown batch: {batch_id}")
            return

        context = context or {}
        report = self.active_reports[batch_id]
        report.add_error(error, context, operation_id, operation_type)

        # Update global patterns
        self._update_global_patterns(error, context)

        self.logger.debug(f"Recorded error in batch {batch_id}: {type(error).__name__}")

    def record_success(
        self, batch_id: str, context: dict[str, Any] | None = None
    ) -> None:
        """Record a successful operation for a batch"""
        if batch_id not in self.active_reports:
            self.logger.warning(f"Recording success for unknown batch: {batch_id}")
            return

        context = context or {}
        report = self.active_reports[batch_id]
        report.add_success(context)

    def finish_batch(self, batch_id: str) -> BatchOperationReport:
        """Finish a batch operation and generate final report"""
        if batch_id not in self.active_reports:
            raise ValueError(f"No active batch with ID: {batch_id}")

        report = self.active_reports.pop(batch_id)
        report.finalize()

        self.completed_reports.append(report)

        # Log summary
        self.logger.info(
            f"Completed batch operation: {report.operation_name} "
            f"({report.success_rate:.1f}% success, {report.duration:.2f}s)"
        )

        # Log critical patterns
        critical_patterns = [
            p for p in report.patterns if p.severity == BatchErrorSeverity.CRITICAL
        ]
        if critical_patterns:
            self.logger.error(
                f"Critical error patterns found in batch {batch_id}: "
                f"{[p.error_type for p in critical_patterns]}"
            )

        return report

    def _update_global_patterns(
        self, error: Exception, context: dict[str, Any]
    ) -> None:
        """Update global error patterns across all operations"""
        error_type = type(error).__name__
        message_pattern = self._extract_pattern(str(error))
        pattern_key = f"{error_type}:{message_pattern}"

        if pattern_key in self.global_patterns:
            # This is a simplified update - in a real implementation,
            # you'd want to create a proper BatchErrorItem
            self.global_patterns[pattern_key].occurrences += 1
            self.global_patterns[pattern_key].last_seen = time.time()
        else:
            self.global_patterns[pattern_key] = BatchErrorPattern(
                error_type=error_type,
                message_pattern=message_pattern,
                occurrences=1,
                first_seen=time.time(),
                last_seen=time.time(),
            )

    def _extract_pattern(self, message: str) -> str:
        """Extract pattern from error message (same as in BatchOperationReport)"""
        import re

        pattern = re.sub(
            r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b",
            "<UUID>",
            message,
            flags=re.IGNORECASE,
        )
        pattern = re.sub(r"\b\d+\b", "<NUMBER>", pattern)
        pattern = re.sub(r"https?://[^\s]+", "<URL>", pattern)
        pattern = re.sub(r"/[^/\s]+(?:/[^/\s]+)*", "<PATH>", pattern)
        pattern = re.sub(r'"[^"]*"', "<STRING>", pattern)
        pattern = re.sub(r"'[^']*'", "<STRING>", pattern)

        return pattern

    def generate_summary_report(
        self, include_global_patterns: bool = True, min_pattern_occurrences: int = 2
    ) -> dict[str, Any]:
        """Generate a comprehensive summary report"""
        total_operations = sum(r.total_operations for r in self.completed_reports)
        total_errors = sum(r.failed_operations for r in self.completed_reports)

        # Calculate overall success rate
        overall_success_rate = (
            ((total_operations - total_errors) / total_operations * 100)
            if total_operations > 0
            else 0
        )

        # Most common error types
        all_patterns = []
        for report in self.completed_reports:
            all_patterns.extend(report.patterns)

        error_type_counts = Counter(p.error_type for p in all_patterns)

        # Generate report
        summary = {
            "overview": {
                "total_batches": len(self.completed_reports),
                "total_operations": total_operations,
                "total_errors": total_errors,
                "overall_success_rate": overall_success_rate,
                "avg_batch_duration": (
                    sum(r.duration for r in self.completed_reports)
                    / len(self.completed_reports)
                    if self.completed_reports
                    else 0
                ),
            },
            "top_error_types": dict(error_type_counts.most_common(10)),
            "batch_summaries": [
                {
                    "name": r.operation_name,
                    "success_rate": r.success_rate,
                    "duration": r.duration,
                    "total_operations": r.total_operations,
                    "error_count": r.failed_operations,
                    "top_patterns": [
                        {
                            "type": p.error_type,
                            "pattern": p.message_pattern,
                            "count": p.occurrences,
                            "severity": p.severity,
                        }
                        for p in sorted(
                            r.patterns, key=lambda x: x.occurrences, reverse=True
                        )[:3]
                    ],
                }
                for r in self.completed_reports
            ],
        }

        # Include global patterns if requested
        if include_global_patterns:
            significant_patterns = [
                p
                for p in self.global_patterns.values()
                if p.occurrences >= min_pattern_occurrences
            ]
            significant_patterns.sort(key=lambda x: x.occurrences, reverse=True)

            summary["global_patterns"] = [
                {
                    "type": p.error_type,
                    "pattern": p.message_pattern,
                    "occurrences": p.occurrences,
                    "severity": p.severity,
                    "first_seen": time.strftime(
                        "%Y-%m-%d %H:%M:%S", time.localtime(p.first_seen)
                    ),
                    "last_seen": time.strftime(
                        "%Y-%m-%d %H:%M:%S", time.localtime(p.last_seen)
                    ),
                }
                for p in significant_patterns[:20]  # Top 20 patterns
            ]

        return summary

    def export_report(
        self,
        filepath: str | Path,
        format: str = "json",
        include_detailed_errors: bool = False,
    ) -> None:
        """Export comprehensive report to file"""
        filepath = Path(filepath)
        summary = self.generate_summary_report()

        if include_detailed_errors:
            summary["detailed_reports"] = []
            for report in self.completed_reports:
                detailed_report = {
                    "operation_name": report.operation_name,
                    "start_time": time.strftime(
                        "%Y-%m-%d %H:%M:%S", time.localtime(report.start_time)
                    ),
                    "end_time": (
                        time.strftime(
                            "%Y-%m-%d %H:%M:%S", time.localtime(report.end_time)
                        )
                        if report.end_time
                        else None
                    ),
                    "performance_stats": report.performance_stats,
                    "patterns": [
                        {
                            "error_type": p.error_type,
                            "message_pattern": p.message_pattern,
                            "occurrences": p.occurrences,
                            "severity": p.severity,
                            "operation_types": list(p.operation_types),
                            "suggested_fixes": [
                                {
                                    "suggestion": s.suggestion,
                                    "action": s.action,
                                    "priority": s.priority,
                                }
                                for s in p.suggested_fixes
                            ],
                        }
                        for p in report.patterns
                    ],
                    "suggestions": [
                        {
                            "suggestion": s.suggestion,
                            "action": s.action,
                            "priority": s.priority,
                        }
                        for s in report.suggestions
                    ],
                }
                summary["detailed_reports"].append(detailed_report)

        # Export based on format
        if format.lower() == "json":
            with open(filepath, "w") as f:
                json.dump(summary, f, indent=2, default=str)
        elif format.lower() == "yaml":
            import yaml

            with open(filepath, "w") as f:
                yaml.dump(summary, f, default_flow_style=False)
        else:
            raise ValueError(f"Unsupported export format: {format}")

        self.logger.info(f"Exported batch report to {filepath}")

    def clear_completed_reports(self) -> None:
        """Clear completed reports to free memory"""
        cleared_count = len(self.completed_reports)
        self.completed_reports.clear()
        self.global_patterns.clear()
        self.logger.info(f"Cleared {cleared_count} completed reports")


# Context manager for batch operations
class BatchOperationContext:
    """Context manager for tracking batch operations with automatic error handling"""

    def __init__(
        self,
        aggregator: BatchErrorAggregator,
        batch_id: str,
        operation_name: str,
        auto_log_summary: bool = True,
    ):
        self.aggregator = aggregator
        self.batch_id = batch_id
        self.operation_name = operation_name
        self.auto_log_summary = auto_log_summary
        self.report: BatchOperationReport | None = None

    def __enter__(self) -> BatchOperationReport:
        """Enter the context manager and start batch tracking."""
        self.report = self.aggregator.start_batch(self.batch_id, self.operation_name)
        return self.report

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit the context manager and finalize the batch report."""
        if self.report:
            final_report = self.aggregator.finish_batch(self.batch_id)

            if self.auto_log_summary:
                self._log_summary(final_report)

    def _log_summary(self, report: BatchOperationReport) -> None:
        """Log a summary of the batch operation"""
        logger = self.aggregator.logger

        logger.info(f"Batch Operation Summary: {report.operation_name}")
        logger.info(f"  Success Rate: {report.success_rate:.1f}%")
        logger.info(f"  Total Operations: {report.total_operations}")
        logger.info(f"  Duration: {report.duration:.2f}s")

        if report.patterns:
            logger.info(f"  Error Patterns: {len(report.patterns)}")
            for pattern in report.patterns[:3]:  # Top 3 patterns
                logger.info(
                    f"    {pattern.error_type}: {pattern.occurrences} occurrences"
                )

        if report.suggestions:
            logger.info("  Top Suggestions:")
            for suggestion in report.suggestions[:3]:  # Top 3 suggestions
                logger.info(f"    • {suggestion.suggestion}")


# Global default aggregator instance
_default_aggregator = BatchErrorAggregator("default")


def get_batch_aggregator(name: str = "default") -> BatchErrorAggregator:
    """Get or create a batch error aggregator"""
    global _default_aggregator

    if name == "default":
        return _default_aggregator
    else:
        return BatchErrorAggregator(name)


def batch_operation(
    batch_id: str,
    operation_name: str,
    aggregator: BatchErrorAggregator | None = None,
) -> BatchOperationContext:
    """Create a context manager for batch operations"""
    if aggregator is None:
        aggregator = get_batch_aggregator()

    return BatchOperationContext(aggregator, batch_id, operation_name)
