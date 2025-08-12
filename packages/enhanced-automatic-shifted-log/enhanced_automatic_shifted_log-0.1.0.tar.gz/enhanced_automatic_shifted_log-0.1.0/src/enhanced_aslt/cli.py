#!/usr/bin/env python
"""
Command Line Interface for Enhanced Automatic Shifted Log Transformer

This module provides command-line tools for benchmarking and validation.

Author: Muhammad Akmal Husain
Email: akmalhusain2003@gmail.com
"""

import argparse
import sys
import time
import numpy as np
import pandas as pd
from pathlib import Path

try:
    from .enhanced_aslt import AutomaticShiftedLogTransformer
    from . import check_dependencies
except ImportError:
    # Fallback for direct execution
    from enhanced_aslt import AutomaticShiftedLogTransformer
    from __init__ import check_dependencies


def benchmark_command():
    """Command-line benchmark tool."""
    parser = argparse.ArgumentParser(
        description="Benchmark Enhanced Automatic Shifted Log Transformer"
    )
    parser.add_argument(
        "--samples", "-n", type=int, default=1000,
        help="Number of samples to generate (default: 1000)"
    )
    parser.add_argument(
        "--features", "-f", type=int, default=3,
        help="Number of features to generate (default: 3)"
    )
    parser.add_argument(
        "--mc-iterations", "-m", type=int, default=1000,
        help="Monte Carlo iterations (default: 1000)"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    print(f"Enhanced ASLT Benchmark")
    print(f"Samples: {args.samples}, Features: {args.features}")
    print(f"Monte Carlo iterations: {args.mc_iterations}")
    print("-" * 50)
    
    # Generate test data
    np.random.seed(42)
    data = pd.DataFrame()
    
    for i in range(args.features):
        if i % 3 == 0:
            # Exponential (skewed)
            data[f'feature_{i}'] = np.random.exponential(2, args.samples)
        elif i % 3 == 1:
            # Normal
            data[f'feature_{i}'] = np.random.normal(0, 1, args.samples)
        else:
            # Pareto (heavy-tailed)
            data[f'feature_{i}'] = np.random.pareto(1.5, args.samples)
    
    # Create transformer
    transformer = AutomaticShiftedLogTransformer(
        mc_iterations=args.mc_iterations,
        random_state=42
    )
    
    # Benchmark fit
    print("Fitting transformer...")
    start_time = time.time()
    transformer.fit(data)
    fit_time = time.time() - start_time
    
    # Benchmark transform
    print("Transforming data...")
    start_time = time.time()
    transformed = transformer.transform(data)
    transform_time = time.time() - start_time
    
    # Benchmark inverse transform
    print("Inverse transforming...")
    start_time = time.time()
    reconstructed = transformer.inverse_transform(transformed)
    inverse_time = time.time() - start_time
    
    # Results
    print(f"\nBenchmark Results:")
    print(f"Fit time: {fit_time:.3f}s ({fit_time*1000/args.samples:.2f}ms per sample)")
    print(f"Transform time: {transform_time:.3f}s")
    print(f"Inverse transform time: {inverse_time:.3f}s")
    print(f"Total time: {fit_time + transform_time + inverse_time:.3f}s")
    
    if args.verbose:
        # Show transformation summary
        summary = transformer.get_transformation_summary()
        print(f"\nTransformation Summary:")
        for feature, info in summary.items():
            print(f"  {feature}:")
            print(f"    Complexity: {info['complexity']}")
            print(f"    Transformed: {info['transformed']}")
            if 'optimal_weights' in info:
                weights = info['optimal_weights']
                print(f"    Optimal weights: N={weights['normality']:.3f}, "
                      f"S={weights['skewness']:.3f}, K={weights['kurtosis']:.3f}, "
                      f"T={weights['stability']:.3f}")
        
        # Quality evaluation
        quality = transformer.evaluate_transformation_quality(data)
        print(f"\nQuality Results:")
        for feature, results in quality.items():
            if 'improvement' in results:
                print(f"  {feature}: {results['improvement']:.4f} improvement, "
                      f"Success: {results['is_successful']}")


def validate_command():
    """Command-line validation tool."""
    parser = argparse.ArgumentParser(
        description="Validate Enhanced Automatic Shifted Log Transformer installation"
    )
    parser.add_argument(
        "--quick", "-q", action="store_true",
        help="Quick validation (skip performance tests)"
    )
    
    args = parser.parse_args()
    
    print("Enhanced ASLT Installation Validation")
    print("=" * 50)
    
    # Check dependencies
    print("Checking dependencies...")
    deps = check_dependencies()
    
    all_ok = True
    for name, info in deps.items():
        status = "✓" if info['status'] == 'OK' else "✗"
        version = f"v{info['version']}" if info['version'] else "MISSING"
        print(f"  {status} {name}: {version}")
        if info['status'] != 'OK':
            all_ok = False
    
    if not all_ok:
        print("\nSome dependencies are missing. Please install them:")
        print("pip install numpy pandas scikit-learn scipy numba")
        return 1
    
    print("\nAll dependencies OK")
    
    # Basic functionality test
    print("\nTesting basic functionality...")
    try:
        # Create test data
        np.random.seed(42)
        test_data = pd.DataFrame({
            'col1': np.random.exponential(2, 100),
            'col2': np.random.normal(0, 1, 100)
        })
        
        # Test transformer
        transformer = AutomaticShiftedLogTransformer(
            mc_iterations=100,  # Reduced for quick testing
            random_state=42
        )
        
        # Test fit
        transformer.fit(test_data)
        print("Fit successful")
        
        # Test transform
        transformed = transformer.transform(test_data)
        print("Transform successful")
        
        # Test inverse transform
        reconstructed = transformer.inverse_transform(transformed)
        print("Inverse transform successful")
        
        # Test summary
        summary = transformer.get_transformation_summary()
        print("Summary generation successful")
        
        # Test quality evaluation
        quality = transformer.evaluate_transformation_quality(test_data)
        print("Quality evaluation successful")
        
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    if not args.quick:
        # Performance test
        print("\nPerformance test...")
        try:
            large_data = pd.DataFrame({
                'col1': np.random.exponential(2, 1000),
                'col2': np.random.normal(0, 1, 1000),
                'col3': np.random.pareto(1.5, 1000)
            })
            
            start_time = time.time()
            transformer.fit(large_data)
            fit_time = time.time() - start_time
            
            start_time = time.time()
            _ = transformer.transform(large_data)
            transform_time = time.time() - start_time
            
            print(f"  ✓ Performance test completed")
            print(f"    Fit time: {fit_time:.3f}s")
            print(f"    Transform time: {transform_time:.3f}s")
            
        except Exception as e:
            print(f"  ⚠ Performance test warning: {e}")
    
    print("\n Validation completed successfully!")
    print("Enhanced ASLT is ready to use.")
    return 0


def main():
    """Main CLI entry point."""
    if len(sys.argv) < 2:
        print("Enhanced Automatic Shifted Log Transformer CLI")
        print("Available commands:")
        print("  aslt-benchmark - Run performance benchmarks")
        print("  aslt-validate  - Validate installation")
        return 1
    
    command = sys.argv[1]
    sys.argv = sys.argv[1:]  # Remove script name for argparse
    
    if command == "benchmark":
        return benchmark_command()
    elif command == "validate":
        return validate_command()
    else:
        print(f"Unknown command: {command}")
        return 1


if __name__ == "__main__":
    sys.exit(main())