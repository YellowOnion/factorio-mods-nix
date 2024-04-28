{
  description = "factorio mods";
  inputs = {
    nixpkgs.url = "nixpkgs/nixos-unstable";
    flake-compat.url = "https://flakehub.com/f/edolstra/flake-compat/1.tar.gz";
    typed-systems = {
      url = "github:YellowOnion/nix-typed-systems";
      flake = false;
    };
  };

  outputs = { self, typed-systems, nixpkgs, ... }:
    let
      inherit (import typed-systems) id genAttrsMapBy systems';
      systems = [ systems'.x86_64-linux ]; # include arm mac?
      overlay = self: super:
          let v = { versionsJson = ./versions.json ;};
          in {
            factorio = super.factorio.override v;
            factorio-headless = super.factorio-headless.override v;
            factorio-utils = self.pkgs.callPackage ./utils.nix {};
          };
      mods = pkgs: ((import ./mods.nix) {
        inherit (pkgs.factorio-utils) filterMissing;
        inherit (pkgs.lib) fix;
        factorioMod = pkgs.factorio-utils.factorioMod "/fpd.json";
      });
    in
    {
      packages = (genAttrsMapBy id (system:
        let pkgs = import nixpkgs {
              inherit system;
              overlays = [ overlay ];
            };
        in (mods pkgs) // {
          inherit (pkgs) factorio factorio-headless factorio-utils;
          default = pkgs.factorio;
        }
      ) systems id);
      overlays.default = overlay;
      nixosModules.default = ./module.nix;

      nixosConfigurations = genAttrsMapBy (a: "example")
        (system: nixpkgs.lib.nixosSystem {
        inherit system;
        specialArgs = { factorioMods = self; };
        modules = [ ./example.nix ];
      }) systems id;
    };
}
