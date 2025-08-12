import PyLTSpice as lt

runner = lt.SimRunner(simulator=lt.LTspice)  
raw, log = runner.run_now(lt.AscEditor("test.asc")) #, run_filename=run_netlist_file)

print(  lt.LTSpiceLogReader(log)['result'] ) 
