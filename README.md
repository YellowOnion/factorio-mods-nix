# This is an up to date repo for most Factorio 1.1 mods.

The motivation for this repo is the nixpkgs module stores your authentication information in the nix store, which is readable to every user on the machine.

Commit 3d870d11f421ee147dd1275f73810b28bc3fd792 works with vanilla nixpkgs until my repo is merged, it is not as secure as this version, it will store your password inside the derivation until you collect your garbage.

> [!IMPORTANT]
> Make sure your player-data.json file is accessible to the nix-daemon, use extra-sandbox-paths in your nix.conf or by using --option and make sure the nixbld group can access the file. the default location inside the sandbox is /fpd.json

For maximum compatibility I use a filter system that removes mods and dependencies that are not 1.1 compatible.
This prevents infinite recursion that older mods tend to have, and since some mods also make a reference to older mods, they need to be filtered out, I would prefer to support older mods, but I do not have a sophisticated way of removing the cyclic dependencies yet. Factorio mods will break at runtime if any of the mods are not compatible with v1.1 and have been removed from this repo.

feel free to alter the script to your needs, and if you want to add better cycle detection, I'll definitely accept a PR for that.

## how to use

This is now a flake providing `nixosModules.default` `packages.*` and `overlays.default` and `nixosConfigurations.example`
You can use this by disabling the nixpkgs version of the Factorio module, and importing mine instead, and providing the overlay, and then listing packages:

See `example.nix` for a full NixOS Configuration example

``` shell
$ chmod go-rw ~/.factorio/player-data.json
$ cp -p ~/.factorio/player-data.json /tmp/fpd.json
$ setfacl -m g:nixbld:r ~/tmp/fpd.json
$ nixos-rebuild switch --option extra-sandbox-paths '/fpd.json=/tmp/fpd.json'
$ rm /tmp/fpd.json
```


## support
Feel free to open an issue or @woobilicious on the unofficial NixOS discord if you need help.

## TODO
* Propose to Factorio team to update the api to include just enough info (sha256?) so I only have to send 1 request instead of 3000+ and extremely minimize the amount of time this script takes to work (currently > 10mins) when cache isn't populated.
* provide more robust caching so we don't have to nerf mods/ (we current don't check if they're stale.)
* post RFC in the nix discourse to get it upstreamed.
* add support for agenix or other secret systems.
