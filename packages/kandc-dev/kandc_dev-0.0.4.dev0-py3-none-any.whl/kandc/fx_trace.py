"""
FX-based model tracing with computation graph + timing alignment.

This module provides FX-based alternatives to the current PyTorch profiler-only
tracing system, offering:
1. Computation graph structure via torch.fx
2. Per-node timing via profiler alignment
3. Input/output shapes for each node
4. Per-input-shape tracing for better analysis
"""

import os
import json
import hashlib
from typing import Optional, Any, Dict, List, Tuple
from pathlib import Path

import torch
import torch.fx as fx
from torch.autograd.profiler import record_function
from torch.profiler import profile, ProfilerActivity

from .constants import (
    KANDC_BACKEND_APP_NAME_ENV_KEY,
    KANDC_BACKEND_RUN_ENV_KEY,
    KANDC_JOB_ID_ENV_KEY,
    TRACE_DIR,
    KANDC_TRACE_BASE_DIR_ENV_KEY,
)


def _shape_of(x):
    """Extract shape information from tensors, lists, tuples, dicts recursively."""
    if isinstance(x, torch.Tensor):
        return {
            "type": "tensor",
            "shape": list(x.shape),
            "dtype": str(x.dtype),
            "device": str(x.device),
        }
    elif isinstance(x, (list, tuple)):
        return {
            "type": type(x).__name__,
            "items": [_shape_of(item) for item in x],
        }
    elif isinstance(x, dict):
        return {
            "type": "dict",
            "items": {k: _shape_of(v) for k, v in x.items()},
        }
    elif x is None:
        return {"type": "none"}
    else:
        val_str = str(x)
        return {
            "type": type(x).__name__,
            "value": val_str if len(val_str) < 100 else f"{val_str[:97]}...",
        }


def _input_shape_hash(args, kwargs) -> str:
    """Create a stable hash for input shapes to group traces by input shape."""
    shape_info = {
        "args": _shape_of(args),
        "kwargs": _shape_of(kwargs),
    }
    shape_str = json.dumps(shape_info, sort_keys=True)
    return hashlib.md5(shape_str.encode()).hexdigest()[:8]


def _format_input_shape_name(args, kwargs) -> str:
    """Create a human-readable name for input shapes."""
    parts = []

    # Handle positional arguments
    for i, arg in enumerate(args):
        if isinstance(arg, torch.Tensor):
            shape_str = "x".join(map(str, arg.shape))
            parts.append(f"arg{i}_{shape_str}")
        else:
            # For non-tensors, include type info
            parts.append(f"arg{i}_{type(arg).__name__}")

    # Handle keyword arguments
    for key, value in kwargs.items():
        if isinstance(value, torch.Tensor):
            shape_str = "x".join(map(str, value.shape))
            parts.append(f"{key}_{shape_str}")
        else:
            # For non-tensors, include type info
            parts.append(f"{key}_{type(value).__name__}")

    if not parts:
        return "input_empty"

    # Join parts, but keep it reasonable length
    full_name = "_".join(parts)

    # Check if we have exactly one tensor - use simplified naming
    tensor_count = sum(1 for arg in args if isinstance(arg, torch.Tensor))
    tensor_count += sum(1 for v in kwargs.values() if isinstance(v, torch.Tensor))

    if tensor_count == 1 and len(args) == 1 and not kwargs and isinstance(args[0], torch.Tensor):
        # Single tensor input - use simple format
        shape_str = "x".join(map(str, args[0].shape))
        return f"input_{shape_str}"

    # If the name gets too long, use a more compact format
    if len(full_name) > 100:
        # Create a shorter descriptive name
        if tensor_count == 1:
            # Find the single tensor and use its shape
            for arg in args:
                if isinstance(arg, torch.Tensor):
                    shape_str = "x".join(map(str, arg.shape))
                    return f"input_{shape_str}"
            for key, value in kwargs.items():
                if isinstance(value, torch.Tensor):
                    shape_str = "x".join(map(str, value.shape))
                    return f"input_{key}_{shape_str}"
        else:
            # Multiple tensors - use compact format with hash
            hash_suffix = _input_shape_hash(args, kwargs)
            return f"input_{tensor_count}tensors_{hash_suffix}"

    return f"input_{full_name}"


