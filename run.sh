#!/bin/bash
# 简化运行脚本
export PYTHONPATH=src
uv run python -m video_progress_pkg.cli "$@"


