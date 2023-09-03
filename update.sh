#!/run/current-system/sw/bin/env nix-shell
#! nix-shell -i bash shell.nix

cd "$(dirname "${BASH_SOURCE[0]}")"

TOKEN=$(cat token)
DATE=$(date  --iso-8601)

mkdir -p mods

rm mods.json

[ -z ${SKIPGEN+x} ] && ./generator.py > mods.nix 2>/dev/null

$(nix eval --impure --raw --expr '"${<nixpkgs>}/pkgs/games/factorio/update.py"') \
    --username woobilicious \
    --token $TOKEN


git add versions.json

nix eval --impure --expr 'let x = import ./mods.nix ; in x' || exit $?

git add mods.nix

git commit -m "auto update: $DATE"

git push origin
