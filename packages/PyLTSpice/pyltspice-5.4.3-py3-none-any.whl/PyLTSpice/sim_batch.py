#!/usr/bin/env python
# coding=utf-8

# -------------------------------------------------------------------------------
#    ____        _   _____ ____        _
#   |  _ \ _   _| | |_   _/ ___| _ __ (_) ___ ___
#   | |_) | | | | |   | | \___ \| '_ \| |/ __/ _ \
#   |  __/| |_| | |___| |  ___) | |_) | | (_|  __/
#   |_|    \__, |_____|_| |____/| .__/|_|\___\___|
#          |___/                |_|
#
# Name:        sim_batch.py
# Purpose:     Tool used to launch LTSpice simulation in batch mode. Netlsts can
#              be updated by user instructions
#
# Author:      Nuno Brum (nuno.brum@gmail.com)
#
# Created:     23-12-2016
# Licence:     refer to the LICENSE file
# -------------------------------------------------------------------------------
"""
Allows launching LTSpice simulations from a Python Script, thus allowing to overcome the 3 dimensions STEP limitation on
LTSpice, update resistor values, or component models.

The code snipped below will simulate a circuit with two different diode models, set the simulation
temperature to 80 degrees, and update the values of R1 and R2 to 3.3k. ::

    LTC = SimCommander("my_circuit.asc")
    LTC.set_parameters(temp=80)  # Sets the simulation temperature to be 80 degrees
    LTC.set_component_value('R2', '3.3k')  #  Updates the resistor R2 value to be 3.3k
    for dmodel in ("BAT54", "BAT46WJ"):
        LTC.set_element_model("D1", model)  # Sets the Diode D1 model
        for res_value in sweep(2.2, 2,4, 0.2):  # Steps from 2.2 to 2.4 with 0.2 increments
            LTC.set_component_value('R1', res_value)  #  Updates the resistor R1 value to be 3.3k
            LTC.run()

    LTC.wait_completion()  # Waits for the LTSpice simulations to complete

    print("Total Simulations: {}".format(LTC.runno))
    print("Successful Simulations: {}".format(LTC.okSim))
    print("Failed Simulations: {}".format(LTC.failSim))

The first line will create an python class instance that represents the LTSpice file or netlist that is to be
simulated. This object implements methods that are used to manipulate the spice netlist. For example, the method
set_parameters() will set or update existing parameters defined in the netlist. The method set_component_value() is
used to update existing component values or models.

---------------
Multiprocessing
---------------

For making better use of today's computer capabilities, the SimCommander spawns several LTSpice instances
each executing in parallel a simulation.

By default, the number of parallel simulations is 4, however the user can override this in two ways. Either
using the class constructor argument ``parallel_sims`` or by forcing the allocation of more processes in the
run() call by setting ``wait_resource=False``. ::

    LTC.run(wait_resource=False)

The recommended way is to set the parameter ``parallel_sims`` in the class constructor. ::

    LTC=SimCommander("my_circuit.asc", parallel_sims=8)

The user then can launch a simulation with the updates done to the netlist by calling the run() method. Since the
processes are not executed right away, but rather just scheduled for simulation, the wait_completion() function is
needed if the user wants to execute code only after the completion of all scheduled simulations.

The usage of wait_completion() is optional. Just note that the script will only end when all the scheduled tasks are
executed.

---------
Callbacks
---------

As seen above, the `wait_completion()` can be used to wait for all the simulations to be finished. However, this is
not efficient from a multiprocessor point of view. Ideally, the post-processing should be also handled while other
simulations are still running. For this purpose, the user can use a function call back.

The callback function is called when the simulation has finished directly by the thread that has handling the
simulation. A function callback receives two arguments.
The RAW file and the LOG file names. Below is an example of a callback function::

    def processing_data(raw_filename, log_filename):
        '''This is a call back function that just prints the filenames'''
        print("Simulation Raw file is %s. The log is %s" % (raw_filename, log_filename)
        # Other code below either using LTSteps.py or raw_read.py
        log_info = LTSpiceLogReader(log_filename)
        log_info.read_measures()
        rise, measures = log_info.dataset["rise_time"]

The callback function is optional. If  no callback function is given, the thread is terminated just after the
simulation is finished.
"""
__author__ = "Nuno Canto Brum <nuno.brum@gmail.com>"
__copyright__ = "Copyright 2020, Fribourg Switzerland"

import os
import pathlib
import threading
import time
import traceback
from time import sleep
from typing import Callable, Union, Any, Tuple
from warnings import warn
import logging
_logger = logging.getLogger("PyLTSpice.SimBatch")

from .SpiceEditor import SpiceEditor
from .simulator import clock_function, Simulator

