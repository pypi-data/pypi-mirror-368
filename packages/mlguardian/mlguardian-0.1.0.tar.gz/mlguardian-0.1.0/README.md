# MLGuardian Agent

MLGuardian Agent SDK lets you monitor ML models by capturing telemetry (latency, input/output shapes) and sending it to an MLGuardian core endpoint.

## Key features
- Easy wrapper `MonitoredModel` — wrap any model with `.predict()`.
- Non-blocking background batching and retrying sender.
- Function decorator `monitor_function(mm, name)` to monitor arbitrary functions.
- Configurable sampling, batch sizes, retries via environment variables or constructor args.

## Install
```bash
pip install mlguardian
