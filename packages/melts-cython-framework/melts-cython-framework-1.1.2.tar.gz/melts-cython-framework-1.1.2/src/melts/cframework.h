//
//  cframework.h
//
//  Created by Mark Ghiorso
//  October 2021
//

#define PARSE_ERROR             0
#define GENERIC_CALC            1
#define RUN_LIQUIDUS_CALC       2
#define RUN_EQUILIBRATE_CALC    3
#define RETURN_WITHOUT_CALC     4
#define RETURN_DO_FRACTIONATION 5
#define RUN_WET_LIQUIDUS_CALC   6

int MELTScalculationModeConstant(void);
int pMELTScalculationModeConstant(void);
int xMELTScalculationModeConstant(void);
int MELTSandCO2calculationModeConstant(void);
int MELTSandCO2_H2OcalculationModeConstant(void);

int num_oxides(void);
int num_phase_components(void);
int num_phases(int modelSelection);
char **oxideListAsStrings(void);
char **phaseListAsStrings(int modelSelection);

int init(int modelSelection);
void createDefaultSilminState(void);
void destroyDefaultSilminState(void);
int parseAndLoadDataStructuresFromXMLstring(char *inputXMLstringt);
char *writeDataStructuresToXMLstring(char *sessionID);
int performMELTScalculation(int type);

double initialTemperature(void);
void setInitialTemperature(double tValue);

double finalTemperature(void);
void setFinalTemperature(double tValue);

double incrementTemperature(void);
void setIncrementTemperature(double tValue);

double initialPressure(void);
void setInitialPressure(double pValue);

double finalPressure(void);
void setFinalPressure(double pValue);

double incrementPressure(void);
void setIncrementPressure(double pValue);

double initialVolume(void);
void setInitialVolume(double vValue);

double finalVolume(void);
void setFinalVolume(double vValue);

double incrementVolume(void);
void setIncrementVolume(double vValue);

double initialEnthalpy(void);
void setInitialEnthalpy(double hValue);

double finalEnthalpy(void);
void setFinalEnthalpy(double hValue);

double incrementEnthalpy(void);
void setIncrementEnthalpy(double hValue);

double initialEntropy(void);
void setInitialEntropy(double sValue);

double finalEntropy(void);
void setFinalEntropy(double sValue);

double incrementEntropy(void);
void setIncrementEntropy(double sValue);

int isIsochoric(void);
void setIsochoric(int value);
int isIsenthalpic(void);
void setIsenthalpic(int value);
int isIsotropic(void);
void setIsotropic(int value);

double *bulkCompAsPtr(void);
void setBulkCompAsPtr(double *value);

double **liquidCompAsPtr(void);
void setLiquidCompAsPtr(double **value);

int nLiquidCoexist(void);
void setnLiquidCoexist(int value);

double liquidMass(void);
void setLiquidMass(double value);

int multipleLiqs(void);
void setMultipleLiqs(int value);

double **solidCompAsPtr(void);
void setSolidCompAsPtr(double **value);

int nComponentsInSolidPhase(int index);

int *nSolidCoexist(void);
void setnSolidCoexist(int* value);

double solidMass(void);
void setSolidMass(double value);

int *incSolids(void);
void setIncSolids(int *value);

double fo2(void);
void setfo2(double value);

int fo2Path(void);
void setfo2Path(int value);

double fo2Delta(void);
void setfo2Delta(double value);

double oxygenContent(void);
void setOxygenContent(double value);

int fractionateSol(void);
void setFractionateSol(int value);

int fractionateLiq(void);
void setFractionateLiq(int value);

int fractionateFlu(void);
void setFractionateFlu(int value);

double **fracSComp(void);
void setFracSComp(double **values);

int *nFracCoexist(void);
void setnFracCoexist(int *values);

double *fracLComp(void);
void setFracLComp(double *values);

double fracMass(void);
void setFracMass(double value);

