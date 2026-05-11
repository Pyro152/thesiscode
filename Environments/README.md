This folder contains environment activation scripts for the computers used in the thesis. Scripts are for example and convenience; users will 
still need to configure their environment either with Spack or some other software. Most cluster administrators maintain the necessary
software for gcclassic.gnu12.env, which is a slightly modified version of the official GCC version

On Negishi, gcclassic.gnu12.env was the environment
On home PC, the environment was gcclassic.home.env

setupenv.txt shows an older version of the home script with a bash command to copy the environment to your run directory for ease.
datacompressionfix.txt is a solution to a netcdf variable compression issue that can happen building an environment with Spack.
