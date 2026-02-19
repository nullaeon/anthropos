# Visualization setup
## Steps before running sudo ./dev.sh
Run the following on the host machine: 
`xhost +local:docker`

Then in the dev docker, run:
`python3 -m mujoco.viewer --mjcf anthropos.xml`