class FXTimedInterpreter(fx.Interpreter):
    """FX Interpreter that records timing and shape information for each node."""

    def __init__(self, gm: fx.GraphModule, model_name: str):
        super().__init__(gm)
        self.model_name = model_name
        self.node_records: List[Dict[str, Any]] = []

    def run_node(self, n: fx.Node):
        """Run a single FX node with timing and shape recording."""
        args, kwargs = self.fetch_args_kwargs_from_env(n)

        # Record input shapes
        input_shapes = {
            "args": _shape_of(args),
            "kwargs": _shape_of(kwargs),
        }

        # Create profiler marker for this node
        marker_name = f"fx::{n.name}"

        # Execute node with profiler marker
        with record_function(marker_name):
            output = super().run_node(n)

        # Record output shapes
        output_shapes = _shape_of(output)

        # Store node information
        self.node_records.append(
            {
                "node_name": n.name,
                "node_op": n.op,
                "node_target": str(n.target),
                "input_shapes": input_shapes,
                "output_shapes": output_shapes,
                "marker_name": marker_name,
            }
        )

        return output


def _extract_fx_timings_from_profiler(
    prof, node_records: List[Dict[str, Any]]
) -> Dict[str, Dict[str, float]]:
    """Extract timing information for FX nodes from profiler events."""
    timings = {}

    # Get all profiler events
    events = prof.events()

    for event in events:
        if event.name and event.name.startswith("fx::"):
            # Extract node name from marker
            node_name = event.name[4:]  # Remove "fx::" prefix

            # Get CPU time (in microseconds)
            cpu_time_us = getattr(event, "cpu_time_total", None) or getattr(event, "cpu_time", 0.0)

            # Get CUDA time if available
            cuda_time_us = getattr(event, "cuda_time_total", 0.0)

            timings[node_name] = {
                "cpu_time_us": float(cpu_time_us),
                "cuda_time_us": float(cuda_time_us),
                "cpu_time_ms": float(cpu_time_us) / 1000.0,
                "cuda_time_ms": float(cuda_time_us) / 1000.0,
            }

    return timings


def _profile_fx_model_single_input(
    model: torch.nn.Module,
    model_name: str,
    input_args: Tuple,
    input_kwargs: Dict,
    record_shapes: bool = True,
    profile_memory: bool = True,
) -> Dict[str, Any]:
    """Profile a single forward pass with FX tracing."""

    # Create FX graph
    try:
        gm = fx.symbolic_trace(model)
    except Exception as e:
        print(f"⚠️  FX tracing failed for {model_name}: {e}")
        # Fallback to regular profiling without FX
        return _fallback_profile_without_fx(
            model, model_name, input_args, input_kwargs, record_shapes, profile_memory
        )

    # Create timed interpreter
    interpreter = FXTimedInterpreter(gm, model_name)

    # Set up profiler activities
    activities = [ProfilerActivity.CPU]
    if torch.cuda.is_available():
        activities.append(ProfilerActivity.CUDA)

    # Profile the FX execution
    with profile(
        activities=activities,
        record_shapes=record_shapes,
        profile_memory=profile_memory,
        with_stack=True,
    ) as prof:
        # Run the model through FX interpreter
        output = interpreter.run(*input_args, **input_kwargs)

    # Extract timings from profiler
    timings = _extract_fx_timings_from_profiler(prof, interpreter.node_records)

    # Combine node records with timings
    fx_nodes = []
    for record in interpreter.node_records:
        node_name = record["node_name"]
        timing = timings.get(
            node_name,
            {
                "cpu_time_us": 0.0,
                "cuda_time_us": 0.0,
                "cpu_time_ms": 0.0,
                "cuda_time_ms": 0.0,
            },
        )

        fx_nodes.append(
            {
                **record,
                **timing,
            }
        )

    # Create input shape identifier
    input_shape_name = _format_input_shape_name(input_args, input_kwargs)
    input_shape_hash = _input_shape_hash(input_args, input_kwargs)

    # Calculate total execution time
    total_cpu_time_ms = sum(node["cpu_time_ms"] for node in fx_nodes)
    total_cuda_time_ms = sum(node["cuda_time_ms"] for node in fx_nodes)

    return {
        "model_name": model_name,
        "input_shape_name": input_shape_name,
        "input_shape_hash": input_shape_hash,
        "input_shapes": {
            "args": _shape_of(input_args),
            "kwargs": _shape_of(input_kwargs),
        },
        "output_shapes": _shape_of(output),
        "fx_nodes": fx_nodes,
        "profiler_trace": prof,  # Keep for Chrome trace export
        "summary": {
            "total_nodes": len(fx_nodes),
            "total_cpu_time_ms": total_cpu_time_ms,
            "total_cuda_time_ms": total_cuda_time_ms,
        },
    }


def _fallback_profile_without_fx(
    model: torch.nn.Module,
    model_name: str,
    input_args: Tuple,
    input_kwargs: Dict,
    record_shapes: bool = True,
    profile_memory: bool = True,
) -> Dict[str, Any]:
    """Fallback profiling when FX tracing fails."""
    activities = [ProfilerActivity.CPU]
    if torch.cuda.is_available():
        activities.append(ProfilerActivity.CUDA)

    with profile(
        activities=activities,
        record_shapes=record_shapes,
        profile_memory=profile_memory,
        with_stack=True,
    ) as prof:
        output = model(*input_args, **input_kwargs)

    input_shape_name = _format_input_shape_name(input_args, input_kwargs)
    input_shape_hash = _input_shape_hash(input_args, input_kwargs)

    return {
        "model_name": model_name,
        "input_shape_name": input_shape_name,
        "input_shape_hash": input_shape_hash,
        "input_shapes": {
            "args": _shape_of(input_args),
            "kwargs": _shape_of(input_kwargs),
        },
        "output_shapes": _shape_of(output),
        "fx_nodes": [],  # Empty for fallback
        "profiler_trace": prof,
        "summary": {
            "total_nodes": 0,
            "total_cpu_time_ms": 0.0,
            "total_cuda_time_ms": 0.0,
            "fallback_reason": "FX tracing failed",
        },
    }


def _save_fx_trace_results(trace_result: Dict[str, Any], job_trace_dir: Path):
    """Save FX trace results to files."""
    model_name = trace_result["model_name"]
    input_shape_name = trace_result["input_shape_name"]

    # Save Chrome trace (for Perfetto viewer compatibility)
    chrome_trace_file = job_trace_dir / f"{model_name}_{input_shape_name}.json"
    trace_result["profiler_trace"].export_chrome_trace(str(chrome_trace_file))

    # Save FX graph data (new structured format)
    fx_data = {
        "model_name": trace_result["model_name"],
        "input_shape_name": trace_result["input_shape_name"],
        "input_shape_hash": trace_result["input_shape_hash"],
        "input_shapes": trace_result["input_shapes"],
        "output_shapes": trace_result["output_shapes"],
        "fx_nodes": trace_result["fx_nodes"],
        "summary": trace_result["summary"],
        "version": "fx_v1",
    }

    fx_graph_file = job_trace_dir / f"{model_name}_{input_shape_name}_fx_graph.json"
    with open(fx_graph_file, "w") as f:
        json.dump(fx_data, f, indent=2, default=str)

    print(f"💾 [FX trace] {model_name} → {chrome_trace_file.name} + {fx_graph_file.name}")


def capture_model_instance_fx(
    model_instance,
    model_name: Optional[str] = None,
    record_shapes: bool = True,
    profile_memory: bool = True,
    trace_per_input_shape: bool = True,
    **profiler_kwargs: Any,
):
    """
    FX-based model instance wrapper that captures computation graph + timings.

    This replaces capture_model_instance with FX tracing capabilities:
    - Computation graph structure via torch.fx
    - Per-node timing via profiler alignment
    - Input/output shapes for each node
    - Per-input-shape tracing for better analysis

    Args:
        model_instance: The model instance to wrap
        model_name: Name for the model traces (defaults to model class name)
        record_shapes: Record tensor shapes for each operation
        profile_memory: Profile memory usage
        trace_per_input_shape: Create separate trace for each unique input shape
        **profiler_kwargs: Additional profiler arguments (for compatibility)

    Returns:
        Wrapped model instance that profiles every forward pass with FX
    """
    # Check if we're running on the Keys & Caches backend
    if os.environ.get(KANDC_BACKEND_RUN_ENV_KEY) != "1":
        # Running locally - return original model instance
        return model_instance

    assert os.environ.get(KANDC_BACKEND_APP_NAME_ENV_KEY), "Keys & Caches app name is not set"

    # Store the original forward method
    original_forward = model_instance.forward
    model_name = model_name or model_instance.__class__.__name__

    # Track seen input shapes if trace_per_input_shape is enabled
    seen_input_shapes = set()
    trace_counter = 0

    def fx_profiled_forward(*args, **kwargs):
        nonlocal trace_counter, seen_input_shapes

        # Check if we should profile this input shape
        should_profile = True
        if trace_per_input_shape:
            input_hash = _input_shape_hash(args, kwargs)
            if input_hash in seen_input_shapes:
                should_profile = False
            else:
                seen_input_shapes.add(input_hash)

        if should_profile:
            trace_counter += 1

            # Get job and trace directory info
            job_id = os.environ.get(KANDC_JOB_ID_ENV_KEY)
            if not job_id:
                print("⚠️  No job ID found, skipping FX trace")
                return original_forward(*args, **kwargs)

            base_path_env = os.environ.get(KANDC_TRACE_BASE_DIR_ENV_KEY)
            base_path = Path(base_path_env) if base_path_env else Path("/volume")
            app_name = os.environ.get(KANDC_BACKEND_APP_NAME_ENV_KEY)
            job_trace_dir = base_path / app_name / job_id / TRACE_DIR
            job_trace_dir.mkdir(parents=True, exist_ok=True)

            # Profile with FX
            trace_result = _profile_fx_model_single_input(
                model_instance,
                model_name,
                args,
                kwargs,
                record_shapes=record_shapes,
                profile_memory=profile_memory,
            )

            # Save results
            _save_fx_trace_results(trace_result, job_trace_dir)

            # Return the output from profiling
            return trace_result["output_shapes"]  # This should contain the actual output
        else:
            # Don't profile, just run normally
            return original_forward(*args, **kwargs)

    # Replace the forward method
    model_instance.forward = fx_profiled_forward
    model_instance._fx_model_name = model_name
    model_instance._fx_trace_counter = trace_counter

    return model_instance


