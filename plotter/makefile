# phony targets
.PHONY: all

RUN = 16001

# directories
INPUTDIR       = Jun29
PEDESTALDIR    = $(OUTPUTDIR)/analysis/$(RUN)/pedestal
CLUSTERINGDIR  = $(OUTPUTDIR)/analysis/$(RUN)/clustering
SELECTIONDIR   = $(OUTPUTDIR)/analysis/$(RUN)/selection
TRANSPARENTDIR = $(OUTPUTDIR)/analysis/$(RUN)/transparent
ALIGNMENTDIR   = $(OUTPUTDIR)/analysis/$(RUN)/alignment

# plots
all : pedestal clustering selection transparent alignment
final : clustering_final transparent_final

# pedestal
pedestal : $(PEDESTALDIR)/StripPedestal_Dia.dat
pedestal : $(PEDESTALDIR)/HitPosition_BiggestSignal_Dia.dat
pedestal : $(PEDESTALDIR)/StripSignals_Event176274_Dia.dat
pedestal : $(PEDESTALDIR)/Noise_NonHitChannels_Dia.dat

# clustering
clustering : clustering_silicon signal-to-noise_silicon clustering_diamond signal-to-noise_diamond clustering_residual_diamond
signal-to-noise_silicon : $(CLUSTERINGDIR)/PulseHeight_BiggestAdjacentInSigma_D1X.dat
signal-to-noise_silicon : $(CLUSTERINGDIR)/PulseHeight_BiggestSignalInSigma_D1X.dat
clustering_silicon : $(CLUSTERINGDIR)/PulseHeight_ClusterSize_1-2_D1X.dat
clustering_silicon : $(CLUSTERINGDIR)/PulseHeight_ClusterSize_1-3_D1X.dat
clustering_silicon : $(CLUSTERINGDIR)/PulseHeight_ClusterSize_1_D1X.dat
clustering_diamond : $(CLUSTERINGDIR)/PulseHeight_ClusterSize_1-3_Dia.dat
clustering_diamond : $(CLUSTERINGDIR)/PulseHeight_ClusterSize_1-4_Dia.dat
clustering_diamond : $(CLUSTERINGDIR)/PulseHeight_ClusterSize_1-5_Dia.dat
clustering_diamond : $(CLUSTERINGDIR)/PulseHeight_ClusterSize_1_Dia.dat
clustering_diamond : $(CLUSTERINGDIR)/PulseHeight_ClusterSize_2_Dia.dat
clustering_diamond : $(CLUSTERINGDIR)/PulseHeight_ClusterSize_3_Dia.dat
clustering_diamond : $(CLUSTERINGDIR)/PulseHeight_ClusterSize_4_Dia.dat
#clustering_diamond : $(CLUSTERINGDIR)/PulseHeight_ClusterSize_5_Dia.dat
clustering_diamond : $(CLUSTERINGDIR)/ClusterSize_Dia.dat
clustering_diamond : clustering_final
clustering_final : $(CLUSTERINGDIR)/PulseHeight_ClusterSize_1-2_Dia.dat
clustering_residual_diamond : $(CLUSTERINGDIR)/Residual_ChargeWeighted_Dia.dat
clustering_residual_diamond : $(CLUSTERINGDIR)/Residual_Digital_Dia.dat
clustering_residual_diamond : $(CLUSTERINGDIR)/Residual_EtaCorrected_Dia.dat
clustering_residual_diamond : $(CLUSTERINGDIR)/Residual_HighestPair_Dia.dat
signal-to-noise_diamond : $(CLUSTERINGDIR)/PulseHeight_BiggestAdjacentInSigma_Dia.dat
signal-to-noise_diamond : $(CLUSTERINGDIR)/PulseHeight_BiggestSignalInSigma_Dia.dat
eta_diamond : $(CLUSTERINGDIR)/Eta_Dia.dat
eta_diamond : $(CLUSTERINGDIR)/EtaIntegral_Dia.dat

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
