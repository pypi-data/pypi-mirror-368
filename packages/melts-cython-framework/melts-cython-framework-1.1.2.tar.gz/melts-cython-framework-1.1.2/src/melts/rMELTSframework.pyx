cdef extern from "cframework.h":
	int MELTScalculationModeConstant();
	int pMELTScalculationModeConstant();
	int xMELTScalculationModeConstant();
	int MELTSandCO2calculationModeConstant();
	int MELTSandCO2_H2OcalculationModeConstant();
	int num_oxides();
	int num_phase_components();
	int num_phases(int modelSelection);
	char **oxideListAsStrings();
	char **phaseListAsStrings(int modelSelection);
	int init(int modelSelection);
	void createDefaultSilminState();
	void destroyDefaultSilminState();
	int parseAndLoadDataStructuresFromXMLstring(char *inputXMLstringt);
	char *writeDataStructuresToXMLstring(char *sessionID);
	int performMELTScalculation(int typeOfCalc);
	double initialTemperature();
	void setInitialTemperature(double tValue);
	double finalTemperature();
	void setFinalTemperature(double tValue);
	double incrementTemperature();
	void setIncrementTemperature(double tValue);
	double initialPressure();
	void setInitialPressure(double pValue);
	double finalPressure();
	void setFinalPressure(double pValue);
	double incrementPressure();
	void setIncrementPressure(double pValue);
	double initialVolume();
	void setInitialVolume(double vValue);
	double finalVolume();
	void setFinalVolume(double vValue);
	double incrementVolume();
	void setIncrementVolume(double vValue);
	double initialEnthalpy();
	void setInitialEnthalpy(double hValue);
	double finalEnthalpy();
	void setFinalEnthalpy(double hValue);
	double incrementEnthalpy();
	void setIncrementEnthalpy(double hValue);
	double initialEntropy();
	void setInitialEntropy(double sValue);
	double finalEntropy();
	void setFinalEntropy(double sValue);
	double incrementEntropy();
	void setIncrementEntropy(double sValue);
	int isIsochoric();
	void setIsochoric(int value);
	int isIsenthalpic();
	void setIsenthalpic(int value);
	int isIsotropic();
	void setIsotropic(int value);
	double *bulkCompAsPtr();
	void setBulkCompAsPtr(double *value);
	double **liquidCompAsPtr();
	void setLiquidCompAsPtr(double **value);
	int nLiquidCoexist();
	void setnLiquidCoexist(int value);
	double liquidMass();
	void setLiquidMass(double value);
	int multipleLiqs();
	void setMultipleLiqs(int value);
	double **solidCompAsPtr();
	void setSolidCompAsPtr(double **value);
	int nComponentsInSolidPhase(int index);
	int *nSolidCoexist();
	void setnSolidCoexist(int* value);
	double solidMass();
	void setSolidMass(double value);
	int *incSolids();
	void setIncSolids(int *value);
	double fo2();
	void setfo2(double value);
	int fo2Path();
	void setfo2Path(int value);
	double fo2Delta();
	void setfo2Delta(double value);
	double oxygenContent();
	void setOxygenContent(double value);
	int fractionateSol();
	void setFractionateSol(int value);
	int fractionateLiq();
	void setFractionateLiq(int value);
	int fractionateFlu();
	void setFractionateFlu(int value);
	double **fracSComp();
	void setFracSComp(double **values);
	int *nFracCoexist(); 
	void setnFracCoexist(int *values);
	double *fracLComp();
	void setFracLComp(double *values);
	double fracMass();
	void setFracMass(double value);


from libc.stdlib cimport malloc, free
from cpython cimport PyObject, Py_INCREF
import ctypes

# Import the Python-level symbols of numpy
import numpy as np

# Import the C-level symbols of numpy
cimport numpy as np

# Numpy must be initialized. When using numpy from C or Cython you must
# _always_ do that, or you will have segfaults
np.import_array()

# here is the "wrapper" signature

def cy_MELTScalculationModeConstant():
	return MELTScalculationModeConstant()

