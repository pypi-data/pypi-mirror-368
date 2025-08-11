# Contributing

Thanks for your interest in contributing!

## Prerequisites

- Rust toolchain (stable)
- cargo-make (provides the `makers` command)
  - Install via cargo: `cargo install cargo-make`
  - or via Homebrew (macOS): `brew install cargo-make`
- Python 3 and optionally `uv`
  - For E2E, ensure `grpcio-tools` is available to your `python_exe`
    - Example with uv: `uv pip install grpcio-tools`
    - Example with pip: `python3 -m pip install grpcio-tools`

## Dev Workflow

- Run formatting and lint before committing (requires `cargo-make`):
  ```bash
  makers format
  makers lint
  ```
  - Alternatively, without cargo-make:
    ```bash
    cargo fmt --all
    cargo clippy --all-targets --all-features -- -Dwarnings
    ```
- Build and run tests:
  ```bash
  makers build
  makers test
  ```
  - Alternatively, without cargo-make:
    ```bash
    cargo build --all-targets
    cargo test --all
    ```

## Commit style

- Keep messages concise and focused on intent. Use conventional prefixes where appropriate (feat, fix, docs, test, refactor, chore).
