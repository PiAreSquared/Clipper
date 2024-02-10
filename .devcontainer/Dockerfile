FROM mcr.microsoft.com/devcontainers/base:ubuntu

# install pip package manager
RUN apt-get update && apt-get install -y python3-pip
RUN python3 -m pip install --upgrade pip

# install act (for CI testing)
RUN curl -fsSL https://get.docker.com | sh
RUN curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash