import pygame
import time
from colorama import Fore, Back, Style
from collections import Counter
from threading import Thread, Event
import requests
import json
from datetime import datetime
import os
import webbrowser

version = "2.0.0.0"

# Глобальна змінна для порогу руху стіку
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
        return 0, 1  # Left stick: axes 0 (X) and 1 (Y)
    elif choice == '2':
        return 2, 3  # Right stick: axes 2 (X) and 3 (Y)
    else:
        print("Invalid choice, defaulting to left stick.")
        return 0, 1

def filter_noise(results):
    if not results:
        return []

    filtered_results = [results[0]]
    for i in range(1, len(results)):
        current_value = results[i]
        previous_values = results[:i]
        if current_value not in filtered_results and all(prev <= current_value for prev in previous_values):
            filtered_results.append(current_value)

    return filtered_results

def visualize_stick_movement(screen, joystick, positions, stop_event, countdown_duration=5, guide_radius=100, guide_duration=10, guide_size=12, x_axis=0, y_axis=1):
    global calibration_completed
    center = (320, 240)
    font_large = pygame.font.Font(None, 72)
    font_small = pygame.font.Font(None, 24)
    font_coords = pygame.font.Font(None, 36)
    calibration_rounds = 0
    stick_centered = False
    guide_phase_started = False
    guide_visible = False
    movement_started = False
    threshold_reached = False
    upper_threshold_reached = False
    lower_threshold_reached = False
    guide_delay = 3
    guide_x = center[0]
    guide_stopped = False
    test_completed = False
    result_shown = False

    while not stop_event.is_set():
        current_time = time.time()
        screen.fill((30, 30, 30))

        pygame.draw.circle(screen, (200, 200, 200), center, guide_radius, 1)
        pygame.draw.line(screen, (200, 200, 200), (center[0] - guide_radius, center[1]), (center[0] + guide_radius, center[1]), 1)
        pygame.draw.line(screen, (200, 200, 200), (center[0], center[1] - guide_radius), (center[0], center[1] + guide_radius), 1)

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
                guide_visible = True
                movement_started = True
                positions.clear()
                start_time = time.time()
                continue
            else:
                instruction_text = "Get ready to follow the guide."
                instruction_rendered = font_small.render(instruction_text, True, (255, 255, 255))
                instruction_rect = instruction_rendered.get_rect(center=(center[0], center[1] - 140))
                screen.blit(instruction_rendered, instruction_rect)

        elif guide_visible and not test_completed:
            instruction_text = "Follow the guide"
            instruction_rendered = font_small.render(instruction_text, True, (255, 255, 255))
            instruction_rect = instruction_rendered.get_rect(center=(center[0], center[1] - 140))
            screen.blit(instruction_rendered, instruction_rect)

            linear_elapsed_time = time.time() - start_time
            guide_x = center[0] - int((linear_elapsed_time / guide_duration) * guide_radius)

            if guide_x < center[0] - guide_radius:
                guide_x = center[0] - guide_radius

            pygame.draw.circle(screen, (255, 255, 255), (guide_x, center[1]), guide_size, 2)

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
            pygame.draw.circle(screen, (255, 255, 255), (guide_x, center[1]), guide_size, 2)
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
            distance = abs(x - prev_x)
            prev_x = x
            points.append(abs(x))
            if abs(x) != 1.0:
                print(f"{abs(x):.5f} [{distance:.4f}]")

        if abs(x) >= 0.99:
            running = False

    end_time = time.time() if points else None
    stop_event.set()
    return points, start_time, end_time

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

def prepare_test_data(points, fpoints, test_duration, resolution, num_points, fnum_points, tremor, avg_step_resolution, stick_resolution, joystick_name):
    # Format points to exactly 5 decimal places
    formatted_points = [f"{p:.5f}" for p in points]
    formatted_fpoints = [f"{p:.5f}" for p in fpoints]
    
    return {
        "lin_test": True,
        "test_key2": generate_test_id(),
        "method": "LIN",
        "version": version,
        "name": joystick_name,
        "all_stats": {
            "duration": float(f"{test_duration:.5f}"),
            "min_resolution": float(f"{resolution:.5f}"),
            "avg_resolution": float(f"{avg_step_resolution:.5f}"),
            "total_points": num_points,
            "analog_points": fnum_points,
            "tremor": float(f"{tremor:.5f}"),
            "stick_resolution": stick_resolution
        },
        "all_delays": {
            "raw": formatted_points,
            "filtered": formatted_fpoints
        }
    }


