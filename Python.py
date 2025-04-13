import pygame
import time
from colorama import Fore, Back, Style
from collections import Counter
from threading import Thread, Event
import os
from datetime import datetime
import matplotlib.pyplot as plt
import requests
import json
import webbrowser
import sys

version = "2.0.3.0"
THRESHOLD = 0.05
calibration_completed = False

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_logo():
    print()
    print(f"░██████╗████████╗██╗░█████╗░██╗░░██╗  ░█████╗░███╗░░██╗░█████╗░██╗░░██╗░░░██╗███████╗███████╗██████╗░")
    print(f"██╔════╝╚══██╔══╝██║██╔══██╗██║░██╔╝  ██╔══██╗████╗░██║██╔══██╗██║░░╚██╗░██╔╝╚════██║██╔════╝██╔══██╗")
    print(f"╚█████╗░░░░██║░░░██║██║░░╚═╝█████═╝░  ███████║██╔██╗██║███████║██║░░░╚████╔╝░░░███╔═╝█████╗░░██████╔╝")
    print(f"░╚═══██╗░░░██║░░░██║██║░░██╗██╔═██╗░  ██╔══██║██║╚████║██╔══██║██║░░░░╚██╔╝░░██╔══╝░░██╔══╝░░██╔══██╗")
    print(f"██████╔╝░░░██║░░░██║╚█████╔╝██║░╚██╗  ██║░░██║██║░╚███║██║░░██║███████╗██║░░░███████╗███████╗██║░░██║")
    print(f"╚═════╝░░░░╚═╝░░░╚═╝░╚════╝░╚═╝░░╚═╝  ╚═╝░░╚═╝╚═╝░░╚══╝╚═╝░░╚═╝╚══════╝╚═╝░░░╚══════╝╚══════╝╚═╝░░╚═╝")
    print(f"v.{version} by John Punch (https://gamepadla.com)")
    print(f"Support the project: https://ko-fi.com/gamepadla")
    print()

def init_joystick():
    pygame.init()
    pygame.joystick.init()
    joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
    if not joysticks:
        print("No controller found")
        input("Press Enter to exit...")
        return None
    joystick = joysticks[0]
    joystick.init()
    print(f"\n{Style.BRIGHT}Connected controller: {joystick.get_name()}{Style.RESET_ALL}")
    return joystick

def choose_stick():
    print("Please select which stick to use:")
    print("1. Left stick")
    print("2. Right stick")
    choice = input("Enter 1 or 2: ").strip()
    if choice == '1':
        return 0, 1  # Left stick
    elif choice == '2':
        return 2, 3  # Right stick
    else:
        print("Invalid choice, defaulting to left stick.")
        return 0, 1

def filter_noise(results, timestamps, min_threshold=0.0001):
    if not results or not timestamps:
        return [], []
    filtered_data = []
    filtered_timestamps = []
    max_value = float('-inf')
    for i in range(len(results)):
        if i == 0 or (results[i] - max_value >= min_threshold):
            filtered_data.append(results[i])
            filtered_timestamps.append(timestamps[i])
            max_value = results[i]
    return filtered_data, filtered_timestamps

