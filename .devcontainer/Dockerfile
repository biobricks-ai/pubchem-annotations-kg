FROM mcr.microsoft.com/devcontainers/python:3.9

# Install necessary packages
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    xvfb \
    libxi6 \
    libgconf-2-4 \
    libnss3-dev \
    libxss1 \
    libappindicator1 \
    fonts-liberation \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    libgbm1 \
    libasound2 \
    libdpkg-perl \
    libatomic1 \
    ca-certificates \
    curl \
    gnupg \
    python3-venv \
    awscli \
    build-essential \
    git \
    liblzma-dev \
    zlib1g-dev \
    libserd-0-0 \
    libserd-dev \
    default-jre \
    maven \
    libboost-all-dev && \
    rm -rf /var/lib/apt/lists/* && \
    git clone https://github.com/rdfhdt/hdt-java.git /opt/hdt-java
    # git clone https://github.com/rdfhdt/hdt-cpp.git /opt/hdt-cpp

# Install pipx and biobricks
RUN python3 -m pip install --user pipx \
    && python3 -m pipx ensurepath

# Create /mnt/biobricks directory and set permissions
RUN mkdir -p /mnt/biobricks/biobricks-ai \
    && chown -R vscode:vscode /mnt/biobricks

# Add pipx binaries to the PATH for all users
RUN echo 'export PATH="$PATH:$HOME/.local/bin"' >> /etc/bash.bashrc \
    && echo 'export PATH="$PATH:$HOME/.local/bin"' >> /home/vscode/.bashrc

# Switch to vscode user to perform user-specific installations
USER vscode

# Install pybind11 separately because of dependency issues
RUN pip install pybind11==2.13.6

# Install Python dependencies
COPY .devcontainer/requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

# Accept build argument for BIOBRICKS_TOKEN & set to the default value if it is not given.
ARG BIOBRICKS_TOKEN
ENV DEFAULT_TOKEN=VQF6Q2U-NKktZ31ioVYa9w
ENV BIOBRICKS_TOKEN=${BIOBRICKS_TOKEN:-${DEFAULT_TOKEN}}
RUN if [ ${#BIOBRICKS_TOKEN} -lt 5 ]; then export BIOBRICKS_TOKEN=$DEFAULT_TOKEN; fi

# # Download get-pip.py using curl
# WORKDIR /tmp
# RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py

# # Install pip using the downloaded script
# RUN python3 get-pip.py

# # Install Meson via pip
# RUN python3 -m pip install meson

# # Clean up temporary files
# RUN rm get-pip.py

# # Return to the original working directory
# WORKDIR /

# Install biobricks and configure it
RUN /bin/bash -c 'source /etc/bash.bashrc && pipx install biobricks && biobricks version' \
    && /bin/bash -c 'if [ -z "$BIOBRICKS_TOKEN" ] || [ ${#BIOBRICKS_TOKEN} -lt 5 ]; then echo "BIOBRICKS_TOKEN is not set or is too short (less than 5 characters)"; exit 1; fi' \
    && /bin/bash -c 'source /etc/bash.bashrc && biobricks configure --bblib=/mnt/biobricks --token=${BIOBRICKS_TOKEN} --interactive=False'

RUN /bin/bash -c 'biobricks install https://github.com/biobricks-ai/pubchem-annotations#3b1b417e43b17b6caf75a730f8c4119aa76f8c16'

# Switch back to root user to complete setup
USER root

# Build and install hdt-java
# this part took quite long for me, probably a better way to install
WORKDIR /opt/hdt-java
RUN mvn install

# # Build and install hdt-cpp
# WORKDIR /opt/hdt-cpp
# RUN ./autogen.sh && \
#     ./configure && \
#     make -j2 && \
#     make install && \
#     ldconfig && \
#     cd / && \
#     rm -rf /opt/hdt-cpp

# Return to the previous WORKDIR (e.g., root)
WORKDIR /

# # Download and install serd
# RUN 'git clone https://github.com/drobilla/serd.git /tmp/serd' \
#     && 'cd /tmp/serd && meson setup build && cd build && meson compile && yes | meson install && cd -' \
#     && 'rm -rf /tmp/serd'

# # Download and install hdt-cpp
# RUN 'git clone https://github.com/rdfhdt/hdt-cpp.git /tmp/hdt-cpp' \
#     && 'cd /tmp/hdt-cpp && ./autogen.sh && ./configure && make -j2 && sudo make install && cd -' \
#     && 'rm -rf /tmp/hdt-cpp'

# # Run ldconfig to update the shared library cache
# RUN sudo ldconfig

