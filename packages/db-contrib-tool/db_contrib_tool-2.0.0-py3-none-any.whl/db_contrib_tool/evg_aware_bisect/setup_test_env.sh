set -e
db-contrib-tool setup-repro-env \
  --evergreenConfig "$2" \
  --downloadArtifacts \
  --installDir build/resmoke-bisect \
  --linkDir build/resmoke-bisect/"$4" \
  --variant "$3" \
  "$4"
"$1" -m venv build/resmoke-bisect/bisect_venv
source build/resmoke-bisect/bisect_venv/bin/activate

version="$4"
artifact_dir=${version##*_}

dev_requirements="$(find build/resmoke-bisect/$artifact_dir -wholename '*/etc/pip/dev-requirements.txt')"
poetry_sync_script="$(find build/resmoke-bisect/$artifact_dir -wholename '*/buildscripts/poetry_sync.sh')"

if [[ -n $dev_requirements ]]; then
  # If dev-requirements.txt exists, we are on an old branch that uses pip.
  "$1" -m pip install --upgrade pip
  "$1" -m pip install -r $dev_requirements

elif [[ -n $poetry_sync_script ]]; then
  # If poetry_sync.sh exists, use it to setup the env.
  (cd build/resmoke-bisect/"$artifact_dir"/src && . buildscripts/poetry_sync.sh -p `which python3`)

else
  # Otherwise, try a plain poetry install.
  "$1" -m pip install poetry==2.0.0
  (cd build/resmoke-bisect/"$artifact_dir"/src && "$1" -m poetry install --no-root --sync)

fi
deactivate
