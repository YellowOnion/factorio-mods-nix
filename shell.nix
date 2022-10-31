{ pkgs ? import <nixpkgs> {} }:

with pkgs;

mkShell {
  buildInputs = [
    (python3.withPackages (p: [p.requests]))
];
}
