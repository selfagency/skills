#!/usr/bin/env python3
"""
Real-time system health monitoring dashboard.

Usage:
  monitor-system-health.py [--interval 5] [--json] [--disk] [--memory] [--cpu] [--network]

Examples:
  monitor-system-health.py                    # Full dashboard, update every 5 seconds
  monitor-system-health.py --interval 2       # Faster updates
  monitor-system-health.py --json             # Output JSON (once, no loop)
  monitor-system-health.py --disk --memory    # Only disk and memory metrics

Outputs:
  ANSI formatted table (default) or JSON

Exit codes:
  0  Monitoring completed or JSON output successful
  1  Error (missing dependencies, permission denied, etc)
"""

# /// script
# requires-python = ">=3.8"
# dependencies = [
#     "psutil>=5.9.0",
# ]
# ///

import sys
import json
import time
import argparse
import os
from typing import Dict, Any, List
from datetime import datetime

try:
    import psutil
except ImportError:
    print("ERROR: psutil not installed. Install with: pip install psutil", file=sys.stderr)
    sys.exit(1)


def get_cpu_metrics() -> Dict[str, Any]:
    """Get CPU usage metrics."""
    return {
        "percent": psutil.cpu_percent(interval=0.1),
        "count": psutil.cpu_count(),
        "times": {
            "user": psutil.cpu_times().user,
            "system": psutil.cpu_times().system,
            "idle": psutil.cpu_times().idle,
        },
    }


def get_memory_metrics() -> Dict[str, Any]:
    """Get memory usage metrics."""
    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()
    return {
        "total_gb": mem.total / (1024**3),
        "used_gb": mem.used / (1024**3),
        "percent": mem.percent,
        "available_gb": mem.available / (1024**3),
        "swap_total_gb": swap.total / (1024**3),
        "swap_used_gb": swap.used / (1024**3),
        "swap_percent": swap.percent,
    }


def get_disk_metrics() -> Dict[str, List[Dict[str, Any]]]:
    """Get disk usage metrics for all partitions."""
    disks = []
    try:
        for partition in psutil.disk_partitions(all=False):
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disks.append({
                    "device": partition.device,
                    "mountpoint": partition.mountpoint,
                    "fstype": partition.fstype,
                    "total_gb": usage.total / (1024**3),
                    "used_gb": usage.used / (1024**3),
                    "free_gb": usage.free / (1024**3),
                    "percent": usage.percent,
                })
            except (PermissionError, OSError):
                pass
    except Exception as e:
        print(f"Warning: Could not read disk metrics: {e}", file=sys.stderr)

    return {"partitions": disks}


def get_network_metrics() -> Dict[str, Any]:
    """Get network interface metrics."""
    try:
        net = psutil.net_io_counters()
        return {
            "bytes_sent": net.bytes_sent,
            "bytes_recv": net.bytes_recv,
            "packets_sent": net.packets_sent,
            "packets_recv": net.packets_recv,
            "errin": net.errin,
            "errout": net.errout,
            "dropin": net.dropin,
            "dropout": net.dropout,
        }
    except Exception as e:
        print(f"Warning: Could not read network metrics: {e}", file=sys.stderr)
        return {}


def get_process_metrics() -> Dict[str, Any]:
    """Get top processes by CPU and memory."""
    processes = []

    try:
        # Get top 5 by CPU
        for proc in sorted(psutil.process_iter(['pid', 'name', 'cpu_percent']),
                          key=lambda p: p.info.get('cpu_percent', 0) or 0,
                          reverse=True)[:5]:
            try:
                processes.append({
                    "pid": proc.info['pid'],
                    "name": proc.info['name'],
                    "cpu_percent": proc.info.get('cpu_percent') or 0,
                    "type": "cpu",
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
    except Exception as e:
        print(f"Warning: Could not read process metrics: {e}", file=sys.stderr)

    return {"top_cpu_processes": processes}


def format_table(data: Dict[str, Any]) -> str:
    """Format metrics as ANSI table."""
    output = []
    output.append("\n" + "="*70)
    output.append(f"System Health Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    output.append("="*70)

    if "percent" in data.get("cpu", {}):
        cpu = data["cpu"]
        output.append(f"\nCPU: {cpu['percent']:.1f}% ({cpu['count']} cores)")

    if "percent" in data.get("memory", {}):
        mem = data["memory"]
        output.append(f"\nMemory:")
        output.append(f"  Physical: {mem['used_gb']:.1f}GB / {mem['total_gb']:.1f}GB ({mem['percent']:.1f}%)")
        output.append(f"  Swap:     {mem['swap_used_gb']:.1f}GB / {mem['swap_total_gb']:.1f}GB ({mem['swap_percent']:.1f}%)")

    if "partitions" in data.get("disk", {}):
        output.append(f"\nDisk:")
        for disk in data["disk"]["partitions"]:
            output.append(f"  {disk['device']:15} {disk['used_gb']:6.1f}GB / {disk['total_gb']:6.1f}GB ({disk['percent']:5.1f}%) - {disk['mountpoint']}")

    if "bytes_sent" in data.get("network", {}):
        net = data["network"]
        output.append(f"\nNetwork:")
        output.append(f"  Sent:     {net['bytes_sent'] / (1024**3):.2f}GB")
        output.append(f"  Received: {net['bytes_recv'] / (1024**3):.2f}GB")

    if "top_cpu_processes" in data.get("processes", {}):
        output.append(f"\nTop CPU Processes:")
        for proc in data["processes"]["top_cpu_processes"][:5]:
            output.append(f"  {proc['pid']:6} {proc['name']:20} {proc['cpu_percent']:6.1f}%")

    output.append("="*70 + "\n")

    return "\n".join(output)


def collect_metrics(include: Dict[str, bool]) -> Dict[str, Any]:
    """Collect all requested metrics."""
    data = {}

    if include["cpu"]:
        data["cpu"] = get_cpu_metrics()
    if include["memory"]:
        data["memory"] = get_memory_metrics()
    if include["disk"]:
        data["disk"] = get_disk_metrics()
    if include["network"]:
        data["network"] = get_network_metrics()
    if include["processes"]:
        data["processes"] = get_process_metrics()

    data["timestamp"] = datetime.utcnow().isoformat() + "Z"

    return data


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Monitor system health in real-time")
    parser.add_argument("--interval", type=int, default=5, help="Update interval in seconds (default: 5)")
    parser.add_argument("--json", action="store_true", help="Output JSON once and exit")
    parser.add_argument("--cpu", action="store_true", help="Include CPU metrics")
    parser.add_argument("--memory", action="store_true", help="Include memory metrics")
    parser.add_argument("--disk", action="store_true", help="Include disk metrics")
    parser.add_argument("--network", action="store_true", help="Include network metrics")

    args = parser.parse_args()

    # If no specific metrics requested, include all
    include_all = not any([args.cpu, args.memory, args.disk, args.network])

    include = {
        "cpu": args.cpu or include_all,
        "memory": args.memory or include_all,
        "disk": args.disk or include_all,
        "network": args.network or include_all,
        "processes": include_all,  # Always include processes in full report
    }

    try:
        if args.json:
            # Single JSON output and exit
            metrics = collect_metrics(include)
            print(json.dumps(metrics, indent=2))
            return 0
        else:
            # Continuous monitoring (Ctrl+C to exit)
            while True:
                metrics = collect_metrics(include)
                print(format_table(metrics))
                time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\nMonitoring stopped.")
        return 0
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
