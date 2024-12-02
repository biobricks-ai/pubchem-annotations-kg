FROM nixos/nix

# Enable flakes
RUN mkdir -p ~/.config/nix && \
    echo "experimental-features = nix-command flakes" >> ~/.config/nix/nix.conf

# Create and set working directory
WORKDIR /app

# Copy your flake files
COPY flake.nix flake.lock ./

# Build the development environment
RUN nix develop --command echo "Development environment ready"

# Default command to drop into the dev shell
ENTRYPOINT ["nix", "develop"]
CMD ["/bin/bash"]
