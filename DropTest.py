import pygame
import time
import matplotlib.pyplot as plt

version = "1.0.7"
print()
print("   _____ __  _      __      ___                __                     ")
print("  / ___// /_(_)____/ /__   /   |  ____  ____ _/ /_  ______  ___  _____")
print("  \__ \/ __/ / ___/ //_/  / /| | / __ \/ __ `/ / / / /_  / / _ \/ ___/")
print(" ___/ / /_/ / /__/ ,<    / ___ |/ / / / /_/ / / /_/ / / /_/  __/ /    ")
print("/____/\__/_/\___/_/|_|  /_/  |_/_/ /_/\__,_/_/\__, / /___/\___/_/     ")
print("                                             /____/                   ")
print(f"v.{version} by John Punch")
print()

def main():
    pygame.init()
    pygame.joystick.init()

    joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
    if not joysticks:
        print("No controller found")
        input("Press Enter to exit...")
        return

    joystick = joysticks[0]
    joystick.init()

    points = []
    times = []
    prev_x = None
    start_time = None
    last_significant_time = None
    similarity_threshold = 0.02
    zero_count = 0
    timeout = 2.0

    print("---")
    print("Step 1: Deflect the left stick of the gamepad fully to the right on the X-axis.")

    while True:
        pygame.event.pump()
        x = joystick.get_axis(0)
        current_time = time.time()

        if x >= 0.9:
            if not start_time:  # Start timing on initial deflection
                start_time = current_time
            if not points:
                points.append(x)
                times.append(0)  # Initialize the first time point at 0
                print(f"Step 2: Now release the stick!")
                prev_x = x
                last_significant_time = current_time
        elif points:
            elapsed_time = current_time - start_time
            if abs(x - prev_x) > similarity_threshold or not last_significant_time:
                if not last_significant_time:
                    last_significant_time = current_time  # Update significant movement time
                points.append(x)
                times.append(elapsed_time)
                print(f"{x:.5f} at {elapsed_time:.5f} seconds")
                prev_x = x
                zero_count = 0
            elif abs(x) < 0.05:
                zero_count += 1
                if zero_count >= 3:
                    break
            if last_significant_time and (current_time - last_significant_time > timeout):
                print("Timeout reached with no significant movement.")
                break

    if points:
        test_duration = times[-1]
        max_time = max(times)
        inverted_times = [max_time - t for t in times]  # Inverting the time data
        # Remove initial datapoint
        inverted_times = inverted_times[1:]
        points = points[1:]
        print()
        print("TEST RESULTS:")
        print("-------------")
        print(f"Number of points: {len(points)}")
        print(f"Test duration: {test_duration:.5f} seconds")
        with open("stick_release_data.txt", "w") as file:
            data_str = '\n'.join(f"{point:.5f} at {time:.5f} seconds" for point, time in zip(points, inverted_times))
            file.write(data_str)
        print("\nData saved to stick_release_data.txt")
        
        # Plotting the data with inverted time
        plt.style.use('dark_background')
        plt.figure(figsize=(10, 6))
        plt.plot(points, inverted_times, marker='o', linestyle='-', color='#80CBC4', markerfacecolor='#80CBC4', label='Joystick Movement')
        plt.title('Joystick Movement Over Time (Inverted Time)', color='white')
        plt.xlabel('Joystick Position', color='white')
        plt.ylabel('Inverted Time (seconds)', color='white')
        plt.axvline(0, color='#FF5252', linewidth=1, linestyle='--', label='Center Position')
        plt.grid(True, color='#616161')
        plt.gca().set_facecolor('#424242')  # Match axes background to figure background
        plt.gcf().set_facecolor('#424242')  # Ensure the figure background matches the axes
        plt.tight_layout()  # Apply tight layout to ensure all plot elements are neatly contained within the figure
        plt.legend()
        plt.show()

        print("-------------")
        print("Support me: https://ko-fi.com/gamepadla")
        print("I'm on Reddit: https://www.reddit.com/user/JohnnyPunch")
        print("*To open a link, hold down the Ctrl key")
        print()
        input("Press Enter to exit...")
    else:
        print("No stick movement detected.")

if __name__ == "__main__":
    main()