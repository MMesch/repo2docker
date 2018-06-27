import os

from .python import PythonBuildPack


class HaskellBuildPack(PythonBuildPack):
    """
    Setup Haskell for use with a repository

    This sets up Haskell + Jupyter Notebook + IHaskell for a repository that contains:

    1. A `stack.yml` file
    """
    @property
    def runtime(self):
        """
        Return contents of stack.yml if it exists, '' otherwise
        """
        if not hasattr(self, '_runtime'):
            runtime_path = self.binder_path('stack.yaml')
            try:
                with open(runtime_path) as f:
                    self._runtime = f.read().strip()
            except FileNotFoundError:
                self._runtime = ''

        return self._runtime

    def detect(self):
        """
        Check if current repo should be built with the Haskell Build pack

        super().detect() is not called in this function - it would return false
        unless a `requirements.txt` is present and we do not want to require the
        presence of a `requirements.txt` to use Haskell.

        Instead we just check if stack.yml exists
        """
        # If no date is found, then self.checkpoint_date will be False
        # Otherwise, it'll be a date object, which will evaluate to True
        return os.path.exists(self.binder_path('stack.yaml'))

    def get_build_scripts(self):
        """
        Return series of build-steps common to all Haskell repositories

        All scripts here should be independent of contents of the repository.
        """
        return super().get_build_scripts() + [
            (
                "root",
                # Install Stack, Jupyter and IHaskell!
                r"""
                apt-get update && \
                apt-get install -y libmagic-dev && \
                apt-get install -y libblas-dev && \
                apt-get install -y liblapack-dev && \
                apt-get install -y libcairo2-dev && \
                apt-get install -y libpango1.0-dev && \
                apt-get install -y libzmq3-dev && \
                curl -sSL https://get.haskellstack.org/ | sh
                """
            ),
            (
                "${NB_USER}",
                r"""
                git clone https://github.com/gibiansky/IHaskell && \
                cd IHaskell && \
                stack install gtk2hs-buildtools && \
                stack install --fast && \
                ihaskell install --stack
                """
            ),
        ]

    def get_assemble_scripts(self):
        """
        Return series of build-steps specific to this repository

        We set the snapshot date used to install R libraries from based on the
        contents of runtime.txt, and run the `install.R` script if it exists.
        """
        assemble_scripts = super().get_assemble_scripts() + [
            (
                # Not all of these locations are configurable; log_dir is
                "${NB_USER}",
                r"""
                stack setup && \
                stack build
                """
            ),
        ]
        return assemble_scripts

    def get_default_command(self):
        return ["stack", "exec", "--", "jupyter", "notebook", "--ip", "0.0.0.0"]