def cy_pMELTScalculationModeConstant():
	return pMELTScalculationModeConstant()

def cy_xMELTScalculationModeConstant():
	return xMELTScalculationModeConstant()

def cy_MELTSandCO2calculationModeConstant():
	return MELTSandCO2calculationModeConstant()

def cy_MELTSandCO2_H2OcalculationModeConstant():
	return MELTSandCO2_H2OcalculationModeConstant()

def cy_num_oxides():
	return num_oxides()

def cy_num_phase_components():
	return num_phase_components()

def cy_oxideListAsStrings():
	cdef char **names = oxideListAsStrings()
	n = num_oxides()
	result = []
	for i in range(0,n):
		entry = <bytes> names[i]
		result.append(entry.decode('UTF-8'))
	return result

def cy_phaseListAsStrings(int modelSelection):
	cdef char **names = phaseListAsStrings(modelSelection)
	n = num_phases(modelSelection)
	result = []
	for i in range(0,n):
		entry = <bytes> names[i]
		result.append(entry.decode('UTF-8'))
	return result

def cy_init(int modelSelection):
	return init(modelSelection)

def cy_createcreateDefaultSilminState():
	createDefaultSilminState()

def cy_destroyDefaultSilminState():
	destroyDefaultSilminState()

def cy_parseAndLoadDataStructuresFromXMLstring(inputXMLstring):
	return parseAndLoadDataStructuresFromXMLstring(inputXMLstring.encode('utf-8'))

def cy_writeDataStructuresToXMLstring(sessionID):
	result_b = writeDataStructuresToXMLstring(sessionID.encode('utf-8'))
	result = result_b.decode('utf-8')
	free(result_b)
	return result

def cy_performMELTScalculation(typeOfCalc):
	return performMELTScalculation(typeOfCalc)

def cy_initialTemperature():
	return initialTemperature()

def cy_setInitialTemperature(double tValue):
	setInitialTemperature(tValue)

def cy_finalTemperature():
	return finalTemperature()

def cy_setFinalTemperature(double tValue):
	setFinalTemperature(tValue)

def cy_incrementTemperature():
	return incrementTemperature()

def cy_setIncrementTemperature(double tValue):
	setIncrementTemperature(tValue);

def cy_initialPressure():
	return initialPressure()

def cy_setInitialPressure(double pValue):
	setInitialPressure(pValue)

def cy_finalPressure():
	return finalPressure()

def cy_setFinalPressure(double pValue):
	setFinalPressure(pValue)

def cy_incrementPressure():
	return incrementPressure()

def cy_setIncrementPressure(double pValue):
	setIncrementPressure(pValue)

def cy_initialVolume():
	return initialVolume()

def cy_setInitialVolume(double vValue):
	setInitialVolume(vValue)

def cy_finalVolume():
	return finalVolume()

def cy_setFinalVolume(double vValue):
	setFinalVolume(vValue)

def cy_incrementVolume():
	return incrementVolume()

def cy_setIncrementVolume(double vValue):
	setIncrementVolume(vValue)

def cy_initialEnthalpy():
	return initialEnthalpy()

def cy_setInitialEnthalpy(double hValue):
	setInitialEnthalpy(hValue)

def cy_finalEnthalpy():
	return finalEnthalpy()

def cy_setFinalEnthalpy(double hValue):
	setFinalEnthalpy(hValue)

def cy_incrementEnthalpy():
	return incrementEnthalpy()

def cy_setIncrementEnthalpy(double hValue):
	setIncrementEnthalpy(hValue)

def cy_initialEntropy():
	return initialEntropy()

def cy_setInitialEntropy(double sValue):
	setInitialEntropy(sValue)

def cy_finalEntropy():
	return finalEntropy()

def cy_setFinalEntropy(double sValue):
	setFinalEntropy(sValue)

def cy_incrementEntropy():
	return incrementEntropy()

def cy_setIncrementEntropy(double sValue):
	setIncrementEntropy(sValue)

def cy_isIsochoric():
	return isIsochoric()

def cy_setIsochoric(int value):
	setIsochoric(value)

