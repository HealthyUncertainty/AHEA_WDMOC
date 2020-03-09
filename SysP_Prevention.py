import random

class Prevention:
    def __init__(self, alt_estimates):
        self.smoking_reduc = alt_estimates.Smoking_Reduc.sample()
        self.alcohol_reduc = alt_estimates.Alcohol_Reduc.sample()

    def Process(self, entity):
        changeSmoke = random.random()
        changeAlc = random.random()
        scenario = 0
        if entity.smokeStatus == 'Ever':
            entity.resources.append(('Experimental Smoking Cessation', entity.allTime))
            scenario = 1
            if changeSmoke < self.smoking_reduc:
                # The smoking cessation program is effective
                entity.smokeStatus = 'Never'
        if entity.alcStatus == 'Heavy':
            entity.resources.append(('Experimental Alcohol Cessation', entity.allTime))
            scenario = 1
            if changeAlc < self.alcohol_reduc:
                # The alcohol cessation program is effective
                entity.alcStatus = 'Nonheavy'
        if entity.Scenario_Prev == 1 and scenario == 1:
            entity.scenario_desc.append(("Smoking and Alcohol Cessation"))