def visualize_stick_movement(screen, joystick, positions, stop_event, countdown_duration=5, guide_radius=100, guide_duration=10, guide_size=12, x_axis=0, y_axis=1):
    global calibration_completed
    center = (320, 240)
    font_large = pygame.font.Font(None, 72)
    font_small = pygame.font.Font(None, 24)
    font_coords = pygame.font.Font(None, 36)
    calibration_rounds = 0
    stick_centered = False
    guide_phase_started = False
    movement_started = False
    threshold_reached = False
    upper_threshold_reached = False
    lower_threshold_reached = False
    guide_delay = 3
    test_completed = False
    result_shown = False

    while not stop_event.is_set():
        current_time = time.time()
        screen.fill((30, 30, 30))
        pygame.draw.circle(screen, (70, 70, 70), center, guide_radius, 1)
        pygame.draw.line(screen, (50, 50, 50), (center[0] - guide_radius, center[1]), (center[0] + guide_radius, center[1]), 1)
        pygame.draw.line(screen, (50, 50, 50), (center[0], center[1] - guide_radius), (center[0], center[1] + guide_radius), 1)

        x = joystick.get_axis(x_axis)
        y = joystick.get_axis(y_axis)
        stick_position = (center[0] + int(x * guide_radius), center[1] + int(y * guide_radius))
        pygame.draw.line(screen, (0, 150, 255), center, stick_position, 2)
        pygame.draw.circle(screen, (157, 32, 96), stick_position, 5)

        if not calibration_completed:
            instruction_text = "Rotate the stick 3 times clockwise."
            instruction_rendered = font_small.render(instruction_text, True, (255, 255, 255))
            instruction_rect = instruction_rendered.get_rect(center=(center[0], center[1] - 140))
            screen.blit(instruction_rendered, instruction_rect)

            if y >= 0.92:
                upper_threshold_reached = True
            if y <= -0.92 and upper_threshold_reached:
                lower_threshold_reached = True

            if upper_threshold_reached and lower_threshold_reached:
                calibration_rounds += 1
                upper_threshold_reached = False
                lower_threshold_reached = False
                print(f"Calibration round {calibration_rounds}")

            rounds_left = max(0, 3 - calibration_rounds)
            counter_text = font_large.render(str(rounds_left), True, (255, 255, 255))
            counter_rect = counter_text.get_rect(center=center)
            screen.blit(counter_text, counter_rect)

            if calibration_rounds >= 3:
                calibration_completed = True
                stick_centered = False
                continue

        elif not stick_centered and calibration_completed:
            instruction_text = "Return the stick to the center."
            instruction_rendered = font_small.render(instruction_text, True, (255, 255, 255))
            instruction_rect = instruction_rendered.get_rect(center=(center[0], center[1] - 140))
            screen.blit(instruction_rendered, instruction_rect)

            if abs(x) < THRESHOLD and abs(y) < THRESHOLD:
                stick_centered = True
                start_time = time.time()
                continue

        elif not guide_phase_started and stick_centered:
            if time.time() - start_time >= guide_delay:
                guide_phase_started = True
                movement_started = True
                positions.clear()
                start_time = time.time()
                continue
            else:
                instruction_text = "Get ready to move the stick to the LEFT."
                instruction_rendered = font_small.render(instruction_text, True, (255, 255, 255))
                instruction_rect = instruction_rendered.get_rect(center=(center[0], center[1] - 140))
                screen.blit(instruction_rendered, instruction_rect)

        elif guide_phase_started and not test_completed:
            instruction_text = "Move stick LEFT at your own pace"
            instruction_rendered = font_small.render(instruction_text, True, (255, 255, 255))
            instruction_rect = instruction_rendered.get_rect(center=(center[0], center[1] - 140))
            screen.blit(instruction_rendered, instruction_rect)

            if movement_started and (abs(x) >= THRESHOLD or abs(y) >= THRESHOLD):
                threshold_reached = True

            if threshold_reached:
                stick_position = (center[0] + int(x * guide_radius), center[1] + int(y * guide_radius))
                pygame.draw.line(screen, (0, 150, 255), center, stick_position, 2)
                pygame.draw.circle(screen, (157, 32, 96), stick_position, 5)

                positions.append((stick_position, current_time))
                positions[:] = [(pos, t) for pos, t in positions if current_time - t <= 5]

                for pos, t in positions:
                    alpha = max(0, 255 - int((current_time - t) * 255 / 5))
                    color = (0, 0, 255, alpha)
                    s = pygame.Surface((10, 10), pygame.SRCALPHA)
                    pygame.draw.circle(s, color, (5, 5), 2)
                    screen.blit(s, (pos[0] - 5, pos[1] - 5))

            if abs(x) >= 0.99 or abs(y) >= 0.99:
                test_completed = True

            coords_text = f"X: {x:.3f}, Y: {y:.3f}"
            coords_rendered = font_coords.render(coords_text, True, (255, 255, 255))
            screen.blit(coords_rendered, (10, 10))

        if test_completed and not result_shown:
            print("Test completed: Stick reached boundary position.")
            result_shown = True
            stop_event.set()
            return

        pygame.display.flip()
        pygame.time.wait(10)

