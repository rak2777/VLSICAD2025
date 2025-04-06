import argparse
import math

def parse_input_file(file_path):
    """
    Parses the input file and returns the sink details and unit resistance/capacitance.
    """
    sinks = []
    per_unit_resistance = None
    per_unit_capacitance = None

    with open(file_path, 'r') as file:
        lines = file.readlines()
        for line in lines:
            line = line.strip()

            # Skip empty lines or lines that don't start with the expected information
            if not line or line.startswith("#"):
                continue

            # Check for the PerUnitResistance and PerUnitCapacitance
            if 'PerUnitResistance' in line:
                per_unit_resistance = float(line.split(':')[1].strip())
            elif 'PerUnitCapacitance' in line:
                per_unit_capacitance = float(line.split(':')[1].strip())
            elif 'Sink' in line:
                # Get the sink index (e.g., Sink : 0)
                sink_id = int(line.split(':')[1].strip())
                sink = {'sink_id': sink_id}
            elif 'Coordinate' in line:
                # Get the coordinates for the sink
                coordinates = line.split(":")[1].strip().split()
                try:
                    # Check if there are exactly two values to convert to integers
                    if len(coordinates) == 2:
                        x, y = map(int, coordinates)  # Convert to integers
                        sink['x'] = x
                        sink['y'] = y
                    else:
                        print(f"Skipping invalid coordinate line: {line}")
                except ValueError:
                    print(f"Error converting coordinates: {line}")
            elif 'Capacitive Load' in line:
                # Get the capacitive load for the sink
                capacitance = float(line.split(":")[1].strip())
                sink['capacitive_load'] = capacitance
                sinks.append(sink)  # Add sink to the list
    
    return sinks, per_unit_resistance, per_unit_capacitance

def euclidean_distance(x1, y1, x2, y2):
    """Calculate the Euclidean distance between two points."""
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

def generate_htree(sinks):
    """
    Generates an H-tree for the clock sinks with proper parent assignment.
    """
    htree = []
    # Assuming a simple binary tree structure for clock network generation
    def create_node(sink_id, parent=None):
        return {
            'sink_id': sink_id,
            'parent': parent
        }

    # Create a root node (start with the first sink)
    root = create_node(sinks[0]['sink_id'], parent=None)
    htree.append(root)

    # Now add other sinks and create a binary tree structure
    for i in range(1, len(sinks)):
        # Parent will be the previous sink node
        parent = htree[(i - 1) // 2]  # Simple binary tree parent assignment
        node = create_node(sinks[i]['sink_id'], parent=parent)
        htree.append(node)
    
    return htree


def compute_delay_and_capacitance(sinks, per_unit_resistance, per_unit_capacitance):
    """Compute delay and capacitance based on the Elmore model and the provided units."""
    for i, sink in enumerate(sinks):
        for j, target_sink in enumerate(sinks):
            if i != j:
                # Compute distance between sinks
                dist = euclidean_distance(sink['x'], sink['y'], target_sink['x'], target_sink['y'])
                # Compute resistance and capacitance for each segment
                resistance = per_unit_resistance * dist
                capacitance = per_unit_capacitance * dist
                # Calculate delay for this segment using the Elmore delay model (simplified)
                delay = resistance * capacitance
                print(f"Delay between Sink {sink['sink_id']} and Sink {target_sink['sink_id']}: {delay:.6e}")

def write_netlist(htree, output_file):
    with open(output_file, 'w') as file:
        file.write("module clock_tree (\n")
        file.write("    clk,\n")

        # Write the output ports (each sink will be an output port)
        for node in htree:
            file.write(f"    out_{node['sink_id']}, \n")
        file.write(");\n\n")

        file.write("input clk;\n")
        
        # Write the output ports
        for node in htree:
            file.write(f"output out_{node['sink_id']};\n")
        
        file.write("\n")

        # Write the internal connections (create an example circuit)
        for i, node in enumerate(htree):
            if node['parent']:
                parent_id = node['parent']['sink_id']
                file.write(f"nand2x1 I{i} ( .B(out_{parent_id}), .A(out_{node['sink_id']}), .Z(net_{i}) );\n")

        file.write("endmodule\n")


def main():
    # Argument parsing
    parser = argparse.ArgumentParser(description="Generate Clock Tree and SDF File")
    parser.add_argument('input_file', type=str, help="Input file containing clock sink information")
    parser.add_argument('output_netlist', type=str, help="Output Netlist file to write")
    parser.add_argument('output_sdf', type=str, help="Output SDF file to write")
    
    args = parser.parse_args()
    
    # Step 1: Parse the input file
    sinks, per_unit_resistance, per_unit_capacitance = parse_input_file(args.input_file)
    
    # Step 2: Generate the H-tree
    htree = generate_htree(sinks)
    
    # Step 3: Write the netlist to the output file
    write_netlist(htree, args.output_netlist)
    
    # Step 4: Compute delay and capacitance, and print
    compute_delay_and_capacitance(htree, per_unit_resistance, per_unit_capacitance)
    
    # Step 5: Placeholder for writing SDF (Simplified for now)
    print("SDF generation is a placeholder here. You can implement it based on your specific needs.")

if __name__ == '__main__':
    main()
