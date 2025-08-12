# GPU Support for Stockula

Stockula supports GPU acceleration for enhanced time series forecasting performance using NVIDIA CUDA. This can
significantly speed up model training and prediction, especially for neural network-based models in AutoTS.

## Prerequisites

### Hardware Requirements

- NVIDIA GPU with CUDA capability >= 3.7
- Minimum 6GB GPU memory (8GB+ recommended)
- 16GB+ system RAM recommended

### Software Requirements

- NVIDIA drivers >= 450.80.02
- CUDA Toolkit 11.8 or 12.x
- cuDNN 8.x or 9.x
- Python 3.11+ (3.11 used in Docker images)

## Docker Architecture

Our GPU-enabled Docker images are based on official PyTorch images for optimal compatibility:

- **Base Image**: `pytorch/pytorch:2.8.0-cuda12.6-cudnn9-devel` (builder)
- **Runtime Image**: `pytorch/pytorch:2.8.0-cuda12.9-cudnn9-runtime`
- **Python Version**: 3.11 (pre-installed in PyTorch images)
- **Platform**: linux/amd64 only (PyTorch images are not available for ARM)
- **User**: `stockula` (UID 1000) with home directory `/home/stockula`

## Time Series Forecasting Models

Stockula includes state-of-the-art GPU-accelerated time series forecasting:

| Package              | Description                        | GPU Support |
| -------------------- | ---------------------------------- | ----------- |
| PyTorch              | Pre-installed in base image        | ✅ Native   |
| AutoGluon TimeSeries | AutoML for time series             | ✅ Full     |
| GluonTS              | Probabilistic time series modeling | ✅ Full     |
| Chronos              | Zero-shot time series forecasting  | ✅ Full     |
| XGBoost              | Gradient boosting                  | ✅ Full     |
| LightGBM             | Gradient boosting                  | ✅ Full     |

### Note: AutoGluon and Python 3.13+

AutoGluon 1.4 depends on Ray (< 2.45), and as of now Ray does not publish wheels for CPython 3.13. To keep GPU
installations reliable on Python 3.13, our GPU requirements file conditionally installs AutoGluon only on Python < 3.13:

```
autogluon-timeseries==1.4.0; python_version < "3.13"
```

Recommendations:

- Use Python 3.11 (recommended) or 3.12 when you need AutoGluon.

- On Python 3.13, use the Chronos and GluonTS backends (both GPU-friendly) — these are installed by default.

- If you must try AutoGluon on 3.13, allow pre-releases when installing (not recommended for production):

  ```bash
  uv pip install --prerelease=allow autogluon-timeseries
  ```

Our Docker GPU images are based on PyTorch 2.8 and Python 3.11, so AutoGluon works out-of-the-box there.

## Installation Methods

### Method 1: Using Docker (Recommended)

The easiest way to use GPU acceleration is with our pre-built Docker image:

```bash
# Pull the GPU-enabled image
docker pull ghcr.io/mkm29/stockula-gpu:latest

# Run with GPU support
docker run --gpus all ghcr.io/mkm29/stockula-gpu:latest --help

# Run forecasting with GPU acceleration
docker run --gpus all -v $(pwd):/app/data ghcr.io/mkm29/stockula-gpu:latest \
    stockula --ticker AAPL --mode forecast --days 30
```

### Method 2: Using pip with GPU extras

Install Stockula with GPU support using pip:

```bash
# Install with GPU extras
pip install stockula[gpu] --extra-index-url https://download.pytorch.org/whl/cu118

# Or using the requirements file
pip install -r requirements-gpu.txt --extra-index-url https://download.pytorch.org/whl/cu118
```

### Method 3: Using uv package manager

```bash
# Install with GPU extras using uv
uv pip install stockula[gpu] --extra-index-url https://download.pytorch.org/whl/cu118
```

## Verifying GPU Setup

After installation, verify that GPU support is working:

```python
import torch
import tensorflow as tf

# Check PyTorch GPU
print(f"PyTorch CUDA available: {torch.cuda.is_available()}")
print(f"PyTorch GPU count: {torch.cuda.device_count()}")
if torch.cuda.is_available():
    print(f"PyTorch GPU name: {torch.cuda.get_device_name(0)}")

# Check TensorFlow GPU
print(f"TensorFlow GPUs: {tf.config.list_physical_devices('GPU')}")
```

For Docker users, run the GPU info script:

```bash
docker run --gpus all ghcr.io/mkm29/stockula-gpu:latest bash -c "/home/stockula/gpu_info.sh"
```

