import matplotlib.pyplot as plt
import math

def read_points_file(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()
        
        # First line: boundary x1 y1 x2 y2
        boundary = list(map(float, lines[0].strip().split()))
        
        # Second line: number of points
        num_points = int(lines[1].strip())
        
        # Next lines: points
        points = []
        for line in lines[2:2 + len(lines)]:
            x, y = map(float, line.strip().split())
            points.append((x, y))
    
    return boundary, points

def read_taps_file(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()
        
        # Second line: number of points
        num_taps = int(lines[1].strip())
        
        # Next lines: points
        taps = []
        for line in lines[2:2 + len(lines)]:
            x, y = map(float, line.strip().split())
            taps.append((x, y))
    
    return taps

def read_segments_file(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()
        
        # First line: number of segments
        num_segments = int(lines[0].strip())
        
        # Next lines: segments
        segments = []
        totalLength = 0
        for line in lines[1:1 + len(lines)]:
            x1, y1, x2, y2 = map(float, line.strip().split())
            segments.append(((x1, y1), (x2, y2)))
            totalLength += math.sqrt((x2-x1)**2 + (y2-y1)**2)
    
    print(totalLength)
    return segments

def plot_data(boundary, points, taps, segments, output_file='output.png'):
    x_min, y_min, x_max, y_max = boundary
    
    plt.figure(figsize=(8, 8))
    plt.xlim(x_min, x_max)
    plt.ylim(y_min, y_max)

    # Plot points
    if points:
        px = [p[0] for p in points]
        py = [p[1] for p in points]
        plt.scatter(px, py, color='blue', s=10, label='Points')

    # Plot taps
    if taps:
        tx = [t[0] for t in taps]
        ty = [t[1] for t in taps]
        plt.scatter(tx, ty, color='green', s=2, label='Taps')

    # Plot line segments
    for start, end in segments:
        plt.plot([start[0], end[0]], [start[1], end[1]], color='red', label='Line Segment' if 'Line Segment' not in plt.gca().get_legend_handles_labels()[1] else "")
    
    plt.legend()
    plt.title('Points and Line Segments')
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.grid(True)
    plt.savefig(output_file)
    plt.close()
    print(f"Plot saved as '{output_file}'")

# Example usage
if __name__ == "__main__":
    boundary, points = read_points_file('Sinks.txt')
    taps = read_taps_file('Taps.txt')
    segments = read_segments_file('Edges.txt')
    plot_data(boundary, points, taps, segments)
