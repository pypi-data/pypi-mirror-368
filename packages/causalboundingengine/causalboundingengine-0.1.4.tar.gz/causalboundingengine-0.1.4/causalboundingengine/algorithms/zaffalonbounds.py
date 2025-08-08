import os

import pandas as pd
from causalboundingengine.algorithms.algorithm import Algorithm
import numpy as np


from causalboundingengine.algorithms.zaffalonbounds_util.zaffalon_setup import ensure_java_ready


class Zaffalonbounds(Algorithm):
    # This implementation integrates with the Java packages CREMA and CREDICI,
    # developed and maintained by IDSIA:
    #
    # - CREMA:  https://github.com/IDSIA/crema
    # - CREDICI: https://github.com/IDSIA/credici
    #
    # These tools are used via a JVM interface (through jpype) to compute bounds for causal queries
    # under assumptions such as confounding or instrumental variables.
    #
    # Both libraries are distributed under the GNU LGPL-3.0 license.
    # See their respective repositories for more details.

    def _compute_ATE(self, X: np.ndarray, Y: np.ndarray, Z: np.ndarray = None, **kwargs) -> tuple[float, float]:
        ensure_java_ready()
        if Z is not None:
            lower, upper = Zaffalonbounds._run_zaffalon_from_row_dict(
                query="ATE",
                isConf=False,
                X=X,
                Y=Y,
                Z=Z
            )
                
            return lower, upper
        else:
            lower, upper = Zaffalonbounds._run_zaffalon_from_row_dict(
                query="ATE",
                isConf=True,
                X=X,
                Y=Y
            )
            return lower, upper

    def _compute_PNS(self, X: np.ndarray, Y: np.ndarray, Z: np.ndarray = None, **kwargs) -> tuple[float, float]:
        ensure_java_ready()
        if Z is not None:
            lower, upper = Zaffalonbounds._run_zaffalon_from_row_dict(
                query="PNS",
                isConf=False,
                X=X,
                Y=Y,
                Z=Z
             )
            return lower, upper
        else:
            lower, upper = Zaffalonbounds._run_zaffalon_from_row_dict(
                query="PNS",
                isConf=True,
                X=X,
                Y=Y
            )
            return lower, upper
        


    @staticmethod
    def _run_zaffalon_from_row_dict(query, isConf=False, X = None, Y = None, Z = None):
        if isConf:
            df = pd.DataFrame({'Y': Y, 'X': X})
        else:
            df = pd.DataFrame({'Y': Y, 'X': X, 'Z': Z})
        bound_lower, bound_upper = Zaffalonbounds.run_experiment(query, df, isConf=isConf)

        return bound_lower, bound_upper



    @staticmethod
    def run_experiment(query, df, isConf=False):
        import jpype
        import jpype.imports
        from jpype.types import JArray, JByte
        # Resolve path to this file
        this_dir = os.path.abspath(os.path.dirname(__file__))
        
        

        # Resolve jars relative to this file
        jar_zaffalon = os.path.join(this_dir, "zaffalonbounds_util", 'zaffalon', "zaffalon.jar")
        jar_credici = os.path.join(this_dir, "zaffalonbounds_util",  "credici.jar")
        if not jpype.isJVMStarted():
            jpype.startJVM(classpath=[jar_zaffalon, jar_credici])

        csv_data = Zaffalonbounds._dataframe_to_csv_string(df, isConf=isConf)


        ByteArrayInputStream = jpype.JClass("java.io.ByteArrayInputStream")
        input_bytes = JArray(JByte)(csv_data.encode('utf-8'))
        stream = ByteArrayInputStream(input_bytes)
        String = jpype.JClass("java.lang.String")
        query = String(query)

        BinaryTask = jpype.JClass("zaffalon.BinaryIVTask")
        task = BinaryTask(stream, query, jpype.JBoolean(isConf))
        result = task.call()
                
        # result looks like this: '-0.5813,-0.2671'
        # Convert to tuple of floats
        result_str = str(result)  # Convert java.lang.String to Python str

        if 'ERROR' in result_str:
            raise RuntimeError(f"Zaffalon Java returned an error: {result_str}")

        lower, upper = map(float, result_str.strip().split(","))
        return (lower, upper)


    @staticmethod
    def _dataframe_to_csv_string(df, isConf=False):
        if isConf:
            csv_data = "X,Y\n"
            for x, y in zip(df['X'].values, df['Y'].values):
                csv_data += f"{x},{y}\n"
            #write to CSV for testing
            # with open("test.csv", "w") as f:
            #     f.write(csv_data)
            return csv_data.strip()
            
        csv_data = "Z,X,Y\n"
        for z, x, y in zip(df['Z'].values, df['X'].values, df['Y'].values):
            csv_data += f"{z},{x},{y}\n"
        #write to CSV for testing
        # with open("test.csv", "w") as f:
        #     f.write(csv_data)
        return csv_data.strip()