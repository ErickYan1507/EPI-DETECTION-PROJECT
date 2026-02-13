
class MockResult:
    def __init__(self):
        self.training_time_seconds = None

result = MockResult()
try:
    print(f"Time: {result.training_time_seconds or 0:.1f}")
    print("Success for None")
except Exception as e:
    print(f"Error for None: {e}")

result.training_time_seconds = 10.5
try:
    print(f"Time: {result.training_time_seconds or 0:.1f}")
    print("Success for 10.5")
except Exception as e:
    print(f"Error for 10.5: {e}")