def measure_stick_movement(joystick, positions, stop_event, countdown_duration=5, x_axis=0, y_axis=1):
    global calibration_completed
    points = []
    prev_x = 0.0
    start_time = None
    running = True
    threshold_reached = False
    stick_centered = False
    timestamps = []

    print("---")
    print(f"Please switch to the program window and follow the guide's instructions")
    print()

    countdown_start_time = time.time()
    while time.time() - countdown_start_time < countdown_duration:
        pygame.event.pump()

    while not calibration_completed or (not stick_centered and not stop_event.is_set()):
        pygame.event.pump()
        x = joystick.get_axis(x_axis)
        y = joystick.get_axis(y_axis)
        
        if abs(x) < THRESHOLD and abs(y) < THRESHOLD and calibration_completed:
            stick_centered = True
            print("Stick is centered. Starting movement detection.")
        
        pygame.time.wait(10)

    while running and not stop_event.is_set():
        pygame.event.pump()
        x = joystick.get_axis(x_axis)

        if not threshold_reached and abs(x) >= THRESHOLD:
            threshold_reached = True
            start_time = time.time()
            print(f"Threshold reached: X = {x:.3f}")
        elif not threshold_reached:
            continue

        if abs(x) >= THRESHOLD and x != prev_x:
            current_time = time.time()
            distance = abs(x - prev_x)
            prev_x = x
            points.append(abs(x))
            timestamps.append(current_time - start_time if start_time else 0)
            if abs(x) != 1.0:
                print(f"{abs(x):.5f} [{distance:.4f}] at {timestamps[-1]:.4f}s")

        if abs(x) >= 0.99:
            running = False

    end_time = time.time() if points else None
    stop_event.set()
    return points, timestamps, start_time, end_time

def calculate_nonlinearity(points, timestamps):
    if len(points) < 3 or len(timestamps) < 3:
        return 0.0
    
    # Calculate ideal linear trajectory
    start_point = points[0]
    end_point = points[-1]
    start_time = timestamps[0]
    end_time = timestamps[-1]
    
    # Check for zero movement
    movement_range = abs(end_point - start_point)
    if movement_range == 0 or (end_time - start_time) == 0:
        return 0.0
    
    # Calculate deviations
    total_deviation = 0.0
    max_deviation = 0.0
    count = 0
    
    for i in range(1, len(points)-1):
        # Ideal position at this time point
        progress = (timestamps[i] - start_time) / (end_time - start_time)
        ideal_position = start_point + progress * (end_point - start_point)
        
        # Deviation from ideal position
        deviation = abs(points[i] - ideal_position)
        total_deviation += deviation
        max_deviation = max(max_deviation, deviation)
        count += 1
    
    if count == 0:
        return 0.0
    
    # Calculate nonlinearity
    avg_deviation = total_deviation / count
    avg_nonlinearity = (avg_deviation / movement_range) * 100
    max_nonlinearity = (max_deviation / movement_range) * 100
    
    # Weighted formula: 40% average + 60% maximum
    nonlinearity = 0.4 * avg_nonlinearity + 0.6 * max_nonlinearity
    
    # Scaling factor
    nonlinearity *= 1.5
    
    return min(100.0, nonlinearity)

def generate_test_id():
    # Generate a shorter unique test ID combining timestamp and random elements
    import time
    import random
    import string
    
    # Get current timestamp and convert to base36
    timestamp = int(time.time())
    time_part = format(timestamp, 'x')[-6:]  # Last 6 chars of hex timestamp
    
    # Generate 4 random characters
    random_chars = ''.join(random.choices(string.ascii_letters + string.digits, k=4))
    
    # Combine and return
    return f"{time_part}{random_chars}"

