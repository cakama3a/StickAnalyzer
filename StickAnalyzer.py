# Stick resolution analyzer by John Punch
# https://www.reddit.com/user/JohnnyPunch
version = "1.0.3"
import pygame

print(f"   _____ __  _      __      ___                __                     ")
print(f"  / ___// /_(_)____/ /__   /   |  ____  ____ _/ /_  ______  ___  _____")
print(f"  \__ \/ __/ / ___/ //_/  / /| | / __ \/ __ `/ / / / /_  / / _ \/ ___/")
print(f" ___/ / /_/ / /__/ ,<    / ___ |/ / / / /_/ / / /_/ / / /_/  __/ /    ")
print(f"/____/\__/_/\___/_/|_|  /_/  |_/_/ /_/\__,_/_/\__, / /___/\___/_/     ")
print(f"                                             /____/                   ")
print(f"v.{version} by John Punch  |  Support me: https://ko-fi.com/gamepadla")
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
    prev_x = 0.0

    print("---")
    print(f"Start slowly moving the left stick of the gamepad to the side")
    print()

    while True:
        pygame.event.pump()
        x = joystick.get_axis(0)

        if x != 0.0 and x != prev_x:
            if prev_x == 0.0:
                prev_x = x
                points.append(abs(x))
                print(f"{abs(x):.5f}")
            else:
                distance = abs(x - prev_x)
                prev_x = x
                points.append(abs(x))
                if abs(x) != 1.0:
                    print(f"{abs(x):.5f} [{distance:.3f}]")

        if abs(x) >= 0.99:
            break

    if points:
        distances = [abs(points[i] - points[i - 1]) for i in range(1, len(points))]
        avg_distance = sum(distances) / len(distances)
        min_distance = min(distances)
        max_distance = max(distances)
        num_points = len(points)

        # Знайти значення, що повторюється найчастіше
        from collections import Counter
        counts = Counter(distances)
        most_common_value = max(counts, key=counts.get)

        print()
        print(f"\033[1mStick resolution: {most_common_value:.4f}\033[0m")
        print("---")
        print(f"Average distance: {avg_distance:.4f}")
        print(f"Minimum distance: {min_distance:.4f}")
        print(f"Maximum distance: {max_distance:.4f}")
        print(f"Number of points: {num_points}")

        # Вивести скільки разів повторюється кожне значення у відсотках
        total_counts = sum(counts.values())
        print("\nValue Occurrences:")
        for value, count in counts.items():
            percentage = (count / total_counts) * 100
            print(f"{value:.4f}: {count} ({percentage:.2f}%)")

        print()
        data_str = ' '.join(f".{point*100000:05.0f}" for point in points)
        print(f"Data:")
        print(f"{data_str}")
        print()
        input("Press Enter to exit...")
    else:
        print("No stick movement detected.")

if __name__ == "__main__":
    main()