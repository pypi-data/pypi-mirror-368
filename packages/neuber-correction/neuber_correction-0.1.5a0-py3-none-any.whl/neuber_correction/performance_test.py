"""
Performance tests for the NeuberCorrection class.

This module provides comprehensive performance benchmarking for the Neuber correction
functionality, including timing comparisons with and without memoization.
"""

import gc
import random
import sys
import time

from neuber_correction import (
    MaterialForNeuberCorrection,
    NeuberCorrection,
    NeuberSolverSettings,
)


def format_time(seconds: float) -> str:
    """Format time in seconds to a human-readable string."""
    if seconds < 1e-6:
        return f"{seconds * 1e9:.2f} ns"
    if seconds < 1e-3:
        return f"{seconds * 1e6:.2f} μs"
    if seconds < 1:
        return f"{seconds * 1e3:.2f} ms"
    return f"{seconds:.3f} s"


def get_memory_usage():
    """Get current memory usage information."""

    gc.collect()  # Force garbage collection

    # Count instances
    instance_count = len(NeuberCorrection.instances)
    total_cache_entries = sum(
        len(instance.memoization_table)
        for instance in NeuberCorrection.instances.values()
    )

    return {
        "instance_count": instance_count,
        "total_cache_entries": total_cache_entries,
    }


