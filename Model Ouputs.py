from collections import Counter
    
def genVarList(entityrecord, var):
    retvar = []
    for i in range(0, len(entityrecord)):
        if hasattr(entityrecord[i], var) == True:
            retvar.append(getattr(entityrecord[i], var))
    return retvar
    
entityrecord = EntityList

# Prevalence of OPL
outlist_numOPLs = genVarList(entityrecord, 'hasOPL')
val_numOPLs = len(outlist_numOPLs)/len(entityrecord)

cancerrecord = [ent for ent in entityrecord if getattr(ent, 'cancerDetected') == 1]
stg1record = [ent for ent in cancerrecord if getattr(ent, 'cancerStage') == 'I']
surgrecord = [ent for ent in stg1record if getattr(ent, 'tx_prim') == 'Surgery']
survsurg = genVarList(surgrecord, 'time_death')
np.mean(survsurg)
nocancerrecord = [ent for ent in EntityList if getattr(ent, 'cancerDetected') != 1]
for i in range(0, len(entityrecord)):
    if getattr(entityrecord[i], "cancerDetected") == 1:
        cancerrecord.append(entityrecord[i])
        

smokerecord = [ent for ent in entityrecord if ent.smokeStatus == 'Ever']
alcrecord = [ent for ent in entityrecord if ent.alcStatus == 'Heavy']

censrecord = [ent for ent in EntityList if ent.death_type == 'Censored']
cancerdeath = [ent for ent in EntityList if ent.death_type == 1]
cancerdother = [ent for ent in EntityList if ent.death_type != 1]
dother = [ent for ent in EntityList if ent.death_type == 2]

deathtime_dother = genVarList(dother, 'time_death')
startage_dother = genVarList(dother, 'startAge')
deathage_dother = [(ent.startAge + ent.time_death/365) for ent in EntityList]


recurrecord = [ent for ent in cancerrecord if hasattr(ent, "recurrence") == True]
for i in range(0, len(cancerrecord)):
    if hasattr(cancerrecord[i], "recurrence") == True:
        recurrecord.append(cancerrecord[i])
        
detCancerrecord = []
symptCancerrecord = []
for i in range(0, len(cancerrecord)):
    if hasattr(cancerrecord[i], 'sympt') == 1:
        symptCancerrecord.append(cancerrecord[i])
    else:
        detCancerrecord.append(cancerrecord[i])

outlist_byStage_cancer = genVarList(cancerrecord, 'firstcancer')

val_numCancer = len(cancerrecord)
val_byStage_cancer = Counter(outlist_byStage_cancer)

for i in range(0, len(cancerrecord)):
    entity = cancerrecord[i]
    entity.age_Cancer = (entity.time_Cancer + 365*entity.startAge)/365
    entity.age_Diagnosed = (entity.time_cancerDetected + 365*entity.startAge)/365

outlist_byAge_devCancer = genVarList(cancerrecord, 'age_Cancer')
outlist_byAge_diagCancer = genVarList(cancerrecord, 'age_Diagnosed')

byAge_devCancer_mean = numpy.mean(outlist_byAge_devCancer)
byAge_devCancer_std = numpy.std(outlist_byAge_devCancer)
byAge_diagCancer_mean = numpy.mean(outlist_byAge_diagCancer)
byAge_diagCancer_std = numpy.std(outlist_byAge_diagCancer)
val_byAge_devCancer = ["Mean:", byAge_devCancer_mean, "SD:", byAge_devCancer_std]
val_byAge_diagCancer = ["Mean:", byAge_diagCancer_mean, "SD:", byAge_diagCancer_std]

for i in range(0, len(entityrecord)):
    entity = entityrecord[i]
    entity.age_death = (entity.time_death + 365*entity.startAge)/365
    
outlist_byAge_death = genVarList(entityrecord, 'age_death')
byAge_death_mean = numpy.mean(outlist_byAge_death)
byAge_death_std = numpy.std(outlist_byAge_death)
val_byAge_death = ["Mean:", byAge_death_mean, "SD:", byAge_death_std]

byDeath_cancer = []

for i in range(0, len(entityrecord)):
    if getattr(entityrecord[i], 'death_type') == 1:
        byDeath_cancer.append(entityrecord[i])

