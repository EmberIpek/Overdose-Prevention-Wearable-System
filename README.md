# Overdose Prevention Wearable System
## Pilot Proposal

Studies indicate that individuals involved in the criminal justice system are significantly more likely to die of overdose than the general population [1], [2], with those on probation up to 15 times more likely to die of opioid-related overdose [2]. Additional risk factors identified for those on probation included age >45, prior positive drug screen result for opioids or cocaine, and prior placement in drug treatment programs [2]. This pilot proposal evaluates whether wearable devices that includes voluntary healthcare-managed heartrate monitor and oxygen saturation monitor combined with rapid outreach programs reduce fatal overdoses in high-risk populations. The program prioritizes protection of healthcare data, early detection of overdose, and non-punitive medical response.

Current GPS monitoring programs are designed for location tracking and compliance monitoring and provide no mechanism for detecting medical emergencies. This program aims to bridge the gap through an optional HIPAA compliant healthcare-managed monitoring program for participants already required to wear GPS tracking device. Participants who opt in would receive a tracker device that integrates heartrate and oxygen saturation monitors, with health data accessible only to healthcare providers. No probation violation is triggered from medical alerts.

Eligible participants for the program must meet one of the following criteria:

- Adults with ≥1 non-fatal overdose incidents within the past 12 months
- Individuals referred through diversion programs
- Prior placement in a drug/alcohol treatment program
- Documented history of substance use disorder

## Protocol

1.	Device detects one of the following: 

- Oxygen saturation < 90% for 30 seconds 
- Abnormal heart rate (< 50 or > 240)

2.	Device vibrates and displays: 
"Health Check Required. Press button within 60 seconds."

4.	If user presses button:
- Log event
- Clear alert

5.	Else if no response:
- Device sounds alarm
- Send text message to designated contact

6.	If still no response and high-risk pattern after additional timeout:
- EMS dispatched
- Connection to peer support specialist/behavioral services

## Circuit Diagram

<img width="975" height="473" alt="image" src="https://github.com/user-attachments/assets/969f7f10-38e8-41ad-9554-d0a7c9fb42bd" />

## Outcomes

The program will measure the following outcomes:

Primary:
- Reduction in emergency response time to overdose events
- Reduction in fatal overdoses

Secondary:
- Initiation of substance abuse treatment
- Hospital admission reduction
- EMS activation accuracy (false positive, true positive, and false negative rates)

## Works Cited

[1] I. A. Binswanger, A. P. Nguyen, J. D. Morenoff, S. Xu, and D. J. Harding, “The association of criminal justice supervision setting with overdose mortality: a longitudinal cohort study,” Addiction, vol. 115, no. 12, pp. 2329–2338, Dec. 2020, doi: 10.1111/add.15077. PMID: 32267585.

[2] J. K. Boulger, K. Hinami, T. Lyons, and J. Nowinski Konchak, “Prevalence and risk factors for opioid related mortality among probation clients in an American city,” Journal of Substance Abuse Treatment, vol. 137, p. 108712, Jun. 2022, doi: 10.1016/j.jsat.2021.108712. PMID: 35067401.


