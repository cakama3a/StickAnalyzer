# Stick resolution analyzer by John Punch
# https://www.reddit.com/user/JohnnyPunch
version = "1.1.0"
import pygame
import time  # Імпортуємо модуль time для таймера
import matplotlib.pyplot as plt  # Імпортуємо Matplotlib для візуалізації
from colorama import Fore, Back, Style

print()
print(f"░██████╗████████╗██╗░█████╗░██╗░░██╗  ░█████╗░███╗░░██╗░█████╗░██╗░░██╗░░░██╗███████╗███████╗██████╗░")
print(f"██╔════╝╚══██╔══╝██║██╔══██╗██║░██╔╝  ██╔══██╗████╗░██║██╔══██╗██║░░╚██╗░██╔╝╚════██║██╔════╝██╔══██╗")
print(f"╚█████╗░░░░██║░░░██║██║░░╚═╝█████═╝░  ███████║██╔██╗██║███████║██║░░░╚████╔╝░░░███╔═╝█████╗░░██████╔╝")
print(f"░╚═══██╗░░░██║░░░██║██║░░██╗██╔═██╗░  ██╔══██║██║╚████║██╔══██║██║░░░░╚██╔╝░░██╔══╝░░██╔══╝░░██╔══██╗")
print(f"██████╔╝░░░██║░░░██║╚█████╔╝██║░╚██╗  ██║░░██║██║░╚███║██║░░██║███████╗██║░░░███████╗███████╗██║░░██║")
print(f"╚═════╝░░░░╚═╝░░░╚═╝░╚════╝░╚═╝░░╚═╝  ╚═╝░░╚═╝╚═╝░░╚══╝╚═╝░░╚═╝╚══════╝╚═╝░░░╚══════╝╚══════╝╚═╝░░╚═╝")
print(f"v.{version} by John Punch")
print()

# Фільтрація нелінійних результатів руху стіку, залишаємо лише один напрямок
def filter_noise(results):
    if not results:
        return []

    filtered_results = [results[0]]  # Починаємо з першого значення

    for i in range(1, len(results)):
        current_value = results[i]
        previous_values = results[:i]

        # Перевірка, чи всі попередні значення менші або рівні поточному
        # І чи поточне значення не було додано раніше
        if current_value not in filtered_results and all(prev <= current_value for prev in previous_values):
            filtered_results.append(current_value)

    return filtered_results

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
    start_time = None  # Ініціалізуємо змінну для зберігання часу початку тесту

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
                start_time = time.time()  # Зберігаємо час початку тесту
            else:
                distance = abs(x - prev_x)
                prev_x = x
                points.append(abs(x))
                if abs(x) != 1.0:
                    print(f"{abs(x):.5f} [{distance:.4f}]")

        if abs(x) >= 0.99:
            break

    if points:
        end_time = time.time()  # Зберігаємо час завершення тесту
        test_duration = end_time - start_time  # Обчислюємо тривалість тесту

        fpoints = filter_noise(points)  # Фільтруємо результати

        # Filtered list
        # print("\nFiltered results:")
        # for i in range(1, len(fpoints)):
        #     point = fpoints[i]
        #     prev_point = fpoints[i - 1]
        #     difference = abs(point - prev_point)
        #     print(f"{point:.5f} [{difference:.5f}]")

        distances = [abs(points[i] - points[i - 1]) for i in range(1, len(points))]
        fdistances = [abs(fpoints[i] - fpoints[i - 1]) for i in range(1, len(fpoints))]

        # avg_distance = sum(distances) / len(distances)
        # min_distance = min(distances)
        # max_distance = max(distances)
        num_points = len(points)
        fnum_points = len(fpoints)

        # Знайти значення, що повторюється найчастіше
        from collections import Counter
        counts = Counter(distances)
        fcounts = Counter(fdistances)
        # most_common_value = max(counts, key=counts.get)
        fmost_common_value = max(fcounts, key=fcounts.get)
        # avg_resolution = sum(fdistances) / len(fdistances)

        tremor = 100-((100/num_points)*fnum_points)
        if tremor <= 0:
            tremor = 0

        print()
        print("TEST RESULTS:")
        if test_duration < 3:
            print("\033[31mWARNING:\033[0m The test duration should be at least 3 seconds! The test should be repeated!")
        print("-------------")
        # print(f"Stick resolution: {most_common_value:.5f}")
        print(f"Test duration: {test_duration:.2f} seconds")  # Виводимо тривалість тесту
        print(f"Stick resolution: {fmost_common_value:.5f}")
        # print(f"AVG resolution: {avg_resolution:.5f}")
        print(f"Analog points: {fnum_points} of {num_points}")
        print(f"Tremor: {tremor:.1f}%")
        # print()
        # print(f"Average distance: {avg_distance:.5f}")
        # print(f"Minimum distance: {min_distance:.5f}")
        # print(f"Maximum distance: {max_distance:.5f}")
        # print()

        # Вивести скільки разів повторюється кожне значення у відсотках
        total_counts = sum(fcounts.values())
        print("\nTop 5 Value Occurrences:")
        for i, (value, count) in enumerate(sorted(fcounts.items(), key=lambda x: x[1], reverse=True)):
            if i < 5:  # Виводимо лише перші 5 значень
                percentage = (count / total_counts) * 100
                print(f"{value:.5f}: {count} ({percentage:.2f}%)")
            else:
                break  # Вийти з циклу після виведення перших 5 значень

        # Зберегти дані в текстовий файл
        with open("stick_data.txt", "w") as file:
            data_str = ' '.join(f".{point*100000:05.0f}" for point in points)
            file.write(data_str)
        print("\nData saved to stick_data.txt")

        # Додати посилання
        print()
        print("-------------")
        print("Support me: \033[4m\033[94mhttps://ko-fi.com/gamepadla\033[0m")
        print("I'm on Reddit: \033[4m\033[94mhttps://www.reddit.com/user/JohnnyPunch\033[0m")
        print("*To open a link, hold down the Ctrl key")
        
        print()

        # Візуалізація за допомогою Matplotlib
        plt.style.use("dark_background")
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(points)
        ax.set_xlabel("Samples")
        ax.set_ylabel("Stick Value")
        ax.set_title(f"Stick Movement Graph | {test_duration:.2f} seconds")
        
        # Вивід тексту під графіком
        # text_to_display = f"Stick Resolution: {most_common_value:.5f}\n" \
        text_to_display = f"Stick Resolution: {fmost_common_value:.5f}\n" \
                          f"Program Points: {num_points}\n" \
                          f"Analog Points: {fnum_points}\n" \
                          f"Tremor: {tremor:.1f}%\n" \
                          f"Test Duration: {test_duration:.2f}"
        fig.text(0.88, 0.15, text_to_display, ha="right", fontsize=10)

        # f"Average Distance: {avg_distance:.5f}\n" \
        # f"Minimum Distance: {min_distance:.5f}\n" \
        # f"Maximum Distance: {max_distance:.5f}\n" \
        
        plt.show()

        input("Press Enter to exit...")
    else:
        print("No stick movement detected.")

if __name__ == "__main__":
    main()