#%% Load modules...
__version__ = "2025.08.08a1"

import pythonnet, clr_loader, os
resources_folder_name = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Resources')

dotnet_folder_name = os.path.join(resources_folder_name, "dotnet")
if os.path.exists(dotnet_folder_name):
    # print("[aesim.simba debug] DOTNET_ROOT=" + dotnet_folder_name )
    os.environ["DOTNET_ROOT"] = dotnet_folder_name

runtime_config_path = os.path.join(resources_folder_name, 'Simba.Data.runtimeconfig.json')

def get_required_dotnet_runtime_version(runtime_config_path):
    import json, os
    with open(runtime_config_path, 'r') as f:
        data = json.load(f)
    name = data["runtimeOptions"]["framework"]["name"]
    version = data["runtimeOptions"]["framework"]["version"]
    return (name, version)

try:
    pythonnet.set_runtime(clr_loader.get_coreclr(runtime_config=runtime_config_path))
except Exception as e:
    (name, version) = get_required_dotnet_runtime_version(runtime_config_path)
    print("[aesim.simba debug] Impossible to load dotnet " + name + " version: " + version)
    print("[aesim.simba debug] dotnet_folder_name " + dotnet_folder_name + " (exists: " + str(os.path.exists(dotnet_folder_name)) + ")")
    raise e

import clr, sys

sys.path.append(resources_folder_name)
clr.AddReference("Simba.Data")

from Simba.Data.Repository import ProjectRepository, JsonProjectRepository
from Simba.Data import License, Design, Circuit, DesignExamples, ACSweep, SweepType, Status, Subcircuit
from Simba.Data import ThermalComputationMethodType, ThermalDataType, ThermalDataSemiconductorType
from Simba.Data.Thermal import ThermalData, IV_T, EI_VT
from Simba.Data.PsimImport import PsimImporter
from System import Array
import Simba.Data

# Make sure the assembly resolver is set up properly.
Simba.Data.FunctionsAssemblyResolver.RedirectAssembly()

# Register pythonnet type conversions for relevant Simba types.
import Python.Runtime
Python.Runtime.PyObjectConversions.RegisterEncoder(Simba.Data.DoubleArrayPythonEncoder.Instance)
Python.Runtime.PyObjectConversions.RegisterEncoder(Simba.Data.Double2DArrayPythonEncoder.Instance)
Python.Runtime.PyObjectConversions.RegisterEncoder(Simba.Data.ParameterToPythonEncoder.Instance)
Python.Runtime.PyObjectConversions.RegisterEncoder(Simba.Data.DoubleArrayPythonEncoder.Instance)
Python.Runtime.PyObjectConversions.RegisterDecoder(Simba.Data.PythonToParameterDecoder.Instance)
Python.Runtime.PyObjectConversions.RegisterDecoder(Python.Runtime.Codecs.IterableDecoder.Instance)
Python.Runtime.PyObjectConversions.RegisterDecoder(Python.Runtime.Codecs.ListDecoder.Instance)

# Optionally activate license from an environment variable if present.
if os.environ.get('SIMBA_DEPLOYMENT_KEY') is not None:
    License.Activate(os.environ.get('SIMBA_DEPLOYMENT_KEY'))

def create_analysis_progress(callback):
    """
    Create a Progress[AnalysisProgress] instance from a Python callback.

    Parameters
    ----------
    callback : callable
        A Python function or lambda that accepts either:
            - Two arguments: (progress_value, status), or
            - One argument: (analysis_progress) if you'd like the raw object.
        Typically, you'd use something like:

            def my_callback(progress_value, status):
                print(f"Progress: {progress_value}, Status: {status}")

    Returns
    -------
    progress_instance : Progress[AnalysisProgress]
        An instance that can be passed to NewJob(progress_instance).
    """
    from System import Action, Progress
    from Simba.Data.Analysis import AnalysisProgress

    def _handler(analysis_progress):
        # If you want to pass the entire object, do:
        # callback(analysis_progress)
        # If you'd like to pass only progress/status, do:
        callback(analysis_progress.Progress, analysis_progress.Status)

    # Create a .NET Action<AnalysisProgress> from our Python function:
    action = Action[AnalysisProgress](_handler)

    # Create and return the Progress<AnalysisProgress> object:
    return Progress[AnalysisProgress](action)


def import_psim_xml(file_path):
    """
    Import a PSIM XML file into a SIMBA repository.
    Parameters
    ----------
    file_path : str
        The path to the PSIM XML file to import.
    Returns
    -------
    Tuple[ProjectRepository, JsonProjectRepository, str]
        A tuple containing:
            - status: The status of the import operation
            - ProjectRepository: The  project repository with the SIMBA design.
            - str: Error message if any, otherwise an empty string.
    """
    from Simba.Data.PsimImport import PsimImporter
    ret = PsimImporter.CreateSIMBARepositoryFromPSIMFile(file_path);
    return ret.Item1, ret.Item2, ret.Item3