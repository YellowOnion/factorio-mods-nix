{ factorioMods ?  import (builtins.fetchTarball "http://github.com/YellowOnion/factorio-mods-nix/archive/master.tar.gz")
, config, pkgs, ...}: {
  disabledModules = [ "services/games/factorio.nix" ];
  imports = [
      factorioMods.nixosModules.default
  ];

  nixpkgs.config.allowUnfree = true;
  nixpkgs.overlays = [
    factorioMods.overlays.default
  ];

  services.factorio = {
    enable = true;
    game-name = "Example";
    mods = builtins.attrValues {
      inherit (factorioMods.packages.${pkgs.system})
        "AfraidOfTheDark"
        "even-distribution"
        "QuickItemSearch"
        "RateCalculator"
        "sonaxaton-research-queue"
        "StatsGui"
        "TaskList"
      ;};
  };
}