def prepare_test_data(points, timestamps, test_duration, joystick_name):
    # Calculate nonlinearity
    nonlinearity = calculate_nonlinearity(points, timestamps)
    
    # Calculate linearity (100% - nonlinearity)
    linearity = 100 - nonlinearity
    
    # Round values to reduce size
    rounded_times = [round(t, 5) for t in timestamps]
    rounded_positions = [round(p, 5) for p in points]
    
    # Create structured data in optimized format
    data = {
        "version": version,
        "test_info": {
            "duration": round(test_duration, 2),
            "nonlinearity": round(nonlinearity, 1),
            "linearity": round(linearity, 1),  # Added linearity value
            "total_points": len(points)
        },
        "controller": joystick_name,
        # Store points as two parallel arrays instead of array of objects
        "times": rounded_times,
        "positions": rounded_positions
    }
    
    # Serialize data to JSON
    json_data = json.dumps(data)
    
    # Prepare data for sending
    return {
        "test_key": generate_test_id(),
        "data_json": json_data,
        "stick_analyzer": "1"  # Marker that request is from Stick Analyzer
    }

def submit_test_results(data):
    url = "https://gamepadla.com/scripts/poster.php"
    
    try:
        response = requests.post(url, data=data)
        if response.status_code == 200:
            print(f"\n{Fore.GREEN}Test results successfully submitted to gamepadla.com{Style.RESET_ALL}")
            test_id = data['test_key']
            print(f"Test ID: {test_id}")
            
            results_url = f"https://gamepadla.com/stick_analyzer/{test_id}/"
            
            # Automatically open results in browser
            webbrowser.open(results_url)
            
            print(f"Results page opened in your browser")
            return True
        else:
            print(f"\n{Fore.RED}Failed to submit results. Status code: {response.status_code}{Style.RESET_ALL}")
            return False
    except Exception as e:
        print(f"\n{Fore.RED}Error submitting results: {str(e)}{Style.RESET_ALL}")
        return False

def save_results(points, timestamps, test_duration):
    try:
        # Get the correct program directory whether running as script or exe
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            program_dir = os.path.dirname(sys.executable)
        else:
            # Running as script
            program_dir = os.path.dirname(os.path.abspath(__file__))
            
        results_dir = os.path.join(program_dir, "Results")
        
        if not os.path.exists(results_dir):
            try:
                os.makedirs(results_dir)
                print(f"{Fore.GREEN}Created Results folder{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}Failed to create Results folder: {e}{Style.RESET_ALL}")
                results_dir = program_dir
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"stick_analyzer_{timestamp}.txt"
        filepath = os.path.join(results_dir, filename)
        
        nonlinearity = calculate_nonlinearity(points, timestamps)
        
        with open(filepath, "w") as file:
            file.write("# Stick Analyzer Results\n")
            file.write(f"# Test Duration: {test_duration:.2f} seconds\n")
            file.write(f"# Version: {version}\n")
            file.write(f"# Nonlinearity: {nonlinearity:.1f}%\n")
            file.write("# Raw Data\n")
            file.write("# Time,Position\n")
            for i in range(len(points)):
                file.write(f"{timestamps[i]:.5f},{points[i]:.5f}\n")
        
        print(f"\n{Fore.GREEN}Data successfully saved to: {filepath}{Style.RESET_ALL}")
        return True
    except Exception as e:
        print(f"\n{Fore.RED}Error saving data: {e}{Style.RESET_ALL}")
        return False

