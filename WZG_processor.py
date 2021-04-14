import numpy as np
import awkward1 as ak
from coffea.nanoevents import NanoEventsFactory, NanoAODSchema
from coffea import processor, hist
from coffea.util import  load, save
import time
import json
import glob
import os
import argparse
import matplotlib.pyplot as plt
from coffea import lumi_tools


#file_list = glob.glob("/home/dylee/workspace/Processor/scheme2_many/tri1/condorOut/s4*.root")
fname = "/home/dylee/workspace/Processor/WZG/scheme2_nano.root"
events = NanoEventsFactory.from_file(fname, schemaclass=NanoAODSchema).events()

#sample_name="WZG"


# --> Class MyProcessor
class MyProcessor(processor.ProcessorABC):

	# -- Initializer
	def __init__(self):
		self._histo = hist.Hist(
			"Events",
			hist.Cat("dataset", "Dataset"),
			hist.Bin("mass", "Z mass", 50, 50, 150)			
		)	


	# -- Accumulator : accumulate in histograms
	@property
	def accumulator(self):
		return self._histo


	# -- Main function : Process events
	def process(self, events):

	
		# Initialize accumulator
		output = self.accumulator.identity()


		# Flat dim for histo fill		
		def flat_dim(arr):
			sub_arr = ak.flatten(arr)
			mask = ~ak.is_none(sub_arr)
			return ak.to_numpy(sub_arr[mask])
	

		# Drop empty array 
		def drop_na(arr):
			mask = ~ak.is_none(arr)
			return ak.to_numpy(arr[mask])


		# Particle Selection
		Electron = events.Electron
		Muon = events.Muon
		Photon = events.Photon
		MET = events.MET


		# Define Particle_Selection
		def Particle_Selection(MET, Electron, Photon):
			MET_mask = MET.pt > 20
			Electron_mask = (Electron.pt > 20) & (np.abs(Electron.eta) < 2.5) & (Electron.cutBased > 1)
			Photon_mask = (Photon.pt > 20) & (np.abs(Photon.eta) < 2.5) & (Photon.cutBasedBitmap > 0)
			return (MET_mask, Electron_mask, Photon_mask)

		MET_mask, Electron_mask, Photon_mask = Particle_Selection(MET, Electron, Photon)


		# Particle selection mask
		# Number of Electron > 2 and Photon > 0
		Ele_Sel_mask = ak.num(Electron[Electron_mask]) > 2
		Pho_Sel_mask = ak.num(Photon[Photon_mask]) > 0

		Event_mask = Ele_Sel_mask & Pho_Sel_mask & MET_mask

		# Event Selection - eee channel

		# Apply Event mask
		Ele_channel_events = events[Event_mask]	
		
		# Variable cut setting once more
		MET_second_mask = Ele_channel_events.MET.pt > 20
		Electron_second_mask = (Ele_channel_events.Electron.pt > 20) & (np.abs(Ele_channel_events.Electron.eta) < 2.5) & (Ele_channel_events.Electron.cutBased > 1)
		Photon_second_mask = (Ele_channel_events.Photon.pt > 20) & (np.abs(Ele_channel_events.Photon.eta) < 2.5) & (Ele_channel_events.Photon.cutBasedBitmap > 0)
	

#		Ele = Ele_channel_events.Electron
#		Pho = Ele_channel_events.Photon
#		Met = Ele_channel_events.MET

		Elesel = Ele_channel_events.Electron[Electron_second_mask]
		Phosel = Ele_channel_events.Photon[Photon_second_mask]
		Metsel = Ele_channel_events.MET[MET_second_mask]

		# All possible triplet of Electron in each event
		Tri_ele = ak.combinations(Elesel, 3, axis=1)

		# Veto same sign set and events
		N_Before_ss_filter = len(flat_dim(Tri_ele))
		Tri_SSVeto_Mask = ~((Tri_ele.slot0.charge == Tri_ele.slot1.charge) == Tri_ele.slot2.charge)
		Tri_ele = Tri_ele[Tri_SSVeto_Mask]

		Tri_SSVeto_evtMask = ak.num(Tri_ele) > 0
		Tri_ele = Tri_ele[Tri_SSVeto_evtMask]
		MET_SSVeto = Metsel[Tri_SSVeto_evtMask]

		N_After_ss_filter = len(flat_dim(Tri_ele))

		print("Veto SS Eff : {0}%".format(round(N_After_ss_filter / N_Before_ss_filter * 100,2)))

		# Select High-PT ordered set -> one triplet per one event
		Tri_ele = Tri_ele[ak.argmax(Tri_ele.slot0.pt, axis=1)]
#		Tri_ele = Tri_ele[ak.argmax(Tri_ele.slot0.pt, axis=1, keepdims=True)]

		# Choose Opposite Sign Same Flavor lepton pairs that meet Z mass window
		def ossf_zmass_check(p1, p2):
			return ((p1.charge != p2.charge) & (np.abs(91.18 - (p1 + p2).mass) < 30.))

		e1e2 = ossf_zmass_check(Tri_ele.slot0, Tri_ele.slot1)
		e1e3 = ossf_zmass_check(Tri_ele.slot0, Tri_ele.slot2)
		e2e3 = ossf_zmass_check(Tri_ele.slot1, Tri_ele.slot2)

		Triplet = Tri_ele[ak.num(Tri_ele[e1e2]) > 0]
		MET_OSSF = MET_SSVeto[ak.num(Tri_ele[e1e2]) > 0]

		Di_ele = Triplet.slot0 + Triplet.slot1
		Mee = ak.to_numpy(Di_ele.mass)
		Mee = Mee.flatten()

		output.fill(
			dataset = events.metadata["dataset"],
			mass = Mee
		)		
		return output

	# -- Return accumulator
	def postprocess(self, accumulator):
		return accumulator

samples = {
	"Processor": [fname]
#	sample_name: [file_list[0]]
}

result = processor.run_uproot_job(
	samples,
	"Events",
	MyProcessor(),
	processor.futures_executor,
	#executor_args = {"schema": NanoAODSchema},
	executor_args = {"schema": NanoAODSchema, "workers": 20},
)

# Draw Hist
hist.plot1d(result, stack=True)
plt.show(result)
