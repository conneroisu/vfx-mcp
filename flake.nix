{
  description = "VFX MCP - Video editing server using FastMCP";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        
        python = pkgs.python313;
        
        pythonEnv = python.withPackages (ps: with ps; [
          # Runtime dependencies (managed by uv)
          pip
          virtualenv
        ]);


        rooted = text:
          builtins.concatStringsSep "\n" [
            ''
              REPO_ROOT="$(git rev-parse --show-toplevel)"
            ''
            text
          ];

        scripts = {
          dx = {
            text = rooted ''$EDITOR "$REPO_ROOT"/flake.nix'';
            description = "Edit flake.nix";
          };
          tests = {
            text = rooted ''
              cd "$REPO_ROOT"
            '';
            runtimeInputs = with pkgs; [go bun];
            description = "Run all go tests";
          };
          run = {
            text = rooted ''cd "$REPO_ROOT" && air'';
            env.DEBUG = "true";
            runtimeInputs = with pkgs; [air git];
            description = "Run the application with air for hot reloading";
          };
        };

        scriptPackages =
          pkgs.lib.mapAttrs
          (
            name: script:
              pkgs.writeShellApplication {
                inherit name;
                inherit (script) text;
                runtimeInputs = script.runtimeInputs or [];
                runtimeEnv = script.env or {};
              }
          )
          scripts;
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            # Python environment
            pythonEnv
            uv
            
            # Video processing
            ffmpeg-full
            
            # Development tools
            ruff
            black
            basedpyright
            
            # Shell utilities
            git
            jq
            ripgrep
            
            # Optional: For advanced video processing
            imagemagick
            sox  # For audio processing
          ]

            ++ builtins.attrValues scriptPackages;

          shellHook = ''
            echo "🎬 VFX MCP Development Environment"
            echo ""
            echo "Available commands:"
            echo "  uv sync          - Install Python dependencies"
            echo "  uv run main.py   - Run the MCP server"
            echo "  pytest           - Run tests"
            echo "  ruff check .     - Run linting"
            echo "  ruff format .    - Format code"
            echo ""
            echo "FFmpeg version: $(ffmpeg -version | head -n1)"
            echo "Python version: ${python.version}"
            echo ""
            
            # Create virtual environment if it doesn't exist
            if [ ! -d ".venv" ]; then
              echo "Creating virtual environment..."
              uv venv
            fi
            
            # Ensure uv uses the correct Python
            export UV_PYTHON="${pythonEnv}/bin/python"
          '';

          # Environment variables
          FFMPEG_PATH = "${pkgs.ffmpeg-full}/bin/ffmpeg";
          FFPROBE_PATH = "${pkgs.ffmpeg-full}/bin/ffprobe";
        };

        # Optional: Package the MCP server
        packages.default = pkgs.python313Packages.buildPythonApplication {
          pname = "vfx-mcp";
          version = "0.1.0";
          
          src = ./.;
          
          propagatedBuildInputs = with pkgs.python313Packages; [
            # Dependencies will be managed by uv/pyproject.toml
          ];
          
          # Use uv for dependency management
          format = "pyproject";
          
          nativeBuildInputs = with pkgs.python313Packages; [
            setuptools
            wheel
          ];
        };

        # App to run the server directly
        apps.default = flake-utils.lib.mkApp {
          drv = self.packages.${system}.default;
          exePath = "/bin/vfx-mcp";
        };
      });
}
