"""
Test suite for the Servo class.

This module contains comprehensive tests for the servo control functionality
including unit tests, integration tests, and mock hardware tests.

Author: GPIO Servo Test Suite
Date: August 8, 2025
"""

import unittest
import time
import threading
from unittest.mock import Mock, MagicMock, patch, call
import sys
import os

# Add the parent directory to the path to import the servo module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from servo import Servo, ServoError
except ImportError:
    # Fallback for when running as a package
    from .servo import Servo, ServoError


class MockGpiodLine:
    """Mock gpiod Line for testing."""
    def __init__(self):
        self.value = 0
        self.requested = False
        self.consumer = None
        self.request_type = None
        
    def request(self, consumer, type):
        self.requested = True
        self.consumer = consumer
        self.request_type = type
        
    def set_value(self, value):
        self.value = value
        
    def release(self):
        self.requested = False


class MockGpiodChip:
    """Mock gpiod Chip for testing."""
    def __init__(self, path):
        self.path = path
        self.lines = {}
        self.closed = False
        
    def get_line(self, pin):
        if pin not in self.lines:
            self.lines[pin] = MockGpiodLine()
        return self.lines[pin]
        
    def close(self):
        self.closed = True


class TestServoInitialization(unittest.TestCase):
    """Test servo initialization and basic functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        import gpiod
        if not hasattr(gpiod, 'LINE_REQ_DIR_OUT'):
                gpiod.LINE_REQ_DIR_OUT = 0
        self.chip_patcher = patch('servo.gpiod.Chip', MockGpiodChip)
        self.chip_patcher.start()
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.chip_patcher.stop()
    
    def test_default_initialization(self):
        """Test servo initialization with default parameters."""
        servo = Servo(pin=18)
        
        self.assertEqual(servo.pin, 18)
        self.assertEqual(servo.frequency, 50)
        self.assertEqual(servo.min_pulse_width, 1.0)
        self.assertEqual(servo.max_pulse_width, 2.0)
        self.assertEqual(servo.min_angle, 0)
        self.assertEqual(servo.max_angle, 90)
        self.assertEqual(servo.period, 0.02)  # 1/50 Hz
        self.assertEqual(servo.period_ms, 20)
        self.assertFalse(servo.running)
        
        servo.cleanup()
    
    def test_custom_initialization(self):
        """Test servo initialization with custom parameters."""
        servo = Servo(
            pin=20,
            frequency=60,
            min_pulse_width=0.5,
            max_pulse_width=2.5,
            min_angle=-90,
            max_angle=90
        )
        
        self.assertEqual(servo.pin, 20)
        self.assertEqual(servo.frequency, 60)
        self.assertEqual(servo.min_pulse_width, 0.5)
        self.assertEqual(servo.max_pulse_width, 2.5)
        self.assertEqual(servo.min_angle, -90)
        self.assertEqual(servo.max_angle, 90)
        self.assertAlmostEqual(servo.period, 1/60, places=5)
        
        servo.cleanup()
    
    def test_gpio_initialization_failure(self):
        """Test handling of GPIO initialization failure."""
        with patch('servo.gpiod.Chip', side_effect=Exception("GPIO not available")):
            with self.assertRaises(ServoError) as context:
                Servo(pin=18)
            self.assertIn("Failed to initialize GPIO pin 18", str(context.exception))


class TestServoAngleControl(unittest.TestCase):
    """Test servo angle control functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        import gpiod
        if not hasattr(gpiod, 'LINE_REQ_DIR_OUT'):
                gpiod.LINE_REQ_DIR_OUT = 0
        self.chip_patcher = patch('servo.gpiod.Chip', MockGpiodChip)
        self.chip_patcher.start()
        self.servo = Servo(pin=18)
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.servo.cleanup()
        self.chip_patcher.stop()
    
    def test_set_angle_valid_range(self):
        """Test setting angles within valid range."""
        test_angles = [0, 22.5, 45, 67.5, 90]
        
        for angle in test_angles:
            self.servo.set_angle(angle)
            self.assertEqual(self.servo.get_current_angle(), angle)
    
    def test_set_angle_invalid_range(self):
        """Test setting angles outside valid range."""
        invalid_angles = [-10, 100, -1, 91]
        
        for angle in invalid_angles:
            with self.assertRaises(ServoError):
                self.servo.set_angle(angle)
    
    def test_angle_to_pulse_width_conversion(self):
        """Test conversion from angle to pulse width."""
        # Test extremes
        self.servo.set_angle(0)
        self.assertAlmostEqual(self.servo.get_current_pulse_width(), 1.0, places=3)
        
        self.servo.set_angle(90)
        self.assertAlmostEqual(self.servo.get_current_pulse_width(), 2.0, places=3)
        
        # Test middle
        self.servo.set_angle(45)
        self.assertAlmostEqual(self.servo.get_current_pulse_width(), 1.5, places=3)
    
    def test_center_position(self):
        """Test center position functionality."""
        self.servo.center()
        self.assertEqual(self.servo.get_current_angle(), 45)
        self.assertAlmostEqual(self.servo.get_current_pulse_width(), 1.5, places=3)
    
    def test_min_max_positions(self):
        """Test minimum and maximum position methods."""
        self.servo.move_to_min()
        self.assertEqual(self.servo.get_current_angle(), 0)
        
        self.servo.move_to_max()
        self.assertEqual(self.servo.get_current_angle(), 90)


