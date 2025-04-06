import sys

# Function to parse the sink list file and return the sinks
def parse_sink_file(file_path):
    sinks = []
    with open(file_path, 'r') as file:
        lines = file.readlines()
    
    sink_data = {}
    for line in lines:
        line = line.strip()

        if line.startswith("Sink :"):
            # If we encountered a new Sink entry, store the previous sink if any
            if sink_data:
                sinks.append(sink_data)

            # Start a new sink entry
            sink_id = int(line.split(":")[1].strip())
            sink_data = {'sink_id': sink_id}
        
        elif "Coordinate :" in line:
            # Extract coordinates
            coords = line.split(":")[1].strip().split()
            x_coord, y_coord = int(coords[0]), int(coords[1])
            sink_data['coordinate'] = (x_coord, y_coord)
        
        elif "Capacitive Load :" in line:
            # Extract capacitive load
            load = float(line.split(":")[1].strip())
            sink_data['capacitive_load'] = load
    
    # Append the last sink entry
    if sink_data:
        sinks.append(sink_data)
    
    # Debug: Print the parsed sinks
    if not sinks:
        print("No sinks found. Please check the input file format.")
    else:
        print(f"Parsed sinks: {sinks}")
    
    return sinks

# Function to generate Verilog netlist from sink data
def generate_netlist(sinks, module_name="clock_tree"):
    netlist = []

    if not sinks:
        return "Error: No sinks to generate a netlist."

    # Module declaration
    netlist.append(f"module {module_name} ( clk, ")
    for sink in sinks:
        netlist.append(f"  sink{sink['sink_id']},")
    netlist[-1] = netlist[-1][:-1]  # Remove the last comma
    netlist.append(");")
    
    # I/O declaration
    netlist.append("input clk;")
    for sink in sinks:
        netlist.append(f"output sink{sink['sink_id']};")
    
    # Flip-Flop instances for each sink
    for sink in sinks:
        netlist.append(f"  dff dff{sink['sink_id']} ( .clk(clk), .d(1'b0), .q(sink{sink['sink_id']}));")

    netlist.append("endmodule")
    
    return "\n".join(netlist)

# Main function to handle input/output file paths via command-line arguments
def main():
    if len(sys.argv) != 3:
        print("Usage: python generate_netlist.py <input_file> <output_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]  # First argument is the input file
    output_file = sys.argv[2]  # Second argument is the output file
    
    # Parse the sink list file
    sinks = parse_sink_file(input_file)
    
    # Generate the Verilog netlist
    verilog_netlist = generate_netlist(sinks)
    
    if verilog_netlist.startswith("Error"):
        print(verilog_netlist)
        sys.exit(1)
    
    # Write the netlist to the output file
    with open(output_file, 'w') as file:
        file.write(verilog_netlist)
    
    print(f"Verilog netlist generated: {output_file}")

if __name__ == "__main__":
    main()
