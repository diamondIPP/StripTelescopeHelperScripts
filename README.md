# StripTelescopeHelperScripts

Some scripts for the StripTelescopeAnalysis


## Charge feed across correction
This script creates a new `rawData` file corrected for charge feed across.


### Usage
- Change to the output directory of a run
  ```
  cd <RUN OUTPUT DIRECTORY>
  ```
- Get the correction factors from `crossTalkCorrectionFactors.<RUN>.txt`
- Average correction factors of silicon planes
- Run the [correction script](createAsymmetricEtaSample.C)
  ```
  root <SCRIPT DIRECTORY>/createAsymmetricEtaSample.C
  ```
  and enter the prompted correction factors


## Job committer
This script can be used to submit multiple analysis jobs.


## Usage
- Setup a directory with links to the data `RZ` files.
- Adjust the [config file](jobCommitter/config.cfg) or create a new one.
  - paths of data, settings, analysis, and output
  - file system with support of symbolic links
  - format of `CSV` files
  - email address for status updates
- Create a `CSV` file with the run list similar to this [run list](jobCommitter/csvs/RunList-800_MeV_proton.csv).
- Run the [job handler script](jobCommitter/analysis.py):
  ```
  ./analysis.py -f <RUNLIST> -c -j NJOBS -p config.cfg
  ```
  Run
  ```
  ./analysis.py --help
  ```
  for all options.