class TestServoPulseWidthControl(unittest.TestCase):
    """Test servo pulse width control functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        import gpiod
        if not hasattr(gpiod, 'LINE_REQ_DIR_OUT'):
                gpiod.LINE_REQ_DIR_OUT = 0
        self.chip_patcher = patch('servo.gpiod.Chip', MockGpiodChip)
        self.chip_patcher.start()
        self.servo = Servo(pin=18)
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.servo.cleanup()
        self.chip_patcher.stop()
    
    def test_set_pulse_width_valid_range(self):
        """Test setting pulse width within valid range."""
        test_pulse_widths = [0.5, 1.0, 1.5, 2.0, 2.5]
        
        for pw in test_pulse_widths:
            self.servo.set_pulse_width(pw)
            self.assertAlmostEqual(self.servo.get_current_pulse_width(), pw, places=3)
    
    def test_set_pulse_width_invalid_range(self):
        """Test setting pulse width outside valid range."""
        invalid_pulse_widths = [-1, 25, 30]  # Beyond 20ms period
        
        for pw in invalid_pulse_widths:
            with self.assertRaises(ServoError):
                self.servo.set_pulse_width(pw)
    
    def test_pulse_width_to_angle_conversion(self):
        """Test conversion from pulse width to angle."""
        self.servo.set_pulse_width(1.0)
        self.assertEqual(self.servo.get_current_angle(), 0)
        
        self.servo.set_pulse_width(2.0)
        self.assertEqual(self.servo.get_current_angle(), 90)
        
        self.servo.set_pulse_width(1.5)
        self.assertEqual(self.servo.get_current_angle(), 45)


class TestServoPercentageControl(unittest.TestCase):
    """Test servo percentage control functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        import gpiod
        if not hasattr(gpiod, 'LINE_REQ_DIR_OUT'):
                gpiod.LINE_REQ_DIR_OUT = 0
        self.chip_patcher = patch('servo.gpiod.Chip', MockGpiodChip)
        self.chip_patcher.start()
        self.servo = Servo(pin=18)
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.servo.cleanup()
        self.chip_patcher.stop()
    
    def test_set_position_percent_valid_range(self):
        """Test setting position by percentage within valid range."""
        test_percentages = [0, 25, 50, 75, 100]
        expected_angles = [0, 22.5, 45, 67.5, 90]
        
        for percent, expected_angle in zip(test_percentages, expected_angles):
            self.servo.set_position_percent(percent)
            self.assertEqual(self.servo.get_current_angle(), expected_angle)
            self.assertAlmostEqual(self.servo.get_current_position_percent(), percent, places=1)
    
    def test_set_position_percent_invalid_range(self):
        """Test setting position by percentage outside valid range."""
        invalid_percentages = [-10, 110, -1, 101]
        
        for percent in invalid_percentages:
            with self.assertRaises(ServoError):
                self.servo.set_position_percent(percent)


