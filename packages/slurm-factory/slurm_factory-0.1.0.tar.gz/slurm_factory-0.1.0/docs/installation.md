---
layout: default
title: Installation Guide
nav_order: 2
permalink: /installation/
---

# Installation Guide

Coming soon! For now, please refer to the [README.md](https://github.com/vantagecompute/slurm-factory/blob/dev/README.md) for installation instructions.

## Quick Start

```bash
# Install LXD and UV
sudo snap install lxd && sudo lxd init
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and setup
git clone https://github.com/vantagecompute/slurm-factory.git
cd slurm-factory && uv sync

# Build latest Slurm
uv run slurm-factory build
```

For detailed installation instructions, please see the [project README](https://github.com/vantagecompute/slurm-factory/blob/dev/README.md).
