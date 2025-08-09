#!/usr/bin/env bash
set -euo pipefail

SELF=$(readlink -f "${BASH_SOURCE[0]}")
source "${SELF%/*/*}/env.sh"

venv_dir=$HYDRONAUT_DEFAULT_VENV_DIR

function show_help()
{
  cat <<HELP
SYNOPSIS

  Run hydronaut-run in a virtual environment in the current directory. It will
  perform the following actions:

  1. Create the virtual environment (venv) if it is missing.
  2. Activate the venv.
  3. Install Hydronaut.
  4. If the current directory contains a pyproject.toml file, install the
     directory in the virtual environment.
  5. Otherwise, if the current directory contains a requirements.txt file,
     install the requirements in the virtual environment.
  6. Run hydronaut-run in the current directory.

  This script is useful for batching jobs on a cluster or for setting up the
  virtual environment. For interactive use, it is recommended to activate the
  virtual environment and run hydronaut-run directly.

USAGE

  ${0##*/} [--help] [--upgrade] [--venv <venv dir>] [<hydronaut-run args>]

OPTIONS

  --help
    Show this message and exit.

  --upgrade
    Pass the --upgrade flag when installing packages with pip.
    
  --venv <venv dir>
    Use the virtual environment located at <venv dir>. If it does not exist then
    it will be created.

    Default:
      $venv_dir

  <hr-run args>
    All other arguments are passed through to hydronaut-run.
    
HELP
  exit "$1"
}

hf_run_args=()
install_cmd=(pip3 install)
install_in_venv_args=()
while [[ ${#@} -gt 0 ]]
do
  arg=$1
  shift
  case "$arg" in
    --help)
      show_help 0
      ;;
    --upgrade)
      install_cmd+=(--upgrade)
      install_in_venv_args+=(-u)
      ;;
    --venv)
      venv_dir=$(readlink -f "$1")
      install_in_venv_args+=(-v "$venv_dir")
      shift
      ;;
    *)
      hf_run_args+=("$arg")
  esac
done

"$HYDRONAUT_DIR/scripts/hydronaut-install_in_venv.sh" "${install_in_venv_args[@]}"

if [[ -z ${VIRTUAL_ENV:+x} ]]
then
  source "$venv_dir/bin/activate"

elif [[ ! -e $VIRTUAL_ENV ]]
then
  echo "ERROR: Virtual environment $VIRTUAL_ENV is active but it no longer exists." >&2
  exit 1

else
  echo "WARNING: Using active virtual environment: $VIRTUAL_ENV" >&2
fi

# Install the package in the runtime directory if there is one, or any
# requirements specified by the requirements.txt file.
if [[ -e pyproject.toml ]]
then
  "${install_cmd[@]}" .
elif [[ -e requirements.txt ]]
then
  "${install_cmd[@]}" -r requirements.txt
fi

# Run the Hydronaut experiment with the given command-line arguments.
hydronaut-run "${hf_run_args[@]}"
