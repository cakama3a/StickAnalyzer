import pygame
import time
from colorama import Fore, Back, Style
from collections import Counter
from threading import Thread, Event
import os
import json
from datetime import datetime
import matplotlib.pyplot as plt

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

def filter_noise(results, timestamps):
    if not results or not timestamps:
        return [], []

    # Модифікований фільтр, який враховує також часові проміжки між точками
    filtered_data = []
    filtered_timestamps = []
    
    for i in range(len(results)):
        # Перевіряємо, чи точка відповідає критеріям фільтрації
        if i == 0 or (results[i] > results[i-1]):
            filtered_data.append(results[i])
            filtered_timestamps.append(timestamps[i])
    
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
    guide_visible = False
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

        # Малюємо основну сітку
        pygame.draw.circle(screen, (100, 100, 100), center, guide_radius, 1)
        pygame.draw.line(screen, (100, 100, 100), (center[0] - guide_radius, center[1]), (center[0] + guide_radius, center[1]), 1)
        pygame.draw.line(screen, (100, 100, 100), (center[0], center[1] - guide_radius), (center[0], center[1] + guide_radius), 1)

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
                instruction_text = "Get ready to move the stick to the LEFT in your own pace."
                instruction_rendered = font_small.render(instruction_text, True, (255, 255, 255))
                instruction_rect = instruction_rendered.get_rect(center=(center[0], center[1] - 140))
                screen.blit(instruction_rendered, instruction_rect)

        elif guide_visible and not test_completed:
            instruction_text = "Move stick LEFT at your own pace - TEST YOUR CURVE"
            instruction_rendered = font_small.render(instruction_text, True, (255, 255, 255))
            instruction_rect = instruction_rendered.get_rect(center=(center[0], center[1] - 140))
            screen.blit(instruction_rendered, instruction_rect)
            
            # Малюємо тільки тонку стрілку над віссю X зліва
            arrow_start = (center[0] - guide_radius + 40, center[1] - 5)
            arrow_end = (center[0] - guide_radius + 10, center[1] - 5)
            
            # Лінія стрілки
            pygame.draw.line(screen, (200, 200, 200), arrow_start, arrow_end, 1)
            
            # Наконечник стрілки
            arrow_head = [
                arrow_end,
                (arrow_end[0] + 5, arrow_end[1] - 3),
                (arrow_end[0] + 5, arrow_end[1] + 3),
            ]
            pygame.draw.polygon(screen, (200, 200, 200), arrow_head)

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
    timestamps = []  # Додаємо для збереження часу кожної точки

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
            timestamps.append(current_time - start_time if start_time else 0)  # Зберігаємо відносний час
            if abs(x) != 1.0:
                print(f"{abs(x):.5f} [{distance:.4f}] at {timestamps[-1]:.4f}s")

        if abs(x) >= 0.99:
            running = False

    end_time = time.time() if points else None
    stop_event.set()
    return points, timestamps, start_time, end_time

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

def save_results(points, timestamps, fpoints, ftimestamps, test_duration):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"stick_analyzer_{timestamp}.txt"
    with open(filename, "w") as file:
        file.write("# Stick Analyzer Results\n")
        file.write(f"# Test Duration: {test_duration:.2f} seconds\n")
        file.write("# Raw Data\n")
        file.write("# Time,Position\n")
        for i in range(len(points)):
            file.write(f"{timestamps[i]:.5f},{points[i]:.5f}\n")
        
        file.write("\n# Filtered Data\n")
        file.write("# Time,Position\n")
        for i in range(len(fpoints)):
            file.write(f"{ftimestamps[i]:.5f},{fpoints[i]:.5f}\n")
    
    print(f"\nData saved to {filename}")

