
{
  description = "vfx-mcp documentation";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    bun2nix = {
      url = "github:baileyluTCD/bun2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = {
    self,
    nixpkgs,
    bun2nix,
    ...
  }: let
    systems = [
      "x86_64-linux"
      "x86_64-darwin"
      "aarch64-linux"
      "aarch64-darwin"
    ];

    forAllSystems = nixpkgs.lib.genAttrs systems;
  in {
    devShells = forAllSystems (system: let
      pkgs = nixpkgs.legacyPackages.${system};
    in {
      default = pkgs.mkShell {
        packages = with pkgs; [
          bun
          nodePackages.typescript
          bun2nix.packages.${system}.default
          typescript-language-server
          astro-language-server
        ];
        shellHook = ''
          # Setup the environment
          export PATH=$PWD/node_modules/.bin:$PATH
        '';
      };
    });

    packages = forAllSystems (system: let
      pkgs = nixpkgs.legacyPackages.${system};
    in rec {
      vfx-mcp-docs = bun2nix.lib.${system}.mkBunDerivation {
        pname = "vfx-mcp-docs";
        version = "0.0.1";
        src = ./.;
        bunNix = ./bun.nix;

        buildPhase = ''
          cp -r ${./../examples} ./.
          # Build the Astro site
          bun run build
        '';

        installPhase = ''
          cp -r dist $out
        '';
      };
      default = vfx-mcp-docs;
    });

    apps = forAllSystems (system: let
      pkgs = nixpkgs.legacyPackages.${system};
    in {
      default = {
        type = "app";
        program = "${pkgs.writeShellScript "serve-docs" ''
          ${pkgs.python3}/bin/python3 -m http.server 8000 -d ${self.packages.${system}.default}
        ''}";
      };
    });

    formatter = forAllSystems (system: nixpkgs.legacyPackages.${system}.nixpkgs-fmt);
  };
}
