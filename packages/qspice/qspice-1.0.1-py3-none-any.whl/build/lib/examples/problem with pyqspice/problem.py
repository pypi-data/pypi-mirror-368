from qspice import SimRunner, SpiceEditor,RawRead, sweep

def processing_data(raw_file, log_file):
    print("Handling the simulation data of %s, log file %s" % (raw_file, log_file))
    raw_data = RawRead(raw_file)
    I_L1 = raw_data.get_wave('I(L1)')
    I_L5 = raw_data.get_wave('I(L5)')
    I_L6 = raw_data.get_wave('I(L6)')
    Vcoil = raw_data.get_wave('V(n05)')
    return raw_file, I_L1.max(), I_L5.max(), I_L6.max(),Vcoil.max()

# select spice circuit
sim = SimRunner()
netlist = SpiceEditor('coupled_network_finding_resonance.cir')
#print(netlist())
# set default arguments
#netlist.set_component_value('R1', '4k')
#netlist.set_element_model('V1', "SINE(0 1 3k 0 0 0)")  # Modifying the
#netlist.add_instruction(".tran 1n 3m")
#netlist.add_instruction(".plot V(out)")
#netlist.add_instruction(".save all")

sim_no =1
# .step param fsw  list 82000  87000

for freq in sweep(82000, 83000, 1000):
    netlist.set_parameter('fsw', freq)
    sim.run(netlist, callback=processing_data)
    sim_no += 1

# Reading the data
results = {}
for raw_file, I_L1, I_L5, I_L6, Vcoil in sim:  # Iterate over the results of the callback function
    results[raw_file.name] = I_L1
# The block above can be replaced by the following line
# results = {raw_file.name: vout_max for raw_file, vout_max in sim}
print(results)