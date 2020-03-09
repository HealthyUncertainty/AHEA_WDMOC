# -*- coding: utf-8 -*-
"""
The progression of an OPL to stage I cancer, or spontaneously resolving

@author: icromwell
"""
import math
import numpy
from Glb_GenTime import GenTime

class OPLProg:
    
    def __init__(self, estimates, regcoeffs):
        self._estimates = estimates
        self._regcoeffs = regcoeffs
    
    def Process(self, entity): 
        # If this person doesn't already have the 'natHist' list created, create it for them
        if getattr(entity, "natHist", 0) == 0:                     
             entity.natHist = []
             
        if hasattr(entity, 'age') == 0:
            entity.age = entity.startAge

        t_OPL_NED = self._estimates.NatHist_timeOPL_NED.sample()
                
        # Randomly sample two competing TTE risks      
        # Time to OPL progression to cancer        
        if entity.OPLRisk == 'Lo':
            OPL_samptime = self._estimates.time_OPLCan_lo.sample()
        elif entity.OPLRisk == 'Med':
            OPL_samptime = self._estimates.time_OPLCan_med.sample()
        elif entity.OPLRisk == 'Hi':
            OPL_samptime = self._estimates.time_OPLCan_hi.sample()
        else:
            entity.stateNum = 99
            entity.currentState = "Error: Entity has not been assigned an OPL risk score - check NatHist_OPLProg.py"
            
        # Convert 5-year probabilities into annual probabilities by converting to annual rate
        rate_StageOne = -1/5*math.log(1-OPL_samptime)
        prob_StageOne = 1-math.exp(-rate_StageOne)
        
        # Convert annual probability into time estimate (Weibull)
        lmbd_StageOne = -(math.log(1.0 - prob_StageOne)/365.0)
        beta_StageOne = 1/lmbd_StageOne
        t_OPL_StageOne =  numpy.random.exponential(beta_StageOne)
        
        # Schedule the event that happens first
        if t_OPL_StageOne < t_OPL_NED:                              
            entity.nh_status = 2.0
            entity.nh_time += t_OPL_StageOne
            entity.natHist.append(("Stage 1", entity.nh_status, entity.nh_time))
        elif entity.natHist_deathAge < t_OPL_NED:
            entity.nh_time = entity.natHist_deathAge
            entity.nh_status = 0.9
        else:                                                          
            entity.nh_status = 0.0
            entity.nh_time += t_OPL_NED
            entity.natHist.append(("NED", entity.nh_status, entity.nh_time))


############################################################################################
# VARIABLES CREATED IN THIS STEP
#   
# None