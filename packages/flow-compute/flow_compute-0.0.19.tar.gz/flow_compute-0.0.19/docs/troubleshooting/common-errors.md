# Troubleshooting Common Errors

## Authentication Failed
```
Error: Invalid API key
```
Solution: Run `flow init` and ensure your API key is correct. Get a new key at [app.mithril.ai](https://app.mithril.ai/account/apikeys).

## No Available Instances
```
Error: No instances available for type 'a100'
```
Solution: Try a different region or instance type. Check availability with `flow status`.

## Quota Exceeded
```
Error: GPU quota exceeded in region us-east-1
```
Solution: Try a different region or contact support for quota increase.

## Invalid Instance Type
```
ValidationError: Invalid instance type 'a100x8'
```
Solution: Use correct format: `8xa100` (not `a100x8`). See the main README for instance types.

## Task Timeout
```
Error: Task exceeded max_run_time_hours limit
```
Solution: Increase `max_run_time_hours` in your config or optimize your code.

## File Not Found
```
python: can't open file 'train.py': No such file or directory
```
Solution: Ensure `upload_code=True` (default) or that your file exists in the Docker image.

## Module Not Found
```
ModuleNotFoundError: No module named 'torch'
```
Solution: Install dependencies first: `flow.run("pip install torch && python train.py")`.

## Python Version Too Old
```
Error: Flow SDK requires Python 3.10 or later. You are using Python 3.9.
```
Solutions:
1. Install and use `uv` (recommended):
   - macOS/Linux:
     ```bash
     curl -LsSf https://astral.sh/uv/install.sh | sh
     uv tool install flow-compute
     ```
   - Windows (PowerShell):
     ```powershell
     powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
     uv tool install flow-compute
     ```
2. Or upgrade Python to 3.10+ and reinstall `flow-compute`.

## Upload Size Limit
```
Error: Project size (15.2MB) exceeds limit (10MB)
```
Note: Files are automatically compressed (gzip), but the 10MB limit applies after compression.

Solutions (in order of preference):
1. **Use .flowignore** to exclude unnecessary files (models, datasets, caches)
2. **Clone from Git**:
   ```python
   flow.run("git clone https://github.com/myorg/myrepo.git . && python train.py", 
            instance_type="a100", upload_code=False)
   ```
3. **Pre-built Docker image** with your code:
   ```python
   flow.run("python /app/train.py", instance_type="a100",
            image="myorg/myapp:latest", upload_code=False)
   ```
4. **Download from S3/GCS**:
   ```python
   flow.run("aws s3 cp s3://mybucket/code.tar.gz . && tar -xzf code.tar.gz && python train.py",
            instance_type="a100", upload_code=False)
   ```
5. **Mount code via volume** (for development):
   ```python
   # First upload to a volume manually, then:
   flow.run("python /code/train.py", instance_type="a100",
            volumes=[{"name": "my-code", "mount_path": "/code"}],
            upload_code=False)
   ```
   Note: Volumes are empty by default. You must manually populate them first (e.g., via git clone or rsync).