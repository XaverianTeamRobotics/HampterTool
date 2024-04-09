import os
import sys
import threading
import time
import json

if not os.path.exists("./data"):
    os.mkdir("./data")

if not os.path.exists("./data.json"):
    with open("./data.json", "w") as f:
        f.write("[]")

if not os.path.exists("./report_path.txt"):
    with open("./report_path.txt", "w") as f:
        f.write("./reports_file_here")


def get_files_in_folder(folder_path):
    file_list = []
    for file in os.listdir(folder_path):
        if os.path.isfile(os.path.join(folder_path, file)):
            file_list.append(os.path.join(folder_path, file))
    return file_list


print("Starting the data transfer service. Press ENTER to enter analysis mode.")

transfer_stop_request = threading.Event()


def transfer_service():
    while not transfer_stop_request.is_set():
        with open("./report_path.txt", "r") as f:
            report_path = f.read().strip()
        files = get_files_in_folder("./data")
        try:
            if os.path.exists(report_path):
                files.append(report_path)
        except Exception as e:
            pass

        if len(files) > 0:
            data = []
            if os.path.exists("./data.json"):
                with open("./data.json", "r") as f:
                    data = json.load(f)
            for file in files:
                with open(file, "r") as f:
                    f_data = json.load(f)
                    data.extend(f_data)
                os.remove(file)
            with open("./data.json", "w") as f:
                json.dump(data, f)
            print(f"Transfer Completed. Remember to press RESET on the board.")
        time.sleep(1)


transfer_thread = threading.Thread(target=transfer_service)
transfer_thread.start()

try:
    while True:
        input()
        print("Pausing the data transfer service...")
        transfer_stop_request.set()
        transfer_thread.join()
        transfer_stop_request.clear()
        print("Data transfer is temporarily paused.")
        while True:
            choice = input("Data analysis mode...\n\t1. Lookup team information\n\t2. Best teams by category\n\t3. "
                           "Exit analysis mode and resume data transfer\n\t4. Exit\nEnter your choice: ")
            if choice == "1":
                team_number = input("Enter team number: ")
                with open("./data.json", "r") as f:
                    data = json.load(f)
                team_data = [d for d in data if d[0] == int(team_number)]
                if len(team_data) == 0:
                    print("No data found for the team.")
                else:
                    purple_pixels = sum([1 for d in team_data if d[1]]) / len(team_data)
                    yellow_pixels = sum([1 for d in team_data if d[2]]) / len(team_data)
                    auto_white_pixels = sum([d[3] for d in team_data]) / len(team_data)
                    auto_park = sum([1 for d in team_data if d[4]]) / len(team_data)
                    teleop_pixels = sum([d[5] for d in team_data]) / len(team_data)
                    drone_points = sum([d[6] for d in team_data]) / len(team_data)
                    hanging = sum([1 for d in team_data if d[7]]) / len(team_data)
                    parking = sum([1 for d in team_data if d[8]]) / len(team_data)
                    mosiacs = sum([d[9] for d in team_data]) / len(team_data)
                    set_lines = sum([d[10] for d in team_data]) / len(team_data)
                    robot_issues = sum([1 for d in team_data if d[11]]) / len(team_data)
                    robot_dnf = sum([1 for d in team_data if d[12]]) / len(team_data)
                    print("\n"
                          "Autonomous")
                    print(f"\tPercent of purple pixels scored: {purple_pixels * 100}%")
                    print(f"\tPercent of yellow pixels scored: {yellow_pixels * 100}%")
                    print(f"\tAverage white pixels scored: {auto_white_pixels}"
                          f"")
                    print(f"\tPercent of times auto parked: {auto_park * 100}%")
                    print(f"Teleop")
                    print(f"\tAverage pixels scored: ", teleop_pixels)
                    print(f"\tAverage drone points: ", drone_points)
                    print(f"\tPercent of times hung: {hanging * 100}%")
                    print(f"\tPercent of times parked: {parking * 100}%")
                    print(f"\tAverage mosiacs scored: ", mosiacs)
                    print(f"\tAverage set lines: ", set_lines)
                    print(f"Other")
                    print(f"\tPercent of matches with robot issues: {robot_issues * 100}%")
                    print(f"\tPercent of matches with robot DNF: {robot_dnf * 100}%")
                    input("Press ENTER to continue...\n\n")
            elif choice == "2":
                with open("./data.json", "r") as f:
                    data = json.load(f)
                team_data = {}
                for d in data:
                    if d[0] not in team_data:
                        team_data[d[0]] = []
                    auto_points = 0
                    teleop_points = 0
                    # Auto points is 20 if purple + 25 if yellow + 5 * white + 5 if parked
                    auto_points += 20 if d[1] else 0
                    auto_points += 25 if d[2] else 0
                    auto_points += 5 * d[3]
                    auto_points += 5 if d[4] else 0
                    # Teleop points is pixels + drone + 20 if hung + 5 if parked + 10 * mosaics + 10 * set lines
                    teleop_points += d[5]
                    teleop_points += d[6]
                    teleop_points += 20 if d[7] else 0
                    teleop_points += 5 if d[8] else 0
                    teleop_points += 10 * d[9]
                    teleop_points += 10 * d[10]
                    team_data[d[0]].append((auto_points, teleop_points))
                for team in team_data:
                    team_data[team] = (sum([d[0] for d in team_data[team]]) / len(team_data[team]),
                                       sum([d[1] for d in team_data[team]]) / len(team_data[team]))
                auto_sorted = sorted(team_data.items(), key=lambda x: x[1][0], reverse=True)
                teleop_sorted = sorted(team_data.items(), key=lambda x: x[1][1], reverse=True)
                print("\nBest teams by autonomous points")
                num_to_display = min(5, len(team_data))
                for i in range(num_to_display):
                    print(f"\t{auto_sorted[i][0]}: {auto_sorted[i][1][0]}")
                print("Best teams by teleop points")
                for i in range(num_to_display):
                    print(f"\t{teleop_sorted[i][0]}: {teleop_sorted[i][1][1]}")

                input("Press ENTER to continue...\n\n")
            elif choice == "3":
                print("Resuming the data transfer service.")
                transfer_thread = threading.Thread(target=transfer_service)
                transfer_thread.start()
                break
            elif choice == "4":
                print("Exiting...")
                sys.exit(0)

except KeyboardInterrupt:
    print("Shutting down the data transfer service...")
    transfer_stop_request.set()
    transfer_thread.join()
    print("Data transfer service has been shut down.")
