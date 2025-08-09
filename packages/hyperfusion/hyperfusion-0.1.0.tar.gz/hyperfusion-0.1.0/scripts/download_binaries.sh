#!/usr/bin/env bash
# Script to download pre-built binaries from GitHub releases (for CI/CD)

set -eo pipefail

get_platform_info() {
    local system=$(uname -s | tr '[:upper:]' '[:lower:]')
    local arch=$(uname -m)
    
    # Normalize architecture names
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
    
    echo "${system} ${arch}"
}

get_binary_filename() {
    local system="$1"
    local arch="$2"
    
    if [[ "$system" == "windows" ]]; then
        echo "hyperfusion-${system}-${arch}.exe"
    else
        echo "hyperfusion-${system}-${arch}"
    fi
}

download_binary() {
    local repo="$1"
    local version="$2"
    local system="$3"
    local arch="$4"
    local dest_dir="$5"
    
    local binary_name=$(get_binary_filename "$system" "$arch")
    
    # Construct GitHub release URL
    local url
    if [[ "$version" == "latest" ]]; then
        url="https://api.github.com/repos/${repo}/releases/latest"
    else
        url="https://api.github.com/repos/${repo}/releases/tags/${version}"
    fi
    
    echo "Fetching release info from $url"
    
    # Get release data
    local release_data=$(curl -s "$url")
    
    # Find the matching asset URL
    local asset_url=$(echo "$release_data" | jq -r --arg pattern "${system}-${arch}" '
        .assets[] | 
        select(.name | contains($pattern)) | 
        .browser_download_url
    ' | head -n1)
    
    if [[ -z "$asset_url" || "$asset_url" == "null" ]]; then
        echo "No binary found for ${system}-${arch}. Available assets:"
        echo "$release_data" | jq -r '.assets[].name'
        exit 1
    fi
    
    # Download the binary
    echo "Downloading $asset_url"
    
    local dest_path="${dest_dir}/${binary_name}"
    mkdir -p "$dest_dir"
    
    curl -L "$asset_url" -o "$dest_path"
    
    # Make executable on Unix systems
    if [[ "$system" != "windows" ]]; then
        chmod +x "$dest_path"
    fi
    
    echo "Binary downloaded to $dest_path"
}

main() {
    if [[ $# -lt 1 ]]; then
        echo "Usage: $0 <repo> [version]"
        echo "Example: $0 hyperdance/hyperfusion latest"
        exit 1
    fi
    
    local repo="$1"
    local version="${2:-latest}"
    
    # Get platform info
    read system arch <<< $(get_platform_info)
    
    echo "Downloading binary for ${system}-${arch}"
    
    # Set destination directory
    local script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    local package_root="$(dirname "$script_dir")"
    local dest_dir="${package_root}/src/hyperfusion/binaries"
    
    # Check if jq is available
    if ! command -v jq &> /dev/null; then
        echo "Error: jq is required for JSON parsing"
        echo "Install with: brew install jq (macOS) or apt-get install jq (Ubuntu)"
        exit 1
    fi
    
    download_binary "$repo" "$version" "$system" "$arch" "$dest_dir"
    echo "Download completed successfully!"
}

# Run main function if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi