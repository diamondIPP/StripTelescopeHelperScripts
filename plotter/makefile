# phony targets
.PHONY: all

RUN = 16001

# directories
INPUTDIR       = Jun29
NOISEDIR       = $(OUTPUTDIR)/analysis/$(RUN)/noise
CLUSTERINGDIR  = $(OUTPUTDIR)/analysis/$(RUN)/clustering
SELECTIONDIR   = $(OUTPUTDIR)/analysis/$(RUN)
TRANSPARENTDIR = $(OUTPUTDIR)/analysis/$(RUN)/transparent
ALIGNMENTDIR   = $(OUTPUTDIR)/analysis/$(RUN)/alignment

# plots
all : noise clustering selection transparent alignment
final : clustering_final transparent_final

# noise
noise : $(NOISEDIR)/Noise_NonHitChannels_Dia.dat

# clustering
clustering : clustering_silicon clustering_diamond signal-to-noise_diamond
clustering_silicon : $(CLUSTERINGDIR)/PulseHeight_BiggestAdjacentInSigma_D1X.dat
clustering_silicon : $(CLUSTERINGDIR)/PulseHeight_BiggestSignalInSigma_D1X.dat
clustering_silicon : $(CLUSTERINGDIR)/PulseHeight_ClusterSize_1-2_D1X.dat
clustering_silicon : $(CLUSTERINGDIR)/PulseHeight_ClusterSize_1-3_D1X.dat
clustering_silicon : $(CLUSTERINGDIR)/PulseHeight_ClusterSize_1_D1X.dat
clustering_diamond : $(CLUSTERINGDIR)/PulseHeight_BiggestAdjacentInSigma_Dia.dat
clustering_diamond : $(CLUSTERINGDIR)/PulseHeight_BiggestSignalInSigma_Dia.dat
clustering_diamond : $(CLUSTERINGDIR)/PulseHeight_ClusterSize_1-3_Dia.dat
clustering_diamond : $(CLUSTERINGDIR)/PulseHeight_ClusterSize_1-4_Dia.dat
clustering_diamond : $(CLUSTERINGDIR)/PulseHeight_ClusterSize_1-5_Dia.dat
clustering_diamond : $(CLUSTERINGDIR)/PulseHeight_ClusterSize_1_Dia.dat
clustering_diamond : $(CLUSTERINGDIR)/ClusterSize_Dia.dat
clustering_diamond : clustering_final
clustering_final : $(CLUSTERINGDIR)/PulseHeight_ClusterSize_1-2_Dia.dat
signal-to-noise_diamond : $(CLUSTERINGDIR)/PulseHeight_BiggestAdjacentInSigma_Dia.dat
signal-to-noise_diamond : $(CLUSTERINGDIR)/PulseHeight_BiggestSignalInSigma_Dia.dat

# selection
selection : $(SELECTIONDIR)/TrackPosition_OneAndOnlyOneSiCluster.dat
selection : $(SELECTIONDIR)/TrackPosition_OneAndOnlyOneSiCluster_DiamondCluster.dat

# transparent
transparent : transparent_final
transparent : $(TRANSPARENTDIR)/PulseHeight_nStrips_1.dat
transparent : $(TRANSPARENTDIR)/PulseHeight_nStrips_10.dat
transparent : $(TRANSPARENTDIR)/PulseHeight_nStrips_2.dat
transparent : $(TRANSPARENTDIR)/PulseHeight_nStrips_3.dat
transparent_final : $(TRANSPARENTDIR)/PulseHeight_nStrips_2in10.dat
#transparent : $(TRANSPARENTDIR)/PulseHeight_nStrips_4.dat
#transparent : $(TRANSPARENTDIR)/PulseHeight_nStrips_5.dat
#transparent : $(TRANSPARENTDIR)/PulseHeight_nStrips_6.dat
#transparent : $(TRANSPARENTDIR)/PulseHeight_nStrips_7.dat
#transparent : $(TRANSPARENTDIR)/PulseHeight_nStrips_8.dat
#transparent : $(TRANSPARENTDIR)/PulseHeight_nStrips_9.dat

# alignment
alignment : $(ALIGNMENTDIR)/PostAlignment_Plane2_XPred_DeltaY.dat
alignment : $(ALIGNMENTDIR)/PostAlignment_Plane2_YPred_DeltaX.dat
alignment : $(ALIGNMENTDIR)/PreAlignment_Plane2_XPred_DeltaY.dat
alignment : $(ALIGNMENTDIR)/PreAlignment_Plane2_YPred_DeltaX.dat

# copy
$(OUTPUTDIR)/analysis/%.dat : $(INPUTDIR)/%.dat
	mkdir -p $(dir $@)
	cp -p $< $@