END_LINE_TERM = '\n'

logging.basicConfig(filename='SpiceBatch.log', level=logging.INFO)




class RunTask(threading.Thread):
    """This is an internal Class and should not be used directly by the User."""

    def __init__(self, simulator: Simulator,  run_no, netlist_file: str, callback: Callable[[str, str], Any], timeout=None, verbose=True):
        self.verbose = verbose
        self.timeout = timeout  # Thanks to Daniel Phili for implementing this

        threading.Thread.__init__(self)
        self.setName("sim%d" % run_no)
        self.simulator = simulator
        self.run_no = run_no
        self.netlist_file = netlist_file
        self.callback = callback
        self.retcode = -1  # Signals an error by default
        self.raw_file = None
        self.log_file = None

    def run(self):
        # Running the Simulation

        self.start_time = clock_function()
        if self.verbose:
            print(time.asctime(), ": Starting simulation %d" % self.run_no)

        # start execution
        self.retcode = self.simulator.run(self.netlist_file, self.timeout)

        # print simulation time
        sim_time = time.strftime("%H:%M:%S", time.gmtime(clock_function() - self.start_time))
        netlist_radic, extension = os.path.splitext(self.netlist_file)
        self.log_file = netlist_radic + '.log'

        # Cleanup everything
        if self.retcode == 0:
            # simulation successful
            _logger.info("Simulation Successful. Time elapsed: %s" % sim_time)
            if self.verbose:
                print(time.asctime() + ": Simulation Successful. Time elapsed %s:%s" % (sim_time, END_LINE_TERM))

            self.raw_file = netlist_radic + '.raw'

            if os.path.exists(self.raw_file) and os.path.exists(self.log_file):
                if self.callback:
                    if self.verbose:
                        print("Calling the callback function")
                    try:
                        self.callback(self.raw_file, self.log_file)
                    except Exception as err:
                        error = traceback.format_tb(err)
                        _logger.error(error)
                else:
                    if self.verbose:
                        print('No Callback')
            else:
                _logger.error("Simulation Raw file or Log file were not found")
        else:
            # simulation failed

            _logger.warning(time.asctime() + ": Simulation Failed. Time elapsed %s:%s" % (sim_time, END_LINE_TERM))
            if os.path.exists(self.log_file):
                old_log_file = self.log_file
                self.log_file = netlist_radic + '.fail'
                os.rename(old_log_file, self.log_file)

    def wait_results(self) -> Tuple[str, str]:
        """
        Waits for the completion of the task and returns a tuple with the raw and log files.
        :returns: Tupple with the path to the raw file and the path to the log file
        :rtype: tuple(str, str)
        """
        while self.is_alive() or self.retcode == -1:
            sleep(0.1)
        if self.retcode == 0:  # All finished OK
            return self.raw_file, self.log_file
        else:
            return '', ''


