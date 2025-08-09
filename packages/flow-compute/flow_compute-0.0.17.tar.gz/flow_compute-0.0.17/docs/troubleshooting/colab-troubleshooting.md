# Google Colab Integration Troubleshooting

## Common Issues and Solutions

### 1. Instance Takes Too Long to Start

**Problem**: The GPU instance is stuck in "pending" state for more than 20 minutes.

**Solution**:
- Mithril instances typically take 10-15 minutes to start
- If it takes longer than 20 minutes, cancel and retry:
  ```bash
  flow stop <task-id>
  flow colab connect --instance-type <type> --hours <hours>
  ```
- Try a different instance type if the issue persists
- Check Mithril status page for any ongoing issues

### 2. SSH Tunnel Connection Failed

**Problem**: The SSH command fails with "Connection refused" or "Operation timed out".

**Solution**:
- Verify the instance is in "running" state:
  ```bash
  flow status <task-id>
  ```
- Check if your firewall allows outbound SSH (port 22)
- If behind a corporate proxy, configure SSH to use it:
  ```bash
  ssh -o ProxyCommand="nc -X connect -x proxy.company.com:8080 %h %p" \
      -L 8888:localhost:8888 ubuntu@<instance-ip>
  ```
- Try using a different network connection

### 3. Colab Cannot Connect to Local Runtime

**Problem**: Google Colab shows "Failed to connect to the runtime" after pasting the URL.

**Solution**:
- Ensure the SSH tunnel is active and running
- Verify the connection URL format is exactly: `http://localhost:8888/?token=<token>`
- Check that port 8888 is not already in use:
  ```bash
  lsof -i :8888  # macOS/Linux
  netstat -an | findstr :8888  # Windows
  ```
- If port is in use, kill the process or use a different port:
  ```bash
  ssh -L 8889:localhost:8888 ubuntu@<instance-ip>
  # Then use http://localhost:8889/?token=<token>
  ```

### 4. Jupyter Token Not Found

**Problem**: The logs don't show JUPYTER_TOKEN or the server fails to start.

**Solution**:
- Check the full logs for errors:
  ```bash
  flow logs <task-id> --tail 200
  ```
- Common issues:
  - Python environment problems: Ensure base image has Python 3.x
  - Network issues during pip install: Retry the launch
  - Disk space issues: Use a larger instance type

### 5. Lost Connection During Work

**Problem**: Colab disconnects unexpectedly during use.

**Solution**:
- Check if the SSH tunnel is still active
- Verify the GPU instance is still running:
  ```bash
  flow status <task-id>
  ```
- If instance is running but SSH died, restart the tunnel:
  ```bash
  ssh -L 8888:localhost:8888 ubuntu@<instance-ip>
  ```
- Reconnect from Colab using the same URL

### 6. Cannot Import GPU Libraries

**Problem**: PyTorch/TensorFlow cannot find CUDA or reports no GPU.

**Solution**:
- Verify GPU is available in the instance:
  ```python
  import torch
  print(torch.cuda.is_available())
  print(torch.cuda.get_device_name())
  ```
- Check instance type actually has GPU (not CPU instance)
- May need to install GPU-specific packages:
  ```python
  !pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
  ```

### 7. Notebook State Lost After Reconnection

**Problem**: Variables and imports are gone after reconnecting.

**Solution**:
- This is expected behavior - Colab sessions don't persist state
- Best practices:
  - Save important variables to disk regularly
  - Use checkpointing for model training
  - Consider using Flow volumes for persistence
  - Re-run initialization cells after reconnection

### 8. Multiple Sessions Conflict

**Problem**: Cannot connect to a second Colab session.

**Solution**:
- Use different local ports for each session:
  ```bash
  # Session 1
  ssh -L 8888:localhost:8888 ubuntu@<ip1>
  
  # Session 2
  ssh -L 8889:localhost:8888 ubuntu@<ip2>
  ```
- Connect Colab to the appropriate port:
  - Session 1: `http://localhost:8888/?token=<token1>`
  - Session 2: `http://localhost:8889/?token=<token2>`

## Performance Tips

1. **Use Screen or Tmux** for SSH tunnels to prevent disconnection:
   ```bash
   screen -S colab-tunnel
   ssh -L 8888:localhost:8888 ubuntu@<instance-ip>
   # Detach with Ctrl+A, D
   ```

2. **Pre-install Common Libraries** in custom images to reduce startup time

3. **Use Flow Volumes** for datasets to avoid re-downloading:
   ```python
   config = TaskConfig(
       volumes=[{"name": "datasets", "mount_path": "/data"}],
       ...
   )
   ```

## Getting Help

If issues persist:

1. Check Flow SDK logs:
   ```bash
   flow logs <task-id> --tail 500
   ```

2. Verify your Flow SDK version:
   ```bash
   flow --version
   ```

3. Report issues: https://github.com/mlfoundry/flow-sdk/issues

Include:
- Flow SDK version
- Instance type used
- Complete error messages
- Steps to reproduce