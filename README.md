# Stick Analyzer

**Stick Analyzer** is a powerful open-source tool designed to evaluate and analyze the performance of game controller analog sticks. By measuring stick movement, resolution, linearity, and tremor, it provides detailed insights into joystick precision and responsiveness, making it an essential utility for gamers, developers, and hardware enthusiasts. Whether you're troubleshooting stick drift, assessing hardware quality, or optimizing controller performance, Stick Analyzer delivers comprehensive results in an accessible format.

**Author**: John Punch  
**Support the Project**: [ko-fi.com/gamepadla](https://ko-fi.com/gamepadla)  
**Guide**: [How to Use Stick Analyzer](https://www.reddit.com/r/Controller/comments/1i831jw/stick_analyzer_complete_guide_to_gamepad_stick/)  

<img width="735" alt="2025-04-12_12-53" src="https://github.com/user-attachments/assets/cc31ffb5-cbdf-4547-9a46-de2c29e41ef1" />

---

## Features

Stick Analyzer offers a robust set of tools to analyze joystick performance:

- **Precision Measurement**: Tracks stick movement from center to edge, capturing fine-grained displacement data to evaluate resolution and accuracy.
- **Linearity Analysis**: Calculates nonlinearity and linearity percentages to assess how closely stick movement matches an ideal linear path.
- **Tremor Detection**: Identifies inconsistencies in stick movement, quantifying tremor as a percentage to highlight potential hardware issues.
- **Real-Time Visualization**: Displays live stick movement with a graphical interface, guiding users through calibration and testing phases.
- **Detailed Statistics**: Provides metrics such as test duration, total data points, resolution, and step resolution for in-depth analysis.
- **Data Export**: Saves raw test data to text files and generates visual plots using Matplotlib for easy review.
- **Online Submission**: Optionally submits results to [gamepadla.com](https://gamepadla.com) for sharing and further analysis, with automatic browser opening to view results.
- **Cross-Platform Compatibility**: Supports Windows, macOS, and Linux (with compatible controllers and dependencies).

---

## Screenshots

![Calibration Phase](https://github.com/user-attachments/assets/08025433-c260-4a5b-a30d-e80de79ba32f)  
*Calibration phase guiding the user to rotate the stick.*

![Results Plot](https://github.com/user-attachments/assets/4eb09041-64b2-448a-9fe9-476a7ff78e1f)  
*Graphical plot showing stick movement and linearity analysis.*

<img width="941" alt="2025-04-12_12-54" src="https://github.com/user-attachments/assets/1af91fd9-e7df-4673-aa95-8008f44366c2" />  
*Web version of the test after sending it to Gamepadla.com servers*

---

## Installation

### Windows (Executable Version)
For Windows users, simply download and run the pre-built executable:

1. Visit the [releases page](https://github.com/cakama3a/StickAnalyzer/releases).
2. Download the latest `.exe` file (e.g., `StickAnalyzer-v2.0.3.0.exe`).
3. Double-click the `.exe` file to launch Stick Analyzer—no additional setup required.
4. Ensure a compatible game controller is connected.

> **Note**: The executable includes all dependencies, making it the easiest option for Windows users.

### Console Version (Python)
For cross-platform use or development:

#### Prerequisites
- **Python 3.8+**
- **Dependencies**:
  - `pygame`: For joystick input and visualization.
  - `colorama`: For colored terminal output.
  - `matplotlib`: For generating result plots.
  - `requests`: For submitting results to gamepadla.com.
  - `webbrowser`: For opening results in a browser.

Install dependencies using pip:

```bash
pip install pygame colorama matplotlib requests