class TestServoPWMControl(unittest.TestCase):
    """Test servo PWM control functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        import gpiod
        if not hasattr(gpiod, 'LINE_REQ_DIR_OUT'):
                gpiod.LINE_REQ_DIR_OUT = 0
        self.chip_patcher = patch('servo.gpiod.Chip', MockGpiodChip)
        self.chip_patcher.start()
        self.servo = Servo(pin=18)
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.servo.cleanup()
        self.chip_patcher.stop()
    
    def test_start_stop_pwm(self):
        """Test starting and stopping PWM."""
        self.assertFalse(self.servo.is_running())
        
        self.servo.start()
        self.assertTrue(self.servo.is_running())
        
        self.servo.stop()
        self.assertFalse(self.servo.is_running())
    
    def test_double_start_error(self):
        """Test that starting PWM twice raises an error."""
        self.servo.start()
        
        with self.assertRaises(ServoError):
            self.servo.start()
        
        self.servo.stop()
    
    def test_stop_when_not_running(self):
        """Test that stopping PWM when not running doesn't raise error."""
        self.servo.stop()  # Should not raise an error
    
    @patch('time.sleep')
    def test_pwm_signal_generation(self, mock_sleep):
        """Test PWM signal generation timing."""
        self.servo.set_pulse_width(1.5)  # 1.5ms pulse width
        self.servo.start()
        
        # Give the thread a moment to start
        time.sleep(0.1)
        
        # Stop and check that sleep was called with correct timing
        self.servo.stop()
        
        # Should have calls for high and low periods
        # High period: 1.5ms = 0.0015s
        # Low period: 20ms - 1.5ms = 18.5ms = 0.0185s
        expected_calls = [call(0.0015), call(0.0185)]
        
        # Check if any of the sleep calls match our expected timing
        sleep_calls = mock_sleep.call_args_list
        high_time_found = any(abs(call_args.args[0] - 0.0015) < 0.0001 for call_args in sleep_calls)
        low_time_found = any(abs(call_args.args[0] - 0.0185) < 0.001 for call_args in sleep_calls)
        
        self.assertTrue(high_time_found, "High time sleep call not found")
        self.assertTrue(low_time_found, "Low time sleep call not found")


class TestServoSweep(unittest.TestCase):
    """Test servo sweep functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        import gpiod
        if not hasattr(gpiod, 'LINE_REQ_DIR_OUT'):
                gpiod.LINE_REQ_DIR_OUT = 0
        self.chip_patcher = patch('servo.gpiod.Chip', MockGpiodChip)
        self.chip_patcher.start()
        self.servo = Servo(pin=18)
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.servo.cleanup()
        self.chip_patcher.stop()
    
    def test_sweep_not_running_error(self):
        """Test that sweep fails when PWM is not running."""
        with self.assertRaises(ServoError):
            self.servo.sweep(0, 90, 1.0)
    
    @patch('time.sleep')
    def test_sweep_timing(self, mock_sleep):
        """Test sweep timing and angle progression."""
        self.servo.start()
        
        # Perform sweep
        self.servo.sweep(0, 90, duration=1.0, steps=10)
        
        # Check final position
        self.assertEqual(self.servo.get_current_angle(), 90)
        
        # Should have exactly 10 calls to sleep (steps = 10)
        # Each step should be 1.0/10 = 0.1 seconds
        expected_sleep_calls = [call(0.1)] * 10
        actual_sleep_calls = [call for call in mock_sleep.call_args_list if call.args[0] == 0.1]
        
        self.assertEqual(len(actual_sleep_calls), 10)
        
        self.servo.stop()


class TestServoCalibration(unittest.TestCase):
    """Test servo calibration functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        import gpiod
        if not hasattr(gpiod, 'LINE_REQ_DIR_OUT'):
                gpiod.LINE_REQ_DIR_OUT = 0
        self.chip_patcher = patch('servo.gpiod.Chip', MockGpiodChip)
        self.chip_patcher.start()
        self.servo = Servo(pin=18)
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.servo.cleanup()
        self.chip_patcher.stop()
    
    def test_calibrate_valid_range(self):
        """Test calibration with valid pulse width range."""
        self.servo.calibrate(0.5, 2.5)
        
        self.assertEqual(self.servo.min_pulse_width, 0.5)
        self.assertEqual(self.servo.max_pulse_width, 2.5)
    
    def test_calibrate_invalid_range(self):
        """Test calibration with invalid pulse width range."""
        # Min >= Max
        with self.assertRaises(ServoError):
            self.servo.calibrate(2.0, 1.0)
        
        # Negative values
        with self.assertRaises(ServoError):
            self.servo.calibrate(-1.0, 2.0)
        
        # Beyond period
        with self.assertRaises(ServoError):
            self.servo.calibrate(1.0, 25.0)