## Performance Considerations

### GPU Memory Management

AutoTS and other ML libraries can be memory-intensive. To optimize GPU memory usage:

1. **Reduce batch sizes** in AutoTS:

   ```python
   from stockula.forecasting import StockForecaster

   forecaster = StockForecaster(
       model_list="fast",
       ensemble="simple",
       max_generations=5,
       num_validations=2,  # Reduce for less memory usage
       validation_method="backwards"  # Less memory than "similarity"
   )
   ```

1. **Set environment variables** to limit GPU memory growth:

   ```bash
   export TF_FORCE_GPU_ALLOW_GROWTH=true
   export CUDA_VISIBLE_DEVICES=0  # Use only first GPU
   ```

1. **Monitor GPU usage**:

   ```bash
   nvidia-smi -l 1  # Update every second
   ```

### Model Selection for GPU

Best GPU-accelerated models in Stockula:

- **Chronos**: Zero-shot time series forecasting with pretrained transformer models
- **GluonTS**: Advanced probabilistic models (DeepAR, SimpleFeedForward, Transformer)
- **AutoGluon**: AutoML with neural networks and gradient boosting
- **XGBoost/LightGBM**: GPU-accelerated gradient boosting
- **Neural Networks**: LSTM, GRU, Transformer models via PyTorch

Models that don't benefit from GPU:

- Statistical models (ARIMA, ETS, Prophet)
- Simple regression models
- Naive forecasting methods

### Optimization Tips

1. **Use appropriate model lists** for GPU:

   ```python
   # GPU-optimized model list
   gpu_models = [
       'GLS', 'GLM', 'ETS', 'ARIMA',
       'FBProphet', 'SeasonalNaive', 'LastValueNaive',
       'GluonTS', 'NVAR', 'VECM', 'DynamicFactor',
       'DynamicFactorMQ', 'WindowRegression', 'VAR'
   ]
   ```

1. **Batch processing**: Process multiple tickers simultaneously to maximize GPU utilization

1. **Mixed precision training**: Enable for faster computation (if supported):

   ```python
   import torch
   torch.set_float32_matmul_precision('medium')
   ```

## Troubleshooting

### Common Issues

1. **CUDA out of memory**:

   - Reduce batch size
   - Use fewer parallel jobs: `export AUTOTS_N_JOBS=1`
   - Clear GPU cache: `torch.cuda.empty_cache()`

1. **CUDA version mismatch**:

   - Ensure PyTorch CUDA version matches system CUDA
   - Check with: `python -c "import torch; print(torch.version.cuda)"`

1. **GPU not detected**:

   - Verify drivers: `nvidia-smi`
   - Check Docker runtime: `docker run --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi`

1. **Slow GPU performance**:

   - Ensure GPU is not thermal throttling
   - Check PCIe bandwidth
   - Verify no other processes are using GPU

### Environment Variables

Key environment variables for GPU configuration:

```bash
# AutoTS GPU settings
export AUTOTS_GPU_ENABLED=true
export AUTOTS_N_JOBS=1  # Reduce for stability

# CUDA settings
export CUDA_VISIBLE_DEVICES=0  # Select GPU
export CUDA_LAUNCH_BLOCKING=1  # For debugging

# TensorFlow settings
export TF_CPP_MIN_LOG_LEVEL=2  # Reduce logging
export TF_FORCE_GPU_ALLOW_GROWTH=true  # Dynamic memory allocation

# PyTorch settings
export TORCH_CUDA_ARCH_LIST="6.0 6.1 7.0 7.5 8.0 8.6 9.0+PTX"
```

## Performance Benchmarks

Typical speedups with GPU acceleration (results may vary):

| Model Type             | CPU Time | GPU Time | Speedup         |
| ---------------------- | -------- | -------- | --------------- |
| Neural Networks (LSTM) | 120s     | 15s      | 8x              |
| XGBoost                | 60s      | 12s      | 5x              |
| LightGBM               | 45s      | 10s      | 4.5x            |
| GluonTS                | 180s     | 25s      | 7.2x            |
| Statistical (ARIMA)    | 30s      | 30s      | 1x (no benefit) |

## Additional Resources

- [AutoTS GPU Documentation](https://winedarksea.github.io/AutoTS/build/html/source/tutorial.html#gpu-acceleration)
- [PyTorch CUDA Installation](https://pytorch.org/get-started/locally/)
- [TensorFlow GPU Guide](https://www.tensorflow.org/install/gpu)
- [NVIDIA Docker Documentation](https://github.com/NVIDIA/nvidia-docker)
