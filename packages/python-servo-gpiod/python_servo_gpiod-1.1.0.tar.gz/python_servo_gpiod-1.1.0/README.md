# Servo Control with gpiod

A comprehensive Python implementation for controlling servo motors using the `gpiod` library on Raspberry Pi and other Linux systems with GPIO support.

## Features

- **Full PWM Control**: Software-generated PWM signals using gpiod
- **Flexible Configuration**: Customizable frequency, pulse width ranges, and angle limits
- **Multiple Control Methods**: Angle-based, pulse width direct, and percentage-based control
- **Thread-Safe**: Concurrent access protection with threading locks
- **Sweep Functions**: Smooth servo movement between positions
- **Calibration Support**: Custom pulse width calibration for different servo types
- **Context Manager**: Automatic cleanup with `with` statement
- **Comprehensive Testing**: Full test suite with mock hardware support
- **Error Handling**: Custom exceptions and robust error management

# Servo Control with gpiod

A comprehensive Python implementation for controlling servo motors using the `gpiod` library on Raspberry Pi and other Linux systems with GPIO support.

---

## Requirements

![PyPI Version](https://img.shields.io/pypi/v/python-servo-gpiod)
![PyPI Status](https://img.shields.io/pypi/status/python-servo-gpiod)
![Python Version](https://img.shields.io/pypi/pyversions/python-servo-gpiod)
![PyPI Downloads](https://img.shields.io/pypi/dm/python-servo-gpiod)
![License](https://img.shields.io/github/license/Svndsn/python-servo)
![GitHub Stars](https://img.shields.io/github/stars/Svndsn/python-servo)
![GitHub Issues](https://img.shields.io/github/issues/Svndsn/python-servo)
![GitHub Forks](https://img.shields.io/github/forks/Svndsn/python-servo)
![Build and Test](https://github.com/Svndsn/python-servo/actions/workflows/test.yml/badge.svg)
![Publish to PyPI](https://github.com/Svndsn/python-servo/actions/workflows/publish.yml/badge.svg)
![Code Size](https://img.shields.io/github/languages/code-size/Svndsn/python-servo)

## Useful Links

- [gpiod Python API Documentation](https://python-gpiod.readthedocs.io/en/latest/)
- [Raspberry Pi GPIO Guide](https://www.raspberrypi.com/documentation/computers/raspberry-pi.html#gpio)
- [Servo Motor Basics](https://learn.sparkfun.com/tutorials/hobby-servo-tutorial/all)

### Servo Class

#### Constructor

```python
Servo(pin, chip="gpiochip4", frequency=50, min_pulse_width=1.0, max_pulse_width=2.0, min_angle=0, max_angle=90)
```

| Parameter         | Type    | Default      | Description                                 |
|-------------------|---------|--------------|---------------------------------------------|
| pin               | int     | required     | GPIO pin number for servo signal            |
| chip              | str     | "gpiochip4" | GPIO chip name                             |
| frequency         | int     | 50           | PWM frequency in Hz                        |
| min_pulse_width   | float   | 1.0          | Minimum pulse width in ms                   |
| max_pulse_width   | float   | 2.0          | Maximum pulse width in ms                   |
| min_angle         | int     | 0            | Minimum servo angle in degrees              |
| max_angle         | int     | 90           | Maximum servo angle in degrees              |

#### Methods

| Method                          | Description                                      |
|----------------------------------|--------------------------------------------------|
| `set_angle(angle)`               | Set specific angle (degrees)                     |
| `set_angle_rad(angle)`           | Set specific angle (radians)                     |
| `center()`                       | Move to center position                          |
| `move_to_min()`                  | Move to minimum angle                            |
| `move_to_max()`                  | Move to maximum angle                            |
| `set_pulse_width(width_ms)`      | Set pulse width directly (ms)                    |
| `set_position_percent(percent)`  | Set position as percentage (0-100%)              |
| `sweep(start, end, duration, steps=50)` | Smooth sweep between angles over duration   |
| `get_current_angle()`            | Returns current angle                            |
| `get_current_pulse_width()`      | Returns current pulse width (ms)                 |
| `get_current_position_percent()` | Returns current position (%)                     |
| `is_running()`                   | Returns True if PWM is active                    |
| `start()`                        | Start PWM signal generation                      |
| `stop()`                         | Stop PWM signal generation                       |
| `cleanup()`                      | Release GPIO resources                           |
| `calibrate(min_pulse, max_pulse)`| Calibrate pulse width range                      |

- Python 3.12.3+
- `gpiod` library (version 2.0+)
- Linux system with GPIO support (Raspberry Pi, etc.)

## Installation

### From PyPI (Recommended)
```bash
pip install python-servo-gpiod
```

### From Source
```bash
git clone https://github.com/Svndsn/python-servo.git
cd python-servo
pip install -e .
```

## Quick Start

```python
from python_servo_gpiod import Servo

# Create and use servo with context manager (recommended)
with Servo(pin=18) as servo:
    servo.set_angle(90)    # Move to 90 degrees
    servo.center()         # Move to center position
    servo.sweep(0, 90, 3) # Sweep from 0 to 90 degrees over 3 seconds

# Manual control
servo = Servo(pin=18)
servo.start()              # Start PWM
servo.set_angle(45)        # Set angle
servo.stop()               # Stop PWM
servo.cleanup()            # Clean up resources
```

## API Reference

### Servo Class

#### Constructor
```python
Servo(pin, chip="gpiochip4", frequency=50, 
      min_pulse_width=1.0, max_pulse_width=2.0, 
      min_angle=0, max_angle=90)
```

**Parameters:**
- `pin`: GPIO pin number for servo signal
- `chip`: GPIO chip (default: "gpiochip4")
- `frequency`: PWM frequency in Hz (default: 50Hz)
- `min_pulse_width`: Minimum pulse width in ms (default: 1.0ms)
- `max_pulse_width`: Maximum pulse width in ms (default: 2.0ms)
- `min_angle`: Minimum servo angle in degrees (default: 0°)
- `max_angle`: Maximum servo angle in degrees (default: 90°)

#### Control Methods

**Angle Control:**
```python
servo.set_angle(angle)              # Set specific angle
servo.center()                      # Move to center position
servo.move_to_min()                 # Move to minimum angle
servo.move_to_max()                 # Move to maximum angle
```

**Pulse Width Control:**
```python
servo.set_pulse_width(width_ms)     # Set pulse width directly (ms)
```

**Percentage Control:**
```python
servo.set_position_percent(percent) # Set position as percentage (0-100%)
```

**Movement Functions:**
```python
servo.sweep(start_angle, end_angle, duration, steps=50)
# Smooth sweep between angles over specified duration
```

#### Status Methods
```python
servo.get_current_angle()           # Returns current angle
servo.get_current_pulse_width()     # Returns current pulse width (ms)
servo.get_current_position_percent() # Returns current position (%)
servo.is_running()                  # Returns True if PWM is active
```

#### PWM Control
```python
servo.start()                       # Start PWM signal generation
servo.stop()                        # Stop PWM signal generation
servo.cleanup()                     # Release GPIO resources
```

#### Calibration
```python
servo.calibrate(min_pulse, max_pulse) # Calibrate pulse width range
```

## Examples

### Basic Usage
```python
from python_servo_gpiod import Servo
import time

# Initialize servo on GPIO pin 18
servo = Servo(pin=18)
servo.start()

# Test different positions
servo.set_angle(0)      # 0 degrees
time.sleep(1)
servo.set_angle(45)     # 45 degrees  
time.sleep(1)
servo.set_angle(90)    # 90 degrees
time.sleep(1)

servo.cleanup()
```

### Custom Servo Configuration
```python
# Configure for a servo with different specifications
servo = Servo(
    pin=20,
    frequency=60,           # 60Hz instead of 50Hz
    min_pulse_width=0.5,    # 0.5ms minimum pulse
    max_pulse_width=2.5,    # 2.5ms maximum pulse
    min_angle=-90,          # -90 to +90 degree range
    max_angle=90
)
```

### Percentage Control
```python
with Servo(pin=18) as servo:
    servo.set_position_percent(0)    # Minimum position
    time.sleep(1)
    servo.set_position_percent(50)   # Center position
    time.sleep(1)
    servo.set_position_percent(100)  # Maximum position
```

### Smooth Sweeping
```python
with Servo(pin=18) as servo:
    # Sweep from 0 to 90 degrees over 5 seconds
    servo.sweep(0, 90, duration=5.0, steps=100)
    
    # Sweep back with fewer steps (less smooth)
    servo.sweep(90, 0, duration=3.0, steps=30)
```

### Calibration for Custom Servos
```python
servo = Servo(pin=18)
# Calibrate for a servo that needs 0.8ms to 2.2ms pulse widths
servo.calibrate(0.8, 2.2)
servo.start()

# Now angle control uses the calibrated pulse widths
servo.set_angle(90)  # Uses 1.5ms pulse width
```

## Testing

### Run Unit Tests
```bash
python test_servo.py --verbose
```

### Hardware Testing
```bash
# WARNING: Only run with real servo connected!
python test_servo.py --hardware
```

### Demo Scripts
```bash
# Simple demonstration
python demo.py simple

# Interactive control
python demo.py interactive

# Performance benchmark
python demo.py benchmark
```

## PWM Signal Details

The servo generates PWM signals with the following characteristics:

- **Default Frequency**: 50Hz (20ms period)
- **Pulse Width Range**: 1.0ms to 2.0ms
- **Resolution**: Limited by Python's `time.sleep()` precision
- **Duty Cycle**: 5% (1ms) to 10% (2ms) at 50Hz

### Timing Calculations
- **0° position**: 1.0ms pulse width (5% duty cycle)
- **45° position**: 1.5ms pulse width (7.5% duty cycle)  
- **90° position**: 2.0ms pulse width (10% duty cycle)

## Thread Safety

The Servo class is thread-safe for concurrent access:
- Multiple threads can safely call angle/position setting methods
- PWM generation runs in a separate daemon thread
- Thread locks protect shared state variables

## Error Handling

The implementation includes comprehensive error handling:

```python
try:
    servo = Servo(pin=18)
    servo.start()
    servo.set_angle(270)  # Invalid angle
except ServoError as e:
    print(f"Servo error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
finally:
    servo.cleanup()
```

Common error conditions:
- GPIO initialization failures
- Invalid angle ranges
- Invalid pulse width values
- PWM already running when starting
- Hardware access permissions

## Hardware Connections

### Standard Servo Connection
```
Servo Wire Colors:
- Red:  +5V power supply
- Brown/Black: Ground (GND)
- Orange: Signal (connect to GPIO pin)
```

## Limitations

1. **Software PWM**: Uses software timing, less precise than hardware PWM
2. **CPU Usage**: PWM generation consumes CPU cycles
3. **Timing Jitter**: Python's threading may introduce small timing variations
4. **Single Servo**: Each instance controls one servo (multiple instances needed for multiple servos)

## Performance

Typical performance characteristics:
- **Command Response**: < 1ms for angle/position changes
- **PWM Frequency**: Stable 50Hz ±1Hz
- **Pulse Width Accuracy**: ±50μs (depending on system load)
- **CPU Usage**: ~1-2% per active servo on Raspberry Pi 5

## License

This project is licensed under the MIT License.

See [LICENSE.md](LICENSE.md) for full license details.

## Contributing

Feel free to submit issues, improvements, or extensions to this servo control implementation.
