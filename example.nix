let
  pkgs = import (builtins.fetchTarball "http://github.com/YellowOnion/nixpkgs/archive/factorio-patch2.tar.gz") { config.allowUnfree = true; };
  utils = pkgs.factorio-utils;
  mods =  import ./mods.nix {
    inherit (pkgs.lib) fix;
    inherit (utils) filterMissing;
    factorioMod = utils.factorioMod "/fpd.json";
  };
  modList = builtins.attrValues { inherit (mods)
        AfraidOfTheDark
        even-distribution
        QuickItemSearch
        RateCalculator
        sonaxaton-research-queue
        StatsGui
        TaskList
    ;};
  modsPack = utils.mkModDirPackage modList null "test";
in {
  modsPack = modsPack;
  modsZip = utils.mkModZipPackage modsPack;
  factorio = pkgs.factorio.override ({versionJson = ./versions.json ;});
}