def visualize_results(points, fpoints, timestamps, ftimestamps, test_duration):
    # Налаштування стилю графіка для темного фону
    plt.style.use("dark_background")
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10))
    
    # Перший графік - позиція стіка відносно часу
    ax1.plot(timestamps, points, 'o-', label="Raw Points", alpha=0.7)
    ax1.plot(ftimestamps, fpoints, 'o-', label="Filtered Points", color='red', linewidth=2)
    ax1.set_xlabel("Time (seconds)")
    ax1.set_ylabel("Stick Value")
    ax1.set_title(f"Stick Movement Graph | {test_duration:.2f} seconds")
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Другий графік - швидкість руху стіка
    velocities = []
    velocity_times = []
    
    if len(timestamps) > 1:
        for i in range(1, len(points)):
            if timestamps[i] != timestamps[i-1]:  # Уникаємо ділення на нуль
                velocity = (points[i] - points[i-1]) / (timestamps[i] - timestamps[i-1])
                velocities.append(velocity)
                velocity_times.append(timestamps[i])
    
    if velocities:
        ax2.plot(velocity_times, velocities, 'o-', label="Velocity", color='yellow')
        ax2.set_xlabel("Time (seconds)")
        ax2.set_ylabel("Velocity (position/second)")
        ax2.set_title("Stick Movement Velocity")
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # Обчислення статистики
        avg_velocity = sum(velocities) / len(velocities)
        min_velocity = min(velocities)
        max_velocity = max(velocities)
        
        # Додавання статистики до графіка
        stats_text = f"Min Velocity: {min_velocity:.3f}\n" \
                    f"Max Velocity: {max_velocity:.3f}\n" \
                    f"Avg Velocity: {avg_velocity:.3f}\n" \
                    f"Raw Points: {len(points)}\n" \
                    f"Filtered Points: {len(fpoints)}"
        
        # Розміщення текстового блоку з інформацією
        fig.text(0.02, 0.02, stats_text, fontsize=10, bbox=dict(facecolor='black', alpha=0.7))
    
    plt.tight_layout()
    plt.show()

def analyze_results(points, start_time, end_time, joystick_name, timestamps):
    if not points:
        print("No valid points detected for analysis.")
        return

    test_duration = end_time - start_time
    fpoints, ftimestamps = filter_noise(points, timestamps)

    if not fpoints:
        print("No filtered points available for analysis.")
        return

    # Обчислення швидкості руху для кожної точки
    velocities = []
    if len(points) > 1 and len(timestamps) > 1:
        for i in range(1, len(points)):
            # Швидкість = зміна позиції / зміна часу
            if timestamps[i] != timestamps[i-1]:  # Уникаємо ділення на нуль
                velocity = (points[i] - points[i-1]) / (timestamps[i] - timestamps[i-1])
                velocities.append(velocity)
        
        if velocities:
            avg_velocity = sum(velocities) / len(velocities)
            min_velocity = min(velocities)
            max_velocity = max(velocities)
            print(f"Min velocity: {min_velocity:.5f}")
            print(f"Max velocity: {max_velocity:.5f}")
            print(f"Avg velocity: {avg_velocity:.5f}")

    distances = [abs(points[i] - points[i - 1]) for i in range(1, len(points))]
    fdistances = [abs(fpoints[i] - fpoints[i - 1]) for i in range(1, len(fpoints))]

    num_points = len(points)
    fnum_points = len(fpoints)
    
    if fdistances:
        fcounts = Counter(fdistances)
        fmost_common_value = max(fcounts, key=fcounts.get)
        avg_step_resolution = sum(fdistances) / len(fdistances)
    else:
        fmost_common_value = 0
        avg_step_resolution = 0
    
    tremor = max(100 - ((100 / num_points) * fnum_points), 0) if num_points > 0 else 0
    stick_resolution = int(1 / avg_step_resolution) if avg_step_resolution > 0 else 0

    print("\nTEST RESULTS:")
    if test_duration < 3:
        print("\033[31mWARNING:\033[0m The test duration should be at least 3 seconds! The test should be repeated!")
    print("-------------")
    print(f"Test duration:          {test_duration:.2f} seconds")
    print(f"Min. Step Resolution:   {fmost_common_value:.5f}")
    print(f"Avg. Step Resolution:   {avg_step_resolution:.5f}")
    print(f"Analog points:          {fnum_points} of {num_points}")
    print(f"Tremor:                 {tremor:.1f}%")
    
    # Замість відправки на сервер зберігаємо результати та показуємо графік
    save_results(points, timestamps, fpoints, ftimestamps, test_duration)
    visualize_results(points, fpoints, timestamps, ftimestamps, test_duration)

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
    
    points, timestamps, start_time, end_time = measure_stick_movement(joystick, positions, stop_event, countdown_duration, x_axis, y_axis)
    visualization_thread.join()

    pygame.quit()

    if points and start_time and end_time:
        analyze_results(points, start_time, end_time, joystick_name, timestamps)
    else:
        print("No stick movement detected.")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()