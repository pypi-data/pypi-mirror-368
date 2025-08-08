import numpy as np
import pandas as pd
from causalboundingengine.algorithms.algorithm import Algorithm

from causalboundingengine.algorithms.autobound_pkg.autobound.causalProblem import causalProblem
from causalboundingengine.algorithms.autobound_pkg.autobound.DAG import DAG
import warnings


class Autobound(Algorithm):
    # This module integrates code from the AutoBound project,
    # developed by Guilherme Duarte, Dean Knox, Jonathan Mummolo, and Ilya Shpitser.
    # 
    # The original implementation is available at:
    # https://www.tandfonline.com/doi/full/10.1080/01621459.2023.2216909
    # 
    # The code is distributed under the MIT License.
    # Minor adjustments were made to ensure compatibility within the CausalBoundingEngine.


    def _compute_ATE(self, X: np.ndarray, Y: np.ndarray, Z: np.ndarray = None, **kwargs) -> tuple[float, float]:
        if Z is not None:
            df = pd.DataFrame({'Y': Y, 'X': X, 'Z': Z})
            joint_probs = Autobound._compute_joint_probabilities_IV(df)
            lower, upper = Autobound.run_experiment('ATE', dagstring="Z -> X, X -> Y, U -> X, U -> Y", unob="U", joint_probs=joint_probs)

                
            return lower, upper
        else:
            df = pd.DataFrame({'Y': Y, 'X': X})
            joint_probs = Autobound._compute_joint_probabilities_IV(df)
            lower, upper = Autobound.run_experiment('ATE', dagstring="X -> Y, U -> X, U -> Y", unob="U", joint_probs=joint_probs)
            return lower, upper

    def _compute_PNS(self, X: np.ndarray, Y: np.ndarray, Z: np.ndarray = None, **kwargs) -> tuple[float, float]:
        if Z is not None:
            df = pd.DataFrame({'Y': Y, 'X': X, 'Z': Z})
            joint_probs = Autobound._compute_joint_probabilities_IV(df)
            lower, upper = Autobound.run_experiment('PNS', dagstring="Z -> X, X -> Y, U -> X, U -> Y", unob="U", joint_probs=joint_probs)                
            return lower, upper
        else:
            df = pd.DataFrame({'Y': Y, 'X': X})
            joint_probs = Autobound._compute_joint_probabilities_IV(df)
            lower, upper = Autobound.run_experiment('PNS', dagstring="X -> Y, U -> X, U -> Y", unob="U", joint_probs=joint_probs)
            return lower, upper

        

    @staticmethod
    def run_experiment(query, dagstring, unob, joint_probs):
        """
        Run the AutoBound experiment.
        Parameters:
            dag (DAG): The directed acyclic graph representing the causal structure.
            df (pd.DataFrame): DataFrame containing the data for the experiment.
        Returns:
            tuple: (lower_bound, upper_bound) from AutoBound
        """
        dag = DAG()
        dag.from_structure(dagstring, unob)   
        

        problem = causalProblem(dag)

        problem.load_data_pandas(joint_probs)
        problem.add_prob_constraints()

        if query == 'ATE':
            problem.set_ate(ind='X', dep='Y')
        elif query == 'PNS':
            pns_query = problem.query('Y(X=1)=1 & Y(X=0)=0')
            problem.set_estimand(pns_query)
        else:
            raise ValueError("Query must be either 'ATE' or 'PNS'.")

        program = problem.write_program()
        lb, ub = program.run_pyomo(solver_name='highs', verbose=False)

        return lb, ub
    
    @staticmethod
    def _compute_joint_probabilities_IV(df):
        """
        Computes the joint probabilities for each combination of Z, X, and Y in the input DataFrame.
        If Z is not present, computes joint probabilities for X and Y only.

        Parameters:
            df (pd.DataFrame): Input DataFrame with columns ['X', 'Y'] or ['X', 'Y', 'Z'].

        Returns:
            pd.DataFrame: DataFrame with columns ['Z', 'X', 'Y', 'prob'] or ['X', 'Y', 'prob'].
        """
        if 'Z' in df.columns:
            joint_counts = df.groupby(['Z', 'X', 'Y']).size().reset_index(name='count')
            total_count = len(df)
            joint_counts['prob'] = joint_counts['count'] / total_count
            joint_probs = joint_counts.drop(columns=['count'])
        else:
            joint_counts = df.groupby(['X', 'Y']).size().reset_index(name='count')
            total_count = len(df)
            joint_counts['prob'] = joint_counts['count'] / total_count
            joint_probs = joint_counts.drop(columns=['count'])
        return joint_probs