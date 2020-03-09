###################################################################################
#                                                                                 #
# TITLE: WDMOC - calculate incremental cost-effectiveness of model outputs        #
#                                                                                 #
# AUTHOR: Ian Cromwell, PhD                                                       #
# DATE: March, 2020                                                               #
#                                                                                 #
# DESCRIPTION: This program reads in .csv files from the WDMOC, containing        #
#               discounted LYG, QALYs, and costs. It produces estimates of the    #
#               ICER, QICER, and Cost-effectiveness planes and CEACs.             #
#                                                                                 #
###################################################################################

### LOAD REQUIRED PACKAGES

library(BCEA)
library(coda)
library(MCMCpack)
options(scipen = 999)

### STEP 1: Read in .csv files from alternative scenarios
# NOTE: the number of entities in each scenario must be the same

Source <- read.table("Scenario_Output.csv", sep=",", stringsAsFactors=FALSE,)
  colnames(Source) <- c("B - LY", "B - QALY", "B - Cost", "B - OPL", "A - LY", "A - QALY", "A - Cost", "A - OPL")

Comparator <- Source[c(1:4)]
Alternative <- Source[c(5:8)]

Alt_OPL <- Alternative[which(Alternative[,4] > 0),]
Comp_OPL <- Comparator[which(Comparator[,4] > 0),]

### STEP 2: Bootstrap 10,000 Incremental values

  nsample <- 1000
  nboot <- 10000
  lambda <- 100000

  # From full population  
  LYGboot <- QALYboot <- Costboot <- ICERboot <- QICERboot <- array(0, dim = c(nboot, 1))
    LYGboot_A <- LYGboot_B <- QALYboot_A <- QALYboot_B <- Costboot_A <- Costboot_B <- array(0, dim = c(nboot, 1))
  
  for (i in 1:nboot){
    Bootsample_A <- Alternative[sample(nrow(Alternative), size=nsample, replace = TRUE),]
    Bootsample_B <- Comparator[sample(nrow(Comparator), size=nsample, replace = TRUE),]

    LYGboot_A[i] <- mean(Bootsample_A[,1])
    LYGboot_B[i] <- mean(Bootsample_B[,1])
    QALYboot_A[i] <- mean(Bootsample_A[,2])
    QALYboot_B[i] <- mean(Bootsample_B[,2])
    Costboot_A[i] <- mean(Bootsample_A[,3])
    Costboot_B[i] <- mean(Bootsample_B[,3])
  }

  LYG_A <- LYGboot_A
  QALY_A <- QALYboot_A
  Cost_A <- Costboot_A
  
  LYG_B <- LYGboot_B
  QALY_B <- QALYboot_B
  Cost_B <- Costboot_B
  
  DeltaC <- Cost_A - Cost_B
  DeltaE <- LYG_A - LYG_B
  DeltaQ <- QALY_A - QALY_B
  ICER <- DeltaC/DeltaE
  QICER <- DeltaC/DeltaQ
  
  # From OPL+ population  
  OLYGboot <- OQALYboot <- OCostboot <- ICERboot <- QICERboot <- array(0, dim = c(nboot, 1))
  OLYGboot_A <- OLYGboot_B <- OQALYboot_A <- OQALYboot_B <- OCostboot_A <- OCostboot_B <- array(0, dim = c(nboot, 1))
  
  onboot <- nrow(Alt_OPL)
  lambda <- 100000
  
  for (i in 1:nboot){
    Bootsample_A <- Alt_OPL[sample(nrow(Alt_OPL), size=nsample, replace = TRUE),]
    Bootsample_B <- Comp_OPL[sample(nrow(Comp_OPL), size=nsample, replace = TRUE),]
    
    OLYGboot_A[i] <- mean(Bootsample_A[,1])
    OLYGboot_B[i] <- mean(Bootsample_B[,1])
    OQALYboot_A[i] <- mean(Bootsample_A[,2])
    OQALYboot_B[i] <- mean(Bootsample_B[,2])
    OCostboot_A[i] <- mean(Bootsample_A[,3])
    OCostboot_B[i] <- mean(Bootsample_B[,3])
  }
  
  OLYG_A <- OLYGboot_A
  OQALY_A <- OQALYboot_A
  OCost_A <- OCostboot_A
  
  OLYG_B <- OLYGboot_B
  OQALY_B <- OQALYboot_B
  OCost_B <- OCostboot_B
  
  ODeltaC <- OCost_A - OCost_B
  ODeltaE <- OLYG_A - OLYG_B
  ODeltaQ <- OQALY_A - OQALY_B
  OICER <- ODeltaC/ODeltaE
  OQICER <- ODeltaC/ODeltaQ