class TestServoContextManager(unittest.TestCase):
    """Test servo context manager functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        import gpiod
        if not hasattr(gpiod, 'LINE_REQ_DIR_OUT'):
                gpiod.LINE_REQ_DIR_OUT = 0
        self.chip_patcher = patch('servo.gpiod.Chip', MockGpiodChip)
        self.chip_patcher.start()
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.chip_patcher.stop()
    
    def test_context_manager(self):
        """Test using servo as context manager."""
        with Servo(pin=18) as servo:
            self.assertTrue(servo.is_running())
            servo.set_angle(45)
            self.assertEqual(servo.get_current_angle(), 45)
        
        # After context, servo should be stopped and cleaned up
        self.assertFalse(servo.is_running())


class TestServoThreadSafety(unittest.TestCase):
    """Test servo thread safety."""
    
    def setUp(self):
        """Set up test fixtures."""
        import gpiod
        if not hasattr(gpiod, 'LINE_REQ_DIR_OUT'):
                gpiod.LINE_REQ_DIR_OUT = 0
        self.chip_patcher = patch('servo.gpiod.Chip', MockGpiodChip)
        self.chip_patcher.start()
        self.servo = Servo(pin=18)
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.servo.cleanup()
        self.chip_patcher.stop()
    
    def test_concurrent_angle_setting(self):
        """Test concurrent angle setting from multiple threads."""
        self.servo.start()
        
        angles = [0, 22.5, 45, 67.5, 90]
        threads = []
        
        def set_angle_worker(angle):
            self.servo.set_angle(angle)
            time.sleep(0.1)
        
        # Start multiple threads setting different angles
        for angle in angles:
            thread = threading.Thread(target=set_angle_worker, args=(angle,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Servo should be in one of the valid angles
        final_angle = self.servo.get_current_angle()
        self.assertIn(final_angle, angles)
        
        self.servo.stop()


def run_hardware_test():
    """
    Hardware test function for real servo testing.
    This should only be run when connected to actual hardware.
    """
    print("Hardware Test Mode")
    print("=================")
    print("WARNING: This will control a real servo motor!")
    print("Make sure your servo is properly connected to GPIO pin 18.")
    
    response = input("Continue with hardware test? (y/N): ")
    if response.lower() != 'y':
        print("Hardware test cancelled.")
        return
    
    try:
        print("Starting hardware test...")
        
        with Servo(pin=18) as servo:
            print("Servo started. Testing basic movements...")
            
            # Test basic positions
            positions = [
                ("Center", 45),
                ("Minimum", 0),
                ("Maximum", 90),
                ("Quarter", 22.5),
                ("Three-quarter", 67.5)
            ]
            
            for name, angle in positions:
                print(f"Moving to {name} ({angle}°)...")
                servo.set_angle(angle)
                time.sleep(2)
            
            # Test sweep
            print("Performing sweep test...")
            servo.sweep(0, 90, 3.0)
            servo.sweep(90, 0, 3.0)
            
            # Test percentage control
            print("Testing percentage control...")
            for percent in [0, 25, 50, 75, 100]:
                print(f"Setting to {percent}%...")
                servo.set_position_percent(percent)
                time.sleep(1)
            
            print("Hardware test completed successfully!")
            
    except Exception as e:
        print(f"Hardware test failed: {e}")


def main():
    """Main test runner."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Servo Test Suite')
    parser.add_argument('--hardware', action='store_true', 
                       help='Run hardware test (requires real servo)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose test output')
    
    args = parser.parse_args()
    
    if args.hardware:
        run_hardware_test()
        return
    
    # Run unit tests
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestServoInitialization,
        TestServoAngleControl,
        TestServoPulseWidthControl,
        TestServoPercentageControl,
        TestServoPWMControl,
        TestServoSweep,
        TestServoCalibration,
        TestServoContextManager,
        TestServoThreadSafety
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    verbosity = 2 if args.verbose else 1
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    
    # Print summary
    print(f"\nTest Summary:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    # Return appropriate exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    exit(main())
