#!/usr/bin/env bash

set -eo pipefail

get_binary_name() {
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        echo "hyperfusion.exe"
    else
        echo "hyperfusion"
    fi
}

get_platform_info() {
    local system=$(uname -s | tr '[:upper:]' '[:lower:]')
    local arch=$(uname -m)

    case "$arch" in
        x86_64|amd64)
            arch="x86_64"
            ;;
        aarch64|arm64)
            arch="arm64"
            ;;
        arm*)
            arch="arm64"
            ;;
    esac
    
    echo "${system}-${arch}"
}

build_rust_binary() {
    local project_root="$1"
    local rust_dir="${project_root}/hyperfusion-rs"
    
    if [[ ! -d "$rust_dir" ]]; then
        echo "Error: Rust project not found at $rust_dir" >&2
        exit 1
    fi

    (cd "$rust_dir" && cargo build --release)
    
    local binary_name=$(get_binary_name)
    local binary_path="${rust_dir}/target/release/${binary_name}"
    
    if [[ ! -f "$binary_path" ]]; then
        echo "Error: Built binary not found at $binary_path" >&2
        exit 1
    fi

    return 0
}

copy_binary_to_package() {
    local binary_path="$1"
    local package_root="$2"
    local binaries_dir="${package_root}/src/hyperfusion/binaries"

    mkdir -p "$binaries_dir"

    local platform_info=$(get_platform_info)
    local binary_name=$(get_binary_name)

    local base_name="${binary_name%.*}"
    local platform_binary_name="${base_name}-${platform_info}"
    if [[ "$binary_name" == *.exe ]]; then
        platform_binary_name="${platform_binary_name}.exe"
    fi
    
    local dest_path="${binaries_dir}/${platform_binary_name}"

    cp "$binary_path" "$dest_path"

    local generic_dest="${binaries_dir}/${binary_name}"
    cp "$binary_path" "$generic_dest"
}

main() {
    local script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    local package_root="$(dirname "$script_dir")"
    local project_root="$(dirname "$package_root")"

    build_rust_binary "$project_root"

    local rust_dir="${project_root}/hyperfusion-rs"
    local binary_name=$(get_binary_name)
    local binary_path="${rust_dir}/target/release/${binary_name}"

    copy_binary_to_package "$binary_path" "$package_root"
    
    echo "Build completed successfully!"
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi