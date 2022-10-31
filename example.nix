{ token, username, pkgs ? import <nixpkgs> {} }:

with pkgs;

mkShell {
  buildInputs = [
    (python3.withPackages (p: [p.requests]))
    (factorio.override {
      inherit token username;
      releaseType = "alpha";
      mods = (let m = import ./mods.nix { inherit token username factorio-utils lib fetchurl; }; in [
        m.factoryplanner
        m.FNEI
        m.AfraidOfTheDark
        m.AutoDeconstruct
        m.even-distribution
        m.Todo-List
        m.YARM
        m.sonaxaton-research-queue
      ]);
    })
];
}