class SimCommander(SpiceEditor):
    """
    The SimCommander class implements all the methods required for launching batches of LTSpice simulations.
    It takes a parameter the path to the LTSpice .asc file to be simulated, or directly the .net file.
    If an .asc file is given, the class will try to generate the respective .net file by calling LTspice with
    the --netlist option

    :param circuit_file: Path to the circuit to simulate. It can be either a .asc or a .net file
    :type circuit_file: str
    :param parallel_sims: Defines the number of parallel simulations that can be executed at the same time. Ideally this
                          number should be aligned to the number of CPUs (processor cores) available on the machine.
    :type parallel_sims: int, optional
    :param timeout: Timeout parameter as specified on the os subprocess.run() function
    :type timeout: float, optional
    :param verbose: If True, it enables a richer printout of the program execution.
    :type verbose: bool, optional
    :param encoding: Forcing the encoding to be used on the circuit netlile read. Defaults to 'autodetect' which will
                     call a function that tries to detect the encoding automatically. This however is not 100% fool
                     proof.
    :type encoding: str, optional
    :param simulator: Forcing a given simulator executable.
    :type simulator: str or Simulator, optional
    """

    def __init__(self, circuit_file: str, parallel_sims: int = 4, timeout=None, verbose=True, encoding='autodetect',
                 simulator=None):
        """
        Class Constructor. It serves to start batches of simulations.
        See Class documentation for more information.
        """

        self.verbose = verbose
        self.timeout = timeout

        self.file_path = os.path.dirname(circuit_file)
        if self.file_path == '':
            self.file_path = os.path.abspath(os.curdir)
        self.file_name, file_ext = os.path.splitext(os.path.basename(circuit_file))
        self.circuit_radic = os.path.join(self.file_path, self.file_name)

        self.parallel_sims = parallel_sims
        self.threads = []

        # master_log_filename = self.circuit_radic + '.masterlog' TODO: create the JSON or YAML file
        self.logger = logging.getLogger("SimCommander")
        self.logger.setLevel(logging.INFO)
        # TODO redirect this logger to a file.

        self.runno = 0  # number of total runs
        self.failSim = 0  # number of failed simulations
        self.okSim = 0  # number of succesfull completed simulations
        # self.failParam = []  # collects for later user investigation of failed parameter sets

        # Gets a simulator.
        if simulator is None:
            self.simulator = Simulator.get_default_simulator()
        elif isinstance(simulator, Simulator):
            self.simulator = simulator
        elif isinstance(simulator, (str, pathlib.Path)):
            self.simulator = Simulator.create_from(simulator)
        else:
            raise TypeError("Invalid simulator type. Either use a string with the ")

        if file_ext == '.asc':
            netlist_file = self.circuit_radic + '.net'
            if self.verbose:
                print("Creating Netlist")
            retcode = self.simulator.create_netlist(circuit_file)
            if retcode == 0 and os.path.exists(netlist_file):
                if self.verbose:
                    print("The Netlist was successfully created")
            else:
                if self.verbose:
                    print("Unable to create the Netlist from %s" % circuit_file)
                netlist_file = None
        elif os.path.exists(circuit_file):
            netlist_file = circuit_file
        else:
            netlist_file = None
            if self.verbose:
                print("Unable to find the Netlist: %s" % circuit_file)

        super(SimCommander, self).__init__(netlist_file, encoding=encoding)
        self.reset_netlist()
        if len(self.netlist) == 0:
            self.logger.error("Unable to create Netlist")

    def __del__(self):
        """Class Destructor : Closes Everything"""
        self.logger.debug("Waiting for all spawned threads to finish.")
        self.wait_completion()  # TODO: Kill all pending simulations
        self.logger.debug("Exiting SimCommander")

    def setLTspiceRunCommand(self, spice_tool: Union[str, Simulator]) -> None:
        """
        Manually setting the LTSpice run command.

        :param spice_tool: String containing the path to the spice tool to be used, or alternatively the Simulator
                           object.
        :type spice_tool: str or Simulator
        :return: Nothing
        :rtype: None
        """
        if isinstance(spice_tool, str):
            self.simulator = Simulator.create_from(spice_tool)
        elif isinstance(spice_tool, Simulator):
            self.simulator = spice_tool
        else:
            raise TypeError("Expecting str or Simulator objects")

    def add_LTspiceRunCmdLineSwitches(self, *args) -> None:
        """
        Used to add an extra command line argument such as -I<path> to add symbol search path or -FastAccess
        to convert the raw file into Fast Access.
        The arguments is a list of strings as is defined in the LTSpice command line documentation.

        :param args: list of strings
            A list of command line switches such as "-ascii" for generating a raw file in text format or "-alt" for
            setting the solver to alternate. See Command Line Switches information on LTSpice help file.
        :type args: list[str]
        :returns: Nothing
        """
        self.simulator.add_command_line_switch(*args)

    def run(self, run_filename: str = None, wait_resource: bool = True,
            callback: Callable[[str, str], Any] = None, timeout: float = 600) -> RunTask:
        """
        Executes a simulation run with the conditions set by the user.
        Conditions are set by the set_parameter, set_component_value or add_instruction functions.

        :param run_filename:
            The name of the netlist can be optionally overridden if the user wants to have a better control of how the
            simulations files are generated.
        :type run_filename: str, optional
        :param wait_resource:
            Setting this parameter to False will force the simulation to start immediately, irrespective of the number
            of simulations already active.
            By default the SimCommander class uses only four processors. This number can be overridden by setting
            the parameter ´parallel_sims´ to a different number.
            If there are more than ´parallel_sims´ simulations being done, the new one will be placed on hold till one
            of the other simulations are finished.
        :type wait_resource: bool, optional
        :param callback:
            The user can optionally give a callback function for when the simulation finishes so that processing can
            be done immediately.
        :type: callback: function(raw_file, log_file), optional
        :param timeout: Timeout to be used in waiting for resources. Default time is 600 seconds, i.e. 10 minutes.
        :type timeout: float, optional

        :returns: The task object of type RunTask
        """
        # decide sim required
        if self.netlist is not None:
            # update number of simulation
            self.runno += 1  # Using internal simulation number in case a run_id is not supplied

            # Write the new settings
            if run_filename is None:
                run_netlist_file = "%s_%i.net" % (self.circuit_radic, self.runno)
            else:
                run_netlist_file = run_filename

            self.write_netlist(run_netlist_file)
            t0 = time.perf_counter()  # Store the time for timeout calculation
            while time.perf_counter() - t0 < timeout:
                self.updated_stats()  # purge ended tasks

                if (wait_resource is False) or (len(self.threads) < self.parallel_sims):
                    t = RunTask(self.simulator, self.runno, run_netlist_file, callback,
                                timeout=self.timeout, verbose=self.verbose)
                    self.threads.append(t)
                    t.start()
                    sleep(0.01)  # Give slack for the thread to start
                    return t  # Returns the task number
                sleep(0.1)  # Give Time for other simulations to end
            else:
                self.logger.error("Timeout waiting for resources for simulation %d" % self.runno)
                if self.verbose:
                    print("Timeout on launching simulation %d." % self.runno)

        else:
            # no simulation required
            raise UserWarning('skipping simulation ' + str(self.runno))

    def updated_stats(self):
        """
        This function updates the OK/Fail statistics and releases finished RunTask objects from memory.

        :returns: Nothing
        """
        i = 0
        while i < len(self.threads):
            if self.threads[i].is_alive():
                i += 1
            else:
                if self.threads[i].retcode == 0:
                    self.okSim += 1
                else:
                    # simulation failed
                    self.failSim += 1
                del self.threads[i]

    @staticmethod
    def kill_all_ltspice():
        """Function to terminate LTSpice in windows"""
        simulator = Simulator.get_default_simulator()
        simulator.kill_all()

    def wait_completion(self, timeout=None, abort_all_on_timeout=False) -> bool:
        """
        This function will wait for the execution of all scheduled simulations to complete.

        :param timeout: Cancels the wait after the number of seconds specified by the timeout.
            This timeout is reset everytime that a simulation is completed. The difference between this timeout and the
            one defined in the SimCommander instance, is that the later is implemented by the subprocess class, and the
            this timeout just cancels the wait.
        :type timeout: int
        :param abort_all_on_timeout: attempts to stop all LTSpice processes if timeout is expired.
        :type abort_all_on_timeout: bool
        :returns: True if all simulations were executed successfully
        :rtype: bool
        """
        self.updated_stats()
        timeout_counter = 0
        sim_counters = (self.okSim, self.failSim)

        while len(self.threads) > 0:
            sleep(1)
            self.updated_stats()
            if timeout is not None:
                if sim_counters == (self.okSim, self.failSim):
                    timeout_counter += 1
                    print(timeout_counter, "timeout counter")
                else:
                    timeout_counter = 0

                if timeout_counter > timeout:
                    if abort_all_on_timeout:
                        self.kill_all_ltspice()
                    return False

        return self.failSim == 0


