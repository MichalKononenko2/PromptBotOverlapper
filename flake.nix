{
  description = "The Content Assessment and LLM Tokenization App";
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.05";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
      in
      {
        devShell = pkgs.mkShell {
          name = "content-evaluator-dev";

          # Packages necessary for developing a TypeScript/Angular app
          packages = with pkgs; [
            nodejs_20
            typescript
            nodePackages.npm
          ];

          # Environment variables and setup commands
          shellHook = ''
            echo "--- Welcome to the Content Evaluator Dev Shell ---"
            echo "Node.js (v20) and TypeScript are available."
            echo "You can start development by installing dependencies (e.g., 'npm install')."
          '';
        };
      }
    );
}