def cy_isIsenthalpic():
	return isIsenthalpic()

def cy_setIsenthalpic(int value):
	setIsenthalpic(value)

def cy_isIsotropic():
	return isIsotropic()

def cy_setIsotropic(int value):
	setIsotropic(value)

def cy_bulkCompAsList():
	cdef double *bc = bulkCompAsPtr()
	n = num_oxides()
	result = []
	for i in range(0,n):
		entry = <double> bc[i]
		result.append(entry)
	return result

def cy_setBulkCompAsList(list values = []):
	n = num_oxides()
	cdef double *bc = <double *>malloc(n*sizeof(double))
	for i in range (0,n):
		bc[i] = <double> values[<int>i]
	setBulkCompAsPtr(<double *> bc)
	# free (bc) memory management in C function

def cy_liquidCompAsListOfLists():
	cdef double **lc = liquidCompAsPtr()
	nl = nLiquidCoexist()
	nc = num_oxides()
	result = []
	for i in range(0, nl):
		result.append([lc[i][j] for j in range(0, nc)])
	return result

def cy_setLiquidCompAsListOfLists(list values = [[]]):
	nl = nLiquidCoexist()
	nc = num_oxides()
	cdef double **lc = <double **>malloc(nl*sizeof(double *))
	for i in range(0, nl):
		lc[i] = <double *>malloc(nc*sizeof(double))
		for j in range(0, nc):
			lc[i][j] = values[<int>i][<int>j]
	setLiquidCompAsPtr(<double **> lc)
	#for i in range(0, nl):
	#	free(lc[i])
	#free (lc)  memory management in C function

def cy_nLiquidCoexist():
	return nLiquidCoexist()

def cy_setnLiquidCoexist(int value):
	setnLiquidCoexist(<int> value)

def cy_liquidMass():
	return <double> liquidMass()

def cy_setLiquidMass(double value):
	setLiquidMass(<double> value);

def cy_multipleLiqs():
	return False if multipleLiqs() == 0 else True;

def cy_setMultipleLiqs(bint value):
	setMultipleLiqs(<int> (1 if value else 0))

def cy_nSolidCoexistAsList():
	cdef int *ns = nSolidCoexist()
	npc = num_phase_components()
	result = [<int> ns[i] for i in range(0,npc)]
	return result

def cy_setnSolidCoexistAsList(list values = []):
	npc = num_phase_components()
	cdef int *ns = <int *>malloc(npc*sizeof(int))
	for i in range(0,npc):
		ns[i] = <int> values[<int>i]
	setnSolidCoexist(<int *> ns)
	# free (ns)  memory management in C function

def cy_solidCompAsListOfLists():
	cdef double **sc = solidCompAsPtr()
	cdef int *ns = nSolidCoexist()
	npc = num_phase_components()
	ns_copy = []
	for i in range(0,npc):
		ns_copy.append(ns[i])
	i = 0
	while i < npc:
		if ns_copy[i] > 0:
			nc = nComponentsInSolidPhase(i)
			if nc > 1:
				for j in range(1,nc+1):
					ns_copy[i+j] = ns_copy[i]
				i += nc
		i += 1
	result = []
	for i in range(0, npc):
		result.append([sc[i][j] for j in range(0, max(ns_copy[i],1))])
	return result

def cy_setSolidCompAsListOfLists(list values = [[]]):
	cdef int *ns = nSolidCoexist()
	npc = num_phase_components()
	ns_copy = []
	for i in range(0,npc):
		ns_copy.append(ns[i])
	i = 0
	while i < npc:
		if ns_copy[i] > 0:
			nc = nComponentsInSolidPhase(i)
			if nc > 1:
				for j in range(1,nc+1):
					ns_copy[i+j] = ns_copy[i]
				i += nc
		i += 1
	cdef double **sc = <double **>malloc(npc*sizeof(double *))
	for i in range(0, npc):
		sc[i] = <double *>malloc(max(ns_copy[i],1)*sizeof(double))
		for j in range(0, max(ns_copy[i],1)):
			sc[i][j] = values[<int>i][<int>j]
	setSolidCompAsPtr(<double **> sc)
	#for i in range(0, npc):
	#	free(sc[i])
	#free (sc)  memory management in C function

