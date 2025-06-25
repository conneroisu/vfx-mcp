
{
  description = "vfx-mcp documentation";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs = {
    self,
    nixpkgs,
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
          nodejs_20
          nodePackages.npm
          nodePackages.typescript
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
      vfx-mcp-docs = pkgs.buildNpmPackage {
        pname = "vfx-mcp-docs";
        version = "0.0.1";
        src = ./.;

        npmDepsHash = "sha256-YwKKA9gCF/Z/y2bXFlD6guExjf2GQj+hE0LawhWz9Ow=";
        
        makeCacheWritable = true;

        buildPhase = ''
          runHook preBuild
          
          # Copy examples
          cp -r ${./../examples} ./.
          
          # Build the Astro site
          npm run build
          
          runHook postBuild
        '';

        installPhase = ''
          runHook preInstall
          
          cp -r dist $out
          
          runHook postInstall
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
