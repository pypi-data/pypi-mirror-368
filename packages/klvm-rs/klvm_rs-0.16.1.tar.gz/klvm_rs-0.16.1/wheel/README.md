Rust implementation of klvm.

![GitHub](https://img.shields.io/github/license/Chik-Network/klvm_rs?logo=Github)
[![Coverage Status](https://coveralls.io/repos/github/Chik-Network/klvm_rs/badge.svg?branch=main)](https://coveralls.io/github/Chik-Network/klvm_rs?branch=main)
![Build Crate](https://github.com/Chik-Network/klvm_rs/actions/workflows/build-crate.yml/badge.svg)
![Build Wheels](https://github.com/Chik-Network/klvm_rs/actions/workflows/build-test.yml/badge.svg)

![PyPI](https://img.shields.io/pypi/v/klvm_rs?logo=pypi)
[![Crates.io](https://img.shields.io/crates/v/klvmr.svg)](https://crates.io/crates/klvmr)

The cargo workspace includes an rlib crate, for use with rust or other applications, and a python wheel.

The python wheel is in `wheel`. The npm package is in `wasm`.

## Tests

In order to run the unit tests, run:

```
cargo test
```

## Fuzzing

The fuzzing infrastructure for `klvm_rs` uses [cargo-fuzz](https://github.com/rust-fuzz/cargo-fuzz).

Documentation for setting up fuzzing in rust can be found [here](https://rust-fuzz.github.io/book/cargo-fuzz.html).

To generate an initial corpus (for the `run_program` fuzzer), run:

```
cd tools
cargo run generate-fuzz-corpus
```

To get started, run:

```
cargo fuzz run fuzz_run_program --jobs=32 -- -rss_limit_mb=4096
```

But with whatever number of jobs works best for you.

If you find issues in `klvm_rs` please use our [bug bounty program](https://hackerone.com/chik_network).

## Build Wheel

The `klvm_rs` wheel has python bindings for the rust implementation of klvm.

Use `maturin` to build the python interface. First, install into current virtualenv with

```
$ pip install maturin
```

While in the `wheel` directory, build `klvm_rs` into the current virtualenv with

```
$ maturin develop --release
```

On UNIX-based platforms, you may get a speed boost on `sha256` operations by building
with OpenSSL.

```
$ maturin develop --release --features=openssl
```

To build the wheel, do

```
$ maturin build --release
```

or

```
$ maturin build --release --features=openssl
```

## Bumping Version Number

Make sure you have `cargo-workspaces` installed:

```bash
cargo install cargo-workspaces
```

To bump the versions of all relevant crates:

```bash
cargo ws version --force "**" --all --no-git-commit
```

Select "minor update" if there has not been any incompatible API changes, otherwise "major update".
