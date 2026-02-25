"""
Interactive console UI for exploring Zipf distributions.

This script is designed for non-technical users who want to quickly
provide Zipf parameters and generate plots without editing code.

Usage examples:
  python RS_vs/zipf_console_ui.py
  python RS_vs/zipf_console_ui.py --s 1.4 --n 500 --plot both
"""

from __future__ import annotations

import argparse
import os
from datetime import datetime
from typing import List, Tuple

import matplotlib.pyplot as plt

import zipf_utils


def parse_s_values(s_text: str) -> List[float]:
    """Parse comma-separated Zipf exponents into a list of floats."""
    values: List[float] = []
    raw_parts = s_text.split(",")
    for raw_part in raw_parts:
        cleaned = raw_part.strip()
        if cleaned == "":
            continue
        values.append(float(cleaned))
    return values


def ask_string(prompt_text: str, default_value: str) -> str:
    """Prompt for a string, falling back to a default if user presses Enter."""
    entered = input(f"{prompt_text} [{default_value}]: ").strip()
    if entered == "":
        return default_value
    return entered


def ask_int(prompt_text: str, default_value: int, minimum: int = 1) -> int:
    """Prompt for an integer with basic validation and retry loop."""
    while True:
        entered = input(f"{prompt_text} [{default_value}]: ").strip()
        if entered == "":
            return default_value
        try:
            parsed = int(entered)
        except ValueError:
            print("Please enter a valid integer.")
            continue
        if parsed < minimum:
            print(f"Please enter a value >= {minimum}.")
            continue
        return parsed


def ask_float_list(prompt_text: str, default_value: str) -> List[float]:
    """Prompt for one or more comma-separated float values."""
    while True:
        entered = input(f"{prompt_text} [{default_value}]: ").strip()
        if entered == "":
            entered = default_value
        try:
            values = parse_s_values(entered)
        except ValueError:
            print("Please enter comma-separated numeric values, e.g. 1.0,1.4,2.0")
            continue
        if len(values) == 0:
            print("Please provide at least one s value.")
            continue
        return values


def ensure_out_dir(out_dir: str) -> str:
    """Create output directory if needed and return the absolute path."""
    os.makedirs(out_dir, exist_ok=True)
    return os.path.abspath(out_dir)


def compute_rank_and_cdf(probabilities: List[float]) -> Tuple[List[int], List[float]]:
    """Build rank axis and cumulative probability values for plotting."""
    ranks: List[int] = []
    cdf_values: List[float] = []
    cumulative = 0.0

    index = 0
    while index < len(probabilities):
        rank = index + 1
        probability = probabilities[index]
        cumulative = cumulative + probability
        ranks.append(rank)
        cdf_values.append(cumulative)
        index = index + 1

    return ranks, cdf_values


def plot_zipf_curves(
    s_values: List[float],
    pool_size: int,
    plot_type: str,
    output_directory: str,
    title_suffix: str,
) -> List[str]:
    """Generate PMF/CDF plots for one or more Zipf exponents."""
    saved_paths: List[str] = []
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    if plot_type in ("pmf", "both"):
        plt.figure(figsize=(10, 6))
        for exponent_s in s_values:
            pmf_array = zipf_utils.zipf_pmf(pool_size, exponent_s)
            pmf_values: List[float] = []
            for value in pmf_array:
                pmf_values.append(float(value))
            ranks = list(range(1, pool_size + 1))
            plt.plot(ranks, pmf_values, label=f"s={exponent_s}")

        plt.xscale("log")
        plt.yscale("log")
        plt.xlabel("Rank (log scale)")
        plt.ylabel("Probability (log scale)")
        plt.title(f"Zipf PMF by rank {title_suffix}")
        plt.grid(True, linestyle="--", alpha=0.4)
        plt.legend()
        plt.tight_layout()

        pmf_filename = f"zipf_pmf_{timestamp}.png"
        pmf_path = os.path.join(output_directory, pmf_filename)
        plt.savefig(pmf_path, dpi=180)
        plt.close()
        saved_paths.append(pmf_path)

    if plot_type in ("cdf", "both"):
        plt.figure(figsize=(10, 6))
        for exponent_s in s_values:
            pmf_array = zipf_utils.zipf_pmf(pool_size, exponent_s)
            pmf_values: List[float] = []
            for value in pmf_array:
                pmf_values.append(float(value))
            ranks, cdf_values = compute_rank_and_cdf(pmf_values)
            plt.plot(ranks, cdf_values, label=f"s={exponent_s}")

        plt.xscale("log")
        plt.xlabel("Rank (log scale)")
        plt.ylabel("CDF")
        plt.title(f"Zipf CDF by rank {title_suffix}")
        plt.grid(True, linestyle="--", alpha=0.4)
        plt.legend()
        plt.tight_layout()

        cdf_filename = f"zipf_cdf_{timestamp}.png"
        cdf_path = os.path.join(output_directory, cdf_filename)
        plt.savefig(cdf_path, dpi=180)
        plt.close()
        saved_paths.append(cdf_path)

    return saved_paths