def benchmark_memoization_effectiveness():
    """Benchmark the effectiveness of memoization with clear isolation."""
    # Clear all existing instances to ensure clean state
    NeuberCorrection.clear_all_instances()

    # Check initial memory state
    initial_memory = get_memory_usage()

    print("NEUBER CORRECTION MEMOIZATION BENCHMARK")
    print("=" * 60)
    print(
        f"Initial state: {initial_memory['instance_count']} instances, "
        f"{initial_memory['total_cache_entries']} cache entries"
    )
    print()

    # Create test material (S355 steel)
    material = MaterialForNeuberCorrection(
        yield_strength=315,
        sigma_u=470,
        elastic_mod=210000,
        eps_u=0.12,
    )

    # Test stress values
    stress_values = [400, 500, 600, 700, 800, 900, 1000]

    print("Material: S355 Steel")
    print(f"Test stresses: {stress_values}")
    print()

    # Test 1: No memoization (very high precision)
    print("TEST 1: No Memoization (Precision = 1e-12)")
    print("-" * 40)

    settings_no_memo = NeuberSolverSettings(memoization_precision=1e-12)
    neuber_no_memo = NeuberCorrection(material=material, settings=settings_no_memo)

    # First run - all calculations
    start_time = time.perf_counter()
    for stress in stress_values:
        neuber_no_memo.correct_stress_values([stress])
    first_run_time = time.perf_counter() - start_time

    # Second run - should recalculate everything
    start_time = time.perf_counter()
    for stress in stress_values:
        neuber_no_memo.correct_stress_values([stress])
    second_run_time = time.perf_counter() - start_time

    print(f"First run:  {format_time(first_run_time)}")
    print(f"Second run: {format_time(second_run_time)}")
    print(f"Cache entries: {len(neuber_no_memo.memoization_table)}")
    print()

    # Test 2: With memoization (realistic precision)
    print("TEST 2: With Memoization (Precision = 0.1 MPa)")
    print("-" * 40)

    settings_with_memo = NeuberSolverSettings(memoization_precision=0.1)
    neuber_with_memo = NeuberCorrection(material=material, settings=settings_with_memo)

    # First run - all calculations
    start_time = time.perf_counter()
    for stress in stress_values:
        neuber_with_memo.correct_stress_values([stress])
    first_run_time = time.perf_counter() - start_time

    # Second run - should use cache
    start_time = time.perf_counter()
    for stress in stress_values:
        neuber_with_memo.correct_stress_values([stress])
    second_run_time = time.perf_counter() - start_time

    print(f"First run:  {format_time(first_run_time)}")
    print(f"Second run: {format_time(second_run_time)}")
    print(f"Cache entries: {len(neuber_with_memo.memoization_table)}")
    print(f"Speedup: {first_run_time / second_run_time:.2f}x")
    print()

    # Test 3: Precision-based cache hits
    print("TEST 3: Precision-Based Cache Hits")
    print("-" * 40)

    settings_precision = NeuberSolverSettings(
        memoization_precision=1.0
    )  # 1 MPa precision
    neuber_precision = NeuberCorrection(material=material, settings=settings_precision)

    # Calculate for stress 500
    start_time = time.perf_counter()
    result1 = neuber_precision.correct_stress_values([500])[0]
    time1 = time.perf_counter() - start_time

    # Calculate for stress 500.5 (within 1 MPa precision)
    start_time = time.perf_counter()
    result2 = neuber_precision.correct_stress_values([500.5])[0]
    time2 = time.perf_counter() - start_time

    # Calculate for stress 502 (outside 1 MPa precision)
    start_time = time.perf_counter()
    result3 = neuber_precision.correct_stress_values([502])[0]
    time3 = time.perf_counter() - start_time

    print(f"Stress 500.0: {format_time(time1)} -> {result1:.2f} MPa")
    print(
        f"Stress 500.5: {format_time(time2)} -> {result2:.2f} MPa (cache hit: {result1 == result2})"
    )
    print(
        f"Stress 502.0: {format_time(time3)} -> {result3:.2f} MPa (cache hit: {result1 == result3})"
    )
    print(f"Cache entries: {len(neuber_precision.memoization_table)}")
    print()

    # Test 4: Large dataset performance
    print("TEST 4: Large Dataset Performance")
    print("-" * 40)

    # Generate 1000 stress values with many duplicates
    random.seed(42)  # For reproducible results

    # Create a smaller set of unique values
    unique_stresses = [500 + i * 10 for i in range(5000)]  # 50 unique values

    large_stress_list = []
    for i in range(1000):
        # Pick from the unique values (many duplicates)
        large_stress_list.append(random.choice(unique_stresses))

    # Test without memoization (very high precision = no cache hits)
    settings_large_no_memo = NeuberSolverSettings(memoization_precision=1e-12)
    neuber_large_no_memo = NeuberCorrection(
        material=material, settings=settings_large_no_memo
    )

    start_time = time.perf_counter()
    results_no_memo = neuber_large_no_memo.correct_stress_values(large_stress_list)
    time_no_memo = time.perf_counter() - start_time

    # Test with memoization (same precision, will benefit from duplicates)
    settings_large_with_memo = NeuberSolverSettings(
        memoization_precision=1e-12
    )  # Same precision
    neuber_large_with_memo = NeuberCorrection(
        material=material, settings=settings_large_with_memo
    )

    start_time = time.perf_counter()
    results_with_memo = neuber_large_with_memo.correct_stress_values(large_stress_list)
    time_with_memo = time.perf_counter() - start_time

    print(f"Dataset size: {len(large_stress_list)} stress values")
    print(f"Without memoization: {format_time(time_no_memo)}")
    print(f"With memoization:    {format_time(time_with_memo)}")
    print(f"Speedup: {time_no_memo / time_with_memo:.2f}x")
    print(f"Cache entries: {len(neuber_large_with_memo.memoization_table)}")
    print(
        f"Results identical: {all(abs(a - b) < 1e-10 for a, b in zip(results_no_memo, results_with_memo))}"
    )
    print(
        "Max difference: ",
        max(abs(a - b) for a, b in zip(results_no_memo, results_with_memo)),
    )

    # Test 5: Memory efficiency
    print("TEST 5: Memory Efficiency")
    print("-" * 40)

    # Test with different cache sizes
    cache_sizes = [100, 500, 1000, 2000]

    for size in cache_sizes:
        settings_memory = NeuberSolverSettings(memoization_precision=0.1)
        neuber_memory = NeuberCorrection(material=material, settings=settings_memory)

        # Generate stress values
        stress_values_memory = [200 + i * 0.1 for i in range(size)]

        # Calculate all values
        for stress in stress_values_memory:
            neuber_memory.correct_stress_values([stress])

        cache_size = len(neuber_memory.memoization_table)
        memory_usage = sys.getsizeof(neuber_memory.memoization_table)

        print(
            f"Cache size {size:4d}: {cache_size:4d} entries, {memory_usage:6d} bytes "
            f"({memory_usage/cache_size:.1f} bytes/entry)"
        )

    print()

    # Check final memory state
    final_memory = get_memory_usage()
    print("=" * 60)
    print("BENCHMARK COMPLETE")
    print("=" * 60)
    print(
        f"Final state: {final_memory['instance_count']} instances, "
        f"{final_memory['total_cache_entries']} cache entries"
    )
    print(
        f"Memory growth: {final_memory['instance_count'] - initial_memory['instance_count']} instances, "
        f"{final_memory['total_cache_entries'] - initial_memory['total_cache_entries']} cache entries"
    )


if __name__ == "__main__":
    benchmark_memoization_effectiveness()
