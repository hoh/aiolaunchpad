{
  description = "Nix packaging and development shell for aiolaunchpad";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.11";
  };

  outputs = { self, nixpkgs }:
    let
      systems = [
        "x86_64-linux"
        "aarch64-linux"
        "x86_64-darwin"
        "aarch64-darwin"
      ];
      forAllSystems = nixpkgs.lib.genAttrs systems;
    in
    {
      packages = forAllSystems (system:
        let
          pkgs = import nixpkgs { inherit system; };
          aiolaunchpad = pkgs.python3Packages.callPackage ./default.nix { };
        in
        {
          inherit aiolaunchpad;
          default = aiolaunchpad;
        });

      devShells = forAllSystems (system:
        let
          pkgs = import nixpkgs { inherit system; };
          pythonEnv = pkgs.python3.withPackages (ps: [
            (ps.callPackage ./default.nix { })
          ]);
        in
        {
          default = pkgs.mkShellNoCC {
            packages = [
              pythonEnv
            ];

            shellHook = ''
              echo "aiolaunchpad is available in this shell."
              echo "Run the README example with: python - <<'PY' ..."
            '';
          };
        });

      checks = forAllSystems (system:
        let
          pkgs = import nixpkgs { inherit system; };
          aiolaunchpad = pkgs.python3Packages.callPackage ./default.nix { };
        in
        {
          inherit aiolaunchpad;
        });
    };
}
