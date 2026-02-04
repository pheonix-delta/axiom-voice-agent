#!/usr/bin/env python3
"""
AXIOM - Real-time Resource Monitoring & Performance Metrics
Tracks CPU, GPU, Memory, and Latency during inference
"""

import psutil
import threading
import time
import json
from datetime import datetime
from pathlib import Path
import numpy as np

class ResourceMonitor:
    def __init__(self, output_file="benchmarks/runtime_metrics.json"):
        self.output_file = Path(output_file)
        self.metrics = {
            "timestamp": datetime.now().isoformat(),
            "system": self._get_system_info(),
            "observations": []
        }
        self.running = False
        self.process = psutil.Process()
        
    def _get_system_info(self):
        """Capture system specifications"""
        return {
            "cpu_count": psutil.cpu_count(),
            "cpu_freq_ghz": psutil.cpu_freq().current / 1000,
            "memory_gb": psutil.virtual_memory().total / (1024**3),
            "gpu": self._get_gpu_info(),
            "os": f"{psutil.uname().system} {psutil.uname().release}",
            "python_version": __import__('sys').version.split()[0]
        }
    
    def _get_gpu_info(self):
        """Try to get GPU info"""
        try:
            import subprocess
            result = subprocess.run(['nvidia-smi', '--query-gpu=name,memory.total', '--format=csv,noheader'],
                                   capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                line = result.stdout.strip().split(',')
                return {
                    "model": line[0].strip() if len(line) > 0 else "N/A",
                    "memory_mb": int(''.join(filter(str.isdigit, line[1]))) if len(line) > 1 else 0
                }
        except:
            pass
        return {"model": "None", "memory_mb": 0}
    
    def record_snapshot(self, phase_name="unknown"):
        """Record a single resource snapshot"""
        try:
            cpu_percent = self.process.cpu_percent(interval=0.1)
            memory_info = self.process.memory_info()
            
            snapshot = {
                "timestamp": datetime.now().isoformat(),
                "phase": phase_name,
                "cpu_percent": cpu_percent,
                "memory_mb": memory_info.rss / (1024**2),
                "threads": threading.active_count()
            }
            
            # Try to get GPU metrics
            try:
                import subprocess
                result = subprocess.run(['nvidia-smi', '--query-processes=used_memory', '--format=csv,noheader'],
                                       capture_output=True, text=True, timeout=2)
                if result.returncode == 0 and result.stdout.strip():
                    gpu_mem = sum(int(line.split()[0]) for line in result.stdout.strip().split('\n') if line.strip())
                    snapshot["gpu_memory_mb"] = gpu_mem
            except:
                snapshot["gpu_memory_mb"] = 0
            
            self.metrics["observations"].append(snapshot)
            return snapshot
        except Exception as e:
            print(f"Error recording snapshot: {e}")
            return None
    
    def save_metrics(self):
        """Save collected metrics to file"""
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.output_file, 'w') as f:
            json.dump(self.metrics, f, indent=2)
        print(f"✓ Metrics saved to {self.output_file}")
    
    def print_summary(self):
        """Print summary statistics"""
        if not self.metrics["observations"]:
            return
        
        observations = self.metrics["observations"]
        cpu_values = [o["cpu_percent"] for o in observations]
        mem_values = [o["memory_mb"] for o in observations]
        gpu_values = [o.get("gpu_memory_mb", 0) for o in observations if "gpu_memory_mb" in o]
        
        print("\n" + "="*60)
        print("RESOURCE METRICS SUMMARY")
        print("="*60)
        print(f"Total Observations: {len(observations)}")
        print(f"\nCPU Usage:")
        print(f"  Average: {np.mean(cpu_values):.2f}%")
        print(f"  Max:     {np.max(cpu_values):.2f}%")
        print(f"  Min:     {np.min(cpu_values):.2f}%")
        print(f"\nMemory Usage (MB):")
        print(f"  Average: {np.mean(mem_values):.2f}")
        print(f"  Peak:    {np.max(mem_values):.2f}")
        print(f"  Min:     {np.min(mem_values):.2f}")
        if gpu_values:
            print(f"\nGPU Memory Usage (MB):")
            print(f"  Average: {np.mean(gpu_values):.2f}")
            print(f"  Peak:    {np.max(gpu_values):.2f}")
        print("="*60 + "\n")


if __name__ == "__main__":
    import time
    
    # Example usage
    monitor = ResourceMonitor()
    
    print("Starting resource monitoring...")
    print(f"System: {monitor.metrics['system']}")
    
    # Simulate monitoring over time
    for i in range(10):
        monitor.record_snapshot(f"iteration_{i}")
        time.sleep(0.5)
    
    monitor.save_metrics()
    monitor.print_summary()
