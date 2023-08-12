# This is an up to date repo for most Factorio 1.1 mods.

The motivation for this repo is the nixpkgs module stores your authentication information in the nix store, which is readable to every user on the machine.

Commit 3d870d11f421ee147dd1275f73810b28bc3fd792 works with vanilla nixpkgs until my repo is merged, it is not as secure as this version, it will store your password inside the derivation until you collect your garbage.

> [!IMPORTANT]
> Make sure your player-data.json file is accessible to the nix-daemon, use extra-sandbox-paths in your nix.conf or by using --option and make sure the nixbld group can access the file. the default location inside the sandbox is /fpd.json

For maximum compatibility I use a filter system that removes mods and dependencies that are not 1.1 compatible.
This prevents infinite recursion that older mods tend to have, and since some mods also make a reference to older mods, they need to be filtered out, I would prefer to support older mods, but I do not have a sophisticated way of removing the cyclic dependencies yet. Factorio mods will break at runtime if any of the mods are not compatible with v1.1 and have been removed from this repo.

feel free to alter the script to your needs, and if you want to add better cycle detection, I'll definitely accept a PR for that.

## how to use

This version currently needs a custom version of the Factorio module from nixpkgs, it is available as a fork of [nixpkgs](https://github.com/YellowOnion/nixpkgs/tree/factorio-patch2)

You can use this by disabling the nixpkgs version of the Factorio module, and importing mine instead, and providing the `factorio-utils` package in an overlay.

``` nix
let
  factorio-nixpkgs-dir = builtins.fetchTarball "http://github.com/YellowOnion/nixpkgs/archive/factorio-patch2.tar.gz";
  factorio-nixpkgs = import factorio-nixpkgs-dir { config.allowUnfree = true; };
in
{
  disabledModules = [ "services/games/factorio.nix" ];
  imports = [
      "${factorio-nixpkgs-dir}/nixos/modules/services/games/factorio.nix"
      ];

  nixpkgs.overlays = [
    (self: super: {
      factorio-utils    = factorio-nixpkgs.factorio-utils;
    })
  ];
}
```

You then need to import this repo with, `fix`, `filterMissing` from my nixpkgs, and providing a path to your `player-data.json` file, this will be in `~/.factorio/player-data.json`for steam clients, `<game folder>/player-data.json` for the installer from the official site, in your `config.services.factorio.stateDir` directory (by default: `/var/lib/factorio`) for the nixos server module.

checkout `example.nix` for comprehensive usage of the modding system and new auth system in nixpkgs.

``` shell
$ chmod go-rw ~/.factorio/player-data.json
$ cp -p ~/.factorio/player-data.json /tmp/fpd.json
$ setfacl -m g:nixbld:r ~/tmp/fpd.json
$ nix-build example.nix -A factorio --option extra-sandbox-paths '/fpd.json=/tmp/fpd.json'
$ rm /tmp/fpd.json
```


## support
Feel free to open an issue or @woobilicious on the unofficial NixOS discord if you need help.
