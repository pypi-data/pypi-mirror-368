def ensure_r_ready(r_path: str = None):
    """
    Ensure that R, rpy2, and the R package 'causaloptim' are available.
    Optionally accepts a manual R path (r_path), or expects R_HOME to be set.
    """
    import os
    import subprocess

    # Set R_HOME manually if provided
    if r_path:
        os.environ['R_HOME'] = r_path

    # Try to set R_HOME if not already set
    if 'R_HOME' not in os.environ:
        try:
            r_home = subprocess.check_output(["R", "RHOME"], text=True).strip()
            os.environ['R_HOME'] = r_home
        except Exception as e:
            raise RuntimeError(
                "R is not installed or not found in PATH.\n\n"
                "To fix this:\n"
                " - Make sure R is installed and accessible from the command line.\n"
                " - Then either:\n"
                "   • Set the R_HOME environment variable manually:\n"
                "       os.environ['R_HOME'] = 'path/to/R'\n"
                "   • Or call the algorithm with r_path='path/to/R' like this:\n"
                "       scenario.ATE.causaloptim(r_path='path/to/R')"
            ) from e

    try:
        import rpy2.robjects as robjects
        import rpy2.robjects.packages as rpackages
        import rpy2.robjects.vectors as rvectors
    except ImportError as e:
        raise ImportError(
            "CausalOptim requires the optional Python package 'rpy2'.\n"
            "Please install it with:\n\n"
            "    pip install causalboundingengine[r]"
        ) from e

    # Ensure R package is installed
    if not rpackages.isinstalled("causaloptim"):
        print("Installing R package 'causaloptim'...")

        utils = rpackages.importr("utils")
        utils.chooseCRANmirror(ind=1)
        utils.install_packages(rvectors.StrVector(["causaloptim"]))
