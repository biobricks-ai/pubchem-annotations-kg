{
  description = "pubchem-annotations-kg";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-23.05";
    flake-utils.url = "github:numtide/flake-utils";
    hdt-cpp = {
      url = "github:insilica/nix-hdt";
      inputs.flake-utils.follows = "flake-utils";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    hdt-java = {
      url = "github:insilica/nix-hdt-java";
      inputs.flake-utils.follows = "flake-utils";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, nixpkgs, flake-utils, hdt-cpp, hdt-java }:
    flake-utils.lib.eachDefaultSystem (system:
      with import nixpkgs { inherit system; }; {
	devShells.default = mkShell {
	  buildInputs = [
            hdt-cpp.packages.${system}.default
	    hdt-java.packages.${system}.default
	    apache-jena
	    apache-jena-fuseki
	    jq
	  ];
	  env = {
	    JENA_HOME = "${apache-jena}";
	  };
	};
      });
}
