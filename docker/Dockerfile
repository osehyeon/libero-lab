# Linux render box for LIBERO-Plus gallery tiles.
# Mesa's OSMesa renders on the CPU, so nothing goes through Apple's OpenGL.
# gcc + kernel headers: robosuite pulls pynput, which builds evdev from source.
FROM python:3.10-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
        libosmesa6 libgl1 libglib2.0-0 libmagickwand-dev \
        gcc libc6-dev linux-libc-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
        "numpy<2" "robosuite==1.4.1" "mujoco==2.3.7" "bddl==1.0.1" \
        easydict "hydra-core==1.2.0" opencv-python-headless "gym==0.25.2" \
        matplotlib cloudpickle future einops thop termcolor imageio h5py \
        tqdm psutil pillow scikit-image wand PyOpenGL \
    && pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu \
    && pip install --no-cache-dir --no-deps "robomimic==0.3.0"

ENV MUJOCO_GL=osmesa PYOPENGL_PLATFORM=osmesa
