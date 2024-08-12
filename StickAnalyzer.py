# Stick resolution analyzer by John Punch
# https://www.reddit.com/user/JohnnyPunch
version = "1.6.1"
import pygame
import time
import math
import matplotlib.pyplot as plt
from colorama import Fore, Back, Style
from collections import Counter
from threading import Thread, Event

print()
print(f"░██████╗████████╗██╗░█████╗░██╗░░██╗  ░█████╗░███╗░░██╗░█████╗░██╗░░██╗░░░██╗███████╗███████╗██████╗░")
print(f"██╔════╝╚══██╔══╝██║██╔══██╗██║░██╔╝  ██╔══██╗████╗░██║██╔══██╗██║░░╚██╗░██╔╝╚════██║██╔════╝██╔══██╗")
print(f"╚█████╗░░░░██║░░░██║██║░░╚═╝█████═╝░  ███████║██╔██╗██║███████║██║░░░╚████╔╝░░░███╔═╝█████╗░░██████╔╝")
print(f"░╚═══██╗░░░██║░░░██║██║░░██╗██╔═██╗░  ██╔══██║██║╚████║██╔══██║██║░░░░╚██╔╝░░██╔══╝░░██╔══╝░░██╔══██╗")
print(f"██████╔╝░░░██║░░░██║╚█████╔╝██║░╚██╗  ██║░░██║██║░╚███║██║░░██║███████╗██║░░░███████╗███████╗██║░░██║")
print(f"╚═════╝░░░░╚═╝░░░╚═╝░╚════╝░╚═╝░░╚═╝  ╚═╝░░╚═╝╚═╝░░╚══╝╚═╝░░╚═╝╚══════╝╚═╝░░░╚══════╝╚══════╝╚═╝░░╚═╝")
print(f"v.{version} by John Punch")
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
    return joystick

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

def visualize_stick_movement(screen, joystick, positions, stop_event, countdown_duration=5, guide_radius=100, guide_duration=10, guide_size=12):
    center = (320, 240)
    font_large = pygame.font.Font(None, 72)
    font_small = pygame.font.Font(None, 24)
    font_coords = pygame.font.Font(None, 36)
    start_time = time.time()

    while not stop_event.is_set():
        current_time = time.time()
        elapsed_time = current_time - start_time
        
        screen.fill((30, 30, 30))
        pygame.draw.circle(screen, (200, 200, 200), center, guide_radius, 1)
        pygame.draw.line(screen, (200, 200, 200), (center[0] - guide_radius, center[1]), (center[0] + guide_radius, center[1]), 1)
        pygame.draw.line(screen, (200, 200, 200), (center[0], center[1] - guide_radius), (center[0], center[1] + guide_radius), 1)

        # Countdown
        if elapsed_time < countdown_duration:
            countdown = countdown_duration - int(elapsed_time)
            countdown_text = font_large.render(str(countdown), True, (255, 255, 255))
            countdown_rect = countdown_text.get_rect(center=center)
            screen.blit(countdown_text, countdown_rect)

            instruction_text = "Rotate the stick 3 times clockwise and release it."
            instruction_rendered = font_small.render(instruction_text, True, (255, 255, 255))
            instruction_rect = instruction_rendered.get_rect(center=(center[0], center[1] - 140))
            screen.blit(instruction_rendered, instruction_rect)
        else:
            # Guide animation
            guide_elapsed_time = elapsed_time - countdown_duration
            if guide_elapsed_time <= guide_duration:
                guide_x = center[0] - int((guide_elapsed_time / guide_duration) * guide_radius)
                guide_surface = pygame.Surface((guide_size * 2, guide_size * 2), pygame.SRCALPHA)
                pygame.draw.circle(guide_surface, (255, 255, 255, 128), (guide_size, guide_size), guide_size, 2)
                screen.blit(guide_surface, (guide_x - guide_size, center[1] - guide_size))

                # Add the new instruction text
                guide_instruction_text = "Move the left stick according to the guide"
                guide_instruction_rendered = font_small.render(guide_instruction_text, True, (255, 255, 255))
                guide_instruction_rect = guide_instruction_rendered.get_rect(center=(center[0], center[1] + 140))
                screen.blit(guide_instruction_rendered, guide_instruction_rect)

            x_axis = joystick.get_axis(0)
            y_axis = joystick.get_axis(1)

            stick_position = (center[0] + int(x_axis * guide_radius), center[1] + int(y_axis * guide_radius))
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

            coords_text = f"X: {x_axis:.3f}, Y: {y_axis:.3f}"
            coords_rendered = font_coords.render(coords_text, True, (255, 255, 255))
            screen.blit(coords_rendered, (10, 10))
        
        pygame.display.flip()
        pygame.time.wait(10)  # Додаємо невелику затримку, щоб зменшити навантаження на процесор

