# Stick resolution analyzer by John Punch
# https://www.reddit.com/user/JohnnyPunch
version = "1.0.6"
import pygame
import time  # Імпортуємо модуль time для таймера

print()
print(f"   _____ __  _      __      ___                __                     ")
print(f"  / ___// /_(_)____/ /__   /   |  ____  ____ _/ /_  ______  ___  _____")
print(f"  \__ \/ __/ / ___/ //_/  / /| | / __ \/ __ `/ / / / /_  / / _ \/ ___/")
print(f" ___/ / /_/ / /__/ ,<    / ___ |/ / / / /_/ / / /_/ / / /_/  __/ /    ")
print(f"/____/\__/_/\___/_/|_|  /_/  |_/_/ /_/\__,_/_/\__, / /___/\___/_/     ")
print(f"                                             /____/                   ")
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
    prev_x = None  # Ініціалізуємо змінну для зберігання попереднього значення
    start_time = None  # Ініціалізуємо змінну для зберігання часу початку тесту

    print("---")
    print("Step 1: Deflect the left stick of the gamepad fully to the right on the X-axis.")

    while True:
        pygame.event.pump()
        x = joystick.get_axis(0)

        if x >= 0.99:  # Якщо стік відхилено максимально вправо
            if not points:  # Якщо це перший запис
                points.append(x)
                print(f"Step 2: Now release the stick!")
                start_time = time.time()  # Зберігаємо час початку тесту
        elif points:  # Якщо стік вже було відпущено
            if x != prev_x:  # Якщо нове значення відрізняється від попереднього
                points.append(x)
                print(f"{x:.5f}")
                prev_x = x  # Зберігаємо поточне значення як попереднє

            if x < 0.01:  # Якщо значення стіка менше 0.01
                break

    if points:
        end_time = time.time()  # Зберігаємо час завершення тесту
        test_duration = end_time - start_time  # Обчислюємо тривалість тесту

        print()
        print("TEST RESULTS:")
        print("-------------")
        print(f"Number of points: {len(points)}")
        print(f"Test duration: {test_duration:.2f} seconds")  # Виводимо тривалість тесту

        # Зберегти дані в текстовий файл
        with open("stick_release_data.txt", "w") as file:
            data_str = ' '.join(f"{point:.5f}" for point in points)
            file.write(data_str)
        print("\nData saved to stick_release_data.txt")

        # Додати посилання
        print()
        print("-------------")
        print("Support me: \033[4m\033[94mhttps://ko-fi.com/gamepadla\033[0m")
        print("I'm on Reddit: \033[4m\033[94mhttps://www.reddit.com/user/JohnnyPunch\033[0m")
        print("*To open a link, hold down the Ctrl key")
        
        print()
        input("Press Enter to exit...")
    else:
        print("No stick movement detected.")

if __name__ == "__main__":
    main()