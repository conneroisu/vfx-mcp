{
  description = "VFX MCP - Video editing server using FastMCP";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    treefmt-nix.url = "github:numtide/treefmt-nix";
  };

  outputs = {
    self,
    nixpkgs,
    flake-utils,
    treefmt-nix,
  }:
    flake-utils.lib.eachDefaultSystem (system: let
      pkgs = nixpkgs.legacyPackages.${system};

      treefmtEval = treefmt-nix.lib.evalModule pkgs {
        projectRootFile = "flake.nix";
        programs = {
          ruff = {
            enable = true;
            format = true;
          };
          black.enable = true;
          alejandra.enable = true;
        };
      };

      python = pkgs.python313;

      pythonEnv = python.withPackages (ps:
        with ps; [
          # Runtime dependencies (managed by uv)
          pip
          virtualenv
        ]);

      rooted = text:
        builtins.concatStringsSep "\n" [
          ''
            REPO_ROOT="$(git rev-parse --show-toplevel)"
            uv venv
            # shellcheck disable=SC1091
            source "$REPO_ROOT"/.venv/bin/activate
            uv sync
          ''
          text
        ];

      scripts = {
        dx = {
          text = rooted ''$EDITOR "$REPO_ROOT"/flake.nix'';
          description = "Edit flake.nix";
        };
        lint = {
          text = rooted ''
            cd "$REPO_ROOT"
            uv sync
            uv run ruff check .
          '';
          description = "Run linting";
        };
        tests = {
          text = rooted ''
            pytest
          '';
          description = "Run all tests";
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
    in {
      devShells.default = pkgs.mkShell {
        buildInputs = with pkgs;
          [
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
            sox # For audio processing
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

      # Script packages only (no main application packages due to fastmcp dependency issues)
      packages = scriptPackages;

      # Formatter output
      formatter = treefmtEval.config.build.wrapper;
    });
}