def print_entropy_table(s_values: List[float], pool_size: int) -> None:
    """Print Shannon entropy for each chosen s value."""
    print("\nEntropy summary (bits):")
    print("-----------------------")
    for exponent_s in s_values:
        entropy_bits = zipf_utils.zipf_entropy_bits(pool_size, exponent_s)
        print(f"s={exponent_s:<6} H={entropy_bits:.6f}")


def build_parser() -> argparse.ArgumentParser:
    """Build command-line parser for optional non-interactive runs."""
    parser = argparse.ArgumentParser(description="Interactive Zipf graph console.")
    parser.add_argument("--s", type=str, default=None, help="Comma-separated s values, e.g. 1.0,1.4,2.0")
    parser.add_argument("--n", type=int, default=None, help="Pool size / number of ranks (n)")
    parser.add_argument("--plot", choices=["pmf", "cdf", "both"], default=None, help="Plot type")
    parser.add_argument("--out-dir", type=str, default=None, help="Output directory for saved plots")
    parser.add_argument("--title-suffix", type=str, default="", help="Optional suffix appended to plot titles")
    parser.add_argument("--no-prompt", action="store_true", help="Require all args; do not prompt interactively")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    # Defaults are intentionally simple for first-time users.
    default_s_text = "1.0,1.4,2.0"
    default_n = 1000
    default_plot_type = "both"
    default_out_dir = os.path.join("RS_vs", "Reports", "zipf_console")

    if args.no_prompt:
        if args.s is None or args.n is None or args.plot is None:
            raise ValueError("With --no-prompt you must pass --s, --n, and --plot")

    if args.s is None and not args.no_prompt:
        s_values = ask_float_list("Enter Zipf s values (comma-separated)", default_s_text)
    else:
        s_input_text = default_s_text if args.s is None else args.s
        s_values = parse_s_values(s_input_text)

    if args.n is None and not args.no_prompt:
        pool_size = ask_int("Enter n (pool size / number of ranks)", default_n, minimum=2)
    else:
        if args.n is None:
            pool_size = default_n
        else:
            pool_size = args.n

    if args.plot is None and not args.no_prompt:
        plot_type = ask_string("Choose plot type: pmf, cdf, or both", default_plot_type)
    else:
        plot_type = default_plot_type if args.plot is None else args.plot

    if plot_type not in ("pmf", "cdf", "both"):
        raise ValueError("plot type must be one of: pmf, cdf, both")

    if args.out_dir is None and not args.no_prompt:
        output_directory_text = ask_string("Output directory", default_out_dir)
    else:
        output_directory_text = default_out_dir if args.out_dir is None else args.out_dir

    output_directory = ensure_out_dir(output_directory_text)

    print("\nGenerating plots...")
    print(f"  s values: {s_values}")
    print(f"  n (pool size): {pool_size}")
    print(f"  plot type: {plot_type}")
    print(f"  output directory: {output_directory}")

    saved_paths = plot_zipf_curves(
        s_values=s_values,
        pool_size=pool_size,
        plot_type=plot_type,
        output_directory=output_directory,
        title_suffix=args.title_suffix,
    )

    print_entropy_table(s_values, pool_size)

    print("\nSaved files:")
    for saved_path in saved_paths:
        print(f"  - {saved_path}")


if __name__ == "__main__":
    main()
