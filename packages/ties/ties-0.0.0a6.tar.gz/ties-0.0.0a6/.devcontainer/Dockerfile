FROM mcr.microsoft.com/devcontainers/base:debian AS default
USER vscode
COPY ./.devcontainer/install-go.sh ./
ENV GOPATH=/home/vscode/go
ENV PATH="/home/vscode/.local/bin/:/home/vscode/.local/go/bin/:/github/home/.local/bin:/github/home/.local/go/bin:$GOPATH/bin:$PATH"
RUN --mount=type=cache,dst=/root/.cache/ \
    echo uv && curl -LsSf https://astral.sh/uv/install.sh | sh && \
    chmod +x $HOME/.local/bin/uv $HOME/.local/bin/uvx && \
    echo trivy && curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b $HOME/.local/bin v0.65.0 && \
    chmod +x $HOME/.local/bin/trivy && \
    echo taplo && curl -fsSL https://github.com/tamasfe/taplo/releases/latest/download/taplo-linux-$(uname -m).gz \
    | gzip -d - | install -m 755 /dev/stdin $HOME/.local/bin/taplo && \
    echo go && ./install-go.sh
RUN --mount=type=cache,dst=/root/.cache/ \
    uv self update && uvx --version && trivy --version && taplo --version && go version && \
    go install github.com/isaacphi/mcp-language-server@latest && mcp-language-server --help

USER root

COPY dev-pyproject/ ./
RUN --mount=type=cache,dst=/root/.cache/ \
    DEBIAN_FRONTEND=noninteractive mkdir -p /home/vscode/.cache && chmod 777 /home/vscode/.cache && \
    echo apt-tools && apt-get update && apt-get upgrade -y --no-install-recommends && \
    apt-get install -y --no-install-recommends apt-transport-https \
    ca-certificates gnupg curl pkg-config cmake libssl-dev git expect && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    echo nodejs && apt-get install -y --no-install-recommends nodejs && npm install -g npm@latest && node -v && npm -v && \
    echo claude && npm install -g @anthropic-ai/claude-code && claude --version && \
    echo pyright && npm install -g pyright && pyright --version && \
    echo repomix && npm install -g repomix && repomix --version

COPY ./.devcontainer/migrate_claude.exp ./
USER vscode
RUN expect migrate_claude.exp