def submit_test_results(data):
    url = "https://gamepadla.com/scripts/poster.php"
    
    data['all_stats'] = json.dumps(data['all_stats'])
    data['all_delays'] = json.dumps(data['all_delays'])
    
    try:
        response = requests.post(url, data=data)
        if response.status_code == 200:
            print("\nTest results successfully submitted to gamepadla.com")
            test_id = data['test_key2']
            print(f"Test ID: {test_id}")
            
            results_url = f"https://gamepadla.com/stick_analyzer/{test_id}/"
            webbrowser.open(results_url)
            print(f"You can view your results at: {results_url}")
            return True
        else:
            print(f"\nFailed to submit results. Status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"\nError submitting results: {str(e)}")
        return False

def save_results(points):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"stick_analyzer_{timestamp}.txt"
    with open(filename, "w") as file:
        data_str = ' '.join(f".{point*100000:05.0f}" for point in points)
        file.write(data_str)
    print(f"\nData saved to {filename}")

def visualize_results(points, fpoints, test_duration, resolution, num_points, fnum_points, tremor, avg_step_resolution, stick_resolution):
    plt.style.use("dark_background")
    fig, ax = plt.subplots(figsize=(10, 6))
    
    x_points = list(range(len(points)))
    x_fpoints = list(range(len(fpoints)))
    
    ax.plot(x_points, points, label="Raw Points")
    ax.plot(x_fpoints, fpoints, label="Filtered Points")
    ax.set_xlabel("Samples")
    ax.set_ylabel("Stick Value")
    ax.set_title(f"Stick Movement Graph | {test_duration:.2f} seconds")
    ax.legend()

    text_to_display = f"Raw Points: {num_points}\n" \
                      f"Filtered Points: {fnum_points}\n" \
                      f"Step Res.: {avg_step_resolution:.5f}\n" \
                      f"Tremor: {tremor:.1f}%\n"
    fig.text(0.88, 0.15, text_to_display, ha="right", fontsize=10)
    
    plt.show()

def analyze_results(points, start_time, end_time, joystick_name):
    if not points:
        print("No valid points detected for analysis.")
        return

    test_duration = end_time - start_time
    fpoints = filter_noise(points)

    if not fpoints:
        print("No filtered points available for analysis.")
        return

    distances = [abs(points[i] - points[i - 1]) for i in range(1, len(points))]
    fdistances = [abs(fpoints[i] - fpoints[i - 1]) for i in range(1, len(fpoints))]

    num_points = len(points)
    fnum_points = len(fpoints)
    
    fcounts = Counter(fdistances)
    fmost_common_value = max(fcounts, key=fcounts.get)

    avg_step_resolution = sum(fdistances) / len(fdistances)
    tremor = max(100 - ((100 / num_points) * fnum_points), 0)
    stick_resolution = int(1 / avg_step_resolution)

    print("\nTEST RESULTS:")
    if test_duration < 3:
        print("\033[31mWARNING:\033[0m The test duration should be at least 3 seconds! The test should be repeated!")
    print("-------------")
    print(f"Test duration:          {test_duration:.2f} seconds")
    print(f"Min. Step Resolution:   {fmost_common_value:.5f}")
    print(f"Avg. Step Resolution:   {avg_step_resolution:.5f}")
    print(f"Analog points:          {fnum_points} of {num_points}")
    print(f"Tremor:                 {tremor:.1f}%")

    test_data = prepare_test_data(
        points=points,
        fpoints=fpoints,
        test_duration=test_duration,
        resolution=fmost_common_value,
        num_points=num_points,
        fnum_points=fnum_points,
        tremor=tremor,
        avg_step_resolution=avg_step_resolution,
        stick_resolution=stick_resolution,
        joystick_name=joystick_name
    )
    submit_test_results(test_data)

def main():
    clear_screen()
    print_logo()
    
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
    pygame.display.set_caption("Test 1: Linear test")
    
    visualization_thread = Thread(target=visualize_stick_movement, args=(screen, joystick, positions, stop_event, countdown_duration, guide_radius, guide_duration, guide_size, x_axis, y_axis))
    visualization_thread.start()
    
    points, start_time, end_time = measure_stick_movement(joystick, positions, stop_event, countdown_duration, x_axis, y_axis)
    visualization_thread.join()

    pygame.quit()

    if points and start_time and end_time:
        analyze_results(points, start_time, end_time, joystick_name)
    else:
        print("No stick movement detected.")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()