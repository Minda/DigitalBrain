#!/usr/bin/env python3
"""
Get email statistics and calculate sample size for classification.

⚠️ PRIVACY: Results will be stored in personal/data/email-classifier/
"""

import math
from datetime import datetime


def calculate_sample_size(population_size, confidence_level=0.95, margin_of_error=0.05):
    """
    Calculate the required sample size for statistical validity.

    Args:
        population_size: Total number of emails
        confidence_level: Desired confidence level (default 95%)
        margin_of_error: Acceptable margin of error (default 5%)

    Returns:
        Required sample size
    """
    # Z-scores for common confidence levels
    z_scores = {
        0.90: 1.645,
        0.95: 1.96,
        0.99: 2.576
    }

    z = z_scores.get(confidence_level, 1.96)

    # Assume maximum variability (p = 0.5) for conservative estimate
    p = 0.5

    # Calculate sample size for infinite population
    n0 = (z**2 * p * (1 - p)) / (margin_of_error**2)

    # Adjust for finite population
    n = n0 / (1 + ((n0 - 1) / population_size))

    return math.ceil(n)


def get_sampling_strategy(total_emails):
    """
    Determine the appropriate sampling strategy based on email count.

    Args:
        total_emails: Total number of emails in account

    Returns:
        Dictionary with sampling details
    """
    sample_size = calculate_sample_size(total_emails)

    # Determine sampling approach
    if total_emails < 1000:
        strategy = "small_population"
        recommendation = f"Process {sample_size} emails (~{sample_size/total_emails*100:.1f}% of total)"
    elif total_emails < 10000:
        strategy = "medium_population"
        recommendation = f"Process {sample_size} emails (~{sample_size/total_emails*100:.1f}% of total)"
    else:
        strategy = "large_population"
        # For very large populations, sample size plateaus around 385-400
        recommendation = f"Process {sample_size} emails (~{sample_size/total_emails*100:.2f}% of total)"

    return {
        "total_emails": total_emails,
        "required_sample_size": sample_size,
        "confidence_level": "95%",
        "margin_of_error": "5%",
        "strategy": strategy,
        "recommendation": recommendation,
        "percentage_to_sample": round(sample_size / total_emails * 100, 2)
    }


def format_statistics(stats):
    """
    Format statistics for display.

    Args:
        stats: Statistics dictionary

    Returns:
        Formatted string
    """
    output = [
        "\n" + "="*60,
        "📊 EMAIL SAMPLING STATISTICS",
        "="*60,
        f"Total emails in account: {stats['total_emails']:,}",
        f"Required sample size: {stats['required_sample_size']:,}",
        f"Confidence level: {stats['confidence_level']}",
        f"Margin of error: ±{stats['margin_of_error']}",
        "",
        f"📌 Recommendation: {stats['recommendation']}",
        "",
        "This sample size ensures that our classification results",
        "will be statistically representative of your entire inbox.",
        "="*60
    ]

    return "\n".join(output)


# Example usage (will be called with actual Gmail data)
if __name__ == "__main__":
    # Test with different email counts
    test_counts = [500, 2000, 8543, 25000, 100000]

    print("\nSample Size Calculations for Different Email Counts:")
    print("-" * 60)

    for count in test_counts:
        stats = get_sampling_strategy(count)
        print(f"{count:,} emails → sample {stats['required_sample_size']:,} "
              f"({stats['percentage_to_sample']:.2f}%)")

    print("\n" + "-" * 60)
    print("Ready to process actual Gmail data...")