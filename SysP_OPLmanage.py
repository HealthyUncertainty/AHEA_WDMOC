# -*- coding: utf-8 -*-
"""
An alternative scenario for OPL Follow-up and management.

At initial evaluation, people with detected OPLs are administered a genomic test
that tells them their LOH risk score. Based on the results of the test, the entity
will periodically re-evaluated for evidence of progression to cancer at a schedule
informed by their risk score:

- Low risk: biopsied every 5 years
- Intermediate risk: biopsied every 3 years
- High risk: referred for surgery (treated as an HGL)

@author: icromwell
"""

# STEP 1: Load alternative scenario parameter values

from Glb_Estimates import Estimates
from Glb_Estimates import Estimate

#  STEP 2: Define class that describes entity's changed trajectory

import random

class OPLManage:
    def __init__(self, alt_estimates, regcoeffs):
        self._estimates = alt_estimates
        self._regcoeffs = regcoeffs        

        self.appInt_med = 365*alt_estimates.Appint_med.sample()
        self.appInt_lo = 365*alt_estimates.Appint_lo.sample()
        self.appInt_gen = 365*alt_estimates.Appint_gen.sample()
        self.sensitivity = alt_estimates.OPLfu_sensitivity.sample()
        self.specificity = alt_estimates.OPLfu_specificity.sample()
        self.dischargetime = 365*alt_estimates.time_Discharge.sample()
        self.biopsytime_med = 365*alt_estimates.time_Biopsy_med.sample()
        self.biopsytime_lo = 365*alt_estimates.time_Biopsy_lo.sample()
        self.biopsytime_gen = 365*alt_estimates.time_Biopsy_gen.sample()

    def Process(self, entity,):
        entity.OPLDetected = 1
        if hasattr(entity, 'firstOPL') == False:
            # This is the entity's first time in this state
            entity.resources.append(("Biopsy", entity.allTime))
            entity.firstOPL = 1
            entity.time_OPLDetected = entity.allTime                           
            entity.currentState = "2.0 - OPL Detected"
            entity.utility.append(("Detected OPL", self._estimates.Util_OPL_Detected.sample(), entity.allTime))
            if entity.altscen == 1:
                # Entity receives genomic test during first appointment
                entity.resources.append(("OPL genomic test", entity.allTime))
        
        if hasattr(entity, 'altscen') == False:
            entity.altscen = 99
        if entity.altscen == 0:
            appInt = self.appInt_gen
            biopsytime = self.biopsytime_gen
        elif entity.altscen == 1:
            if entity.OPLRisk == 'Lo':
                appInt = self.appInt_lo
                biopsytime = self.biopsytime_lo
            elif entity.OPLRisk == 'Med':
                appInt = self.appInt_med
                biopsytime = self.biopsytime_med
            elif entity.OPLRisk == 'Hi':
                entity.hasCancer = 1
                entity.hiriskdet = 1
                entity.firstcancer = 'HGL at first appointment'
                entity.time_OPLfu = 66666 # This triggers referral for immediate treatment
        else:
            print("Please specify 'entity.altscen' as either 1 or 0")
            
        if hasattr(entity, 'hiriskdet') == True:
            entity.events.append(("High risk lesion first detected at OPL followup", entity.allTime))
            entity.cancer_screenDetected = 1
            entity.cancerDetected = 1
            entity.time_cancerDetected = entity.allTime                  # The time at which the entity's cancer was detected
            entity.stateNum = 3.0
            entity.cancerStage = 'HGL'
            entity.firstCancer = 'HGL'
            temp = entity.time_Sysp
            entity.time_Sysp = 66666    # this routes the entity to the proper 'if' condition
            entity.currentState = "3.0 - Invasive cancer detected"
            
        # DECIDE WHAT EVENT IS SUPPOSED TO HAPPEN NOW
        if entity.time_Sysp == 66666:
            # This step allows the entity to bypass the usual screening process
            # The 'temp' thing is a fudge to make sure that we don't mess up the time_Sysp checks
            entity.time_Sysp = temp
        elif entity.time_Sysp > entity.allTime:
            # Have not yet reached next system process event, do nothing
            pass
        else:
            # IS THE ENTITY DISCHARGED?
            "How long has the entity been undergoing OPL surveillance?"
            if hasattr(entity, 'time_OPLfu') == False:
                entity.time_OPLfu = 0
                entity.tottime_OPLfu = 0
            else:
                # If follow-up > discharge time, entity waits for next event
                if entity.tottime_OPLfu >= self.dischargetime:
                    entity.discharge = 1
                    entity.OPLStatus = 9                 
                    entity.stateNum = 1.8
                    entity.currentState = "1.8 - Waiting for disease event"

            if hasattr(entity, 'discharge') == True:
                # If the entity is due to be discharged from follow-up, do nothing
                pass
            
            # ENTITY RECEIVES OPL FOLLOWUP SCREENING    
            elif entity.time_OPLfu < biopsytime:   # The entity is not yet due for a biopsy 
                entity.resources.append(("OPL surveillance appointment", entity.allTime))
                if entity.hasCancer == 0: 
                    # If the person does not have cancer, re-evaluate them at the next appointment
                    if entity.time_OPLfu > 0:
                        # Not possible to get biopsied twice at first appointment
                        pass
                    else:
                        falsePos = random.random()
                        if falsePos > self.specificity:
                            # Visual screen returns false positive, sent for biopsy
                            entity.resources.append(("Biopsy", entity.allTime))
                    entity.time_Sysp += appInt
                    
                else:
                    # If a person has cancer, it is visually inspected and may yield a false negative
                    falseNeg = random.random()
                    if falseNeg > self.sensitivity:
                        entity.time_Sysp += appInt
                    else:
                        # True positive, cancer is detected and referred for treatment                    
                        entity.resources.append(("Biopsy", entity.allTime))                                # Add biopsy into resources list
                        entity.events.append(("Cancer first detected at OPL followup", entity.allTime))
                        
                        entity.cancer_screenDetected = 1
                        entity.cancerDetected = 1
                        entity.time_cancerDetected = entity.allTime                  # The time at which the entity's cancer was detected
                        entity.stateNum = 3.0
                        entity.currentState = "3.0 - Invasive cancer detected"
                        
            else:                                                       # Once the biopsy time is reached
                entity.time_OPLfu = 0                                   # Reset follow-up time
                entity.resources.append(("OPL surveillance appointment", entity.allTime))          # Enter appointment into resources list
                entity.resources.append(("Biopsy", entity.allTime))                                # Add biopsy into resources list
                
                if entity.hasCancer == 1:
                    entity.events.append(("Cancer first detected at regular biopsy", entity.allTime))
                    entity.cancer_screenDetected = 1
                    entity.cancerDetected = 1
                    entity.time_cancerDetected = entity.allTime                          # The time at which the entity's cancer was detected
                    entity.stateNum = 3.0
                    entity.currentState = "3.0 - Invasive cancer detected"
                else:
                    #OPL is biopsied - no cancer detected
                    entity.time_Sysp += appInt
        
        # ENTITY RETURNS TO REGULAR DENTAL APPOINTMENT
        # If the entity does not have a detected cancer
        if entity.cancerDetected == 0:
            entity.time_OPLfu += appInt
            entity.tottime_OPLfu += appInt
            if hasattr(entity, 'discharge') == True:
                # If the entity is due to be discharged from follow-up, set next followup to implausible value
                entity.time_OPLfu = 555555
                entity.tottime_OPLfu = 555555
            # If the entity has a dentist, they return to regular dental appointments
            elif entity.hasDentist == 1:
                if hasattr(entity, 'time_Dentist') == False:
                    # The entity's next dental appointment has not been assigned
                    entity.time_Dentist = 90
                    # Entity goes back to their dentist in 3 months
                if entity.time_Sysp > entity.time_Dentist:
                    # The next scheduled system process time is the dental appointment
                    entity.time_Sysp = entity.time_Dentist
                    entity.stateNum = 1.0
                    entity.currentState = '1.0 - Dental Screening'

