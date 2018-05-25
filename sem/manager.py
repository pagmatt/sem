from .database import DatabaseManager
from .runner import SimulationRunner
from git import Repo


class CampaignManager(object):
    """
    The main Simulation Execution Manager class can be used to load, save,
    execute and access the results of simulation campaigns.
    """

    #######################################
    # Campaign initialization and loading #
    #######################################

    def __init__(self, campaign_db, campaign_runner):
        """
        Initialize the Simulation Execution Manager.
        """
        self.db = campaign_db
        self.runner = campaign_runner

    @classmethod
    def new(cls, path, script, filename):
        """
        Initialize a campaign database based on a script and ns-3 path.
        """
        # Create a runner for the desired configuration
        runner = SimulationRunner(path, script)

        # Get list of available parameters
        params = runner.get_available_parameters()

        # Repository check
        # TODO Make sure there are no staged/unstaged changes
        # Get current commit
        commit = Repo(path).head.commit.hexsha

        # Create a database manager from configuration
        config = {
            'script': script,
            'path': path,
            'params': params,
            'commit': commit
        }

        db = DatabaseManager.new(config, filename)

        return cls(db, runner)

    @classmethod
    def load(cls, filename):
        """
        Read a filename and load the corresponding campaign database.
        """
        # Read from database
        db = DatabaseManager.load(filename)

        # Create a runner
        runner = SimulationRunner(db.get_path(), db.get_script())

        return cls(db, runner)

    #############
    # Utilities #
    #############

    def __str__(self):
        return "--- Campaign info ---\n%s\n------------" % self.db

    ######################
    # Simulation running #
    ######################

    def run_single_simulation(self, param_combination):
        """
        Run the simulations from a dictionary containing parameter/value pairs,
        defining the parameter combination to simulate.
        """
        # Compute next RngRun value
        param_combination['RngRun'] = self.db.get_next_rngrun()

        # Offload simulation execution to self.runner
        result = {}
        result.update(param_combination)

        result['stdout'] = str(self.runner.run_single_simulation(
            param_combination).decode('utf-8'))

        self.db.insert_result(result)

    #####################
    # Result management #
    #####################

    def get_results_as_numpy_array(self, parameter_space):
        """
        Return the results relative to the desired parameter space in the form
        of a numpy array.
        """
        # Collect list of relevant results from DatabaseManager
        # Package results in a numpy array
