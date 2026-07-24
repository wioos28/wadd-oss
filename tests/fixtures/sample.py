"""Sample Python module for testing."""

import json
from typing import Any, Optional


class DataAnalyzer:
    """Analyzes data and extracts insights."""

    def __init__(self, config: Optional[dict] = None):
        self.config = config or {}
        self.results = []

    def analyze(self, data: list[dict[str, Any]]) -> dict:
        """Analyze the input data and return insights."""
        if not data:
            return {"error": "No data provided"}

        total = len(data)
        numeric_fields = self._find_numeric_fields(data)

        result = {
            "total_records": total,
            "numeric_fields": numeric_fields,
            "summary": self._compute_summary(data, numeric_fields),
        }

        self.results.append(result)
        return result

    def _find_numeric_fields(self, data: list[dict]) -> list[str]:
        """Find fields that contain numeric values."""
        if not data:
            return []

        sample = data[0]
        numeric_fields = []
        for key, value in sample.items():
            if isinstance(value, (int, float)):
                numeric_fields.append(key)
        return numeric_fields

    def _compute_summary(self, data: list[dict], fields: list[str]) -> dict:
        """Compute summary statistics for numeric fields."""
        summary = {}
        for field in fields:
            values = [d.get(field, 0) for d in data if isinstance(d.get(field), (int, float))]
            if values:
                summary[field] = {
                    "mean": sum(values) / len(values),
                    "min": min(values),
                    "max": max(values),
                }
        return summary

    def export_results(self, filepath: str) -> None:
        """Export results to a JSON file."""
        with open(filepath, "w") as f:
            json.dump(self.results, f, indent=2)


def process_data(data: list[dict], options: Optional[dict] = None) -> dict:
    """Process data with optional configuration."""
    analyzer = DataAnalyzer(options)
    return analyzer.analyze(data)


# Example usage
if __name__ == "__main__":
    sample_data = [
        {"name": "Alice", "age": 30, "score": 85.5},
        {"name": "Bob", "age": 25, "score": 92.0},
        {"name": "Charlie", "age": 35, "score": 78.3},
    ]

    result = process_data(sample_data)
    print(json.dumps(result, indent=2))
