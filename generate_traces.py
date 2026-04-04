import json
import math
from pathlib import Path

def generate_sinusoidal_trace(task_name, difficulty, steps=50):
    steps_data = []
    for i in range(steps):
        # Smooth sinusoidal load curves for CPU/memory and latency.
        cpu_usage = 45.0 + 28.0 * math.sin(i / steps * 2.0 * math.pi)
        mem_usage = 48.0 + 18.0 * math.sin(i / steps * 2.0 * math.pi + 0.8)
        base_latency = 160.0 + 22.0 * math.sin(i / 12.0 * 2.0 * math.pi)

        if task_name == "cold_start":
            node_size = "S"
            if i < 5:
                active_replicas = 0
            elif i < 9:
                active_replicas = 1
            elif i < 13:
                active_replicas = 2
            elif i < 17:
                active_replicas = 3
            elif i < 21:
                active_replicas = 4
            else:
                active_replicas = 5

            base_error = 0.60 - 0.06 * min(i, 7)
            base_error = max(0.02, base_error)
            steal_pct = 0.01
            p99_latency = base_latency + max(0.0, 50.0 - i * 2.0)
            current_cost = 10.0 + active_replicas * 1.0
            reason = "cold_start_resource_buildout"

        elif task_name == "efficient_squeeze":
            active_replicas = 5
            node_size = "S"
            base_error = 0.02
            steal_pct = max(0.0, min(0.35, 0.18 + 0.08 * math.sin(i / 8.0 * 2.0 * math.pi)))
            p99_latency = base_latency + 18.0 * math.sin(i / 10.0 * 2.0 * math.pi)
            current_cost = 10.0 + active_replicas * 1.0
            reason = "squeeze_24h_cycle"

        else:  # entropy_storm
            active_replicas = 10
            node_size = "M"
            base_error = 0.01
            phase = i % 10
            if phase in (4, 5, 6):
                steal_pct = 0.24 + 0.04 * math.sin(i * 1.8)
            elif phase == 3:
                steal_pct = 0.20 + 0.03 * math.sin(i * 2.0)
            else:
                steal_pct = 0.12 + 0.05 * math.sin(i / 5.0 * 2.0 * math.pi)
            steal_pct = max(0.0, min(0.45, steal_pct))
            p99_latency = base_latency + 15.0 * math.sin(i / 7.0 * 2.0 * math.pi)
            current_cost = 25.0 + active_replicas * 1.0
            reason = "entropy_storm_noisy_neighbor"

        observation = {
            "base_cpu_demand": round(max(0.0, cpu_usage), 2),
            "base_mem_demand": round(max(0.0, mem_usage), 2),
            "base_latency_ms": round(max(40.0, p99_latency), 2),
            "base_error_rate": round(min(1.0, base_error), 4),
            "base_steal_pct": round(steal_pct, 4),
            "active_replicas": active_replicas,
            "buffer_depth": 80 + i * 3,
            "node_size_class": node_size,
            "current_hourly_cost": round(current_cost, 2),
            "node_bin_density": [round(max(0.0, min(1.0, 0.45 + 0.05 * math.sin((i + j) / 4.0))), 4) for j in range(10)]
        }

        steps_data.append({
            "step": i,
            "observation": observation,
            "dynamics": {"reason": reason}
        })

    return {
        "task_name": task_name,
        "task_difficulty": difficulty,
        "description": f"Programmatic {task_name} trace with {steps} steps (Sinusoidal CPU model).",
        "steps": steps_data
    }

def main():
    traces_dir = Path("traces")
    traces_dir.mkdir(exist_ok=True)

    # All 20 traces present in the directory
    trace_files = [
        ("cold_start", "easy", "trace_v1_coldstart.json"),
        ("entropy_storm", "hard", "trace_v1_entropy.json"),
        ("efficient_squeeze", "medium", "trace_v1_squeeze.json"),
        ("cold_start", "easy", "trace_v2_coldstart_gradual.json"),
        ("entropy_storm", "hard", "trace_v2_entropy_chaos.json"),
        ("efficient_squeeze", "medium", "trace_v2_squeeze_steady.json"),
        ("cold_start", "easy", "trace_v3_coldstart_aggressive.json"),
        ("entropy_storm", "hard", "trace_v3_entropy_cascading.json"),
        ("efficient_squeeze", "medium", "trace_v3_squeeze_oscillating.json"),
        ("cold_start", "easy", "trace_v4_coldstart_failed.json"),
        ("entropy_storm", "hard", "trace_v4_entropy_reactive_failure.json"),
        ("efficient_squeeze", "medium", "trace_v4_squeeze_gradual.json"),
        ("cold_start", "easy", "trace_v5_coldstart_optimal.json"),
        ("entropy_storm", "hard", "trace_v5_entropy_extreme_chaos.json"),
        ("efficient_squeeze", "medium", "trace_v5_squeeze_optimized.json"),
        ("entropy_storm", "hard", "trace_v6_entropy_node_upgrade.json"),
        ("efficient_squeeze", "medium", "trace_v6_squeeze_challenge.json"),
        ("entropy_storm", "hard", "trace_v7_entropy_degradation.json"),
        ("entropy_storm", "hard", "trace_v8_entropy_recovery.json"),
        ("entropy_storm", "hard", "trace_v9_entropy_optimal.json"),
    ]

    for task_name, diff, filename in trace_files:
        print(f"Generating {filename}...")
        data = generate_sinusoidal_trace(task_name, diff)
        with (traces_dir / filename).open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    
    print(f"Done generating {len(trace_files)} traces.")

if __name__ == "__main__":
    main()
