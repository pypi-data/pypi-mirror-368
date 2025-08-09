"""
Servo Control Module using gpiod for PWM signal generation.

This module provides a Servo class for controlling servo motors using GPIO pins
with software-generated PWM signals via the gpiod library.

Author: GPIO Servo Controller
Date: August 8, 2025
"""

import time
import threading
import gpiod
import math
if not hasattr(gpiod, 'LINE_REQ_DIR_OUT'):
    gpiod.LINE_REQ_DIR_OUT = 0
from typing import Optional, Union


class ServoError(Exception):
    """Custom exception for servo-related errors."""
    pass


class Servo:
    """
    A class to control servo motors using gpiod PWM signals.
    
    Standard servo motors typically use a 20ms period (50Hz frequency) with
    pulse widths ranging from 1ms (0 degrees) to 2ms (180 degrees).
    """
    
    # Default servo parameters
    DEFAULT_FREQUENCY = 50  # Hz (20ms period)
    DEFAULT_MIN_PULSE_WIDTH = 1.0  # ms (0 degrees)
    DEFAULT_MAX_PULSE_WIDTH = 2.0  # ms (180 degrees)
    DEFAULT_MIN_ANGLE = 0  # degrees
    DEFAULT_MAX_ANGLE = 90  # degrees
    
    def __init__(self, 
                 pin: int,
                 chip: str = "gpiochip4",
                 frequency: float = DEFAULT_FREQUENCY,
                 min_pulse_width: float = DEFAULT_MIN_PULSE_WIDTH,
                 max_pulse_width: float = DEFAULT_MAX_PULSE_WIDTH,
                 min_angle: float = DEFAULT_MIN_ANGLE,
                 max_angle: float = DEFAULT_MAX_ANGLE):
        """
        Initialize the servo controller.
        
        Args:
            pin: GPIO pin number for the servo signal
            chip: GPIO chip (default: "gpiochip4")
            frequency: PWM frequency in Hz (default: 50Hz)
            min_pulse_width: Minimum pulse width in ms (default: 1.0ms)
            max_pulse_width: Maximum pulse width in ms (default: 2.0ms)
            min_angle: Minimum servo angle in degrees (default: 0)
            max_angle: Maximum servo angle in degrees (default: 90)
        """
        self.pin = pin
        self.chip_name = chip
        self.frequency = frequency
        self.min_pulse_width = min_pulse_width
        self.max_pulse_width = max_pulse_width
        self.min_angle = min_angle
        self.max_angle = max_angle
        
        # Calculate period from frequency
        self.period = 1.0 / frequency  # seconds
        self.period_ms = self.period * 1000  # milliseconds
        
        # GPIO and threading control
        self.chip: Optional[gpiod.Chip] = None
        self.line: Optional[gpiod.Chip.get_line] = None
        self.pwm_thread: Optional[threading.Thread] = None
        self.running = False
        self.current_pulse_width = 1.5  # ms (center position)
        self.current_angle = (min_angle + max_angle) / 2
        
        # Thread safety
        self._lock = threading.Lock()
        
        # Initialize GPIO
        self._initialize_gpio()
    
    def _initialize_gpio(self):
        """Initialize the GPIO chip and line."""
        try:
            self.chip = gpiod.Chip(self.chip_name)
            self.line = self.chip.get_line(self.pin)
            self.line.request(consumer="servo_pwm", type=gpiod.LINE_REQ_DIR_OUT)
        except Exception as e:
            raise ServoError(f"Failed to initialize GPIO pin {self.pin}: {e}")
    
    def _pwm_worker(self):
        """Worker thread for generating PWM signal."""
        while self.running:
            with self._lock:
                pulse_width = self.current_pulse_width
            
            # Calculate duty cycle
            high_time = pulse_width / 1000.0  # Convert to seconds
            low_time = self.period - high_time
            
            # Ensure valid timing
            if high_time > self.period:
                high_time = self.period
                low_time = 0
            elif high_time < 0:
                high_time = 0
                low_time = self.period
            
            # Generate PWM signal
            if high_time > 0:
                self.line.set_value(1)
                time.sleep(high_time)
            
            if low_time > 0 and self.running:
                self.line.set_value(0)
                time.sleep(low_time)
    
    def start(self):
        """Start PWM signal generation."""
        if self.running:
            raise ServoError("Servo is already running")
        
        self.running = True
        self.pwm_thread = threading.Thread(target=self._pwm_worker, daemon=True)
        self.pwm_thread.start()
    
    def stop(self):
        """Stop PWM signal generation."""
        if not self.running:
            return
        
        self.running = False
        if self.pwm_thread:
            self.pwm_thread.join(timeout=1.0)
        
        # Ensure pin is low
        if self.line:
            self.line.set_value(0)
    
    def set_pulse_width(self, pulse_width_ms: float):
        """
        Set the pulse width directly in milliseconds.
        
        Args:
            pulse_width_ms: Pulse width in milliseconds
        """
        if not (0 <= pulse_width_ms <= self.period_ms):
            raise ServoError(f"Pulse width must be between 0 and {self.period_ms}ms")
        
        with self._lock:
            self.current_pulse_width = pulse_width_ms
            # Update current angle based on pulse width
            self.current_angle = self._pulse_width_to_angle(pulse_width_ms)
    
    def set_angle(self, angle: float):
        """
        Set the servo angle in degrees.
        
        Args:
            angle: Target angle in degrees
        """
        if not (self.min_angle <= angle <= self.max_angle):
            raise ServoError(f"Angle must be between {self.min_angle} and {self.max_angle} degrees")
        
        pulse_width = self._angle_to_pulse_width(angle)
        
        with self._lock:
            self.current_pulse_width = pulse_width
            self.current_angle = angle
    
    def set_angle_rad(self, angle_rad: float):
        """
        Set the servo angle in radians.
        
        Args:
            angle_rad: Target angle in radians
        """
        angle_deg = angle_rad * (180.0 / math.pi)  # Convert radians to degrees
        self.set_angle(angle_deg)
    
    def set_position_percent(self, percent: float):
        """
        Set servo position as a percentage (0-100%).
        
        Args:
            percent: Position percentage (0% = min_angle, 100% = max_angle)
        """
        if not (0 <= percent <= 100):
            raise ServoError("Percentage must be between 0 and 100")
        
        angle = self.min_angle + (percent / 100.0) * (self.max_angle - self.min_angle)
        self.set_angle(angle)
    
    def sweep(self, start_angle: float, end_angle: float, duration: float, steps: int = 50):
        """
        Sweep the servo from start_angle to end_angle over the specified duration.
        
        Args:
            start_angle: Starting angle in degrees
            end_angle: Ending angle in degrees
            duration: Total sweep duration in seconds
            steps: Number of intermediate steps
        """
        if not self.running:
            raise ServoError("Servo must be started before sweeping")
        
        step_delay = duration / steps
        angle_step = (end_angle - start_angle) / (steps - 1) if steps > 1 else 0
        
        for i in range(steps):
            if steps == 1:
                angle = end_angle
            else:
                angle = start_angle + (i * angle_step)
            self.set_angle(angle)
            time.sleep(step_delay)
    
    def center(self):
        """Move servo to center position."""
        center_angle = (self.min_angle + self.max_angle) / 2
        self.set_angle(center_angle)
    
    def move_to_min(self):
        """Move servo to minimum angle position."""
        self.set_angle(self.min_angle)
    
    def move_to_max(self):
        """Move servo to maximum angle position."""
        self.set_angle(self.max_angle)
    
    def get_current_angle(self) -> float:
        """Get the current servo angle."""
        with self._lock:
            return self.current_angle
    
    def get_current_pulse_width(self) -> float:
        """Get the current pulse width in milliseconds."""
        with self._lock:
            return self.current_pulse_width
    
    def get_current_position_percent(self) -> float:
        """Get the current position as a percentage."""
        angle = self.get_current_angle()
        return ((angle - self.min_angle) / (self.max_angle - self.min_angle)) * 100
    
    def _angle_to_pulse_width(self, angle: float) -> float:
        """Convert angle to pulse width in milliseconds."""
        ratio = (angle - self.min_angle) / (self.max_angle - self.min_angle)
        pulse_width = self.min_pulse_width + ratio * (self.max_pulse_width - self.min_pulse_width)
        return pulse_width
    
    def _pulse_width_to_angle(self, pulse_width: float) -> float:
        """Convert pulse width to angle in degrees."""
        ratio = (pulse_width - self.min_pulse_width) / (self.max_pulse_width - self.min_pulse_width)
        angle = self.min_angle + ratio * (self.max_angle - self.min_angle)
        return angle
    
    def calibrate(self, min_pulse: float, max_pulse: float):
        """
        Calibrate the servo by setting custom pulse width ranges.
        
        Args:
            min_pulse: Minimum pulse width in milliseconds
            max_pulse: Maximum pulse width in milliseconds
        """
        if min_pulse >= max_pulse:
            raise ServoError("Minimum pulse width must be less than maximum")
        
        if min_pulse < 0 or max_pulse > self.period_ms:
            raise ServoError(f"Pulse widths must be between 0 and {self.period_ms}ms")
        
        self.min_pulse_width = min_pulse
        self.max_pulse_width = max_pulse
    
    def is_running(self) -> bool:
        """Check if the servo PWM is currently running."""
        return self.running
    
    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()
        self.cleanup()
    
    def cleanup(self):
        """Clean up GPIO resources."""
        self.stop()
        if self.line:
            self.line.release()
        if self.chip:
            self.chip.close()
    
    def __del__(self):
        """Destructor to ensure cleanup."""
        self.cleanup()