def capture_model_class_fx(
    model_name: Optional[str] = None,
    record_shapes: bool = True,
    profile_memory: bool = True,
    trace_per_input_shape: bool = True,
    **profiler_kwargs: Any,
):
    """
    FX-based model class decorator that captures computation graph + timings.

    This replaces capture_model_class with FX tracing capabilities.

    Args:
        model_name: Name for the model traces (defaults to model class name)
        record_shapes: Record tensor shapes for each operation
        profile_memory: Profile memory usage
        trace_per_input_shape: Create separate trace for each unique input shape
        **profiler_kwargs: Additional profiler arguments (for compatibility)

    Returns:
        Model wrapper class that profiles every forward pass with FX
    """

    def decorator(model_class):
        # Check if we're running on the Keys & Caches backend
        if os.environ.get(KANDC_BACKEND_RUN_ENV_KEY) != "1":
            # Running locally - return original model
            return model_class

        assert os.environ.get(KANDC_BACKEND_APP_NAME_ENV_KEY), "Keys & Caches app name is not set"

        # Create a wrapper class that inherits from the original model
        class FXProfiledModel(model_class):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self._fx_model_name = model_name or model_class.__name__
                self._fx_trace_counter = 0
                self._fx_seen_input_shapes = set()

            def forward(self, *args, **kwargs):
                # Check if we should profile this input shape
                should_profile = True
                if trace_per_input_shape:
                    input_hash = _input_shape_hash(args, kwargs)
                    if input_hash in self._fx_seen_input_shapes:
                        should_profile = False
                    else:
                        self._fx_seen_input_shapes.add(input_hash)

                if should_profile:
                    self._fx_trace_counter += 1

                    # Get job and trace directory info
                    job_id = os.environ.get(KANDC_JOB_ID_ENV_KEY)
                    if not job_id:
                        print("⚠️  No job ID found, skipping FX trace")
                        return super().forward(*args, **kwargs)

                    base_path_env = os.environ.get(KANDC_TRACE_BASE_DIR_ENV_KEY)
                    base_path = Path(base_path_env) if base_path_env else Path("/volume")
                    app_name = os.environ.get(KANDC_BACKEND_APP_NAME_ENV_KEY)
                    job_trace_dir = base_path / app_name / job_id / TRACE_DIR
                    job_trace_dir.mkdir(parents=True, exist_ok=True)

                    # Profile with FX
                    trace_result = _profile_fx_model_single_input(
                        self,
                        self._fx_model_name,
                        args,
                        kwargs,
                        record_shapes=record_shapes,
                        profile_memory=profile_memory,
                    )

                    # Save results
                    _save_fx_trace_results(trace_result, job_trace_dir)

                    # Extract actual output from trace result
                    # Note: We need to run the model again to get the actual output
                    # The profiling run consumed the input, so we need a fresh run
                    return super().forward(*args, **kwargs)
                else:
                    # Don't profile, just run normally
                    return super().forward(*args, **kwargs)

        return FXProfiledModel

    return decorator


# Legacy compatibility functions (these will delegate to FX versions)
def capture_model_instance_legacy_compat(
    model_instance,
    model_name: Optional[str] = None,
    record_shapes: bool = True,
    profile_memory: bool = True,
    **profiler_kwargs: Any,
):
    """Legacy compatibility wrapper - delegates to FX version."""
    return capture_model_instance_fx(
        model_instance=model_instance,
        model_name=model_name,
        record_shapes=record_shapes,
        profile_memory=profile_memory,
        trace_per_input_shape=True,  # Enable new feature by default
        **profiler_kwargs,
    )


def capture_model_class_legacy_compat(
    model_name: Optional[str] = None,
    record_shapes: bool = True,
    profile_memory: bool = True,
    **profiler_kwargs: Any,
):
    """Legacy compatibility wrapper - delegates to FX version."""
    return capture_model_class_fx(
        model_name=model_name,
        record_shapes=record_shapes,
        profile_memory=profile_memory,
        trace_per_input_shape=True,  # Enable new feature by default
        **profiler_kwargs,
    )
