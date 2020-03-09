# -*- coding: utf-8 -*-
"""
A program to describe the treatment and recovery process for an incident Stage I oral cancer.
Entities with a diagnosed stage I cancer will be treated either surgically (with/without RT),
with some other treatment type (usually Chemo+RT), or may receive no treatment. Their
post-treatment survival is calculated based on treatment type, stage, and other individual
characteristics.

After recovery (from surgery, chemo, and/or RT), entities are routed to the follow-up 
surveillance model component. Entities with less than three months survival are routed to 
the "End of Life" component.

Time of recurrence and death of disease (without further treatment) are set here. As with 
"SysP_Followup", the base case of the model is using the date of DIAGNOSIS as the starting 
point, rather than the date cancer is developed. This is consistent with the use of 
retrospective survival data from diagnosed patients.

@author: icromwell
"""

import random
import math
from copy import deepcopy
from Glb_CompTime import CompTime

class StageOneTx:
    def __init__(self, estimates, regcoeffs):
        self._estimates = deepcopy(estimates)
        self._regcoeffs = deepcopy(regcoeffs)

        self.tx_time_treatment = estimates.Tx_time_treatment.sample()
        self.prob_other_RT = estimates.Tx_other_RT.sample()
        self.prob_other_chemo = estimates.Tx_other_chemo.sample()

    def Process(self, entity):
        
        start = entity.allTime
        entity.time_Sysp = entity.allTime
        scenario = 0
        
        # Chapter 6 - Incorporate surgical change
        if entity.Scenario_Surg == 1 and entity.tx_prim == 'Surgery':
            scenario = 1
            int_adj = entity.RR_Surgery
            self._regcoeffs['FirstEvent']['Intercept']['mean'] -= int_adj
            self._regcoeffs['FirstEvent_death']['Intercept']['mean'] -= int_adj

        # Schedule next event
        # Generate random time to event - either recurrence or death
        makeEvent = CompTime(self._estimates, self._regcoeffs)
        nextEvent = makeEvent.Process(entity, 'FirstEvent', 'FirstEvent_death')
           
        if nextEvent[0] < 3650:  # Entity experiences some event between 3 months and 10 years
            entity.utility.append(("Stage I Cancer Under Treatment", self._estimates.Util_StageI_Tx.sample(), entity.allTime))

            "Schedule next event"

            if nextEvent[1] == 1: #Event is recurrence
                entity.time_Recurrence = start + nextEvent[0]
                entity.time_DeadofDisease = 99999
            elif nextEvent[1] == 2: #Event is death
                entity.time_Recurrence = 99999
                entity.time_DeadofDisease = start + nextEvent[0]
                
            """If death or recurrence occurs before 3 months, schedule at that time.
                Otherwise, follow-up starts at 3 months"""
                
            if nextEvent[0] < 90: 
                if nextEvent[1] == 1: #Entity dies before 90 days
                    entity.statenum = 5.0 # Entity is in EoL care state
                    entity.currentState = "Terminal Disease"
                    entity.endOfLife = 1
                entity.time_Sysp += nextEvent[0]
            else: 
                entity.time_Sysp += self.tx_time_treatment 
                entity.stateNum = 4.0
                entity.currentState = "Post-treatment follow-up"          
            
        else: # Entity does not experience another disease event
            entity.time_DeadofDisease = 99999
            entity.time_Recurrence = 99999
            entity.time_Sysp += self.tx_time_treatment 
            entity.stateNum = 4.0
            entity.currentState = "Post-treatment follow-up"  

        # Resource utilization according to treatment type
        if entity.tx_prim == 'Surgery':
            entity.hadSurgery = 1                
            entity.surgery = 1
            entity.resources.append(("Treatment - Stage I - Surgery", entity.allTime))
            entity.events.append(("Treatment - Stage I - Surgery", entity.allTime))
            if entity.Scenario_Surg == 1 and scenario == 1:
                entity.resources.append(('Experimental Surgery', entity.allTime))
                entity.scenario_desc.append(('Experimental Surgery'))
            
        elif entity.tx_prim == 'SurgeryRT':
            entity.hadSurgery = 1
            entity.resources.append(("Treatment - Stage I - Surgery + RT", entity.allTime))
            entity.events.append(("Treatment - Stage I - Surgery + RT", entity.allTime))
            entity.hadRT = 1
            entity.RTCount += 1
            
        elif entity.tx_prim == 'Other':
            probRT = random.random()
            probChemo = random.random()
            
            entity.resources.append(("Treatment - Stage I - Other", entity.allTime))
            entity.events.append(("Treatment - Stage I - Other", entity.allTime))
            
            if probRT < self.prob_other_RT:
                entity.hadRT = 1
                entity.RTCount += 1
                
            if probChemo < self.prob_other_chemo:
                entity.chemoCount += 1
                entity.hadChemo = 1
                
        else:
            entity.stateNum = 99
            entity.currentState = "Error: Entity has not been assigned a valid treatment"