def cy_solidMass():
	return <double> solidMass()

def cy_setSolidMass(double value):
	setSolidMass(<double> value);

def cy_incSolidsAsList():
	npc = num_phase_components()
	cdef int *inc = incSolids();
	result = [True if inc[i] == 1 else False for i in range(0,npc)]
	return result

def cy_setIncSolidsAsList(list values = []): # bint[:]
	npc = num_phase_components()
	cdef int *inc = <int *>malloc(npc*sizeof(int))
	for i in range(0,npc):
		inc[i] = <int> (1 if values[i] else 0)
	setIncSolids(<int *> inc)
	# free (inc)  memory management in C function

def cy_fo2():
	return fo2();

def cy_setfo2(double value):
	setfo2(<double> value)

def cy_fo2Path():
	return fo2Path();

def cy_setfo2Path(int value):
	setfo2Path(<int> value)

def cy_fo2Delta():
	return fo2Delta()

def cy_setfo2Delta(double value):
	setfo2Delta(<double> value)

def cy_oxygenContent():
	return oxygenContent()

def cy_setOxygenContent(double value):
	setOxygenContent(<double> value)

def cy_fractionateSol():
	return True if fractionateSol() == 1 else False

def cy_setFractionateSol(bint value):
	setFractionateSol(<int>(1 if value else 0));

def cy_fractionateLiq():
	return True if fractionateLiq() == 1 else False

def cy_setFractionateLiq(bint value):
	setFractionateLiq(<int>(1 if value else 0))

def cy_fractionateFlu():
	return True if fractionateFlu() == 1 else False

def cy_setFractionateFlu(bint value):
	setFractionateFlu(<int>(1 if value else 0));

def cy_nFracCoexistAsList():
	cdef int *ns = nFracCoexist()
	if ns == NULL:
		return None
	npc = num_phase_components()
	result = [<int> ns[i] for i in range(0,npc)]
	return result

def cy_setnFracCoexistAsList(list values = []):
	if values is None:
		return
	npc = num_phase_components()
	cdef int *ns = <int *>malloc(npc*sizeof(int))
	for i in range(0,npc):
		ns[i] = <int> values[i]
	setnFracCoexist(<int *> ns)
	# free (ns)  memory management in C function

def cy_fracSCompAsListOfLists():
	cdef double **sc = fracSComp()
	cdef int *ns = nSolidCoexist()
	if sc == NULL or ns == NULL:
		return None
	npc = num_phase_components()
	result = []
	for i in range(0, npc):
		result.append([sc[i][j] for j in range(0, max(ns[i],1))])
	return result

def cy_setFracSCompAsListOfLists(list values = [[]]):
	if values is None:
		return
	cdef int *ns = nSolidCoexist()
	npc = num_phase_components()
	cdef double **sc = <double **>malloc(npc*sizeof(double *))
	for i in range(0, npc):
		sc[i] = <double *>malloc(max(ns[i],1)*sizeof(double))
		for j in range(0, max(ns[i],1)):
			sc[i][j] = values[i][j]
	setFracSComp(<double **> sc)
	#for i in range(0, npc):
	#	free(sc[i])
	#free (sc)  memory management in C function

def cy_fracLCompAsList():
	nc = num_oxides()
	cdef double *nl = fracLComp()
	if nl == NULL:
		return None
	result = [<double> nl[i] for i in range(0,nc)]
	return result

def cy_setFracLCompAsList(list values = []):
	if values is None:
		return
	nc = num_oxides()
	cdef double *nl = <double *>malloc(nc*sizeof(double))
	for i in range(0,nc):
		nl[i] = <double> values[i]
	setFracLComp(<double *> nl)
	#free (nl)  memory management in C function

def cy_fracMass():
	return <double> fracMass()

def cy_setFracMass(double value):
	setFracMass = <double> value

