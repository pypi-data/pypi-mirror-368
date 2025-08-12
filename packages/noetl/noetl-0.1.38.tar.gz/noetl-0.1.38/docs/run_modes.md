# NoETL Run Modes

NoETL now supports multiple run modes to provide flexibility in how the application is deployed and used. This document describes the available run modes and how to configure them.

## Available Run Modes

NoETL supports the following run modes:

1. **Server Mode**: Runs NoETL as an API server using uvicorn
2. **Worker Mode**: Runs NoETL as a worker process to execute a specific playbook
3. **CLI Mode**: Runs NoETL as a CLI tool for executing commands

## Command Line Usage

### Server Mode

Run NoETL as a server:

```bash
# Start the server
noetl server start --host 0.0.0.0 --port 8080 --workers 4 --debug

# Stop the server
noetl server stop
```

#### Start Options:
- `--host`: Server host (default: 0.0.0.0)
- `--port`: Server port (default: 8080)
- `--workers`: Number of worker processes (default: 1)
- `--reload`: Enable auto-reload for development mode
- `--debug`: Enable debug logging
- `--no-ui`: Disable the UI components

#### Stop Options:
- `--force`, `-f`: Force stop the server without confirmation

> Note: For backward compatibility, the old `noetl server` command is still available but deprecated.

### Worker Mode

Run NoETL as a worker to execute a playbook:

```bash
# Execute a playbook file
noetl worker /path/to/playbook.yaml --debug

# Execute a playbook from the catalog
noetl worker playbook_name --version 0.1.0 --debug
```

Options:
- `playbook_path`: Path to the playbook file or name of the playbook in the catalog
- `--version`, `-v`: Version of the playbook to execute from the catalog
- `--mock`: Run in mock mode without executing real operations
- `--debug`: Enable debug logging
- `--pgdb`: PostgreSQL connection string (if not provided, uses environment variables)

### CLI Mode

NoETL CLI commands remain the same:

```bash
# Catalog management
noetl catalog register /path/to/playbook.yaml
noetl catalog execute playbook_name --version 0.1.0
noetl catalog list playbook

# Execute playbook directly
noetl execute /path/to/playbook.yaml
```

## Docker Configuration

When running NoETL in Docker, you can use environment variables to configure the run mode:

```bash
# Start the server
docker run -e NOETL_RUN_MODE=server -p 8080:8080 noetl

# Stop the server
docker run -e NOETL_RUN_MODE=server-stop -e NOETL_FORCE_STOP=true noetl

# Run as worker
docker run -e NOETL_RUN_MODE=worker -e NOETL_PLAYBOOK_PATH=/opt/noetl/playbooks/example.yaml noetl

# Run in CLI mode
docker run -e NOETL_RUN_MODE=cli noetl
```

### Environment Variables

The following environment variables are available:

#### General
- `NOETL_RUN_MODE`: Run mode (server, server-stop, worker, cli)
- `NOETL_DEBUG`: Enable debug logging (true/false)

#### Server Mode
- `NOETL_HOST`: Server host
- `NOETL_PORT`: Server port
- `NOETL_WORKERS`: Number of worker processes
- `NOETL_RELOAD`: Enable auto-reload (true/false)
- `NOETL_NO_UI`: Disable UI components (true/false)

#### Server Stop Mode
- `NOETL_FORCE_STOP`: Force stop without confirmation (true/false)

#### Worker Mode
- `NOETL_PLAYBOOK_PATH`: Path to the playbook file
- `NOETL_PLAYBOOK_VERSION`: Version of the playbook to execute
- `NOETL_MOCK_MODE`: Run in mock mode (true/false)

## Kubernetes Configuration

NoETL provides Kubernetes deployment templates for each run mode. You can also create a job to stop a running server:

### Server Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: noetl-server
  labels:
    app: noetl
    component: server
spec:
  replicas: 1
  selector:
    matchLabels:
      app: noetl
      component: server
  template:
    metadata:
      labels:
        app: noetl
        component: server
    spec:
      containers:
      - name: noetl
        image: noetl:latest
        env:
        - name: NOETL_RUN_MODE
          value: "server"
        - name: NOETL_HOST
          value: "0.0.0.0"
        - name: NOETL_PORT
          value: "8080"
        # ... other environment variables
```

### Worker Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: noetl-worker
  labels:
    app: noetl
    component: worker
spec:
  replicas: 1
  selector:
    matchLabels:
      app: noetl
      component: worker
  template:
    metadata:
      labels:
        app: noetl
        component: worker
    spec:
      containers:
      - name: noetl-worker
        image: noetl:latest
        env:
        - name: NOETL_RUN_MODE
          value: "worker"
        - name: NOETL_PLAYBOOK_PATH
          value: "/opt/noetl/playbooks/example_playbook.yaml"
        - name: NOETL_PLAYBOOK_VERSION
          value: ""  # Optional
        # ... other environment variables
```

### CLI Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: noetl-cli
  labels:
    app: noetl
    component: cli
spec:
  replicas: 1
  selector:
    matchLabels:
      app: noetl
      component: cli
  template:
    metadata:
      labels:
        app: noetl
        component: cli
    spec:
      containers:
      - name: noetl-cli
        image: noetl:latest
        env:
        - name: NOETL_RUN_MODE
          value: "cli"
        # ... other environment variables
```

### Server Stop Job

To stop a running NoETL server, you can create a Kubernetes job:

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: noetl-server-stop
spec:
  template:
    spec:
      containers:
      - name: noetl-stop
        image: noetl:latest
        env:
        - name: NOETL_RUN_MODE
          value: "server-stop"
        - name: NOETL_FORCE_STOP
          value: "true"
      restartPolicy: Never
  backoffLimit: 1
```

You can run this job with:

```bash
kubectl apply -f noetl-server-stop-job.yaml
```

Once the job completes, you can delete it:

```bash
kubectl delete job noetl-server-stop
```

## Using the CLI Mode in Docker/Kubernetes

When running in CLI mode, the container will stay alive but won't start any server or worker processes. You can then execute commands using:

```bash
# Docker
docker exec -it <container_name> noetl <command>

# Kubernetes
kubectl exec -it <pod_name> -- noetl <command>
```

For example:

```bash
# List playbooks
kubectl exec -it noetl-cli-pod -- noetl catalog list playbook

# Execute a playbook
kubectl exec -it noetl-cli-pod -- noetl execute /opt/noetl/playbooks/example.yaml
```