### STEP 3: Cost-effectiveness statistical summary
  
  # Full population
  
  CR95_CostA <- c(round(mean(Cost_A) - 1.96*sd(Cost_A), digits = 2), round(mean(Cost_A) + 1.96*sd(Cost_A), digits = 2))
  CR95_CostB <- c(round(mean(Cost_B) - 1.96*sd(Cost_B), digits = 2), round(mean(Cost_B) + 1.96*sd(Cost_B), digits = 2))
  
  CR95_EA <- c(round(mean(LYG_A) - 1.96*sd(LYG_A), digits = 2), round(mean(LYG_A) + 1.96*sd(LYG_A), digits = 2))
  CR95_EB <- c(round(mean(LYG_B) - 1.96*sd(LYG_B), digits = 2), round(mean(LYG_B) + 1.96*sd(LYG_B), digits = 2))
  
  CR95_QA <- c(round(mean(QALY_A) - 1.96*sd(QALY_A), digits = 2), round(mean(QALY_A) + 1.96*sd(QALY_A), digits = 2))
  CR95_QB <- c(round(mean(QALY_B) - 1.96*sd(QALY_B), digits = 2), round(mean(QALY_B) + 1.96*sd(QALY_B), digits = 2))
  
  CR95_DeltaC <- c(round(mean(DeltaC) - 1.96*sd(DeltaC), digits = 2), round(mean(DeltaC) + 1.96*sd(DeltaC), digits = 2))
  CR95_DeltaE <- c(round(mean(DeltaE) - 1.96*sd(DeltaE), digits = 4), round(mean(DeltaE) + 1.96*sd(DeltaE), digits = 4))
  CR95_DeltaQ <- c(round(mean(DeltaQ) - 1.96*sd(DeltaQ), digits = 4), round(mean(DeltaQ) + 1.96*sd(DeltaQ), digits = 4))
  
  CR95_ICER <- round(quantile(ICER, c(0.025, 0.975)), digits = 2)
  CR95_QICER <- round(quantile(QICER, c(0.025, 0.975)), digits = 2)
  NMB <- round(mean(DeltaQ)*lambda - mean(DeltaC), digits = 2)
  CQ <- cbind(DeltaC, DeltaQ, DeltaC/DeltaQ)
  CostEffective <- CQ[which(CQ[,2] > 0 & CQ[,3] < lambda),]
  
  CEASummary <- c('FULL POPULATION:',
                  'Cost_A:', round(mean(Cost_A), digits=2), '95CR - Cost_A:', CR95_CostA, 
                  'LYG_A:', round(mean(LYG_A), digits=5), '95CR - LYG_A:', CR95_EA,
                  'QALY_A:', round(mean(QALY_A), digits=5), '95CR - QALY_A:', CR95_QA, 
                  
                  'Cost_B:', round(mean(Cost_B), digits=2), '95CR - Cost_B:', CR95_CostB,
                  'LYG_B:', round(mean(LYG_B), digits=5), '95CR - LYG_B:', CR95_EB,
                  'QALY_B:', round(mean(QALY_B), digits=5), '95CR - QALY_B:', CR95_QB,
                  
                  'DeltaC:', round(mean(DeltaC), digits=2), '95CR - DeltaC:', CR95_DeltaC, 
                  'DeltaE:', round(mean(DeltaE), digits=5), '95CR - DeltaE:', CR95_DeltaE,
                  'DeltaQ:', round(mean(DeltaQ), digits=5), '95CR - DeltaQ:', CR95_DeltaQ,
                  
                  'ICER:', round(mean(DeltaC)/mean(DeltaE), digits = 2), '95CR - ICER:', CR95_ICER,
                  'QICER:', round(mean(DeltaC)/mean(DeltaQ), digits = 2), '95CR - QICER', CR95_QICER,
                  'NMB:', NMB,
                  '%CE:', 100*nrow(CostEffective)/nboot)
  
  # OPL+ Population
  CR95_OCostA <- c(round(mean(OCost_A) - 1.96*sd(OCost_A), digits = 2), round(mean(OCost_A) + 1.96*sd(OCost_A), digits = 2))
  CR95_OCostB <- c(round(mean(OCost_B) - 1.96*sd(OCost_B), digits = 2), round(mean(OCost_B) + 1.96*sd(OCost_B), digits = 2))
  
  CR95_OEA <- c(round(mean(OLYG_A) - 1.96*sd(OLYG_A), digits = 2), round(mean(OLYG_A) + 1.96*sd(OLYG_A), digits = 2))
  CR95_OEB <- c(round(mean(OLYG_B) - 1.96*sd(OLYG_B), digits = 2), round(mean(OLYG_B) + 1.96*sd(OLYG_B), digits = 2))
  
  CR95_OQA <- c(round(mean(OQALY_A) - 1.96*sd(OQALY_A), digits = 2), round(mean(OQALY_A) + 1.96*sd(OQALY_A), digits = 2))
  CR95_OQB <- c(round(mean(OQALY_B) - 1.96*sd(OQALY_B), digits = 2), round(mean(OQALY_B) + 1.96*sd(OQALY_B), digits = 2))
  
  CR95_ODeltaC <- c(round(mean(ODeltaC) - 1.96*sd(ODeltaC), digits = 2), round(mean(ODeltaC) + 1.96*sd(ODeltaC), digits = 2))
  CR95_ODeltaE <- c(round(mean(ODeltaE) - 1.96*sd(ODeltaE), digits = 4), round(mean(ODeltaE) + 1.96*sd(ODeltaE), digits = 4))
  CR95_ODeltaQ <- c(round(mean(ODeltaQ) - 1.96*sd(ODeltaQ), digits = 4), round(mean(ODeltaQ) + 1.96*sd(ODeltaQ), digits = 4))
  
  CR95_OICER <- round(quantile(OICER, c(0.025, 0.975)), digits = 2)
  CR95_OQICER <- round(quantile(OQICER, c(0.025, 0.975)), digits = 2)
  ONMB <- round(mean(ODeltaQ)*lambda - mean(ODeltaC), digits = 2)
  OCQ <- cbind(ODeltaC, ODeltaQ, ODeltaC/ODeltaQ)
  OCostEffective <- OCQ[which(OCQ[,2] > 0 & OCQ[,3] < lambda),]
  
  OCEASummary <- c('OPL+ POPULATION:',
                  'OCost_A:', round(mean(OCost_A), digits=2), '95CR - OCost_A:', CR95_OCostA, 
                  'OLYG_A:', round(mean(OLYG_A), digits=5), '95CR - OLYG_A:', CR95_OEA,
                  'OQALY_A:', round(mean(OQALY_A), digits=5), '95CR - OQALY_A:', CR95_OQA, 
                  
                  'OCost_B:', round(mean(OCost_B), digits=2), '95CR - OCost_B:', CR95_OCostB,
                  'OLYG_B:', round(mean(OLYG_B), digits=5), '95CR - OLYG_B:', CR95_OEB,
                  'OQALY_B:', round(mean(OQALY_B), digits=5), '95CR - OQALY_B:', CR95_OQB,
                  
                  'ODeltaC:', round(mean(ODeltaC), digits=2), '95CR - ODeltaC:', CR95_ODeltaC, 
                  'ODeltaE:', round(mean(ODeltaE), digits=5), '95CR - ODeltaE:', CR95_ODeltaE,
                  'ODeltaQ:', round(mean(ODeltaQ), digits=5), '95CR - ODeltaQ:', CR95_ODeltaQ,
                  
                  'ICER:', round(mean(OICER), digits = 2), '95CR - ICER:', CR95_OICER,
                  'QICER:', round(mean(OQICER), digits = 2), '95CR - QICER', CR95_OQICER,
                  'NMB:', ONMB,
                  '%CE:', 100*nrow(OCostEffective)/nboot)
  
  
  
  Output_Summary <- c('FULL POPULATION:', 'Average Cost:', round(mean(Cost_A), digits=2), round(mean(Cost_B), digits = 2),
                      'Delta C:', round(mean(DeltaC), digits = 2), 
                      'Delta Q:', round(mean(DeltaQ), digits = 5), 'NMB:', NMB, '%CE:', 
                     100*nrow(CostEffective)/nboot, 
                     "||",
                     'OPL+ POPULATION:', 'Average Cost:', round(mean(OCost_A), digits=2), round(mean(OCost_B), digits = 2),
                     'Delta C:', round(mean(ODeltaC), digits = 2),
                     'Delta Q:', round(mean(ODeltaQ), digits = 5), 'NMB:', ONMB, '%CE:', 
                     100*nrow(OCostEffective)/nboot)
  
  Output_Summary
  
  Output <- c(CEASummary, OCEASummary, Output_Summary)
  saveRDS(Output, file = "Scenario CEA Output")