# AHEA_WDMOC
The version of the WDMOC used in our 2020 submission to Applied Health Economics and Health Policy for the submitted manuscript entitled 'A Whole Disease Model Approach for Conducting Health Technology Management in Oral Cancer'

Author: Ian Andrew Cromwell, PhD

Technical Advisor: Stavros Korokithakis (Stochastic Technologies)

Supervisory Committee: Dr. Nick Bansback, Dr. Catherine Poh, Dr. Stuart Peacock, Dr. Greg Werker, Dr. Charlyn Black

The Whole Disease Model of Oral Cancer (WDMOC) is a decision model developed for Health Technology Assessment (HTA), Health Technology Management (HTM) and cost-effectiveness analysis (CEA). A full description of the model is available under Documentation in the document entitled 'Methods.pdf', but a brief description follows.

The WDMOC is an individual sampling discrete event simulation (DES) model. Entities (simulated people) are created and given characteristics based on user-defined parameters (InputParameters.xlsx). These entities experience events using a time-to-event process. Randomly-sampled values of the input paramters determine each entity's path through various simulated health care processes - screening, management of preclinical lesions, management of invasive and recurring cancers, follow-up, and death. Resource utilization, survival, and health state utility (EQ-5D 3L) are tracked for each entity, along with a history of events experienced. At the end of each entity's simulated trajectory (either at death or a user-defined point), unit costs are applied to resources and overall and quality-adjusted survival are calculated. The user may simulate any number of entities. User-defined results from a cohort of simulated entities can be exported to a .csv file, which can then be analyzed in any software packge the user wishes. The model's structure is described in detail in 'Methods.pdf'.

The WDMOC is built in Python 3.5.1.

**INSTRUCTIONS**

The model runs from a master file called the Sequencer (Sequencer.py). The Sequencer allows the user to specify a number of alternative policy scenarios in isolation and in various combinations (see **line 140**) for a cohort of entities. The size of the cohort can also be specified by the user (see **line 152**). In each run of the sequencer, two arms are considered - an Assay Informed and and Assay Naive arm.

The Sequencer outputs a .csv file that contains LYG, QALY, and cost values for each member of the cohort in both arms. This .csv file can be analyzed and converted into ICERs and other relevant cost-effectiveness values using an R file (Cost-Effectiveness Analysis.R).

All files should be run within a single directory.
