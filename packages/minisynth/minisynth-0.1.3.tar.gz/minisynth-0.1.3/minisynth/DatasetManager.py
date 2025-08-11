import numpy as np
from .ModGenerator import ModGenerator
from .MiniSynth import MiniSynth
import pandas as pd

class DatasetManager:

    def __init__(self, synth:MiniSynth):
        self.synth = synth
        self.sr = synth.sr
        self.duration = synth.duration
        self.samples = int(synth.sr * synth.duration)
        self.modgen = ModGenerator()

        self.params = synth.get_parameters()

    def generate_modulations(self, num_active_mods:int = 1):
        if num_active_mods < 0 or num_active_mods > len(self.params.keys()):
            raise ValueError(f"Number of active mods must be between 0 and {len(self.params.keys())}")
        
        modulations = {}

        active_mods = np.random.choice(
            list(self.params.keys()), 
            size=num_active_mods, 
            replace=False
        )

        for mod in list(self.params.keys()):
            if mod in active_mods:
                minmax_array = np.sort(np.random.uniform(self.params[mod]["range"][0], self.params[mod]["range"][1], size=2))
            else:
                minmax_array = np.tile(np.random.uniform(self.params[mod]["range"][0], self.params[mod]["range"][1]), 2)

            modulations[mod] = self.modgen.init_points_random(
                min=minmax_array[0], 
                max=minmax_array[1], 
                scale=self.params[mod]["scale"]
            ).get_points()


        return modulations
    
    def read_dataset(self, dataset_path:str):
        self.df = pd.read_json(dataset_path)

    def get_plot_points(self, index:int):
        row = self.df.iloc[index]
        points = {}
        for key in row.keys():
            array = np.array(row[key])
            self.modgen.set_points(array)
            points[key] = self.modgen.get_plot_points()
        
        return points
    
    def get_modulation(self, index:int):
        row = self.df.iloc[index]
        modulations = {}
        for key in row.keys():
            array = np.array(row[key])
            self.modgen.set_points(array)
            modulations[key] = self.modgen.render()
        
        return modulations
    
    def get_audio(self, index:int):
        modulations = self.get_modulation(index)
        for key in modulations.keys():
            self.params[key]["set"](modulations[key])

        audio = self.synth.render()
        return audio
