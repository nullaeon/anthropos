# Anthropos

A containerized research environment for a simulated bipedal humanoid robot. It bundles
a [MuJoCo](https://mujoco.org/) physics model, a [ROS 2 Humble](https://docs.ros.org/en/humble/)
control stack, a deep-RL / robotics-learning Python ecosystem, and OpenSCAD for parametric
CAD — all behind a single GPU-enabled Docker image so the whole toolchain runs reproducibly
on a fresh machine.

## What's inside

| Component | Description |
|-----------|-------------|
| **`anthropos.xml`** | MuJoCo MJCF model — a torso on a free joint with two articulated legs (hip / knee / ankle), motor actuators on the hips and knees. |
| **`ros2_ws/`** | ROS 2 workspace with the `anthropos_control` package: a state manager, a controller, and a signal injector for driving experiments. See [`ros2_ws/README.md`](ros2_ws/README.md). |
| **`requirements.txt`** | Python stack: MuJoCo, Gymnasium, Stable-Baselines3, PettingZoo/SuperSuit, PyTorch, Transformers/PEFT/TRL, boto3, and more. |
| **`tools_test/`** | Integration tests (e.g. headless OpenSCAD rendering via Xvfb). |
| **`Dockerfile`** | Ubuntu 22.04 image with ROS 2 Humble, MuJoCo 3.1.2, OpenSCAD, Bazel, AWS CLI, and the Python stack. |

## The ROS 2 control stack

The `anthropos_control` package implements a small state machine over standard ROS 2 topics:

- **`state_manager`** — tracks robot state (`IDLE` → `PLANNING` → `EXECUTING`). Publishes
  `/robot_state`, subscribes to `/state_transition`.
- **`controller`** — updates the robot pose based on state. Subscribes to `/robot_state`,
  publishes `/robot_pose`. Pose advances while `EXECUTING`, holds otherwise.
- **`injector`** — drives the state machine automatically by cycling transitions on a timer,
  so experiments run without manual `ros2 topic pub`.

Full node/topic details and run instructions are in [`ros2_ws/README.md`](ros2_ws/README.md).

## Getting started

### Prerequisites

- Docker with NVIDIA GPU support (the `dev.sh` workflow uses `--gpus all`). For a clean
  install of Docker + the NVIDIA Container Toolkit, follow [`GPUSETUP.md`](GPUSETUP.md).
- An NVIDIA GPU + drivers on the host (optional, but assumed by `dev.sh`).

### Build the image

```bash
sudo ./build.sh        # docker build -t anthropos .
```

### Run a dev container

```bash
sudo ./dev.sh
```

`dev.sh` runs the `anthropos` image interactively with:

- the GPU passed through (`--gpus all`),
- the repo bind-mounted at `/workspace`,
- the host user's UID/GID (volumes stay writable without `sudo`),
- read-only AWS credentials from `~/.aws`,
- X11 forwarding for on-screen viewers.

Environment variables are read from `.env` (create one if you need custom settings).

### Run the ROS 2 harness

Inside the container:

```bash
cd ros2_ws
colcon build
source install/setup.bash
ros2 launch anthropos_control harness.launch.py
```

This starts the state manager, controller, and injector together. Watch the system from
another shell:

```bash
ros2 topic echo /robot_state
ros2 topic echo /robot_pose
```

## Visualizing the MuJoCo model

On the host, allow the container to reach your X server:

```bash
xhost +local:docker
```

Then, inside the dev container:

```bash
python3 -m mujoco.viewer --mjcf anthropos.xml
```

See [`VISUALIZE.md`](VISUALIZE.md) for details.

## Tests

```bash
python3 tools_test/test_openscad.py    # verifies headless OpenSCAD rendering
```

## Container registry

The image is published to [Quay.io](https://quay.io/) as `quay.io/nullaeon/anthropos:latest`.

```bash
./push.sh      # build, tag, and push to Quay
./pull.sh      # pull the latest image and start a container
./remove.sh    # stop and remove the running anthropos container
```

## Local (non-Docker) install

To install just the Python dependencies on the host:

```bash
./install.sh   # apt install python3-pip && pip3 install -r requirements.txt
```

> The fully reproducible path is the Docker image — the local install does not provide
> ROS 2, MuJoCo binaries, or OpenSCAD.

## Repository layout

```
anthropos/
├── anthropos.xml        # MuJoCo MJCF humanoid model
├── Dockerfile           # Ubuntu 22.04 + ROS 2 + MuJoCo + ML stack
├── requirements.txt     # Python dependencies
├── entrypoint.sh        # sources ROS 2, drops to host UID/GID
├── build.sh / dev.sh    # build and run the dev container
├── push.sh / pull.sh / remove.sh   # Quay.io image management
├── install.sh           # host-side Python install
├── GPUSETUP.md          # Docker + NVIDIA toolkit setup
├── VISUALIZE.md         # MuJoCo viewer instructions
├── ros2_ws/             # ROS 2 workspace (anthropos_control package)
└── tools_test/          # integration tests
```
