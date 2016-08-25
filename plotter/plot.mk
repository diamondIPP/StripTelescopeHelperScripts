# phony targets
.PHONY: all pedestal signal-to-noise_silicon signal-to-noise_diamond clustering clustering_silicon clustering_diamond eta residuals alignment selection transparent transparent_final

# definitions
RUN = 17101
POS = .

# files and directories
DATADIR   = ../../../Data/links/
OUTPUTDIR = $(shell date +%b%d)
CONFIG    = config.cfg
RUNCONFIG = PW205B.dat

all : pedestal
all : signal-to-noise_silicon
all : signal-to-noise_diamond
all : clustering
all : eta
#all : residuals
all : alignment
all : selection
all : transparent

pedestal : BiggestHitMap_Dia
pedestal : StripMeanPedestal_Dia
pedestal : Noise
pedestal : Event_Dia

signal-to-noise_silicon : $(shell for i in {1..1}; do for PLANE in X; do echo "PulseHeight_BiggestSignalSNRD$${i}$${PLANE} PulseHeight_BiggestAdjacentSNRD$${i}$${PLANE}"; done; done;)
signal-to-noise_diamond : PulseHeight_BiggestSignalSNRDia
signal-to-noise_diamond : PulseHeight_BiggestAdjacentSNRDia

clustering : clustering_silicon clustering_diamond
clustering_silicon : $(shell for i in {1..3}; do echo "PulseHeight_Cluster$${i}_D1X"; done;)
clustering_silicon : $(shell for i in {2..3}; do echo "PulseHeight_Cluster1-$${i}_D1X"; done;)
clustering_diamond : PulseHeight_ClusterSize
clustering_diamond : ClusterSize
#clustering_diamond : PulseHeight_allCluster

eta       : Eta_Dia
eta       : EtaIntegral_Dia
#eta       : Eta_Dia_Area
residuals : ResidualHighestHit_Clustered
residuals : ResidualChargeWeighted_Clustered
residuals : ResidualHighest2Centroid_Clustered
residuals : ResidualEtaCorrected_Clustered

alignment : PreAlignment_Plane2_YPred_DeltaX
alignment : PostAlignment_Plane2_YPred_DeltaX
alignment : PreAlignment_Plane2_XPred_DeltaY
alignment : PostAlignment_Plane2_XPred_DeltaY

selection : FidCut
selection : TrackPos

transparent       : $(shell for i in {1..10}; do echo "PulseHeight_$${i}Strips"; done;)
transparent       : transparent_final
transparent_final : PulseHeight

# run plotter.py
% :
	echo ${$@%.*}
	python plotter.py -b -r $(RUN) -i $(DATADIR) -p $(POS) -c $(CONFIG) -o $(OUTPUTDIR) --runconfig $(RUNCONFIG) --plots $@