def visualize_results(points, timestamps, test_duration, tremor=0, resolution=0):
    try:
        # Calculate nonlinearity
        nonlinearity = calculate_nonlinearity(points, timestamps)
        
        # Determine color for nonlinearity
        nonlinearity_color = 'green'
        if nonlinearity > 25:
            nonlinearity_color = 'yellow'
        if nonlinearity > 50:
            nonlinearity_color = 'red'
        
        plt.style.use("dark_background")
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Actual stick position
        line_raw = ax.plot(timestamps, points, 'o-', label="Position", 
                         color='cyan', alpha=0.8, markersize=4)
        
        # Ideal linear curve
        if len(timestamps) > 1:
            ideal_times = [timestamps[0], timestamps[-1]]
            ideal_values = [points[0], points[-1]]
            line_ideal = ax.plot(ideal_times, ideal_values, '--', label="Linear (Ideal)", 
                               color='green', linewidth=1.5)
        
        ax.set_xlabel("Time (seconds)")
        ax.set_ylabel("Position")
        ax.grid(True, alpha=0.2)
        
        # Unified legend
        lines = line_raw
        if len(timestamps) > 1:
            lines += line_ideal
        labels = [l.get_label() for l in lines]
        ax.legend(lines, labels, loc='upper left')
        
        ax.set_title(f"Stick Movement Analysis | Duration: {test_duration:.2f} s | v.{version}")
        
        # Unified stats block in the lower right corner without a border
        linearity = 100.0 - nonlinearity
        stats_text = f"Data points: {len(points)}\n" \
                     f"Resolution: {resolution}\n" \
                     f"Tremor: {tremor:.1f}%\n" \
                     f"Linearity: {linearity:.1f}%"
        
        # Position the text in the lower right corner (coordinates 0.95, 0.05)
        # ha='right' aligns text to the right, va='bottom' to the bottom
        plt.figtext(0.96, 0.12, stats_text, fontsize=10, ha='right', va='bottom', color='white')
        plt.figtext(0.99, 0.01, "powered by Gamepadla.com", fontsize=8, ha='right', va='bottom', color='grey')
        
        plt.tight_layout()
        plt.show()
    except Exception as e:
        print(f"\n{Fore.RED}Error visualizing results: {e}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Visualization failed, but data was still saved.{Style.RESET_ALL}")

def analyze_results(points, start_time, end_time, joystick_name, timestamps):
    try:
        if not points:
            print("No valid points detected for analysis.")
            return

        test_duration = end_time - start_time

        # Filter data
        fpoints, ftimestamps = filter_noise(points, timestamps)
        num_points = len(points)
        fnum_points = len(fpoints)
        
        # Calculate tremor
        tremor = max(100 - ((100 / num_points) * fnum_points), 0) if num_points > 0 else 0

        # Calculate step statistics using filtered points
        distances = [abs(fpoints[i] - fpoints[i - 1]) for i in range(1, len(fpoints))]

        common_step_resolution = 0
        min_step_resolution = 0
        avg_step_resolution = 0
        stick_resolution = 0

        if distances:
            common_step_resolution = max(Counter(distances).items(), key=lambda x: x[1])[0]
            min_step_resolution = min(distances)
            avg_step_resolution = sum(distances) / len(distances)
            stick_resolution = int(1 / avg_step_resolution) if avg_step_resolution > 0 else 0

        # Calculate nonlinearity
        nonlinearity = calculate_nonlinearity(points, timestamps)
        linearity = 100.0 - nonlinearity

        # Display results
        print("\n" + "="*50)
        print(f"{'TEST RESULTS':^50}")
        print("="*50)
        
        if test_duration < 3:
            print(f"\n{Fore.RED}WARNING: Test duration is less than 3 seconds!{Style.RESET_ALL}")
            print(f"{Fore.RED}The test should be repeated for accurate results.{Style.RESET_ALL}\n")
        
        print(f"{Fore.CYAN}Test Information:{Style.RESET_ALL}")
        print(f"  Duration:              {test_duration:.2f} seconds")
        print(f"  Total data points:     {num_points}")
        print(f"  Straight move points:  {fnum_points}")
        print(f"  Tremor:                {tremor:.1f}%")
        print(f"  Linearity:             {linearity:.1f}%")
        
        print(f"\n{Fore.CYAN}Resolution (Avg.):{Style.RESET_ALL}")
        print(f"  Stick Resolution:      {stick_resolution}")
        print(f"  Step Resolution:       {avg_step_resolution:.5f}")
       
        # print(f"  ---")
        # print(f"  Common Step:           {common_step_resolution:.5f}")
        # print(f"  Minimum Step:          {min_step_resolution:.5f}")
        
        print("="*50)
        
        # Save and visualize results
        save_success = save_results(points, timestamps, test_duration)
        
        if save_success:
            visualize_results(points, timestamps, test_duration, tremor, stick_resolution)
            
            # Ask about submitting to server
            print(f"\n{Fore.CYAN}Would you like to submit results to gamepadla.com? (y/n){Style.RESET_ALL}")
            choice = input().strip().lower()
            if choice == 'y' or choice == 'yes':
                test_data = prepare_test_data(
                    points=points, 
                    timestamps=timestamps,
                    test_duration=test_duration,
                    joystick_name=joystick_name
                )
                submit_test_results(test_data)
        else:
            print(f"{Fore.YELLOW}Skipping visualization due to file save error.{Style.RESET_ALL}")
    
    except Exception as e:
        print(f"\n{Fore.RED}Error during analysis: {e}{Style.RESET_ALL}")
        
        try:
            test_duration = end_time - start_time
            save_results(points, timestamps, test_duration)
            print(f"{Fore.GREEN}Raw data was saved despite analysis error.{Style.RESET_ALL}")
        except Exception as e2:
            print(f"{Fore.RED}Could not save data: {e2}{Style.RESET_ALL}")

