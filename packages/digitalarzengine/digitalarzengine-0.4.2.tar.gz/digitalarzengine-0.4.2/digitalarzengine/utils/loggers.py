import os
import traceback
from datetime import datetime
import inspect


class DALogger:
    ANSI_COLORS = {
        "DEBUG": "\033[96m",    # Cyan
        "INFO": "\033[94m",     # Blue
        "WARNING": "\033[93m",  # Yellow
        "ERROR": "\033[91m",    # Red
        "SUCCESS": "\033[92m",  # Green
        "RESET": "\033[0m",
    }

    LEVEL_ORDER = {
        "DEBUG": 10,
        "INFO": 20,
        "SUCCESS": 25,
        "WARNING": 30,
        "ERROR": 40,
        "CRITICAL": 50,
    }

    def __init__(self, name="DALogger", enabled=True, trim_length=300,
                 min_level="DEBUG", log_to_file=False, log_file_path="app.log"):
        self.name = name
        self.enabled = enabled
        self.trim_length = trim_length
        self.min_level = min_level
        self.log_to_file = log_to_file
        self.log_file_path = log_file_path

    def _log(self, level: str, label: str, message: str, show_location=False, trim=True):
        if not self.enabled:
            return
        if self.LEVEL_ORDER.get(level, 0) < self.LEVEL_ORDER.get(self.min_level, 0):
            return

        color = self.ANSI_COLORS.get(level, "")
        reset = self.ANSI_COLORS["RESET"]
        location = self._get_location() if show_location else ""
        timestamp = datetime.now().strftime("[%H:%M:%S] ")

        if trim and len(message) > self.trim_length:
            message = message[:self.trim_length] + "..."

        output = f"{color}{timestamp}[{label}] {location}{message}{reset}"

        try:
            print(output)
        except UnicodeEncodeError:
            print(f"{timestamp}[{label}] {location}{message}")  # fallback for non-UTF terminals

        if self.log_to_file:
            try:
                with open(self.log_file_path, "a", encoding="utf-8") as f:
                    f.write(f"{timestamp}[{label}] {location}{message}\n")
            except Exception:
                pass  # Silent fail to avoid interrupting main app

    def _get_location(self):
        frame = inspect.currentframe()
        outer = inspect.getouterframes(frame)[3]  # Caller of public method
        filename = os.path.basename(outer.filename)
        line_number = outer.lineno
        return f"{filename}:{line_number} - "

    def debug(self, message: str, trim=True):
        self._log("DEBUG", "🐛 DEBUG", message, show_location=True, trim=trim)

    def info(self, message: str, trim=True):
        self._log("INFO", "ℹ️  INFO", message, trim=trim)

    def success(self, message: str, trim=True):
        self._log("SUCCESS", "✅ SUCCESS", message, trim=trim)

    def warning(self, message: str, trim=True):
        self._log("WARNING", "⚠️  WARNING", message, show_location=True, trim=trim)

    def error(self, message: str, trim=False):
        self._log("ERROR", "❌ ERROR", message, show_location=True, trim=trim)

    def critical(self, message: str, trim=False):
        self._log("CRITICAL", "🔥 CRITICAL", message, show_location=True, trim=trim)

    def exception(self, message: str = "An exception occurred"):
        tb = traceback.format_exc()
        full_message = f"{message}\n{tb}"
        self._log("ERROR", "💥 EXCEPTION", full_message, show_location=True, trim=False)