if __name__ == "__main__":
    # get script absolute path
    meAbsPath = os.path.dirname(os.path.realpath(__file__))
    meAbsPath, _ = os.path.split(meAbsPath)
    # select spice model
    LTC = SimCommander(meAbsPath + "\\test_files\\testfile.asc")
    # set default arguments
    LTC.set_parameters(res=0.001, cap=100e-6)
    # define simulation
    LTC.add_instructions(
            "; Simulation settings",
            # [".STEP PARAM Rmotor LIST 21 28"],
            ".TRAN 3m",
            # ".step param run 1 2 1"
    )
    # do parameter sweep
    for res in range(5):
        # LTC.runs_to_do = range(2)
        LTC.set_parameters(ANA=res)
        raw, log = LTC.run()
        print("Raw file '%s' | Log File '%s'" % (raw, log))
    # Sim Statistics
    print('Successful/Total Simulations: ' + str(LTC.okSim) + '/' + str(LTC.runno))


    def callback_function(raw_file, log_file):
        print("Handling the simulation data of %s, log file %s" % (raw_file, log_file))


    LTC = SimCommander(meAbsPath + "\\test_files\\testfile.asc", parallel_sims=1)
    tstart = 0
    for tstop in (2, 5, 8, 10):
        tduration = tstop - tstart
        LTC.add_instruction(".tran {}".format(tduration), )
        if tstart != 0:
            LTC.add_instruction(".loadbias {}".format(bias_file))
            # Put here your parameter modifications
            # LTC.set_parameters(param1=1, param2=2, param3=3)
        bias_file = "sim_loadbias_%d.txt" % tstop
        LTC.add_instruction(".savebias {} internal time={}".format(bias_file, tduration))
        tstart = tstop
        LTC.run(callback=callback_function)

    LTC.reset_netlist()
    LTC.add_instruction('.ac dec 40 1m 1G')
    LTC.set_component_value('V1', 'AC 1 0')
    LTC.run(callback=callback_function)
    LTC.wait_completion()
