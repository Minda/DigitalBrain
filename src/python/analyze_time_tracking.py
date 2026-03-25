#!/usr/bin/env python3
"""
Analyze time tracking data from Stay In Session

Compares planned vs. actual time allocation for weekly planning experiments.
"""

import argparse
import csv
import json
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple

def load_csv_export(csv_path: Path) -> List[Dict]:
    """Load Stay In Session CSV export"""
    sessions = []
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            sessions.append(row)
    return sessions

def load_json_export(json_path: Path) -> List[Dict]:
    """Load Stay In Session JSON export"""
    with open(json_path, 'r') as f:
        data = json.load(f)
    return data.get('sessions', [])

def categorize_sessions(sessions: List[Dict]) -> Dict[str, float]:
    """Categorize sessions by project tag and sum hours"""
    categories = defaultdict(float)

    for session in sessions:
        # Adapt these field names based on actual Stay In Session export format
        tag = session.get('tag', session.get('project', 'Untagged'))
        duration_min = float(session.get('duration_minutes', 0))

        categories[tag] += duration_min / 60.0  # Convert to hours

    return dict(categories)

def parse_planned_allocation(planned_text: str) -> Dict[str, float]:
    """
    Parse planned allocation from text format

    Expected format:
    Job Applications: 8h
    Job Board MVP: 8h
    BlueDot Research: 4h
    """
    planned = {}
    for line in planned_text.strip().split('\n'):
        if ':' in line and 'h' in line:
            parts = line.split(':')
            category = parts[0].strip()
            hours_str = parts[1].strip().replace('h', '').strip()
            try:
                hours = float(hours_str.split()[0])  # Handle "8h (40%)" format
                planned[category] = hours
            except ValueError:
                continue
    return planned

def calculate_deviations(planned: Dict[str, float],
                        actual: Dict[str, float]) -> List[Tuple[str, float, float, float]]:
    """
    Calculate deviations between planned and actual

    Returns list of (category, planned, actual, deviation)
    """
    all_categories = set(planned.keys()) | set(actual.keys())
    deviations = []

    for category in sorted(all_categories):
        p = planned.get(category, 0)
        a = actual.get(category, 0)
        d = a - p
        deviations.append((category, p, a, d))

    return deviations

def generate_visualization(deviations: List[Tuple[str, float, float, float]]) -> str:
    """Generate ASCII visualization of planned vs. actual"""

    viz = []
    viz.append("Time Tracking Analysis: Planned vs. Actual")
    viz.append("=" * 70)
    viz.append("")

    total_planned = sum(d[1] for d in deviations)
    total_actual = sum(d[2] for d in deviations)

    viz.append(f"Total Planned: {total_planned:.1f}h")
    viz.append(f"Total Actual:  {total_actual:.1f}h")
    viz.append(f"Difference:    {total_actual - total_planned:+.1f}h")
    viz.append("")
    viz.append("-" * 70)
    viz.append(f"{'Category':<25} {'Planned':>8} {'Actual':>8} {'Deviation':>10}")
    viz.append("-" * 70)

    for category, planned, actual, deviation in deviations:
        if planned == 0 and actual == 0:
            continue

        # Create bar chart
        max_hours = 12  # Scale for visualization
        planned_bar = '█' * int((planned / max_hours) * 20)
        actual_bar = '█' * int((actual / max_hours) * 20)

        deviation_str = f"{deviation:+.1f}h"
        if deviation > 0:
            deviation_str += " ⚠️"  # Over-allocated
        elif deviation < -1:
            deviation_str += " 📉"  # Under-allocated

        viz.append(f"{category:<25} {planned:>6.1f}h {actual:>6.1f}h {deviation_str:>10}")
        viz.append(f"  Planned: {planned_bar}")
        viz.append(f"  Actual:  {actual_bar}")
        viz.append("")

    viz.append("-" * 70)
    viz.append("")

    # Analysis
    viz.append("## Insights")
    viz.append("")

    # Over-allocations
    over_allocated = [(c, d) for c, p, a, d in deviations if d > 1.0]
    if over_allocated:
        viz.append("**Over-allocated** (spent more time than planned):")
        for category, deviation in sorted(over_allocated, key=lambda x: x[1], reverse=True):
            viz.append(f"  • {category}: +{deviation:.1f}h")
        viz.append("")

    # Under-allocations
    under_allocated = [(c, d) for c, p, a, d in deviations if d < -1.0]
    if under_allocated:
        viz.append("**Under-allocated** (spent less time than planned):")
        for category, deviation in sorted(under_allocated, key=lambda x: x[1]):
            viz.append(f"  • {category}: {deviation:.1f}h")
        viz.append("")

    # Accuracy
    accuracy_items = []
    for category, planned, actual, deviation in deviations:
        if planned > 0:
            accuracy = (1 - abs(deviation) / planned) * 100
            accuracy_items.append((category, accuracy))

    if accuracy_items:
        avg_accuracy = sum(a for c, a in accuracy_items) / len(accuracy_items)
        viz.append(f"**Planning Accuracy:** {avg_accuracy:.1f}%")
        viz.append("")

        best = max(accuracy_items, key=lambda x: x[1])
        worst = min(accuracy_items, key=lambda x: x[1])
        viz.append(f"  Best:  {best[0]} ({best[1]:.1f}% accurate)")
        viz.append(f"  Worst: {worst[0]} ({worst[1]:.1f}% accurate)")
        viz.append("")

    return '\n'.join(viz)

def main():
    parser = argparse.ArgumentParser(description='Analyze Stay In Session time tracking data')
    parser.add_argument('data_file', type=Path, help='CSV or JSON export from Stay In Session')
    parser.add_argument('--planned', type=str, help='Planned allocation (text format)')
    parser.add_argument('--output', type=Path, help='Output file for analysis (default: stdout)')

    args = parser.parse_args()

    # Load actual time data
    if args.data_file.suffix == '.csv':
        sessions = load_csv_export(args.data_file)
    elif args.data_file.suffix == '.json':
        sessions = load_json_export(args.data_file)
    else:
        print(f"Error: Unsupported file format {args.data_file.suffix}")
        return 1

    actual = categorize_sessions(sessions)

    # Load planned allocation
    if args.planned:
        planned = parse_planned_allocation(args.planned)
    else:
        # Default example
        planned = {
            "Job Applications": 8.0,
            "Job Board MVP": 8.0,
            "BlueDot Research": 4.0
        }

    # Calculate deviations
    deviations = calculate_deviations(planned, actual)

    # Generate visualization
    viz = generate_visualization(deviations)

    # Output
    if args.output:
        with open(args.output, 'w') as f:
            f.write(viz)
        print(f"Analysis written to {args.output}")
    else:
        print(viz)

    return 0

if __name__ == '__main__':
    exit(main())
