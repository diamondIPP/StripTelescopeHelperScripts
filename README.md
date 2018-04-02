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
