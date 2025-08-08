# This file is part of pygeotools
# (c) 2025 - Geodynamo (ISTerre)

# List of ground observatories retrieved from: https://iaga-vobs.org/
# For more information about Fibonacci grid: https://arxiv.org/pdf/0912.4540

# v0 (draft - ongoing)

import pkg_resources
import matplotlib.axes
import matplotlib.figure
import os, h5py, cdflib, csv, math, numpy, copy, matplotlib, scipy.special, scipy.signal, scipy.interpolate
import matplotlib.pyplot as plt
import cartopy.crs
import cmocean

class pygeotools(dict):

    # Custom error class
    class Error(Exception):
        __errorMessages = {

            # MODELS
            "MODEL_NOT_LOAD_ERROR": "The required model is not loaded yet.",
            "MODEL_ALREADY_LOAD_ERROR": "The model is already loaded.",
            "MODEL_TYPE_ERROR": "The model's type does not exist.",
            "MODEL_PATH_ERROR": "The model's path does not exist.",
            "MODEL_BAD_FORMAT_ERROR": "The model's format is wrong.",
            "MODEL_NOT_REANALYSIS_ERROR": "The model is not a reanalysis.",
            "BAD_MODEL_TYPE_ERROR": "The model has not the required type.",

            # FORMATS
            "NOT_HDF5_ERROR": "The format is not HDF5.",
            "NOT_CDF_ERROR": "The format is not CDF.",

            # QUANTITIES
            "QUANTITY_NOT_EXIST_ERROR": "The required quantity does not exist.",
            "BAD_QUANTITY_ERROR": "The calculation could be done with the required quantity.",

            # MEASURES
            "MEASURE_NOT_EXIST_ERROR": "The required measure does not exist.",
            "MEASURE_RETRIEVE_ERROR": "Failed to retrieve the measure.",

            # CONTEXT
            "CONTEXT_NOT_VALID_ERROR": "The required context is not valid.",

            # COMPONENTS
            "COMPONENT_NOT_EXIST_ERROR": "The required component does not exist.",

            # PHYSICAL
            "BAD_RADIUS_ERROR": "The required radius is outside the physical range.",
            "BAD_LMAX_ERROR": "The required LMAX is outside the physical range.",

            # GRIDS
            "GRID_NOT_EXIST_ERROR": "The required grid does not exist.",
            "GRID_ALREADY_EXIST_ERROR": "The grid already exists.",
            "GRID_ANGULAR_SPACING_ERROR": "The grid angular spacing is invalid.",
            "GRID_NOT_SET_ERROR": "The grid is not set.",

            # COMPUTATIONS
            "NORM_NOT_EXIST_ERROR": "The required norm does not exist.",

            # OPERATORS
            "OPERATOR_NOT_EXIST_ERROR": "The required operator does not exist.",
            "OPERATOR_RETRIEVE_ERROR": "Failed to retrieve the operator.",

            # GAUSS COEFFICIENTS
            "GAUSS_BAD_FORMAT_ERROR": "The Gauss coefficient supplied has not the required shape.",
            "GAUSS_BAD_COEFF_ERROR": "The Gauss coefficient is not valid.",

            # OPERATIONS ON MEASURES
            "EMPTY_MEASURE_ERROR": "A measure must be supplied.",
            "BAD_MEASURE_SHAPE_ERROR": "The measure has not the required shape.",

            # DATA SELECTION
            "BAD_RANGE_SHAPE_ERROR": "The specified range is invalid.",

            # OBSERVATIONS
            "OBSERVATION_ALREADY_LOAD_ERROR": "The observation is already loaded.",
            "OBSERVATIONS_NOT_LOAD_ERROR": "The observation is not loaded yet.",
            "OBSERVATIONS_TYPE_ERROR": "The observation's type does not exist.",
            "OBSERVATIONS_PATH_ERROR": "The observation's path does not exist.",
            "OBSERVATION_NOT_EXIST_ERROR": "The required observation does not exist.",
            "OBSERVATORIES_RETRIEVE_ERROR": "Failed to retrieve the list of observatories.",
            "OBSERVATION_RETRIEVE_ERROR": "Failed to retrieve the observation.",
            "OBSERVATION_TOO_FAR_ERROR": "The retrieved observation is too far from the required location.",

            # FIGURES
            "FIGURE_NOT_EXIST_ERROR": "The figure does not exist.",
            "FIGURE_ALREADY_EXIST_ERROR": "The figure already exists.",
            "BAD_LAYOUT_ERROR": "The figure's layout has not the required shape.",
            "SUBPLOT_ALREADY_EXIST_ERROR": "The subplot already exists.",

            # COLORS
            "BAD_COLOR_ERROR": "The specified color is invalid.",
            "BAD_LINESTYLE_ERROR": "The specified linestyle is invalid.",
            "BAD_LINEWIDTH_ERROR": "The specified linewidth is invalid.",

            # DATA
            "BAD_DATA_SHAPE_ERROR": "The data has not the required shape.",

            # PRECISION / NUMERICAL COST
            "PRECISION_BROADCAST_ERROR": "Error while broadcasting the two shapes.",
            "PRECISION_NOT_EXIST_ERROR": "The required precision does not exist.",
            "NUMERICAL_COST_OVERFLOW_ERROR": "The numerical cost exceeds the maximum limit.",

        }

        def __init__(self, errorMessage: str) -> None:
            if errorMessage in self.__errorMessages:
                self.message = self.__errorMessages[errorMessage]
            else:
                self.message = errorMessage

            super().__init__(self.message)

    # Available models and observations
    __modelTypes = set(["pygeodyn_hdf5", "chaos_hdf5", "covobs_hdf5", "kalmag_hdf5"])
    __observationTypes = set(["govo_cdf", "lod_csv", "oam_hdf5"])

    # Available constants
    constants = {
        "pi": numpy.pi,
        "rEarth": 6371.2,
        "rCore": 3485
    }

    # Available grids (default is normal)
    __grids = {
        "40deg": (numpy.linspace(1e-6, numpy.pi - 1e-6, int(180 / 40) + 1), numpy.linspace(1e-6, 2 * numpy.pi - 1e-6, int(360 / 40) + 1)),
        "20deg": (numpy.linspace(1e-6, numpy.pi - 1e-6, int(180 / 20) + 1), numpy.linspace(1e-6, 2 * numpy.pi - 1e-6, int(360 / 20) + 1)),
        "10deg": (numpy.linspace(1e-6, numpy.pi - 1e-6, int(180 / 10) + 1), numpy.linspace(1e-6, 2 * numpy.pi - 1e-6, int(360 / 10) + 1)),
        "5deg": (numpy.linspace(1e-6, numpy.pi - 1e-6, int(180 / 5) + 1), numpy.linspace(1e-6, 2 * numpy.pi - 1e-6, int(360 / 5) + 1)),
        "1deg": (numpy.linspace(1e-6, numpy.pi - 1e-6, int(180 / 1) + 1), numpy.linspace(1e-6, 2 * numpy.pi - 1e-6, int(360 / 1) + 1))
    }

    # Available types of grids
    __gridTypes = ["spherical"]

    # Available precisions
    __precisions = {
        "half": numpy.float16,
        "single": numpy.float32,
        "double": numpy.float64
    }

    # Initializing the module
    def __init__(self, verbose: bool = True) -> None:
        super().__init__()
        self.setGrid("5deg")
        self.__computedOperators = {}
        self.__observatories = None
        self.__verbose = verbose
        self.__figures = {}
        self.__colors = {}

        # TODO
        self.__numericalCostLimit = 1
        self.__numericalPrecision = "double"

        # Verbose
        if self.__verbose: print("pygeotools was initialized with `verbose=True`.")

    # ---
    # MODELS
    # A Model is a collection of Gauss coefficients of several quantities (MF, SV, U) that approximates the data
    # ---

    # Checking if a model is loaded or not
    def isLoaded(self, modelName: str) -> bool:
        return (modelName in self.keys())
    
    # Retrieving a model
    def getModel(self, modelName: str) -> dict:
        if not self.isLoaded(modelName):
            raise self.Error("MODEL_NOT_LOAD_ERROR")
        
        return self[modelName]
    
    # Loading a model
    def loadModel(self, modelName: str, modelType: str, modelPath: str, state: str = "analysed") -> None:
        if self.isLoaded(modelName):
            raise self.Error("MODEL_ALREADY_LOAD_ERROR")
        
        if modelType not in self.__modelTypes:
            raise self.Error("MODEL_TYPE_ERROR")
        
        if not os.path.isfile(modelPath):
            raise self.Error("MODEL_PATH_ERROR")
        
        match modelType:
            case "pygeodyn_hdf5":   modelQuantities = self.load_pygeodyn_hdf5(modelPath, state)
            case "chaos_hdf5":      modelQuantities = self.load_chaos_hdf5(modelPath)
            case "covobs_hdf5":     modelQuantities = self.load_covobs_hdf5(modelPath)
            case "kalmag_hdf5":     modelQuantities = self.load_kalmag_hdf5(modelPath)
            case default:           pass

        self[modelName] = {
            "type": modelType,
            "path": modelPath,
            "quantities": modelQuantities,
            "measures": {}
        }

    # Deleting a model
    def deleteModel(self, modelName: str) -> None:
        if not self.isLoaded(modelName):
            raise self.Error("MODEL_NOT_LOAD_ERROR")
        
        del self[modelName]

    # Cloning a model
    def cloneModel(self, targetModelName: str, newModelName: str) -> None:
        if not self.isLoaded(targetModelName):
            raise self.Error("MODEL_NOT_LOAD_ERROR")
        
        if self.isLoaded(newModelName):
            raise self.Error("MODEL_ALREADY_LOAD_ERROR")
        
        self[newModelName] = copy.deepcopy(self.getModel(targetModelName))

    # Loading pygeodyn reanalysed model
    def load_pygeodyn_hdf5(self, modelPath: str, state: str = "analysed") -> dict:
        if not os.path.isfile(modelPath):
            raise self.Error("MODEL_PATH_ERROR")
        
        if not h5py.is_hdf5(modelPath):
            raise self.Error("NOT_HDF5_ERROR")
        
        availableCategories = set(['analysed', 'computed', 'forecast', "misfits"])
        
        modelQuantities = {}
        
        with h5py.File(modelPath, "r") as f:
            if availableCategories != f.keys():
                raise Exception("MODEL_BAD_FORMAT_ERROR")
            
            for _c in f.keys():
                if _c == state:
                    for _q in f[_c].keys():
                        modelQuantities[_q] = f[_c][_q][:]

        return modelQuantities
    
    # Loading CHAOS model
    def load_chaos_hdf5(self, modelPath: str) -> dict:
        if not os.path.isfile(modelPath):
            raise self.Error("MODEL_PATH_ERROR")
        
        if not h5py.is_hdf5(modelPath):
            raise self.Error("NOT_HDF5_ERROR")
        
        modelQuantities = {}
        
        with h5py.File(modelPath, "r") as f:
            for _q in f.keys():
                modelQuantities[_q] = f[_q][:]

        return modelQuantities
    
    # Loading KALMAG model
    def load_kalmag_hdf5(self, modelPath: str) -> dict:
        if not os.path.isfile(modelPath):
            raise self.Error("MODEL_PATH_ERROR")
        
        if not h5py.is_hdf5(modelPath):
            raise self.Error("NOT_HDF5_ERROR")
        
        modelQuantities = {}
        
        with h5py.File(modelPath, "r") as f:
            for _q in f.keys():
                modelQuantities[_q] = f[_q][:]

        return modelQuantities
    
    # Loading KALMAG model
    def load_covobs_hdf5(self, modelPath: str) -> dict:
        if not os.path.isfile(modelPath):
            raise self.Error("MODEL_PATH_ERROR")
        
        if not h5py.is_hdf5(modelPath):
            raise self.Error("NOT_HDF5_ERROR")
        
        modelQuantities = {}
        
        with h5py.File(modelPath, "r") as f:
            for _q in f.keys():
                modelQuantities[_q] = f[_q][:]

        return modelQuantities
    
    # ---
    # QUANTITIES
    # Quantities are Gauss coefficients of the MF, SV or U
    # ---

    # Retrieving the available quantities of a model
    def getQuantities(self, modelName: str) -> set:
        if not self.isLoaded(modelName):
            raise self.Error("MODEL_NOT_LOAD_ERROR")
        
        return self.getModel(modelName)["quantities"].keys()
    
    # Does the model have a specific quantity
    def hasQuantity(self, modelName: str, quantityName: str) -> bool:
        if not self.isLoaded(modelName):
            raise self.Error("MODEL_NOT_LOAD_ERROR")
        
        standardQuantityName = self.standardiseQuantityName(modelName, quantityName)
        
        return (standardQuantityName in self.getModel(modelName)["quantities"])
    
    # For names standardisation purpose
    def standardiseQuantityName(self, modelName, quantityName):
        if not self.isLoaded(modelName):
            raise self.Error("MODEL_NOT_LOAD_ERROR")
        
        modelType = self.getModel(modelName)["type"]

        if modelType in ("chaos_hdf5", "covobs_hdf5"):
            if quantityName == "MF": return "gnm"
            if quantityName == "SV": return "dgnm"

        return quantityName
    
    # Retrieving a quantity from a model
    def getQuantity(self, modelName: str, quantityName: str):
        if not self.isLoaded(modelName):
            raise self.Error("MODEL_NOT_LOAD_ERROR")
        
        standardQuantityName = self.standardiseQuantityName(modelName, quantityName)
        
        if not self.hasQuantity(modelName, standardQuantityName):
            raise self.Error("QUANTITY_NOT_EXIST_ERROR")
        
        return self.getModel(modelName)["quantities"][standardQuantityName]
    
    # Deleting a quantity
    def deleteQuantity(self, modelName: str, quantityName: str) -> None:
        if not self.isLoaded(modelName):
            raise self.Error("MODEL_NOT_LOAD_ERROR")
        
        if quantityName not in self.getQuantities(modelName):
            raise self.Error("QUANTITY_NOT_EXIST_ERROR")
        
        del self[modelName]["quantities"][quantityName]

    # ---
    # MEASURES
    # Measures are computed observables from a model quantities
    # ---

    # Does the model have this measure
    def hasMeasure(self, modelName: str, measureName: str) -> bool:
        if not self.isLoaded(modelName):
            raise self.Error("MODEL_NOT_LOAD_ERROR")
        
        return measureName in self.getModel(modelName)["measures"]
    
    # Retrieving the computable measures from the model
    def getComputableMeasures(self, modelName: str) -> bool:
        if not self.isLoaded(modelName):
            raise self.Error("MODEL_NOT_LOAD_ERROR")

        computableMeasures = []

        if self.hasQuantity(modelName, "MF"): computableMeasures.append("MF")
        if self.hasQuantity(modelName, "SV"): computableMeasures.append("SV")
        if self.hasQuantity(modelName, "SA"): computableMeasures.append("SA")
        if self.hasQuantity(modelName, "U"): computableMeasures.append("U")

        return computableMeasures
    
    # Check if a quantity is computable from the current model
    def isMeasureComputable(self, modelName: str, measureName: str) -> bool:
        if not self.isLoaded(modelName):
            raise self.Error("MODEL_NOT_LOAD_ERROR")
        
        return measureName in self.getComputableMeasures(modelName)
    
    # Retrieving the measures done with the model
    def getMeasures(self, modelName: str, measureName: str = None) -> set:
        if not self.isLoaded(modelName):
            raise self.Error("MODEL_NOT_LOAD_ERROR")
        
        if type(measureName) is type(None):
            return self.getModel(modelName)["measures"].keys()
        
        if not self.hasMeasure(modelName, measureName):
            raise self.Error("MEASURE_NOT_EXIST_ERROR")
        
        return self.getModel(modelName)["measures"][measureName]

    # Retrieving a measure with a specific context
    def getMeasure(self, modelName: str, measureName: str, context: dict = {}) -> dict:
        if not self.isLoaded(modelName):
            raise self.Error("MODEL_NOT_LOAD_ERROR")
        
        if not self.hasMeasure(modelName, measureName):
            raise self.Error("MEASURE_NOT_EXIST_ERROR")
        
        assumedContext = self.retrieveFullContext(modelName, measureName)

        if "r" not in context: context["r"] = assumedContext["r"]
        if "lmax" not in context: context["lmax"] = assumedContext["lmax"]
        if "grid" not in context: context["grid"] = assumedContext["grid"]
        if "norm" not in context: context["norm"] = assumedContext["norm"]
        if "phase" not in context: context["phase"] = assumedContext["phase"]
        if "reals" not in context: context["reals"] = assumedContext["reals"]
        
        if not self.isContextValid(context):
            raise self.Error("CONTEXT_NOT_VALID_ERROR")

        for measure in self.getMeasures(modelName, measureName):
            if self.compareContext(measure["context"], context):
                return measure["measure"]

        raise Exception("MEASURE_RETRIEVE_ERROR")

    # Misc for comparing contextes
    def compareContext(self, ctx1: dict, ctx2: dict) -> bool:
        if ctx1.keys() != ctx2.keys():
            return False
        
        for key in ctx1:
            if type(ctx1[key]) == numpy.ndarray:
                if not numpy.array_equiv(ctx1[key], ctx2[key]):
                    return False
                
            if isinstance(ctx1[key], (tuple, list)):
                if not (ctx1[key] == ctx2[key]):
                    return False
            
            if type(ctx1[key]) in (str, float, int, bool):
                if ctx1[key] != ctx2[key]:
                    return False
                
        return True
    
    # Misc for retrieving the full context
    def retrieveFullContext(self, modelName: str, measureName: str) -> dict:
        if not self.isLoaded(modelName):
            raise self.Error("MODEL_NOT_LOAD_ERROR")
        
        if measureName in ("U", "normU", "SpectraU"):
            lmax = self.retrieveLMAX(modelName, "U")
            r = self.constants["rCore"]
        
        if measureName in ("MF", "normMF", "SpectraMF", "PSDMF", "GradMF"):
            lmax = self.retrieveLMAX(modelName, "MF")
            r = self.constants["rEarth"]

        if measureName in ("SV", "normSV", "SpectraSV"):
            lmax = self.retrieveLMAX(modelName, "SV")
            r = self.constants["rEarth"]

        if measureName in ("ER", "normER"):
            lmax = self.retrieveLMAX(modelName, "ER")
            r = self.constants["rEarth"]

        grid = self.getCurrentGrid()[0]
        norm = "schmidt"
        phase = True
        reals = "mean"

        return {
            "r": r,
            "lmax": lmax,
            "grid": grid,
            "norm": norm,
            "phase": phase,
            "reals": reals
        }


    # Misc for checking context
    def isContextValid(self, context: dict) -> bool:
        if not self.hasGrid and "grid" not in context:
            return False
        
        if "r" in context and context["r"] < self.constants["rCore"]:
            return False

        if "lmax" in context and context["lmax"] < 1:
            return False

        return True

    # Adding a measure with a specific context
    def addMeasure(self, modelName: str, measureName: str, context={}) -> numpy.ndarray:
        if not self.isLoaded(modelName):
            raise self.Error("MODEL_NOT_LOAD_ERROR")

        if measureName not in ("MF", "SV", "U", "SpectraMF", "SpectraSV", "SpectraU", "PSDMF", "GradMF", "ER"):
            raise self.Error("MEASURE_NOT_EXIST_ERROR")
        
        if measureName == "U" or measureName == "SpectraU":
            if self.getModel(modelName)["type"] != "pygeodyn_hdf5":
                raise Exception("MODEL_NOT_REANALYSIS_ERROR")
        
        assumedContext = self.retrieveFullContext(modelName, measureName)

        if "r" not in context: context["r"] = assumedContext["r"]
        if "lmax" not in context: context["lmax"] = assumedContext["lmax"]
        if "grid" not in context: context["grid"] = assumedContext["grid"]
        if "norm" not in context: context["norm"] = assumedContext["norm"]
        if "phase" not in context: context["phase"] = assumedContext["phase"]
        if "reals" not in context: context["reals"] = assumedContext["reals"]

        # Checking the context for the grid
        if not isinstance(context["grid"], (str)):
            onGrid = False
            point = context["grid"]
        else:
            onGrid = True
            point = None
        
        if not self.isContextValid(context):
            raise self.Error("CONTEXT_NOT_VALID_ERROR")

        if self.hasMeasure(modelName, measureName):
            for measure in self.getMeasures(modelName, measureName):
                if self.compareContext(measure["context"], context):
                    return measure["measure"]

        match measureName:
            case "MF":          computedMeasure = self.computeObservableMF(modelName, r=context["r"], lmax=context["lmax"], norm=context["norm"], phase=context["phase"], reals=context["reals"], onGrid=onGrid, point=point)
            case "SV":          computedMeasure = self.computeObservableSV(modelName, r=context["r"], lmax=context["lmax"], norm=context["norm"], phase=context["phase"], reals=context["reals"], onGrid=onGrid, point=point, quantity="SV")
            case "ER":          computedMeasure = self.computeObservableSV(modelName, r=context["r"], lmax=context["lmax"], norm=context["norm"], phase=context["phase"], reals=context["reals"], onGrid=onGrid, point=point, quantity="ER")
            case "U":           computedMeasure = self.computeObservableU(modelName, lmax=context["lmax"], norm=context["norm"], phase=context["phase"], reals=context["reals"], onGrid=onGrid, point=point)
            
            case "SpectraMF":   computedMeasure = self.computeObservableSpectra(modelName, "MF", r=context["r"], reals=context["reals"])
            case "SpectraSV":   computedMeasure = self.computeObservableSpectra(modelName, "SV", r=context["r"], reals=context["reals"])
            case "SpectraU":    computedMeasure = self.computeObservableSpectra(modelName, "U", r=context["r"], reals=context["reals"])
            case "PSDMF":       computedMeasure = self.computeObservablePSD(modelName, "MF", reals=context["reals"])
            
            case "GradMF":      computedMeasure = self.computeObservableGradMF(modelName, r=context["r"], lmax=context["lmax"], norm=context["norm"], phase=context["phase"], reals=context["reals"], onGrid=onGrid, point=point)
            
            case default:       raise self.Error("MEASURE_NOT_EXIST_ERROR")

        if not self.hasMeasure(modelName, measureName):
            self[modelName]["measures"][measureName] = []
            if measureName in ("MF", "SV", "U", "GradMF", "ER"):
                self[modelName]["measures"]["norm" + measureName] = []
        
        self[modelName]["measures"][measureName].append({
            "measure": computedMeasure[0] if isinstance(computedMeasure, (tuple)) else computedMeasure,
            "context": context
        })
        
        if measureName in ("MF", "SV", "U", "ER"):
            self[modelName]["measures"]["norm" + measureName].append({
                "measure": computedMeasure[1],
                "context": context
            })

        return self.getMeasure(modelName, measureName, context)

    # ---
    # MAGNETIC COMPONENTS
    # Computing Northward (X), Eastward (Y), Downward (Z) components and
    # Declination (D), Inclination (I), Intensity (F) and Horizontal intensity (H)
    # ---

    def getMagneticComponent(self, modelName: str, measureName: str, measureComponent: str, context = {}) -> numpy.ndarray:
        if not self.isLoaded(modelName):
            raise self.Error("MODEL_NOT_LOAD_EXIST")
        
        if not self.hasMeasure(measureName):
            raise self.Error("MEASURE_NOT_EXIST_ERROR")

        if measureComponent not in ("X", "Y", "Z", "F", "H", "I", "D"):
            raise self.Error("COMPONENT_NOT_EXIST_ERROR")

        # Retrieving the measure
        measure = self.getMeasure(modelName, measureName, context)

        # Retrieving the (r, theta, phi) components
        Br = self.selectFromMeasure(modelName, measure, options={"component": "r"})
        Bt = self.selectFromMeasure(modelName, measure, options={"component": "theta"})
        Bp = self.selectFromMeasure(modelName, measure, options={"component": "phi"})

        # Computing the basic "magnetic" components
        X = -Bt
        Y = Bp
        Z = -Br

        # Computing the "composite" components
        F = numpy.sqrt(X**2 + Y**2 + Z**2)
        H = numpy.sqrt(X**2 + Y**2)
        D = numpy.arctan(Y / X)
        I = numpy.arctan(F / H)

        # Returning the component
        if measureComponent == "X": return X
        if measureComponent == "Y": return Y
        if measureComponent == "Z": return Z
        if measureComponent == "F": return F
        if measureComponent == "H": return H
        if measureComponent == "D": return D
        if measureComponent == "I": return I
    
    # ---
    # SPECTRA
    # ---
    
    # Computing the Lowes spectra of a given quantity (MF, SV or U)
    def computeObservableSpectra(self, modelName: str, quantityName: str, r: float, reals: str | int | tuple = "mean") -> numpy.ndarray:
        if not self.isLoaded(modelName):
            raise self.Error("MODEL_NOT_LOAD_ERROR")
        
        if not self.hasQuantity(modelName, quantityName):
            raise self.Error("QUANTITY_NOT_EXIST_ERROR")
        
        if quantityName not in ("MF", "SV", "U"):
            raise self.Error("BAD_QUANTITY_ERROR")
        
        if r < self.constants["rCore"]:
            raise self.Error("BAD_RADIUS_ERROR")
        
        # Retrieving the Gauss coefficients
        # They are either (ntimes, ngauss) or (nreals, ntimes, ngauss)
        gaussCoefficients = self.selectFromQuantity(modelName, quantityName, options={"reals": reals})

        lmax = self.retrieveLMAX(modelName, quantityName)

        # The spectra is either (nls, nreals, ntimes) or (nls, ntimes)
        spectra = numpy.zeros((lmax + 1,) + gaussCoefficients.shape[:-1])

        kmax = lmax * (lmax + 2)

        if quantityName in ("MF", "SV"):
            for k in range(0, kmax):
                c, n, m = self.retrieveNMFromK(k)
                spectra[n] += (n + 1) * (self.constants["rEarth"] / r)**(2 * n + 4) * gaussCoefficients[...,k]**2

        if quantityName == "U":
            gaussCoefficientsUT = gaussCoefficients[...,:kmax]
            gaussCoefficientsUP = gaussCoefficients[...,kmax:]

            for k in range(0, kmax):
                c, n, m = self.retrieveNMFromK(k)
                spectra[n] += numpy.sqrt(n * (n + 1) / (2 * n + 1)) * gaussCoefficientsUT[...,k]**2
                spectra[n] += numpy.sqrt(n * (n + 1) / (2 * n + 1)) * gaussCoefficientsUP[...,k]**2
        
        # We have (nls, nreals, ntimes) and we want (nreals, ntimes, nls)
        if len(spectra.shape) == 3:
            spectra = numpy.transpose(spectra, (2, 1, 0))

        # We have (nls, ntimes) and we want (ntimes, nls)
        if len(spectra.shape) == 2:
            spectra = numpy.transpose(spectra, (1, 0))

        return spectra
    
    # ---
    # PSD
    # ---

    # Computing the PSD of a given quantity
    def computeObservablePSD(self, modelName: str, quantityName: str, reals: str | int | tuple = "mean") -> numpy.ndarray:
        if not self.isLoaded(modelName):
            raise self.Error("MODEL_NOT_LOAD_ERROR")
        
        if not self.hasQuantity(modelName, quantityName):
            raise self.Error("QUANTITY_NOT_EXIST_ERROR")
        
        # Retrieving the quantity
        # we except its shape to be either (nreals, ntimes, ngauss) or (ntimes, ngauss)
        quantity = self.selectFromQuantity(modelName, quantityName, options={"reals": reals})

        # If there is no realisation, we are adding an axis at the beginning of the array to mimic one
        if len(quantity.shape) == 2:
            quantity = quantity[None,...]

        # Swapping axes
        # (nreals, ngauss, ntimes)
        quantity = numpy.swapaxes(quantity, 1, 2)

        # Retrieving the times
        times = self.getQuantity(modelName, "times")

        # Defining the time-step
        dt = numpy.diff(times)[0]

        # Defining the Hanning window
        window = numpy.hanning(times.size)

        # Computing the end-to-end slope (for detrending purpose)
        slope = (quantity[...,-1] - quantity[...,0]) / (times[-1] - times[0])

        # Defining the end-to-end trend
        trend = numpy.tensordot(slope, times - times[0], axes=0) + numpy.repeat(quantity[...,0,None], times.size, axis=-1)

        # Defining the detrended quantity
        detrendedQuantity = quantity - trend

        # Applying the window (and re-swapping axes)
        detrendedQuantity *= window

        # Computing the frequencies
        freqs = numpy.fft.fftfreq(times.size, dt)

        # Computing the normalised spectra
        spectra = numpy.fft.fft(detrendedQuantity, axis=-1) / times.size

        # Selecting only positive frequencies
        idxFreqs = numpy.argwhere(freqs > 0).ravel()

        # Selecting the corresponding values
        spectra = spectra[:,:,idxFreqs]

        # Swapping the axes
        spectra = numpy.swapaxes(spectra, 1, 2)

        # Collapsing spectra if there is no realisation
        if quantity.shape[0] == 1:
            spectra = spectra[0,...]

        return numpy.abs(spectra)**2
    
    # Misc for retrieving the frequencies
    def getPSDFrequencies(self, modelName: str) -> numpy.ndarray:
        if not self.isLoaded(modelName):
            raise self.Error("MODEL_NOT_LOAD_ERROR")
        
        # Retrieving times
        times = self.getQuantity(modelName, "times")

        # Computing the spacing
        dt = numpy.diff(times)[0]

        # Computing the frequencies
        freqs = numpy.fft.fftfreq(times.size, dt)

        # Selecting only positive frequencies
        idxFreqs = numpy.argwhere(freqs > 0).ravel()

        return freqs[idxFreqs]

    # ---
    # GRIDS
    # ---

    # Checking if a grid exists
    def isGrid(self, gridName: str) -> bool:
        return gridName in self.getGrids()

    # Retrieving the available grids
    def getGrids(self) -> set:
        return self.__grids.keys()

    # Retrieving a specific grid
    def getGrid(self, gridName: str) -> tuple:
        if not self.isGrid(gridName):
            raise self.Error("GRID_NOT_EXIST_ERROR")

        return self.__grids[gridName]
    
    # Setting a grid
    def setGrid(self, gridName: str) -> None:
        if not self.isGrid(gridName):
            raise self.Error("GRID_NOT_EXIST_ERROR")
        
        self.hasGrid = True
        self.currentGrid = gridName

    # Adding a grid and setting it
    def addGrid(self, gridName: str, thetaSpacing: int | float, phiSpacing: int | float) -> None:
        if self.isGrid(gridName):
            raise self.Error("GRID_ALREADY_EXIST_ERROR")
        
        if thetaSpacing < 0 or thetaSpacing > 90:
            raise self.Error("GRID_ANGULAR_SPACING_ERROR")
        
        if phiSpacing < 0 or phiSpacing > 180:
            raise self.Error("GRID_ANGULAR_SPACING_ERROR")
        
        gridTheta = numpy.linspace(1e-6, numpy.pi - 1e-6, int(180 / thetaSpacing) + 1)
        gridPhi = numpy.linspace(1e-6, 2 * numpy.pi - 1e-6, int(360 / thetaSpacing) + 1)

        self.__grids[gridName] = (gridTheta, gridPhi)

        self.setGrid(gridName)

    # Deleting a grid
    def deleteGrid(self, gridName) -> None:
        if self.isGrid(gridName):
            raise self.Error("GRID_ALREADY_EXIST_ERROR")
        
        del self.__grids[gridName]

    # Is the grid set
    def isGridSet(self) -> bool:
        return self.hasGrid

    # Retrieving the current grid
    def getCurrentGrid(self) -> tuple:
        if not self.isGridSet():
            raise self.Error("GRID_NOT_SET_ERROR")
        
        return self.currentGrid, self.getGrid(self.currentGrid)

    # ---
    # COMPUTATIONS of OPERATORS
    # ---

    # Computing the Legendre polynomials (and first derivatives) over the whole grid
    def computeLegendrePolynomials(self, lmax: int, norm: str = "schmidt", phase: bool = True, onGrid: bool = True, point: tuple = None) -> tuple:
        if lmax < 1:
            raise self.Error("BAD_LMAX_ERROR")
        
        if norm not in ("schmidt"):
            raise self.Error("NORM_NOT_EXIST_ERROR")
        
        if not self.isGridSet():
            raise self.Error("GRID_NOT_SET_ERROR")
        
        # Going back on the grid
        if not onGrid and type(point) == type(None):
            onGrid = True
        
        if onGrid:
            gridContext = self.getCurrentGrid()[0]
        else:
            gridContext = point
        
        operatorContext = {
            "lmax": lmax,
            "grid": gridContext,
            "norm": norm,
            "phase": phase
        }
        
        try:
            return self.getOperator("LegendrePolynomials", operatorContext)
        except Exception:
            pass
        
        def factorial(n):
            return numpy.prod(numpy.arange(1.0, n + 1.0, 1.0))
        
        def schmidt(n, m):
            return numpy.sqrt((2 - (m == 0)) * factorial(n - m) / factorial(n + m))
        
        if onGrid:
            _, (thetas, phis) = self.getCurrentGrid()
        else:
            thetas = numpy.deg2rad(numpy.array([point[0]]))
            phis = numpy.deg2rad(numpy.array([point[1]]))
        
        Normalisation = numpy.zeros((lmax + 1, lmax + 1))
        CondonShortleyPhase = numpy.zeros((lmax + 1, lmax + 1))
        
        for n in range(1, lmax + 1):
            for m in range(0, n + 1):
                if norm == "schmidt": Normalisation[n,m] = schmidt(n,m)
                CondonShortleyPhase[n,m] = (-1)**m

        P = numpy.zeros((thetas.size, lmax + 1, lmax + 1))
        dP = numpy.zeros((thetas.size, lmax + 1, lmax + 1))

        for nth, th in enumerate(thetas):
            P[nth,...], dP[nth,...] = scipy.special.lpmn(lmax, lmax, numpy.cos(th))
            dP[nth,...] *= -numpy.sin(th)

        P = numpy.swapaxes(P, 1, 2)
        dP = numpy.swapaxes(dP, 1, 2)

        P *= Normalisation
        dP *= Normalisation

        if phase is True:
            P *= CondonShortleyPhase
            dP *= CondonShortleyPhase

        P_extended = numpy.expand_dims(P, axis=1)
        P_extended = numpy.repeat(P_extended, phis.size, axis=1)

        dP_extended = numpy.expand_dims(dP, axis=1)
        dP_extended = numpy.repeat(dP_extended, phis.size, axis=1)

        self.addOperator("LegendrePolynomials", (P_extended, dP_extended), operatorContext)

        return P_extended, dP_extended
    
    # Computing the Magnetic field operator (for MF, SV and SA)
    def computeOperatorHb(self, r: float, lmax: int, norm: str = "schmidt", phase: bool = True, onGrid: bool = True, point: tuple = None) -> numpy.ndarray:
        if lmax < 1:
            raise self.Error("BAD_LMAX_ERROR")
        
        if norm not in ("schmidt"):
            raise self.Error("NORM_NOT_EXIST_ERROR")
        
        if not self.isGridSet():
            raise self.Error("GRID_NOT_SET_ERROR")
        
        if r < self.constants["rCore"]:
            raise self.Error("BAD_RADIUS_ERROR")
        
        # Going back on the grid
        if not onGrid and type(point) == type(None):
            onGrid = True
        
        if onGrid:
            gridContext = self.getCurrentGrid()[0]
        else:
            gridContext = point
        
        operatorContext = {
            "r": r,
            "lmax": lmax,
            "grid": gridContext,
            "norm": norm,
            "phase": phase
        }

        try:
            return self.getOperator("MagneticFieldOperator", operatorContext)
        except Exception:
            pass
        
        if onGrid:
            _, (thetas, phis) = self.getCurrentGrid()
        else:
            thetas = numpy.deg2rad(numpy.array([point[0]]))
            phis = numpy.deg2rad(numpy.array([point[1]]))

        P, dP = self.computeLegendrePolynomials(lmax, norm, phase, onGrid, point)

        kmax = lmax * (lmax + 2)

        H = numpy.zeros((thetas.size, phis.size, kmax, 3))

        N, M = numpy.meshgrid(numpy.arange(0, lmax + 1), numpy.arange(0, lmax + 1), indexing="ij")
        TH, PH = numpy.meshgrid(thetas, phis, indexing="ij")

        COSMPHI = numpy.cos(numpy.tensordot(PH, M, axes=0))
        SINMPHI = numpy.sin(numpy.tensordot(PH, M, axes=0))
        SINTH = numpy.sin(TH)

        for k in range(0, kmax):
            c, n, m = self.retrieveNMFromK(k)

            if c == "g":
                H[...,k,0] = (n + 1) * (self.constants["rEarth"] / r)**(n + 2) * COSMPHI[...,n,m] * P[...,n,m]
                H[...,k,1] = -(self.constants["rEarth"] / r)**(n + 2) * COSMPHI[...,n,m] * dP[...,n,m]
                H[...,k,2] = m * (self.constants["rEarth"] / r)**(n + 2) * SINMPHI[...,n,m] * P[...,n,m] / SINTH
            else:
                H[...,k,0] = (n + 1) * (self.constants["rEarth"] / r)**(n + 2) * SINMPHI[...,n,m] * P[...,n,m]
                H[...,k,1] = -(self.constants["rEarth"] / r)**(n + 2) * SINMPHI[...,n,m] * dP[...,n,m]
                H[...,k,2] = -m * (self.constants["rEarth"] / r)**(n + 2) * COSMPHI[...,n,m] * P[...,n,m] / SINTH

        self.addOperator("MagneticFieldOperator", H, operatorContext)

        return H
    
    # Computing the Gradient Operator of the Magnetic Field
    def computeOperatorGradHb(self, r: float, lmax: int, norm: str = "schmidt", phase: bool = True, onGrid: bool = True, point: tuple = None) -> numpy.ndarray:
        if lmax < 1:
            raise self.Error("BAD_LMAX_ERROR")
        
        if norm not in ("schmidt"):
            raise self.Error("NORM_NOT_EXIST_ERROR")
        
        if not self.isGridSet():
            raise self.Error("GRID_NOT_SET_ERROR")
        
        if r < self.constants["rCore"]:
            raise self.Error("BAD_RADIUS_ERROR")
        
        # Going back on the grid
        if not onGrid and type(point) == type(None):
            onGrid = True
        
        if onGrid:
            gridContext = self.getCurrentGrid()[0]
        else:
            gridContext = point
        
        operatorContext = {
            "r": r,
            "lmax": lmax,
            "grid": gridContext,
            "norm": norm,
            "phase": phase
        }

        try:
            return self.getOperator("GradMagneticFieldOperator", operatorContext)
        except Exception:
            pass
        
        if onGrid:
            _, (thetas, phis) = self.getCurrentGrid()
        else:
            thetas = numpy.deg2rad(numpy.array([point[0]]))
            phis = numpy.deg2rad(numpy.array([point[1]]))

        P, dP = self.computeLegendrePolynomials(lmax, norm, phase, onGrid, point)

        _, (thetas_grid, _) = self.getCurrentGrid()

        # Computing second-order derivative of the Legendre functions
        # Using finite-difference
        d2P = numpy.gradient(dP, thetas_grid, axis=0)

        kmax = lmax * (lmax + 2)

        H = numpy.zeros((thetas.size, phis.size, kmax, 3))

        N, M = numpy.meshgrid(numpy.arange(0, lmax + 1), numpy.arange(0, lmax + 1), indexing="ij")
        TH, PH = numpy.meshgrid(thetas, phis, indexing="ij")

        COSMPHI = numpy.cos(numpy.tensordot(PH, M, axes=0))
        SINMPHI = numpy.sin(numpy.tensordot(PH, M, axes=0))
        SINTH = numpy.sin(TH)
        SIN2TH = SINTH**2

        for k in range(0, kmax):
            c, n, m = self.retrieveNMFromK(k)

            if c == "g":
                H[...,k,0] = -(n + 1) * (n + 2) * (self.constants["rEarth"] / r)**(n + 2) * COSMPHI[...,n,m] * P[...,n,m] / r
                H[...,k,1] = -(self.constants["rEarth"] / r)**(n + 2) * COSMPHI[...,n,m] * d2P[...,n,m] / r
                H[...,k,2] = m**2 * (self.constants["rEarth"] / r)**(n + 2) * COSMPHI[...,n,m] * P[...,n,m] / (r * SIN2TH)
            else:
                H[...,k,0] = -(n + 1) * (n + 2) * (self.constants["rEarth"] / r)**(n + 2) * SINMPHI[...,n,m] * P[...,n,m] / r
                H[...,k,1] = -(self.constants["rEarth"] / r)**(n + 2) * SINMPHI[...,n,m] * d2P[...,n,m] / r
                H[...,k,2] = m**2 * (self.constants["rEarth"] / r)**(n + 2) * SINMPHI[...,n,m] * P[...,n,m] / (r * SIN2TH)

        self.addOperator("GradMagneticFieldOperator", H, operatorContext)

        return H
    
    # Computing the operator for the Core flow (U)
    # /!\ We are only computing the horizontal components
    # First, the toroidal part, then, the poloidal one
    def computeOperatorHu(self, lmax: int, norm: str = "schmidt", phase: bool = True, onGrid: bool = True, point: tuple = None) -> numpy.ndarray:
        if lmax < 1:
            raise self.Error("BAD_LMAX_ERROR")
        
        if norm not in ("schmidt"):
            raise self.Error("NORM_NOT_EXIST_ERROR")
        
        if not self.isGridSet():
            raise self.Error("GRID_NOT_SET_ERROR")
        
        # Going back on the grid
        if not onGrid and type(point) == type(None):
            onGrid = True
        
        if onGrid:
            gridContext = self.getCurrentGrid()[0]
        else:
            gridContext = point
        
        operatorContext = {
            "lmax": lmax,
            "grid": gridContext,
            "norm": norm,
            "phase": phase
        }

        try:
            return self.getOperator("CoreFlowOperator", operatorContext)
        except Exception:
            pass
        
        if onGrid:
            _, (thetas, phis) = self.getCurrentGrid()
        else:
            thetas = numpy.deg2rad(numpy.array([point[0]]))
            phis = numpy.deg2rad(numpy.array([point[1]]))

        P, dP = self.computeLegendrePolynomials(lmax, norm, phase)

        kmax = lmax * (lmax + 2)

        Y = numpy.zeros((thetas.size, phis.size, kmax, 3))
        Ψ = numpy.zeros((thetas.size, phis.size, kmax, 3))
        Φ = numpy.zeros((thetas.size, phis.size, kmax, 3))

        TH, PH = numpy.meshgrid(thetas, phis, indexing="ij")
        N, M = numpy.meshgrid(numpy.arange(0, lmax + 1),numpy.arange(0, lmax + 1, 1), indexing="ij")

        COSMPH = numpy.cos(numpy.tensordot(PH, M, axes=0))
        SINMPH = numpy.sin(numpy.tensordot(PH, M, axes=0))
        SINTH = numpy.sin(TH)

        for k in range(0, kmax):
            c, n, m = self.retrieveNMFromK(k)

            if c == "g":
                Y[...,k,0] = COSMPH[...,n,m] * P[...,n,m]
                Ψ[...,k,1] = COSMPH[...,n,m] * dP[...,n,m]
                Ψ[...,k,2] = -m * SINMPH[...,n,m] * P[...,n,m] / SINTH
            else:
                Y[...,k,0] = SINMPH[...,n,m] * P[...,n,m]
                Ψ[...,k,1] = SINMPH[...,n,m] * dP[...,n,m]
                Ψ[...,k,2] = m * COSMPH[...,n,m] * P[...,n,m] / SINTH

            Φ[...,k,1] = -Ψ[...,k,2]
            Φ[...,k,2] = Ψ[...,k,1]

        self.addOperator("CoreFlowOperator", (-Φ, Ψ), operatorContext)

        return -Φ, Ψ
    
    # Misc function for retrieving (n,m) from k
    def retrieveNMFromK(self, kSought: int) -> tuple:
        k = 0
        for l in range(1, 50):
            for m in range(0, l + 1):
                if kSought == k: return "g", l, m
                k += 1

                if m != 0:
                    if kSought == k: return "h", l, m
                    k += 1
        raise Exception(self.Error("GAUSS_BAD_COEFF_ERROR"))
    
    # Misc function for retrieving k from (n,m)
    def retrieveKFromNM(self, cSought: str, nSought: int, mSought: int) -> int | None:

        if cSought == "h" and mSought == 0:
            raise Exception(self.Error("GAUSS_BAD_COEFF_ERROR"))

        k = 0
        for l in range(1, 50):
            for m in range(0, l + 1):
                if l == nSought and m == mSought and cSought == "g": return k
                k += 1

                if m != 0:
                    if l == nSought and m == mSought and cSought == "h": return k
                    k += 1
        raise Exception(self.Error("GAUSS_BAD_COEFF_ERROR"))
    
    # COMPUTATIONS of OBSERVABLES

    # Misc for retrieving the maximum degree (lmax) from a model quantity
    def retrieveLMAX(self, modelName: str, quantityName: str) -> int:
        if not self.isLoaded(modelName):
            raise self.Error("MODEL_NOT_LOAD_ERROR")
        
        if not self.hasQuantity(modelName, quantityName):
            raise self.Error("QUANTITY_NOT_EXIST_ERROR")
        
        soughtQuantity = self.getQuantity(modelName, quantityName)

        kmax = soughtQuantity.shape[-1]

        if quantityName == "U":
            kmax //= 2

        return int(numpy.sqrt(kmax + 1)) - 1

    # Computing the magnetic field (and its norm)
    def computeObservableMF(self, modelName: str, r: float, lmax: int, norm: str = "schmidt", phase: bool = True, reals: str | int | tuple = "mean", onGrid: bool = True, point: tuple = None) -> tuple:
        if not self.isLoaded(modelName):
            raise self.Error("MODEL_NOT_LOAD_ERROR")
        
        if not self.hasQuantity(modelName, "MF"):
            raise self.Error("QUANTITY_NOT_EXIST_ERROR")
        
        if r < self.constants["rCore"]:
            raise self.Error("BAD_RADIUS_ERROR")
        
        if lmax < 1:
            raise self.Error("BAD_LMAX_ERROR")
        
        if norm not in ("schmidt"):
            raise self.Error("NORM_NOT_EXIST_ERROR")
        
        # Going back on the grid
        if not onGrid and type(point) == type(None):
            onGrid = True
        
        if onGrid:
            gridContext = self.getCurrentGrid()[0]
        else:
            gridContext = point
        
        measureContext = {
            "r": r,
            "lmax": lmax,
            "grid": gridContext,
            "norm": norm,
            "phase": phase,
            "reals": reals
        }
        
        try:
            return self.getMeasure(modelName, "MF", measureContext)
        except Exception:
            pass
        
        # Retrieving the operator
        operator = self.computeOperatorHb(r, lmax, norm, phase, onGrid, point)

        # Retrieving the Gauss coefficients (either with or without realisations, if any)
        gaussCoefficients = self.selectFromQuantity(modelName, "MF", options={"reals": reals})

        # Retrieving the spherical harmonics maximum degree
        lmaxFromQuantity = self.retrieveLMAX(modelName, "MF")
        lmax = min(lmaxFromQuantity, lmax)

        print(lmax)

        if lmax < 1:
            raise self.Error("BAD_LMAX_ERROR")

        kmax = lmax * (lmax + 2)

        # We want to perform the tensor dot product between H and g

        # (nthetas, nphis, ngauss, ncomps)
        # We are swapping axes to get (nthetas, nphis, ncomps, ngauss)
        operator = numpy.swapaxes(operator, -2, -1)[...,:kmax]

        # either (nreals, ntimes, ngauss) or (ntimes, ngauss)
        # We are swapping axes to get either (ngauss, ntimes) or (ngauss, ntimes, nreals)
        gaussCoefficients = numpy.swapaxes(gaussCoefficients[...,:kmax], 0, -1)

        # Performing the tensor dot product between the operator and the gauss coefficients
        # We get either:
        # (nthetas, nphis, ncomps, ngauss) x (ngauss, ntimes) => (nthetas, nphis, ncomps, ntimes)
        # (nthetas, nphis, ncomps, ngauss) x (ngauss, ntimes, nreals) => (nthetas, nphis, ncomps, ntimes, nreals)
        computedMF = numpy.tensordot(operator, gaussCoefficients, axes=1)

        # We have (nthetas, nphis, ncomps, ntimes) and we want (ntimes, nthetas, nphis, ncomps)
        if len(computedMF.shape) == 4:
            computedMF = numpy.transpose(computedMF, (3, 0, 1, 2))

        # We have (nthetas, nphis, ncomps, ntimes, nreals) and we want (nreals, ntimes, nthetas, nphis, ncomps)
        if len(computedMF.shape) == 5:
            computedMF = numpy.transpose(computedMF, (4, 3, 0, 1, 2))

        normComputedMF = numpy.sqrt(numpy.sum(computedMF**2, axis=-1))

        return computedMF, normComputedMF
    
    # Computing the secular variation (and its norm)
    def computeObservableSV(self, modelName: str, r: float, lmax: int, norm: str = "schmidt", phase: bool = True, reals: str | int | tuple = "mean", onGrid: bool = True, point: tuple = None, quantity: str = "SV") -> tuple:
        if not self.isLoaded(modelName):
            raise self.Error("MODEL_NOT_LOAD_ERROR")
        
        if not self.hasQuantity(modelName, "SV"):
            raise self.Error("QUANTITY_NOT_EXIST_ERROR")
        
        if r < self.constants["rCore"]:
            raise self.Error("BAD_RADIUS_ERROR")
        
        if lmax < 1:
            raise self.Error("BAD_LMAX_ERROR")
        
        if norm not in ("schmidt"):
            raise self.Error("NORM_NOT_EXIST_ERROR")
        
        # Going back on the grid
        if not onGrid and type(point) == type(None):
            onGrid = True
        
        if onGrid:
            gridContext = self.getCurrentGrid()[0]
        else:
            gridContext = point
        
        measureContext = {
            "r": r,
            "lmax": lmax,
            "grid": gridContext,
            "norm": norm,
            "phase": phase,
            "reals": reals
        }

        try:
            return self.getMeasure(modelName, quantity, measureContext)
        except Exception:
            pass
        
        # Retrieving the operator
        operator = self.computeOperatorHb(r, lmax, norm, phase, onGrid, point)

        # Retrieving the Gauss coefficients (either with or without realisations, if any)
        gaussCoefficients = self.selectFromQuantity(modelName, quantity, options={"reals": reals})

        # Retrieving the spherical harmonics maximum degree
        lmaxFromQuantity = self.retrieveLMAX(modelName, quantity)
        lmax = min(lmaxFromQuantity, lmax)

        if lmax < 1:
            raise self.Error("BAD_LMAX_ERROR")

        kmax = lmax * (lmax + 2)

        # We want to perform the tensor dot product between H and g

        # (nthetas, nphis, ngauss, ncomps)
        # We are swapping axes to get (nthetas, nphis, ncomps, ngauss)
        operator = numpy.swapaxes(operator, -2, -1)[...,:kmax]

        # either (nreals, ntimes, ngauss) or (ntimes, ngauss)
        # We are swapping axes to get either (ngauss, ntimes) or (ngauss, ntimes, nreals)
        gaussCoefficients = numpy.swapaxes(gaussCoefficients[...,:kmax], 0, -1)

        # Performing the tensor dot product between the operator and the gauss coefficients
        # We get either:
        # (nthetas, nphis, ncomps, ngauss) x (ngauss, ntimes) => (nthetas, nphis, ncomps, ntimes)
        # (nthetas, nphis, ncomps, ngauss) x (ngauss, ntimes, nreals) => (nthetas, nphis, ncomps, ntimes, nreals)
        computedSV = numpy.tensordot(operator, gaussCoefficients, axes=1)

        # We have (nthetas, nphis, ncomps, ntimes) and we want (ntimes, nthetas, nphis, ncomps)
        if len(computedSV.shape) == 4:
            computedSV = numpy.transpose(computedSV, (3, 0, 1, 2))

        # We have (nthetas, nphis, ncomps, ntimes, nreals) and we want (nreals, ntimes, nthetas, nphis, ncomps)
        if len(computedSV.shape) == 5:
            computedSV = numpy.transpose(computedSV, (4, 3, 0, 1, 2))

        normcomputedSV = numpy.sqrt(numpy.sum(computedSV**2, axis=-1))

        return computedSV, normcomputedSV
    
    # Computing the gradient of the magnetic field
    def computeObservableGradMF(self, modelName: str, r: float, lmax: int, norm: str = "schmidt", phase: bool = True, reals: str | int | tuple = "mean", onGrid: bool = True, point: tuple = None) -> numpy.ndarray:
        if not self.isLoaded(modelName):
            raise self.Error("MODEL_NOT_LOAD_ERROR")
        
        if not self.hasQuantity(modelName, "MF"):
            raise self.Error("QUANTITY_NOT_EXIST_ERROR")
        
        if r < self.constants["rCore"]:
            raise self.Error("BAD_RADIUS_ERROR")
        
        if lmax < 1:
            raise self.Error("BAD_LMAX_ERROR")
        
        if norm not in ("schmidt"):
            raise self.Error("NORM_NOT_EXIST_ERROR")
        
        # Going back on the grid
        if not onGrid and type(point) == type(None):
            onGrid = True
        
        if onGrid:
            gridContext = self.getCurrentGrid()[0]
        else:
            gridContext = point
        
        measureContext = {
            "r": r,
            "lmax": lmax,
            "grid": gridContext,
            "norm": norm,
            "phase": phase,
            "reals": reals
        }
        
        try:
            return self.getMeasure(modelName, "GradMF", measureContext)
        except Exception:
            pass
        
        # Retrieving the operator
        operator = self.computeOperatorGradHb(r, lmax, norm, phase, onGrid, point)

        # Retrieving the Gauss coefficients (either with or without realisations, if any)
        gaussCoefficients = self.selectFromQuantity(modelName, "MF", options={"reals": reals})

        # Retrieving the spherical harmonics maximum degree
        lmaxFromQuantity = self.retrieveLMAX(modelName, "MF")
        lmax = min(lmaxFromQuantity, lmax)

        if lmax < 1:
            raise self.Error("BAD_LMAX_ERROR")

        kmax = lmax * (lmax + 2)

        # We want to perform the tensor dot product between H and g

        # (nthetas, nphis, ngauss, ncomps)
        # We are swapping axes to get (nthetas, nphis, ncomps, ngauss)
        operator = numpy.swapaxes(operator, -2, -1)[...,:kmax]

        # either (nreals, ntimes, ngauss) or (ntimes, ngauss)
        # We are swapping axes to get either (ngauss, ntimes) or (ngauss, ntimes, nreals)
        gaussCoefficients = numpy.swapaxes(gaussCoefficients[...,:kmax], 0, -1)

        # Performing the tensor dot product between the operator and the gauss coefficients
        # We get either:
        # (nthetas, nphis, ncomps, ngauss) x (ngauss, ntimes) => (nthetas, nphis, ncomps, ntimes)
        # (nthetas, nphis, ncomps, ngauss) x (ngauss, ntimes, nreals) => (nthetas, nphis, ncomps, ntimes, nreals)
        computedMF = numpy.tensordot(operator, gaussCoefficients, axes=1)

        # We have (nthetas, nphis, ncomps, ntimes) and we want (ntimes, nthetas, nphis, ncomps)
        if len(computedMF.shape) == 4:
            computedMF = numpy.transpose(computedMF, (3, 0, 1, 2))

        # We have (nthetas, nphis, ncomps, ntimes, nreals) and we want (nreals, ntimes, nthetas, nphis, ncomps)
        if len(computedMF.shape) == 5:
            computedMF = numpy.transpose(computedMF, (4, 3, 0, 1, 2))

        normComputedMF = numpy.sqrt(numpy.sum(computedMF**2, axis=-1))

        return computedMF, normComputedMF
    
    # Computing the core flow (and its norm)
    def computeObservableU(self, modelName: str, lmax: int, norm: str = "schmidt", phase: bool = True, reals: str | int | tuple = "mean", onGrid: bool = True, point: tuple = None) -> tuple:
        if not self.isLoaded(modelName):
            raise self.Error("MODEL_NOT_LOAD_ERROR")
        
        if not self.hasQuantity(modelName, "U"):
            raise self.Error("QUANTITY_NOT_EXIST_ERROR")
        
        if lmax < 1:
            raise self.Error("BAD_LMAX_ERROR")
        
        if norm not in ("schmidt"):
            raise self.Error("NORM_NOT_EXIST_ERROR")
        
        # Going back on the grid
        if not onGrid and type(point) == type(None):
            onGrid = True
        
        if onGrid:
            gridContext = self.getCurrentGrid()[0]
        else:
            gridContext = point
        
        measureContext = {
            "r": self.constants["rCore"],
            "lmax": lmax,
            "grid": gridContext,
            "norm": norm,
            "phase": phase,
            "reals": reals
        }

        try:
            return self.getMeasure(modelName, "U", measureContext)
        except Exception:
            pass
        
        # Retrieving the operators to be applied on the toroidal and poloidal parts
        operatorUT, operatorUP = self.computeOperatorHu(lmax, norm, phase, onGrid, point)

        # Retrieving the Gauss coefficients
        gaussCoefficients = self.selectFromQuantity(modelName, "U", options={"reals": reals})

        # The Gauss coefficients are stored in the same array, we are separating the two coefficients
        kmax = gaussCoefficients.shape[-1] // 2

        # Separating the toroidal part from the poloidal part
        tnm = gaussCoefficients[...,:kmax]
        snm = gaussCoefficients[...,kmax:]

        # Retrieving the spherical harmonics maximum degree
        lmaxFromQuantity = self.retrieveLMAX(modelName, "U")
        lmax = min(lmaxFromQuantity, lmax)

        kmax = lmax * (lmax + 2)

        # We want to perform the tensor dot product Ht x tnm + Hs x snm

        # We have either (nreals, ntimes, ngauss) or (ntimes, ngauss)
        # We are swapping the axes to get either (ngauss, ntimes, reals) or (ngauss, ntimes)
        tnm = numpy.swapaxes(tnm[...,:kmax], 0, -1)
        snm = numpy.swapaxes(snm[...,:kmax], 0, -1)

        # We have (nthetas, nphis, ngauss, ncomps)
        # We are swapping axes to get (nthetas, nphis, ncomps, ngauss)
        operatorUT = numpy.swapaxes(operatorUT, -2, -1)[...,:kmax]
        operatorUP = numpy.swapaxes(operatorUP, -2, -1)[...,:kmax]

        # Performing the tensor dot product
        # We either get:
        # (nthetas, nphis, ncomps, ngauss) x (ngauss, ntimes, nreals) => (nthetas, nphis, ncomps, ntimes, nreals)
        # (nthetas, nphis, ncomps, ngauss) x (ngauss, ntimes) => (nthetas, nphis, ncomps, ntimes)
        computedU = numpy.tensordot(operatorUT, tnm, axes=1) + numpy.tensordot(operatorUP, snm, axes=1)

        # We have (nthetas, nphis, ncomps, ntimes) and we want (ntimes, nthetas, nphis, ncomps)
        if len(computedU.shape) == 4:
            computedU = numpy.transpose(computedU, (3, 0, 1, 2))

        # We have (nthetas, nphis, ncomps, ntimes, nreals) and we want (nreals, ntimes, nthetas, nphis, ncomps)
        if len(computedU.shape) == 5:
            computedU = numpy.transpose(computedU, (4, 3, 0, 1, 2))

        normComputedU = numpy.sqrt(numpy.sum(computedU**2, axis=-1))

        return computedU, normComputedU
    
    # ---
    # OPERATORS
    # ---

    # Does the operator exist
    def hasOperator(self, operatorName: str) -> bool:
        return (operatorName in self.getOperators())
    
    # Retrieving the operators
    def getOperators(self) -> set:
        return self.__computedOperators.keys()
    
    # Retrieving a specific operator
    def getOperator(self, operatorName: str, context: dict) -> numpy.ndarray:
        if not self.hasOperator(operatorName):
            raise self.Error("OPERATOR_NOT_EXIST_ERROR")
        
        for operator in self.__computedOperators[operatorName]:
            if self.compareContext(operator["context"], context):
                return operator["operator"]
            
        raise self.Error("OPERATOR_RETRIEVE_ERROR")
    
    # Adding an operator
    def addOperator(self, operatorName: str, operatorValues: numpy.ndarray, context: dict) -> numpy.ndarray:
        if not self.hasOperator(operatorName):
            self.__computedOperators[operatorName] = []
        
        try:
            self.getOperator(operatorName, context)
        except Exception:
            pass
        
        self.__computedOperators[operatorName].append({
            "operator": operatorValues,
            "context": context
        })

        return self.getOperator(operatorName, context)
    
    # ---
    # DATA FILTERING, TRUNCATION and SELECTION
    # ---

    # Perform a filtering wrt time using a Butterworth filter
    def timeFiltering(self, times: numpy.ndarray, signal: numpy.ndarray, Tmin: int | float, Tmax: int | float, order:int = 2, axis:int = 0) -> numpy.ndarray:
        dt = numpy.diff(times)[0]

        # Computing Nyquist frequency
        nyquist_freq = 1 / (2 * dt)

        min_freq = (1 / Tmin) / nyquist_freq
        max_freq = (1 / Tmax) / nyquist_freq

        window = [max_freq, min_freq]

        # Creating the filter
        bandpass_filter = scipy.signal.butter(order, window, btype="band", output="sos")

        # Applying the filter
        signal_filtered = scipy.signal.sosfiltfilt(bandpass_filter, signal, axis=axis)

        return signal_filtered
    
    # Selecting a quantity for a given time, realisation or coefficient
    def selectFromQuantity(self, modelName: str, quantityName: str, options: dict = {}) -> numpy.ndarray:
        if not self.isLoaded(modelName):
            raise self.Error("MODEL_NOT_LOAD_ERROR")
        
        # To avoid being used with observations, which do not have the same structure at all
        if self.getModel(modelName)["type"] not in self.__modelTypes:
            raise self.Error("BAD_MODEL_TYPE_ERROR")
        
        if not self.hasQuantity(modelName, quantityName):
            raise self.Error("QUANTITY_NOT_EXIST_ERROR")
        
        # Retrieving times
        times = self.getQuantity(modelName, "times")

        # Retrieving the quantity
        quantity = self.getQuantity(modelName, quantityName)

        # Checking for realisations and coefficients
        if quantityName == "times":
            hasReals = False
            hasCoeffs = False
        else:
            if len(quantity.shape) == 3:
                hasReals = True
                hasCoeffs = True
            else:
                hasReals = False
                hasCoeffs = True

        # Selecting a realisation (if any)
        if "reals" in options and hasReals:
            if options["reals"] == "mean":
                quantity = numpy.mean(quantity, axis=0)

            if isinstance(options["reals"], (int)):
                quantity = quantity[options["reals"],...]

            if isinstance(options["reals"], (tuple, list)):
                quantity = quantity[min(options["reals"]):max(options["reals"])+1]

        # Selecting a time
        if "time" in options:
            if isinstance(options["time"], (int, float)):
                idxTime = numpy.argmin(numpy.abs(times - options["time"]))

                if hasReals and len(quantity.shape) == 3:
                    quantity = quantity[:,idxTime,...]
                else:
                    quantity = quantity[idxTime,...]
            
            if isinstance(options["time"], (tuple, list)):
                idxTime0 = numpy.argmin(numpy.abs(times - options["time"][0]))
                idxTime1 = numpy.argmin(numpy.abs(times - options["time"][1]))

                if hasReals and len(quantity.shape) == 3:
                    quantity = quantity[:,min(idxTime0, idxTime1):max(idxTime0, idxTime1)+1,...]
                else:
                    quantity = quantity[min(idxTime0, idxTime1):max(idxTime0, idxTime1)+1,...]
        
        # Selecting a coefficient
        if "coeff" in options and hasCoeffs:
            if isinstance(options["coeff"], (int)):
                quantity = quantity[...,options["coeff"]]

            if isinstance(options["coeff"], (tuple, list)):
                if len(options["coeff"]) != 3:
                    raise self.Error("GAUSS_BAD_FORMAT_ERROR")
                
                c, n, m = options["coeff"]

                # When dealing with U, the toroidal and poloidal Gauss coefficients are stacked
                if quantityName == "U":

                    # Retrieving the SH maximum degree
                    lmax = self.retrieveLMAX(modelName, quantityName)
                    kmax = lmax * (lmax + 2)
                    
                    if c in ("tc", "sc"):
                        k = self.retrieveKFromNM("g", n, m)
                        if c == "sc": k += (kmax // 2)

                    if c in ("ts", "ss"):
                        k = self.retrieveKFromNM("h", n, m)
                        if c == "ss": k += (kmax // 2)

                    if c not in ("tc", "ts", "sc", "ss"):
                        raise self.Error("GAUSS_BAD_COEFF_ERROR")
                    
                else:
                    # Retrieving the corresponding index for MF and SV (no complications)
                    k = self.retrieveKFromNM(c, n, m)

                quantity = quantity[...,k]

        return quantity
    
    # Selecting a specific part of a measure
    # either a time (time range), polar (polar range), azimuthal (azimuthal range) or realisations
    def selectFromMeasure(self, modelName: str, measure: numpy.ndarray = None, options: dict = {}) -> numpy.ndarray:
        if not self.isLoaded(modelName):
            raise self.Error("MODEL_NOT_LOAD_ERROR")
        
        if type(measure) == type(None):
            raise self.Error("EMPTY_MEASURE_ERROR")

        # Checking if there is realisations
        # If not, we are adding an axis at the beginning to avoid complications
        if len(measure.shape) in (2, 4):
            measure = measure[None,...]

        # Here are the expected shapes:
        # - (nreals, ntimes, nls) for spectrum
        # - (nreals, ntimes, nthetas, nphis, ncomps) for fields

        if len(measure.shape) == 3:
            measureType = "spectra"
        elif len(measure.shape) == 5:
            measureType = "field"
        else:
            raise self.Error("BAD_MEASURE_SHAPE_ERROR")
        
        # Retrieving the grid
        _, (thetas, phis) = self.getCurrentGrid()

        # Converting into degrees
        thetas = numpy.rad2deg(thetas)
        phis = numpy.rad2deg(phis)
        
        # Retrieving the times
        times = self.getQuantity(modelName, "times")

        # Retrieving the components
        components = ("r", "theta", "phi")

        # Selecting a component
        if "component" in options and measureType == "field":
            if options["component"] in components:
                idxComponent = components.index(options["component"])
            else:
                idxComponent = 0

            measure = measure[...,idxComponent]

        # Selecting along the azimuthal angle
        if "phi" in options and measureType == "field":
            if isinstance(options["phi"], (tuple, list)):
                if len(options["phi"]) != 2:
                    raise self.Error("BAD_RANGE_SHAPE_ERROR")
                
                idxPhi0 = numpy.argmin(numpy.abs(options["phi"][0] - phis))
                idxPhi1 = numpy.argmin(numpy.abs(options["phi"][1] - phis))

                measure = measure[:,:,:,min(idxPhi0, idxPhi1):max(idxPhi0, idxPhi1)+1,...]
            
            if isinstance(options["phi"], (int, float)):
                idxPhi = numpy.argmin(numpy.abs(options["phi"] - phis))
                measure = measure[:,:,:,idxPhi,...]

        # Selecting along the polar angle
        if "theta" in options and measureType == "field":
            if isinstance(options["theta"], (tuple, list)):
                if len(options["theta"]) != 2:
                    raise self.Error("BAD_RANGE_SHAPE_ERROR")
                
                idxTheta0 = numpy.argmin(numpy.abs(options["theta"][0] - thetas))
                idxTheta1 = numpy.argmin(numpy.abs(options["theta"][1] - thetas))

                measure = measure[:,:,min(idxTheta0, idxTheta1):max(idxTheta0, idxTheta1)+1,...]
            
            if isinstance(options["theta"], (int, float)):
                idxTheta = numpy.argmin(numpy.abs(options["theta"] - thetas))
                measure = measure[:,:,idxTheta,...]

        # Selecting along time
        if "time" in options:
            if isinstance(options["time"], (tuple, list)):
                if len(options["time"]) != 2:
                    raise self.Error("BAD_RANGE_SHAPE_ERROR")
                
                idxTime0 = numpy.argmin(numpy.abs(options["time"][0] - times))
                idxTime1 = numpy.argmin(numpy.abs(options["time"][1] - times))

                measure = measure[:,min(idxTime0, idxTime1):max(idxTime0, idxTime1)+1,...]
            
            if isinstance(options["time"], (int, float)):
                idxTime = numpy.argmin(numpy.abs(options["time"] - times))
                measure = measure[:,idxTime,...]

        # Selecting along realisations
        if "reals" in options:
            if isinstance(options["reals"], (tuple, list)):
                if len(options["reals"]) != 2:
                    raise self.Error("BAD_RANGE_SHAPE_ERROR")
                
                measure = measure[min(options["reals"][0], options["reals"][1]):max(options["reals"][0], options["reals"][1])+1,...]

            if isinstance(options["reals"], (int)):
                measure = measure[options["reals"],...]

        # In the case we extended our array to mimic one realisation, we are collapsing it
        if measure.shape[0] == 1:
            measure = measure[0,...]

        return measure
    
    # ---
    # OBSERVATIONS
    # ---
    
    # Reading observations
    def loadObservation(self, observationName: str, observationType: str, observatoryType: str, observationPath: str) -> None:
        if self.isLoaded(observationName):
            raise self.Error("OBSERVATIONS_ALREADY_LOAD_ERROR")
        
        if observationType not in self.__observationTypes:
            raise self.Error("OBSERVATIONS_TYPE_ERROR")
        
        if not os.path.isfile(observationPath):
            raise self.Error("OBSERVATIONS_PATH_ERROR")
        
        match observationType:
            case "govo_cdf":    observationQuantities = self.load_govo_cdf(observationPath)
            case "lod_csv":     observationQuantities = self.load_lod_csv(observationPath)
            case "oam_hdf5":    observationQuantities = self.load_oam_hdf5(observationPath)
            case default:       pass

        self[observationName] = {
            "observatory": observatoryType,
            "type": observationType,
            "path": observationPath,
            "quantities": observationQuantities
        }
    
    # Misc for checking the validity of the CDF format
    def is_cdf(self, observationPath: str) -> bool:
        if not os.path.isfile(observationPath):
            return False
        
        with open(observationPath, "rb") as f:
            if f.read(4).hex() not in ("cdf30001", "cdf26002", "0000ffff"):
                return False
            
        return True
    
    # Loading GVOs observations (CDF format)
    def load_govo_cdf(self, observationPath: str) -> dict:
        if not os.path.isfile(observationPath):
            raise self.Error("OBSERVATIONS_PATH_ERROR")
        
        if not self.is_cdf(observationPath):
            raise self.Error("NOT_CDF_ERROR")
        
        observationQuantities = {}
        
        with cdflib.CDF(observationPath, "r") as f:
            for key in f.cdf_info().zVariables:
                observationQuantities[key] = f[key][:]

        # Post-processing the data
        # We want to get B_BO, B_SV and B_CF = (ntimes, nlats, nlongs, ncomps)

        # Retrieving the lats and longs
        lats = observationQuantities["Latitude"]
        longs = observationQuantities["Longitude"]

        # Converting into -90° <-> 90° for the latitude
        if numpy.max(lats) > 90:
            lats = 90 - lats

        # Converting into -180° <-> 180° for the longitude
        if numpy.max(longs) > 180:
            longs = (longs + 180) % 360 - 180

        # Creating the angular grid
        lats_grid = numpy.unique(lats)
        longs_grid = numpy.unique(longs)

        # Retrieving the dates
        times = numpy.unique(observationQuantities["Timestamp"]) / (365.25 * 24 * 60 * 60 * 1000)
        times_sv = numpy.unique(observationQuantities["Timestamp_SV"]) / (365.25 * 24 * 60 * 60 * 1000)

        # Computing the average altitude
        averageAltitude = numpy.mean(observationQuantities["Radius"])

        # Creating the matrices
        MF = numpy.zeros((times.size, lats_grid.size, longs_grid.size, 3))
        SV = numpy.zeros((times_sv.size, lats_grid.size, longs_grid.size, 3))
        CF = numpy.zeros((times.size, lats_grid.size, longs_grid.size, 3))

        # Creating the list of available points
        availablePoints = []

        # Looping over the main field observations
        for i in range(observationQuantities["B_OB"].shape[0]):
            currentTime = observationQuantities["Timestamp"][i] / (365.25 * 24 * 60 * 60 * 1000)
            currentLat = lats[i]
            currentLong = longs[i]

            currentMF = observationQuantities["B_OB"][i,:]
            currentCF = observationQuantities["B_CF"][i,:]

            idxTime = numpy.where(currentTime == times)[0][0]
            idxLat = numpy.where(currentLat == lats_grid)[0][0]
            idxLong = numpy.where(currentLong == longs_grid)[0][0]

            if numpy.all(numpy.isfinite(currentMF)) and numpy.all(currentMF != 0):
                if [currentLat, currentLong] not in availablePoints:
                    availablePoints.append([currentLat, currentLong])

            MF[idxTime][idxLat][idxLong] = currentMF
            CF[idxTime][idxLat][idxLong] = currentCF

        # Looping over the secular variation observations
        for i in range(observationQuantities["B_SV"].shape[0]):
            currentTime = observationQuantities["Timestamp_SV"][i] / (365.25 * 24 * 60 * 60 * 1000)
            currentLat = lats[i]
            currentLong = longs[i]

            currentSV = observationQuantities["B_SV"][i,:]

            idxTime = numpy.where(currentTime == times_sv)[0][0]
            idxLat = numpy.where(currentLat == lats_grid)[0][0]
            idxLong = numpy.where(currentLong == longs_grid)[0][0]

            if numpy.all(numpy.isfinite(currentSV)) and numpy.all(currentSV != 0):
                if [currentLat, currentLong] not in availablePoints:
                    availablePoints.append([currentLat, currentLong])

            SV[idxTime][idxLat][idxLong] = currentSV

        # Overwriting the data
        observationQuantities = {
            "times": times,
            "times_sv": times_sv,
            "lats": lats_grid,
            "longs": longs_grid,
            "availablePoints": availablePoints,
            "MF": MF,
            "SV": SV,
            "CF": CF,
            "r": averageAltitude
        }

        return observationQuantities
    
    # Loading OAM data
    # /!\ X, Y, Z components (not Br, Bt, Bp)
    def load_oam_hdf5(self, observationPath: str) -> dict:
        if not os.path.isfile(observationPath):
            raise self.Error("OBSERVATIONS_PATH_ERROR")
        
        if not h5py.is_hdf5(observationPath):
            raise self.Error("NOT_HDF5_ERROR")
        
        observationsQuantities = {}
        
        with h5py.File(observationPath, "r") as f:
            for quantity in f.keys():
                observationsQuantities[quantity] = f[quantity][:]

        return observationsQuantities
    
    # Loading the Length-of-Day data
    def load_lod_csv(self, observationPath: str) -> dict:
        if not os.path.isfile(observationPath):
            raise self.Error("OBSERVATIONS_PATH_ERROR")
        
        times = []
        lods = []
        
        with open(observationPath, newline='') as csvfile:
            data = csv.reader(csvfile, delimiter=',')

            next(data) # Skipping the header

            for line in data:
                times.append(float(line[0]))
                lods.append(float(line[1]))

        return {
            "times": numpy.array(times),
            "lod": numpy.array(lods)
        }
    
    # ---
    # OBSERVED QUANTITIES
    # ---

    # Does the observations have this quantity measured
    def hasObservation(self, observationName: str, quantityName: str) -> bool:
        if not self.isLoaded(observationName):
            raise self.Error("OBSERVATIONS_NOT_LOAD_ERROR")
        
        standardQuantityName = self.standardiseObservationName(observationName, quantityName)
        
        return (standardQuantityName in self.getObservations(observationName)["quantities"])

    # Retrieving observations
    def getObservations(self, observationName: str) -> dict:
        if not self.isLoaded(observationName):
            raise self.Error("OBSERVATIONS_NOT_LOAD_ERROR")
        
        return self[observationName]
    
    # Misc for observation names standardisation
    def standardiseObservationName(self, observationName: str, quantityName: str) -> str:
        if not self.isLoaded(observationName):
            raise self.Error("OBSERVATIONS_NOT_LOAD_ERROR")
        
        observationType = self.getObservations(observationName)["type"]

        return quantityName
    
    # Retrieving an observation
    def getObservation(self, observationName: str, quantityName: str) -> numpy.ndarray:
        if not self.isLoaded(observationName):
            raise self.Error("OBSERVATIONS_NOT_LOAD_ERROR")
        
        standardQuantityName = self.standardiseObservationName(observationName, quantityName)
        
        if not self.hasObservation(observationName, standardQuantityName):
            raise self.Error("OBSERVATION_NOT_EXIST_ERROR")
        
        return self.getObservations(observationName)["quantities"][standardQuantityName]
    
    # Retrieving the list of ground observatories
    def retrieveObservatories(self) -> dict:
        path_to_observatories = pkg_resources.resource_filename(__name__, "data/observatories_list.csv")

        if not os.path.isfile(path_to_observatories):
            raise self.Error("OBSERVATORIES_RETRIEVE_ERROR")
        
        if type(self.__observatories) != type(None):
            return self.__observatories
        
        self.__observatories = {}

        with open(path_to_observatories, newline='') as csvfile:
            data = csv.reader(csvfile, delimiter=',')

            next(data) # Skipping the header

            for observatory in data:
                observatoryCode = observatory[0]
                observatoryName = observatory[3]
                observatoryLat = float(observatory[4])
                observatoryLong = float(observatory[5])
                observatoryStatus = observatory[9]

                self.__observatories[observatoryCode] = {
                    "name": observatoryName,
                    "code": observatoryCode,
                    "lat": observatoryLat,
                    "long": observatoryLong,
                    "status": observatoryStatus
                }

        return self.__observatories
    
    # Retrieve the coordinates of an observatory
    def getObservatoryCoordinates(self, observatoryCode: int = None, observatoryName: str = None) -> dict:
        observatoriesList = self.retrieveObservatories()

        for observatory in observatoriesList:
            if observatoryCode is not None and observatoryCode == observatoriesList[observatory]["code"]:
                return observatoriesList[observatory]
            
            if observatoryName is not None and observatoryName == observatoriesList[observatory]["name"]:
                return observatoriesList[observatory]
            
    # Retrieving the available observatories
    def getAvailableObservatories(self) -> set:
        observatoriesList = self.retrieveObservatories()

        return observatoriesList.keys()
    
    # Checking if the observatory exist
    def isObservatory(self, observatoryName: str) -> bool:
        observatoriesList = self.retrieveObservatories()

        for observatoryCode in observatoriesList:
            if observatoryName == observatoryCode:
                return True
            
            if observatoriesList[observatoryCode]["name"] == observatoryName:
                return True
            
        return False
            
    # Misc for computing the distance between two points using latitudes and longitudes
    # See https://en.wikipedia.org/wiki/Haversine_formula
    def getDistanceBetweenTwoPoints(self, lat1: float, long1: float, lat2: float, long2: float) -> float:
        # Converting into radians
        lat1 = numpy.deg2rad(lat1)
        long1 = numpy.deg2rad(long1)
        lat2 = numpy.deg2rad(lat2)
        long2 = numpy.deg2rad(long2)

        deltaLat = lat2 - lat1
        deltaLong = long2 - long1

        x = numpy.sin(deltaLat / 2)**2 + numpy.cos(lat1) * numpy.cos(lat2) * numpy.sin(deltaLong / 2)**2

        return 2 * numpy.arctan2(numpy.sqrt(x), numpy.sqrt(1 - x))
    
    # Retrieve an observation at a given point
    # Either give the exact position or the observatory name (for GO only)
    # The algorithm will search for the closest grid point
    def getObservationAtPoint(self, observationName: str, quantityName: str, point: dict = {}) -> numpy.ndarray:
        if not self.isLoaded(observationName):
            raise self.Error("OBSERVATIONS_NOT_LOAD_ERROR")
        
        if not self.hasObservation(observationName, quantityName):
            raise self.Error("OBSERVATION_NOT_EXIST_ERROR")
        
        if "code" in point:
            if not self.isObservatory(point["code"]):
                raise self.Error("OBSERVATION_RETRIEVE_ERROR")
            
            point = self.getObservatoryCoordinates(observatoryCode=point["code"])

        if "name" in point:
            if not self.isObservatory(point["name"]):
                raise self.Error("OBSERVATION_RETRIEVE_ERROR")
            
            point = self.getObservatoryCoordinates(observatoryName=point["name"])

        # It will fail if we are not dealing with GO observations
        if "lat" not in point or "long" not in point:
            raise self.Error("OBSERVATION_RETRIEVE_ERROR")
        
        # Retrieving the latitudes and longitudes
        lats = self.getObservation(observationName, "lats")
        longs = self.getObservation(observationName, "longs")

        # Retrieving the list of available observations
        availablePoints = self.getObservation(observationName, "availablePoints")

        foundObservation = False

        for availablePoint in availablePoints:
            if numpy.abs(point["lat"] - availablePoint[0]) < 1e-4 and numpy.abs(point["long"] - availablePoint[1]) < 1e-4:
                foundObservation = True
                break

        if not foundObservation:
            raise self.Error("OBSERVATION_RETRIEVE_ERROR")
        
        idx_lat = numpy.argmin(numpy.abs((point["lat"] - lats)))
        idx_long = numpy.argmin(numpy.abs((point["long"] - longs)))

        observedQuantity = self.getObservation(observationName, quantityName)
        
        # Returning the closest data (if within the 10% spatial error)
        return observedQuantity[:,idx_lat,idx_long,:]
    
    # ---
    # FIGURES and SUBPLOTS
    # General plots and figures management
    # ---

    # Retrieving the available Figures
    def getFigures(self) -> set:
        return self.__figures.keys()
    
    # Retrieving a figure
    def getFigure(self, figureName: str) -> dict:
        if not self.isFigure(figureName):
            raise self.Error("FIGURE_NOT_EXIST_ERROR")
        
        return self.__figures[figureName]

    # Does the Figure exist
    def isFigure(self, figureName: str) -> bool:
        return figureName in self.getFigures()

    # Creating a figure
    def addFigure(self, figureName: str, figureLayout: tuple = (1,1), figureSize=(7, 5), overwrite: bool = True) -> None:
        if self.isFigure(figureName) and not overwrite:
            raise self.Error("FIGURE_ALREADY_EXIST_ERROR")
        
        if not isinstance(figureLayout, (tuple)):
            raise self.Error("BAD_LAYOUT_ERROR")
        
        if figureLayout[0] < 1 or figureLayout[1] < 1:
            raise self.Error("BAD_LAYOUT_ERROR")
        
        # Retrieving the number of rows and columns
        nrows, ncols = figureLayout

        # Creating the figure
        figure = plt.figure(constrained_layout=True, figsize=figureSize)
        gridspec = figure.add_gridspec(nrows, ncols)

        # Saving
        self.__figures[figureName] = {"figure": figure, "gridspec": gridspec, "axes": numpy.full((nrows, ncols), None)}

    # Deleting a figure
    def deleteFigure(self, figureName: str) -> None:
        if not self.isFigure(figureName):
            raise self.Error("FIGURE_NOT_EXIST_ERROR")
        
        del self.__figures[figureName]

    # Saving a figure
    def saveFigure(self, figureName: str, figurePath: str = "MyFigure.png", figureDPI: int = 300) -> None:
        if not self.isFigure(figureName):
            raise self.Error("FIGURE_NOT_EXIST_ERROR")

        self.getFigure(figureName)["figure"].savefig(figurePath, dpi=figureDPI)

    # Adding a subplot
    def addSubplot(self, figureName: str, subplotPosition: tuple = (1,1), subplotProjection: object = None, subplotOptions: dict = {}, overwriting: bool = True) -> None:
        if not self.isFigure(figureName):
            raise self.Error("FIGURE_NOT_EXIST_ERROR")
        
        # TODO: Check there is already a subplot at this position
        # If any, we are overwriting it and show a warning.
        # or do we raise an exception?
        if type(self.getFigure(figureName)["axes"][subplotPosition[0] - 1, subplotPosition[1] - 1]) != type(None) and overwriting == False:
            raise self.Error("SUBPLOT_ALREADY_EXIST_ERROR")
        
        # Retrieving the figure and the grid
        figure, gridspec = self.getFigure(figureName)["figure"], self.getFigure(figureName)["gridspec"]
        
        # Retrieving the geometry of the figure
        nrows, ncols = gridspec.get_geometry()

        # Checking we are not outside the grid
        if subplotPosition[0] > nrows or subplotPosition[1] > ncols:
            raise self.Error("BAD_LAYOUT_ERROR")
        
        # Adding the subplot to the figure
        ax = figure.add_subplot(gridspec[subplotPosition[0] - 1, subplotPosition[1] - 1], projection=subplotProjection)

        # Reading the options
        if "title" in subplotOptions: ax.set_title(subplotOptions["title"])
        if "xlabel" in subplotOptions: ax.set_xlabel(subplotOptions["xlabel"])
        if "ylabel" in subplotOptions: ax.set_ylabel(subplotOptions["ylabel"])
        if "xscale" in subplotOptions: ax.set_xscale(subplotOptions["xscale"])
        if "yscale" in subplotOptions: ax.set_yscale(subplotOptions["yscale"])
        if "grid" in subplotOptions: ax.grid(alpha=0.2)
        if "xlim" in subplotOptions: ax.set_xlim(subplotOptions["xlim"])
        if "ylim" in subplotOptions: ax.set_ylim(subplotOptions["ylim"])

        # Adding the axis
        self.__figures[figureName]["axes"][subplotPosition[0] - 1, subplotPosition[1] - 1] = ax

        # Updating the figure
        self.__figures[figureName]["figure"] = figure

    # Retrieving a subplot axis
    def retrieveSubplot(self, figureName: str, subplotPosition: tuple = (1,1)) -> matplotlib.axes.Axes:
        if not self.isFigure(figureName):
            raise self.Error("FIGURE_NOT_EXIST_ERROR")
        
        # Retrieving the figure and the grid
        gridspec = self.getFigure(figureName)["gridspec"]
        axes = self.getFigure(figureName)["axes"]
        
        # Retrieving the geometry of the figure
        nrows, ncols = gridspec.get_geometry()

        # Checking we are not outside the grid
        if subplotPosition[0] > nrows or subplotPosition[1] > ncols:
            raise self.Error("BAD_LAYOUT_ERROR")

        return axes[subplotPosition[0] - 1, subplotPosition[1] - 1]

    # Deleting a subplot
    def deleteSubplot(self, figureName: str, subplotPosition: tuple = (1,1)) -> None:
        if not self.isFigure(figureName):
            raise self.Error("FIGURE_NOT_EXIST_ERROR")
        
        # Retrieving the figure and the grid
        _, gridspec = self.getFigure(figureName)["figure"], self.getFigure(figureName)["gridspec"]
        
        # Retrieving the geometry of the figure
        nrows, ncols = gridspec.get_geometry()

        # Checking we are not outside the grid
        if subplotPosition[0] > nrows or subplotPosition[1] > ncols:
            raise self.Error("BAD_LAYOUT_ERROR")
        
        # Retrieving the axis
        axis = self.retrieveSubplot(figureName, subplotPosition)

        # Deleting the axis
        axis.remove()

    # ---
    # PLOT STYLES
    # ---

    # Defining styles
    def setColor(self, modelName: str, lineColor: str = "#000000", lineStyle: str = "dotted", lineWidth: int | float = 1) -> None:
        if not self.isLoaded(modelName):
            raise self.Error("MODEL_NOT_LOAD_ERROR")
        
        if len(lineColor) != 7 and lineColor[0] != "#":
            raise self.Error("BAD_COLOR_ERROR")
        
        if lineStyle not in ("dotted", "dashed", "solid", "dashdot"):
            raise self.Error("BAD_LINESTYLE_ERROR")
        
        if lineWidth < 1:
            raise self.Error("BAD_LINEWIDTH_ERROR")
        
        self.__colors[modelName] = {
            "color": lineColor,
            "linestyle": lineStyle,
            "linewidth": lineWidth
        }

    # Checking if a model has a color
    def hasColor(self, modelName: str) -> bool:
        if not self.isLoaded(modelName):
            return False
        
        return (modelName in self.__colors)

    # Retrieving the style
    def getColor(self, modelName: str) -> dict:
        if not self.isLoaded(modelName):
            raise self.Error("MODEL_NOT_LOAD_ERROR")
        
        if not self.hasColor(modelName):
            return {
                "color": "#000000",
                "linestyle": "solid",
                "linewidth": 1
            }
        else:
            return self.__colors[modelName]
        
    # ---
    # PLOTS
    # ---

    # Plotting a serie
    def plotSerie(self, figureName: str, modelName: str, subplotPosition: tuple = (1,1), x: numpy.ndarray = None, y: numpy.ndarray = None, showError: bool = False) -> None:
        if not self.isFigure(figureName):
            raise self.Error("FIGURE_NOT_EXIST_ERROR")
        
        if not self.isLoaded(modelName):
            raise self.Error("MODEL_NOT_LOAD_ERROR")
        
        # Retrieving the figure and the grid
        _, gridspec = self.getFigure(figureName)["figure"], self.getFigure(figureName)["gridspec"]
        
        # Retrieving the geometry of the figure
        nrows, ncols = gridspec.get_geometry()

        # Checking we are not outside the grid
        if subplotPosition[0] > nrows or subplotPosition[1] > ncols:
            raise self.Error("BAD_LAYOUT_ERROR")
        
        # Retrieving the axis
        axis = self.retrieveSubplot(figureName, subplotPosition)

        # Retrieving the style
        modelStyle = self.getColor(modelName)

        if len(x.shape) > 1:
            raise self.Error("BAD_DATA_SHAPE_ERROR")
        
        if len(y.shape) != 2 and len(y.shape) != 1:
            raise self.Error("BAD_DATA_SHAPE_ERROR")
        
        y_std = None
        
        if len(y.shape) == 2:
            y_std = numpy.std(y, axis=0)
            y = numpy.mean(y, axis=0)

        # Plotting
        axis.plot(x, y, label=modelName, **modelStyle)

        # Showing the dispersion
        if showError and type(y_std) != type(None):
            axis.fill_between(x, y - y_std, y + y_std, alpha=0.2, **modelStyle)

        axis.legend()

    # Plotting a map
    # e.g. time-latitude or time-longitude
    def plotMap(self, figureName: str, modelName: str, subplotPosition: tuple = (1,1), x: numpy.ndarray = None, y: numpy.ndarray = None, z: numpy.ndarray = None, options: dict = {}) -> None:
        if not self.isFigure(figureName):
            raise self.Error("FIGURE_NOT_EXIST_ERROR")
        
        if not self.isLoaded(modelName):
            raise self.Error("MODEL_NOT_LOAD_ERROR")
        
        # Retrieving the figure and the grid
        figure, gridspec = self.getFigure(figureName)["figure"], self.getFigure(figureName)["gridspec"]
        
        # Retrieving the geometry of the figure
        nrows, ncols = gridspec.get_geometry()

        # Checking we are not outside the grid
        if subplotPosition[0] > nrows or subplotPosition[1] > ncols:
            raise self.Error("BAD_LAYOUT_ERROR")
        
        # Retrieving the axis
        axis = self.retrieveSubplot(figureName, subplotPosition)

        # Default parameters for the plot
        plotOptions = {
            "vmin": -numpy.max(numpy.abs(z)),
            "vmax": numpy.max(numpy.abs(z)),
            "cmap": cmocean.cm.balance
        }

        # Default parameters for the colorbar
        colorBarOptions = {
            "extend": "both",
            "shrink": 1.0,
            "label": None,
            "orientation": "horizontal"
        }

        # Reading the plot options
        if "vmin" in options: plotOptions["vmin"] = options["vmin"]
        if "vmax" in options: plotOptions["vmax"] = options["vmax"]
        if "cmap" in options: plotOptions["cmap"] = options["cmap"]

        # Reading the colorbar options
        if "extend" in options: colorBarOptions["extend"] = options["extend"]
        if "shrink" in options: colorBarOptions["shrink"] = options["shrink"]
        if "label" in options: colorBarOptions["label"] = options["label"]
        if "orientation" in options: colorBarOptions["orientation"] = options["orientation"]
        
        # Interpolating on a thiner grid
        Xnew, Ynew, Znew = self.interpolation(x, y, z)

        # Plotting the map
        plottedMap = axis.pcolormesh(Xnew, Ynew, Znew, **plotOptions)
        
        # Adding the colorbar
        figure.colorbar(plottedMap, ax=axis, **colorBarOptions)

    def plotField(self, figureName: str, modelName: str, subplotPosition: tuple = (1,1), x: numpy.ndarray = None, y: numpy.ndarray = None, z: numpy.ndarray = None, options: dict = {}) -> None:
        if not self.isFigure(figureName):
            raise self.Error("FIGURE_NOT_EXIST_ERROR")
        
        if not self.isLoaded(modelName):
            raise self.Error("MODEL_NOT_LOAD_ERROR")
        
        # Retrieving the figure and the grid
        figure, gridspec = self.getFigure(figureName)["figure"], self.getFigure(figureName)["gridspec"]
        
        # Retrieving the geometry of the figure
        nrows, ncols = gridspec.get_geometry()

        # Checking we are not outside the grid
        if subplotPosition[0] > nrows or subplotPosition[1] > ncols:
            raise self.Error("BAD_LAYOUT_ERROR")
        
        # Retrieving the axis
        axis = self.retrieveSubplot(figureName, subplotPosition)

        # Default parameters for the plot
        plotOptions = {
            "vmin": -numpy.max(numpy.abs(z)),
            "vmax": numpy.max(numpy.abs(z)),
            "cmap": cmocean.cm.balance
        }

        # Default parameters for the colorbar
        colorBarOptions = {
            "extend": "both",
            "shrink": 1.0,
            "label": None,
            "orientation": "horizontal"
        }

        # Reading the plot options
        if "vmin" in options: plotOptions["vmin"] = options["vmin"]
        if "vmax" in options: plotOptions["vmax"] = options["vmax"]
        if "cmap" in options: plotOptions["cmap"] = options["cmap"]

        # Reading the colorbar options
        if "extend" in options: colorBarOptions["extend"] = options["extend"]
        if "shrink" in options: colorBarOptions["shrink"] = options["shrink"]
        if "label" in options: colorBarOptions["label"] = options["label"]
        if "orientation" in options: colorBarOptions["orientation"] = options["orientation"]

        # Interpolating on a thiner grid
        Xnew, Ynew, Znew = self.interpolation(x, y, z)

        # Adding the coastlines
        axis.coastlines()

        # Plotting the map
        plottedMap = axis.pcolormesh(Ynew, Xnew, Znew, rasterized=True, transform=cartopy.crs.PlateCarree(), **plotOptions)
        
        # Adding the colorbar
        figure.colorbar(plottedMap, ax=axis, **colorBarOptions)

    def streamPlot(self, figureName: str, modelName: str, subplotPosition: tuple = (1,1), x: numpy.ndarray = None, y: numpy.ndarray = None, z: numpy.ndarray = None, vx: numpy.ndarray = None, vy: numpy.ndarray = None, vz: numpy.ndarray = None, options: dict = {}) -> None:
        if not self.isFigure(figureName):
            raise self.Error("FIGURE_NOT_EXIST_ERROR")
        
        if not self.isLoaded(modelName):
            raise self.Error("MODEL_NOT_LOAD_ERROR")
        
        # Retrieving the figure and the grid
        gridspec = self.getFigure(figureName)["gridspec"]
        
        # Retrieving the geometry of the figure
        nrows, ncols = gridspec.get_geometry()

        # Checking we are not outside the grid
        if subplotPosition[0] > nrows or subplotPosition[1] > ncols:
            raise self.Error("BAD_LAYOUT_ERROR")
        
        # Creating the field plot
        self.plotField(figureName, modelName, subplotPosition, x, y, z, options)

        # Creating the stream plot

        # Retrieving the axis
        axis = self.retrieveSubplot(figureName, subplotPosition)

        # Creating the grid
        Y, X = numpy.meshgrid(y, x)

        # Showing the streamlines
        axis.streamplot(Y, X, vx, vy, transform=cartopy.crs.PlateCarree(), density=1.7, color='darkslategrey', linewidth=vz)

    # ---
    # CONVERSION
    # ---

    # Polar angle to latitude conversion
    def convertThetasToLatitudes(self, thetas: float | numpy.ndarray) -> float | numpy.ndarray:
        if numpy.max(thetas) <= numpy.pi:
            thetas = numpy.rad2deg(thetas)

        if numpy.max(thetas) >= 90:
            thetas = 90 - thetas

        return thetas

    # Azimuthal angle to longitude conversion
    def convertPhisToLongitudes(self, phis: float | numpy.ndarray) -> float | numpy.ndarray:
        if numpy.max(phis) <= 2 * numpy.pi:
            phis = numpy.rad2deg(phis)

        if numpy.max(phis) >= 180:
            phis = (phis + 180) % 360 - 180

        return phis
    
    # Latitude to polar angle conversion
    def convertLatitudesToThetas(self, latitudes: float | numpy.ndarray) -> float | numpy.ndarray:
        return 90 - latitudes
    
    # Longitude to azimuthal angle conversion
    def convertLongitudesToPhis(self, longitudes: float | numpy.ndarray) -> float | numpy.ndarray:
        return longitudes % 360
    
    # ---
    # INTERPOLATION
    # ---

    # Interpolating a 2D map on a thiner grid
    # Starting with the initial grid (x, y)
    # Extending it to get (xnew, ynew)
    # Interpolate the missing values of z to get znew
    def interpolation(self, x: numpy.ndarray, y: numpy.ndarray, z: numpy.ndarray) -> tuple:
        
        # Retrieving the grid size
        Nx = x.size
        Ny = y.size

        # Defining the original grid
        X, Y = numpy.meshgrid(x, y, indexing="ij")

        # Creating a denser grid
        xnew = numpy.linspace(x.min(), x.max(), min(10 * Nx, 1000))
        ynew = numpy.linspace(y.min(), y.max(), min(10 * Ny, 1000))

        Xnew, Ynew = numpy.meshgrid(xnew, ynew, indexing="ij")

        if X.shape != z.shape or Y.shape != z.shape:
            raise Exception()
        
        # The known points (from the initial grid)
        knownPoints = numpy.stack([X.ravel(), Y.ravel()], -1)

        # Interpolating the data
        Znew = scipy.interpolate.griddata(knownPoints, z.ravel(), (Xnew, Ynew), method="cubic", fill_value=numpy.nan)

        return Xnew, Ynew, Znew
    
    # ---
    # COMPUTATION COST and PRECISION
    # ---

    # Retrieving the numerical precision
    def getNumericalPrecision(self) -> str:
        return self.__numericalPrecision
    
    # Checking if the numerical precision exists
    def isNumericalPrecision(self, numericalPrecision: str) -> bool:
        return (numericalPrecision in self.getNumericalPrecisions())
    
    # Retrieving the available precisions
    def getNumericalPrecisions(self) -> set:
        return self.__numericalPrecision.keys()
    
    # Setting the numerical precision
    def setNumericalPrecision(self, numericalPrecision: str) -> None:
        if not self.isNumericalPrecision(numericalPrecision):
            raise self.Error("PRECISION_NOT_EXIST_ERROR")
        
        self.__numericalPrecision = numericalPrecision

    # Applying the precision
    def applyPrecision(self, numpyArray: numpy.ndarray) -> numpy.ndarray:
        # Retrieving the current precision
        currentPrecision = self.getNumericalPrecision()

        # Applying on the array
        return numpy.array(numpyArray, dtype=self.__precisions[currentPrecision])

    # Retrieving the numerical cost limit
    def getNumericalCostLimit(self) -> str:
        return self.__numericalCostLimit
    
    # Setting the numerical cost limit
    def setNumericalCostLimit(self, numericalCostLimit: float | int = 1) -> None:
        self.__numericalCostLimit = numericalCostLimit

    # Estimating the numerical cost of a tensor dot product
    def tensorDotProductCostEstimation(self, shape1: tuple, shape2: tuple) -> float:
        if shape1[-1] != shape2[0]:
            raise self.Error("PRECISION_BROADCAST_ERROR")
        
        # Retrieving the shape after the operation
        shapeAfterOperation = shape1[:-1] + shape2[1:]

        # Retrieving the precision (in bits)
        precision = 64

        # Estimating the numerical cost of the operation (in Go)
        numericalCost = math.prod(shapeAfterOperation) * precision / 8e9

        # Do we get past the limit
        if numericalCost > self.getLimit:
            raise self.Error("NUMERICAL_COST_OVERFLOW_ERROR")

        return numericalCost
    
    # Estimating the numerical cost of a tensor product
    def tensorProductCostEstimation(self, shape1: tuple, shape2: tuple) -> float:
        if shape1[-1] != shape2[0]:
            raise self.Error("PRECISION_BROADCAST_ERROR")
        
        # Retrieving the shape after the operation
        shapeAfterOperation = shape1 + shape2

        # Retrieving the precision (in bits)
        precision = 64

        # Estimating the numerical cost of the operation (in Go)
        numericalCost = math.prod(shapeAfterOperation) * precision / 8e9

        # Do we get past the limit
        if numericalCost > self.getLimit:
            raise self.Error("NUMERICAL_COST_OVERFLOW_ERROR")

        return numericalCost
    
    # ---
    # CHECKER
    # ---

    # Introducing a basic checker to check the variable types and values
    def sanitizeCheck(self, variable: object, types: tuple, relation: str = None, condition: int | float | tuple = None) -> bool:

        # Available relations
        availableRelations = set([
            ">", ">=", "<=", "<", "==", "!=", 
            "in", "inrange", "out", "outrange"
        ])

        # Starting by checking the type
        if not isinstance(variable, (types)):
            return False
        
        # Does we have a condition to check
        hasCondition = not(type(relation) == type(None) or type(condition) == type(None))
        
        # In case we are just checking the variable type
        if not hasCondition:
            return True
        
        # Checking the relation
        if hasCondition and relation not in availableRelations:
            raise Exception("The relation was not recognized.")
        
        # In case we have also to check for a relationship
        match relation:
            case "in": return variable in condition
            case "out": return not(variable in condition)
            case "inrange": return all([variable >= condition[0], variable <= condition[1]]) if len(condition) == 2 else False
            case "outrange": return not all([variable >= condition[0], variable <= condition[1]]) if len(condition) == 2 else False
            
        # We assume it is basic mathematical comparison (we are not using `eval` so we have to browse through all cases)
        match relation:
            case ">": return (variable > condition)
            case "<": return (variable < condition)
            case ">=": return (variable >= condition)
            case "<=": return (variable <= condition)
            case "==": return (variable == condition)
            case "!=": return (variable != condition)

        # By default, we are returning `False`
        return False