def measure_stick_movement(joystick, positions, stop_event, countdown_duration=5):
    points = []
    prev_x = 0.0
    start_time = None
    running = True

    print("---")
    print(f"Start slowly moving the left stick of the gamepad to the side")
    print()

    # Відлік часу перед початком тесту
    countdown_start_time = time.time()
    while time.time() - countdown_start_time < countdown_duration:
        pygame.event.pump()

    while running and not stop_event.is_set():
        pygame.event.pump()
        x = joystick.get_axis(0)
        
        if x != 0.0 and x != prev_x:
            if prev_x == 0.0:
                prev_x = x
                points.append(abs(x))  # Збереження значення стіку
                print(f"{abs(x):.5f}")
                start_time = time.time()
            else:
                distance = abs(x - prev_x)
                prev_x = x
                points.append(abs(x))  # Збереження значення стіку
                if abs(x) != 1.0:
                    print(f"{abs(x):.5f} [{distance:.4f}]")

        if abs(x) >= 0.99:
            running = False

    end_time = time.time() if points else None
    stop_event.set()
    return points, start_time, end_time

def analyze_results(points, start_time, end_time):
    if not points:
        return

    test_duration = end_time - start_time
    fpoints = filter_noise(points)

    distances = [abs(points[i] - points[i - 1]) for i in range(1, len(points))]
    fdistances = [abs(fpoints[i] - fpoints[i - 1]) for i in range(1, len(fpoints))]

    num_points = len(points)
    fnum_points = len(fpoints)
    
    fcounts = Counter(fdistances)
    fmost_common_value = max(fcounts, key=fcounts.get)

    tremor = 100 - ((100 / num_points) * fnum_points)
    tremor = max(tremor, 0)

    print()
    print("TEST RESULTS:")
    if test_duration < 3:
        print("\033[31mWARNING:\033[0m The test duration should be at least 3 seconds! The test should be repeated!")
    print("-------------")
    print(f"Test duration: {test_duration:.2f} seconds")
    print(f"Stick resolution: {fmost_common_value:.5f}")
    print(f"Analog points: {fnum_points} of {num_points}")
    print(f"Tremor: {tremor:.1f}%")

    total_counts = sum(fcounts.values())
    print("\nTop 5 Value Occurrences:")
    for i, (value, count) in enumerate(sorted(fcounts.items(), key=lambda x: x[1], reverse=True)):
        if i < 5:
            percentage = (count / total_counts) * 100
            print(f"{value:.5f}: {count} ({percentage:.2f}%)")
        else:
            break

    save_results(points)
    visualize_results(points, fpoints, test_duration, fmost_common_value, num_points, fnum_points, tremor)

def save_results(points):
    with open("stick_data.txt", "w") as file:
        data_str = ' '.join(f".{point*100000:05.0f}" for point in points)
        file.write(data_str)
    print("\nData saved to stick_data.txt")

def visualize_results(points, fpoints, test_duration, resolution, num_points, fnum_points, tremor):
    plt.style.use("dark_background")
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Використання індексів точок для осі X
    x_points = list(range(len(points)))
    x_fpoints = list(range(len(fpoints)))
    
    ax.plot(x_points, points, label="Program Points")
    ax.plot(x_fpoints, fpoints, label="Analog Points")
    ax.set_xlabel("Samples")
    ax.set_ylabel("Stick Value")
    ax.set_title(f"Stick Movement Graph | {test_duration:.2f} seconds")
    ax.legend()

    text_to_display = f"Stick Resolution: {resolution:.5f}\n" \
                      f"Program Points: {num_points}\n" \
                      f"Analog Points: {fnum_points}\n" \
                      f"Tremor: {tremor:.1f}%\n" \
                      f"Test Duration: {test_duration:.2f}"
    fig.text(0.88, 0.15, text_to_display, ha="right", fontsize=10)
    
    plt.show()
    input("Press Enter to exit...")

def main():
    joystick = init_joystick()
    if joystick is None:
        return

    positions = []
    stop_event = Event()
    guide_size = 8  # Розмір гіда
    guide_radius = 100  # Радіус руху гіда
    guide_duration = 8  # Тривалість руху гіда
    countdown_duration = 5  # Тривалість відліку перед початком тесту

    screen = pygame.display.set_mode((640, 480))
    pygame.display.set_caption("Test 1: Linear test")
    visualization_thread = Thread(target=visualize_stick_movement, args=(screen, joystick, positions, stop_event, countdown_duration, guide_radius, guide_duration, guide_size))
    visualization_thread.start()
    
    points, start_time, end_time = measure_stick_movement(joystick, positions, stop_event, countdown_duration)
    visualization_thread.join()

    pygame.quit()  # Закриття вікна візуалізації стіку

    if points and start_time and end_time:
        analyze_results(points, start_time, end_time)
    else:
        print("No stick movement detected.")

if __name__ == "__main__":
    main()
