#!/usr/bin/env fish

function usage
    echo "Usage:"
    echo "  (basename (status current-filename)) --index <PYPI_INDEX_URL>"
    echo
    echo "Example:"
    echo "  ./parse_uv_lock.fish --index https://my.index/simple"
    exit 1
end

#
#   check_pypi <pkg_name> <pkg_version> <index_url>
#
#   1) Normalizes the package name to lowercase (naively) for the simple index
#   2) GETs <index_url>/<normalized_name>/
#   3) Looks for the version text
#
function check_pypi
    set pkg_name $argv[1]
    set pkg_version $argv[2]
    set index_url $argv[3]

    # Lowercase the name as a naive "normalization".
    # PEP 503 normalization might also replace underscores with dashes, etc.
    # Adjust if your private index requires more thorough normalization.
    set norm_name (string lower $pkg_name | string replace -r '_' '-')

    # Construct the URL: e.g. https://my.index/simple/<pkg>/
    set check_url "$index_url/$norm_name/"

    # Attempt to fetch HTML from the index
    set html (curl --fail --silent "$check_url")
    if test $status -ne 0
        echo " ❌  $pkg_name==$pkg_version => $check_url => not found or error fetching"
        return
    end

    # If we got HTML, we simply check if $pkg_version is in that text
    if echo $html | grep -q "$pkg_version"
        echo " ✅  $pkg_name==$pkg_version => found in $index_url"
    else
        echo " ❌  $pkg_name==$pkg_version => missing version in $index_url"
    end
end

#
#   parse_uv_lock <index_url>
#
#   Reads uv.lock, extracts name/version pairs, then calls check_pypi
#
function parse_uv_lock
    set lockfile uv.lock
    set pypi_url $argv[1]

    if not test -f "$lockfile"
        echo "Error: $lockfile not found!"
        return 1
    end

    # Temporaries for storing package name and version lines
    set -l pkg_name ""
    set -l pkg_version ""

    for line in (cat "$lockfile")
        # If line matches: name = "something"
        if string match -qr '^\s*name\s*=\s*".*"$' "$line"
            set segments (echo "$line" | string split '"')
            set pkg_name $segments[2]

            # If line matches: version = "something"
        else if string match -qr '^\s*version\s*=\s*".*"$' "$line"
            set segments (echo "$line" | string split '"')
            set pkg_version $segments[2]

            # We have name + version => print or check
            if test -n "$pkg_name"
                # Check if it’s on the custom PyPI index
                check_pypi $pkg_name $pkg_version $pypi_url

                # Clear them for the next [[package]] block
                set pkg_name ""
                set pkg_version ""
            end
        end
    end
end

#
#   Main script logic
#
if test (count $argv) -lt 2
    usage
end

set pypi_url ""
for idx in (seq 1 (count $argv))
    if test $argv[$idx] = --index
        set pypi_url $argv[(math $idx + 1)]
        break
    end
end

if test -z "$pypi_url"
    usage
end

# All set. Now parse uv.lock and check each package
parse_uv_lock "$pypi_url"

exit 0
