# This file provides a top-level function that will be used by both nixpkgs and nixos
# to generate mod directories for use at runtime by factorio.
{ lib, jq, zip, stdenvNoCC, fetchurl }:
with lib;

let
  recursiveDeps = mod: [mod] ++ map recursiveDeps mod.deps;
  mkModList = mods: unique (flatten (map recursiveDeps mods));
  fetchFactorio =  playerDataJson: args:
    (fetchurl args).overrideAttrs (args2: {
        preHook = ''
          PATH=$PATH:${jq}/bin
          fail () {
              echo ${playerDataJson} seems to be invalid json!
              echo it should look something like this:
              echo " {\"service-username\": \"exampleuser\", \"service-token\": \"exampletoken\"}"
              exit 1
          }

          if test -f "${playerDataJson}"; then
              NAME=$(jq -r '."service-username"' "${playerDataJson}") || fail
              TOKEN=$(jq -r '."service-token"' ${playerDataJson}) || fail
              export NAME TOKEN
          else
              ls -l ${playerDataJson}
              echo ${playerDataJson} is not accessable!
              echo please add it to extra-sandbox-paths in nix.conf!
              and make sure the settings are correct!
              exit 1
          fi
          '';
        curlOptsList = [
        "--get"
        "--header" ("'Accept: application/octet-stream'")
        "--data-urlencode" "username=$NAME"
        "--data-urlencode"   "token=$TOKEN"
        ];
      });

in
{
  inherit fetchFactorio;
  filterMissing = self: lib.foldr (a: b: if builtins.hasAttr a self then [self.${a}]++b else b) [];
  factorioMod = playerDataJson:
    ## https://wiki.factorio.com/Mod_portal_API#Result_Entry
    # most info comes from the above API, specifically the releases
    { file_name         # the name returned by the file_name field: "AfraidOfTheDark_1.1.1.zip"
    , pname             # sanitized nix friendly name
    , url               # url to download file
    , sha1              # the sha1 field
    , version           # version field
    , deps              # all required dependencies
    , optionalDeps      # all dependencies prepended with '?'
    , withOptionalDeps ? false }@args: stdenvNoCC.mkDerivation ({
      inherit pname version deps optionalDeps withOptionalDeps file_name;

      #withOptional = self // {withOptionalDeps = true;};

      src = fetchFactorio playerDataJson {
        inherit (args)  url sha1;
        name = file_name;
      };
        buildCommand = ''
      mkdir -p $out
      cp $src $out/${file_name}
      '';
      preferLocalBuild = true;
    });
  mkModDirPackage = mods: modsDatFile: identifier: # a list of mod derivations
    let
      modString = mod: "ln -s ${mod}/${mod.file_name} $out/${mod.file_name}";
    in
    stdenvNoCC.mkDerivation {
      name = "factorio-mod-directory-${identifier}";

      identifier = identifier;
      preferLocalBuild = true;
      buildCommand = ''
        mkdir -p $out
        ${lib.strings.concatLines (map modString (mkModList mods))}
        _makeSymlinksRelativeInAllOutputs
        '' + (lib.optionalString (modsDatFile != null) ''
       cp ${modsDatFile} $out/mod-settings.dat
      '');
    };

  mkModZipPackage = modDirPackage:
    let
      modString = mod: "${mod}/${mod.file_name}";
    in
    stdenvNoCC.mkDerivation {
      nativeBuildInputs = [ zip ];
      name = "FactorioMods-${modDirPackage.identifier}.zip";
      preferLocalBuild = true;
      buildCommand = ''
      ls -l
      zip -0jr $out ${modDirPackage}
      '';
    };
}