def main():
    """Example usage of the Servo class."""
    print("Servo Control Example")
    print("===================")
    
    try:
        # Create servo instance (using GPIO pin 18)
        servo = Servo(pin=18, frequency=50, max_angle=90)
        
        print(f"Servo initialized on pin {servo.pin}")
        print(f"Frequency: {servo.frequency}Hz")
        print(f"Pulse width range: {servo.min_pulse_width}-{servo.max_pulse_width}ms")
        print(f"Angle range: {servo.min_angle}-{servo.max_angle} degrees")
        
        # Start PWM
        servo.start()
        print("\nPWM started. Beginning servo demonstration...")
        servo.calibrate(min_pulse=1.0, max_pulse=2.0)
        servo.move_to_min()
        time.sleep(1)
        
        # Center position
        print("\n1. Moving to center position...")
        servo.center()
        time.sleep(2)
        
        # Move to minimum position
        print("2. Moving to minimum position...")
        servo.move_to_min()
        time.sleep(2)
        
        # Move to maximum position
        print("3. Moving to maximum position...")
        servo.move_to_max()
        time.sleep(2)
        
        # Set specific angles
        print("4. Testing specific angles...")
        for angle in [22.5, 45, 67.5]:
            print(f"   Setting angle to {angle} degrees")
            servo.set_angle(angle)
            print(f"   Current angle: {servo.get_current_angle():.1f}°")
            print(f"   Current pulse width: {servo.get_current_pulse_width():.2f}ms")
            time.sleep(1.5)
        
        # Percentage control
        print("5. Testing percentage control...")
        for percent in [25, 50, 75]:
            print(f"   Setting position to {percent}%")
            servo.set_position_percent(percent)
            print(f"   Current position: {servo.get_current_position_percent():.1f}%")
            time.sleep(1.5)
        
        # Sweep demonstration
        print("6. Performing sweep from 0° to 90°...")
        servo.sweep(0, 90, duration=3.0, steps=30)
        
        print("7. Performing reverse sweep from 90° to 0°...")
        servo.sweep(90, 0, duration=3.0, steps=30)
        
        # Return to min
        print("8. Returning to min...")
        servo.move_to_min()
        time.sleep(1)
        
        print("\nDemonstration complete!")
        
    except ServoError as e:
        print(f"Servo error: {e}")
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        if 'servo' in locals():
            servo.cleanup()
        print("Servo cleanup completed.")


if __name__ == "__main__":
    main()
