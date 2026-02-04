#!/usr/bin/env python3
"""
AXIOM - Latency Benchmark Suite
Measures inference time for each component
"""

import time
import json
from pathlib import Path
from datetime import datetime
import numpy as np

class LatencyBenchmark:
    """Benchmark latency of individual components"""
    
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "benchmarks": {}
        }
    
    def benchmark_vad(self, audio_chunk_size=512, iterations=100):
        """Benchmark VAD (Voice Activity Detection)"""
        print(f"\n[VAD] Benchmarking Silero VAD with {audio_chunk_size} samples x {iterations} iterations...")
        
        try:
            import numpy as np
            import onnxruntime as ort
            
            # Load VAD model
            providers = ['CUDAExecutionProvider', 'CPUExecutionProvider']
            sess = ort.InferenceSession('models/silero_vad.onnx', providers=providers)
            
            # Prepare audio
            audio = np.random.randn(audio_chunk_size).astype(np.float32)
            input_names = [inp.name for inp in sess.get_inputs()]
            input_name = None
            for candidate in ("input", "x", "input_1"):
                if candidate in input_names:
                    input_name = candidate
                    break
            if input_name is None and input_names:
                input_name = input_names[0]

            if input_name is None:
                raise RuntimeError("VAD model has no inputs")

            # Shape audio if model expects 2D
            audio_input = audio
            input_shape = sess.get_inputs()[input_names.index(input_name)].shape
            if len(input_shape) == 2:
                audio_input = audio.reshape(1, -1)

            # Optional state + sample rate inputs
            state_shape = (2, 1, 64)
            h_state = np.zeros(state_shape, dtype=np.float32)
            c_state = np.zeros(state_shape, dtype=np.float32)
            sr_value = np.array([16000], dtype=np.int64)

            def build_inputs(h_val, c_val):
                feed = {input_name: audio_input}
                if "h" in input_names:
                    feed["h"] = h_val
                if "c" in input_names:
                    feed["c"] = c_val
                if "sr" in input_names:
                    feed["sr"] = sr_value
                return feed

            # Warmup
            outputs = sess.run(None, build_inputs(h_state, c_state))
            if "h" in input_names and len(outputs) >= 2:
                h_state = outputs[-2]
            if "c" in input_names and len(outputs) >= 1:
                c_state = outputs[-1]
            
            # Benchmark
            times = []
            for _ in range(iterations):
                start = time.perf_counter()
                outputs = sess.run(None, build_inputs(h_state, c_state))
                if "h" in input_names and len(outputs) >= 2:
                    h_state = outputs[-2]
                if "c" in input_names and len(outputs) >= 1:
                    c_state = outputs[-1]
                times.append((time.perf_counter() - start) * 1000)  # ms
            
            result = {
                "model": "Silero VAD",
                "audio_chunk_ms": (audio_chunk_size / 16000) * 1000,  # Assuming 16kHz
                "iterations": iterations,
                "latency_ms": {
                    "mean": float(np.mean(times)),
                    "median": float(np.median(times)),
                    "p95": float(np.percentile(times, 95)),
                    "p99": float(np.percentile(times, 99)),
                    "min": float(np.min(times)),
                    "max": float(np.max(times))
                }
            }
            
            self.results["benchmarks"]["vad"] = result
            print(f"  Mean: {result['latency_ms']['mean']:.2f}ms")
            print(f"  P95:  {result['latency_ms']['p95']:.2f}ms")
            
        except Exception as e:
            print(f"  ERROR: {e}")
    
    def benchmark_intent_classifier(self, iterations=100):
        """Benchmark Intent Classification (SetFit)"""
        print(f"\n[Intent] Benchmarking SetFit with {iterations} iterations...")
        
        try:
            from setfit import SetFitModel
            import numpy as np
            
            # Load model
            model = SetFitModel.from_pretrained(
                'models/intent_model/setfit_intent_classifier',
                local_files_only=True
            )
            
            test_texts = [
                "Tell me about the robot dog",
                "What projects can I build",
                "How does the lab work",
                "Show me equipment",
                "What's in inventory"
            ]
            
            # Warmup
            model.predict(test_texts[0])
            
            # Benchmark
            times = []
            for _ in range(iterations):
                text = test_texts[_ % len(test_texts)]
                start = time.perf_counter()
                model.predict(text)
                times.append((time.perf_counter() - start) * 1000)  # ms
            
            result = {
                "model": "SetFit Intent Classifier",
                "iterations": iterations,
                "latency_ms": {
                    "mean": float(np.mean(times)),
                    "median": float(np.median(times)),
                    "p95": float(np.percentile(times, 95)),
                    "min": float(np.min(times)),
                    "max": float(np.max(times))
                }
            }
            
            self.results["benchmarks"]["intent"] = result
            print(f"  Mean: {result['latency_ms']['mean']:.2f}ms")
            print(f"  P95:  {result['latency_ms']['p95']:.2f}ms")
            
        except Exception as e:
            print(f"  ERROR: {e}")
    
    def benchmark_template_lookup(self, iterations=1000):
        """Benchmark Template Database Lookup"""
        print(f"\n[Template] Benchmarking template lookup with {iterations} iterations...")
        
        try:
            import json
            
            # Load template database
            with open('data/template_database.json', 'r') as f:
                templates = json.load(f)
            if isinstance(templates, dict):
                templates = list(templates.values())
            if not templates:
                raise ValueError("Template database is empty")
            
            # Benchmark
            times_us = []
            for i in range(iterations):
                start = time.perf_counter_ns()
                # Simulate lookup
                _ = templates[i % len(templates)]
                elapsed_us = (time.perf_counter_ns() - start) / 1000
                times_us.append(elapsed_us)

            mean_us = float(np.mean(times_us))
            median_us = float(np.median(times_us))
            p95_us = float(np.percentile(times_us, 95))
            min_us = float(np.min(times_us))
            max_us = float(np.max(times_us))
            
            result = {
                "model": "Template Database",
                "total_templates": len(templates),
                "iterations": iterations,
                "latency_us": {
                    "mean": mean_us,
                    "median": median_us,
                    "p95": p95_us,
                    "min": min_us,
                    "max": max_us
                },
                "latency_ms": {
                    "mean": mean_us / 1000,
                    "median": median_us / 1000,
                    "p95": p95_us / 1000,
                    "min": min_us / 1000,
                    "max": max_us / 1000
                }
            }
            
            self.results["benchmarks"]["template"] = result
            print(f"  Mean: {result['latency_us']['mean']:.2f}µs")
            print(f"  Queries/sec: {1_000_000 / result['latency_us']['mean']:.0f}")
            
        except Exception as e:
            print(f"  ERROR: {e}")
    
    def save_results(self):
        """Save benchmark results"""
        output_file = Path("benchmarks/latency_benchmarks.json")
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n✓ Results saved to {output_file}")
    
    def print_summary(self):
        """Print benchmark summary"""
        print("\n" + "="*70)
        print("LATENCY BENCHMARK SUMMARY")
        print("="*70)
        
        for benchmark_name, data in self.results["benchmarks"].items():
            print(f"\n{data['model']}:")
            print(f"  Mean Latency:   {data['latency_ms']['mean']:>8.2f} ms")
            print(f"  Median Latency: {data['latency_ms']['median']:>8.2f} ms")
            print(f"  P95 Latency:    {data['latency_ms']['p95']:>8.2f} ms")
            print(f"  Min/Max:        {data['latency_ms']['min']:>8.2f} / {data['latency_ms']['max']:>8.2f} ms")
        
        print("\n" + "="*70)


if __name__ == "__main__":
    benchmark = LatencyBenchmark()
    
    print("AXIOM Latency Benchmark Suite")
    print("="*70)
    
    # Run benchmarks
    try:
        benchmark.benchmark_vad()
    except Exception as e:
        print(f"VAD benchmark failed: {e}")
    
    try:
        benchmark.benchmark_intent_classifier()
    except Exception as e:
        print(f"Intent benchmark failed: {e}")
    
    try:
        benchmark.benchmark_template_lookup()
    except Exception as e:
        print(f"Template benchmark failed: {e}")
    
    benchmark.save_results()
    benchmark.print_summary()
