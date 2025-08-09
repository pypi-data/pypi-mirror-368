#!/usr/bin/env bash
set -euo pipefail

default_list=(
  lighting_logs
  mlruns
  multirun
  outputs
  '*.log'
)
exclude_list=(
  venv/
  __pycache__/
  '*.pyc'
)

if [[ $# -lt 2 ]]
then
  cat >&2 << HELP
USAGE

  ${0##*/} [rsync options] <source> <destination>

Copy the results files from the source directory to the destination via rsync.
If the source directory is in a Git repository then the untracked files will be
copied with the following exclusions:

$(printf -- '- %s\n' "${exclude_list[@]}")

If the source directory is not part of a Git repository then the following paths
will be included:

$(printf -- '- %s\n' "${default_list[@]}")
HELP
  exit 1
fi

args=("$@")
src=${args[-2]}
dest=${args[-1]}
unset 'args[-1]'
unset 'args[-1]'

src_host=${src%%:*}
src_path=${src#*:}

# Check if the source is accessed via SSH.
if [[ $src_host != "$src" ]]
then
  cmd_prefix=(ssh "$src_host")
else
  cmd_prefix=()
  src_path=$src
fi

tmp_path=$(mktemp)
trap "rm ${tmp_path@Q}" EXIT

cmd=(rsync -rtL)
if "${cmd_prefix[@]}" git -C "$src_path" rev-parse --is-inside-work-tree >/dev/null 2>&1
then
  "${cmd_prefix[@]}" git -C "$src_path" ls-files --others . -- "${exclude_list[@]/#/:\!:}" > "$tmp_path"
  cmd+=(--files-from "$tmp_path")
else
  printf '%s\n' "${default_list[@]}" > "$tmp_path"
  cmd+=(--include='*' --include-from "$tmp_path" --exclude='*')
fi
cmd+=("${args[@]}" "$src" "$dest")
echo "${cmd[*]@Q}"
"${cmd[@]}"