def main():
    try:
        clear_screen()
        print_logo()
        
        # Add detailed instructions for testing
        print("\n" + "="*70)
        print("TEST INSTRUCTIONS".center(70))
        print("="*70)
        print("• Move the stick LEFT at a steady pace without speeding up or slowing down")
        print("• Maintain constant physical movement even if on-screen movement appears")
        print("  different from what you feel in reality")
        print("• For accurate results, optimal test duration should be between 5-8 seconds")
        print("• Do not rush - precision is more important than speed for this test")
        print("="*70 + "\n")

        joystick = init_joystick()
        if joystick is None:
            return
        
        joystick_name = joystick.get_name()
        x_axis, y_axis = choose_stick()

        positions = []
        stop_event = Event()
        guide_size = 8
        guide_radius = 100
        guide_duration = 8
        countdown_duration = 5

        screen = pygame.display.set_mode((640, 480))
        pygame.display.set_caption("Stick Analyzer - Curve Test")
        
        visualization_thread = Thread(target=visualize_stick_movement, 
                                     args=(screen, joystick, positions, stop_event, 
                                          countdown_duration, guide_radius, guide_duration, 
                                          guide_size, x_axis, y_axis))
        visualization_thread.daemon = True
        visualization_thread.start()
        
        points = []
        timestamps = []
        start_time = None
        end_time = None
        
        try:
            points, timestamps, start_time, end_time = measure_stick_movement(
                joystick, positions, stop_event, countdown_duration, x_axis, y_axis)
        except Exception as e:
            print(f"\n{Fore.RED}Error during measurement: {e}{Style.RESET_ALL}")
        
        try:
            if visualization_thread.is_alive():
                visualization_thread.join(timeout=5)
        except Exception as e:
            print(f"\n{Fore.RED}Error in visualization thread: {e}{Style.RESET_ALL}")

        pygame.quit()

        if points and len(points) > 0 and start_time and end_time:
            analyze_results(points, start_time, end_time, joystick_name, timestamps)
        else:
            print(f"{Fore.YELLOW}No stick movement detected or measurement failed.{Style.RESET_ALL}")
    
    except Exception as e:
        print(f"\n{Fore.RED}Unexpected error: {e}{Style.RESET_ALL}")
    
    finally:
        try:
            pygame.quit()
        except:
            pass
        
        input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()