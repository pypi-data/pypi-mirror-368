#!/usr/bin/env python3
"""
Generate screenshots for momovu documentation.

This script automates the process of:
1. Running momovu with various configurations
2. Taking screenshots of different states
3. Saving them for inclusion in Sphinx documentation

Requires Debian/Ubuntu with X11 tools:
- xdotool (for window management and keyboard automation)
- imagemagick (for window-specific screenshots)
"""

import argparse
import atexit
import logging
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Global list to track running processes for cleanup
running_processes: list[subprocess.Popen] = []

# Screenshot output directory
SCREENSHOT_DIR = Path("docs/_source/_static/screenshots")

# Screenshot scenarios based on usage.rst examples
SCENARIOS = [
    # Basic usage examples
    {
        "id": "basic-usage",
        "description": "Basic momovu window with interior PDF",
        "cmd": ["momovu", "samples/bovary-interior.pdf"],
        "wait": 3.0,
        "goto_page": 27,  # Better content page
        "keys": ["f5"],  # Enter presentation mode after navigation
        "wait_after_keys": 1.0,
        "filename": "basic-usage.png",
        "rst_file": "usage.rst",
        "rst_section": "Quick Start",
        "rst_after_line": 17,
    },
    {
        "id": "cover-with-spine",
        "description": "Cover document showing spine width calculation",
        "cmd": ["momovu", "-d", "cover", "-n", "180", "samples/quixote-cover.pdf"],
        "wait": 3.0,
        "keys": ["ctrl+0", "f5"],  # Fit page then presentation mode
        "wait_after_keys": 1.0,
        "filename": "cover-spine.png",
        "rst_file": "usage.rst",
        "rst_section": "Cover Documents",
        "rst_after_line": 197,
    },
    {
        "id": "side-by-side",
        "description": "Interior pages in side-by-side view",
        "cmd": ["momovu", "-s", "samples/bovary-interior.pdf"],
        "wait": 3.0,
        "goto_page": 43,  # Better content page
        "keys": ["ctrl+0", "f5"],  # Fit page then presentation mode
        "wait_after_keys": 1.0,
        "filename": "side-by-side.png",
        "rst_file": "usage.rst",
        "rst_section": "Side-by-Side View",
        "rst_after_line": 260,
    },
    # Document type examples
    {
        "id": "interior-single",
        "description": "Interior document in single page view",
        "cmd": ["momovu", "-d", "interior", "samples/pingouins-interior.pdf"],
        "wait": 3.0,
        "goto_page": 15,
        "keys": ["f5"],  # Enter presentation mode after navigation
        "wait_after_keys": 1.0,
        "filename": "interior-single.png",
        "rst_file": "usage.rst",
        "rst_section": "Interior Documents",
        "rst_after_line": 183,
    },
    {
        "id": "dustjacket",
        "description": "Dustjacket with flaps and fold lines",
        "cmd": [
            "momovu",
            "-d",
            "dustjacket",
            "-n",
            "574",
            "samples/pingouins-dustjacket.pdf",
        ],
        "wait": 3.0,
        "keys": ["ctrl+0", "f5"],  # Fit page then presentation mode
        "wait_after_keys": 1.0,
        "filename": "dustjacket.png",
        "rst_file": "usage.rst",
        "rst_section": "Dustjacket Documents",
        "rst_after_line": 217,
    },
    # Visual overlay examples
    {
        "id": "trim-lines",
        "description": "Trim lines overlay enabled",
        "cmd": [
            "momovu",
            "-d",
            "cover",
            "-n",
            "100",
            "--no-safety-margins",
            "--no-fold-lines",
            "--no-barcode",
            "samples/siddhartha-cover.pdf",
        ],
        "wait": 3.0,
        "keys": ["ctrl+0", "f5"],  # Fit page then presentation mode
        "wait_after_keys": 1.0,
        "filename": "overlay-trim-lines.png",
        "rst_file": "usage.rst",
        "rst_section": "Trim Lines",
        "rst_after_line": 284,
    },
    {
        "id": "safety-margins",
        "description": "Safety margins overlay enabled",
        "cmd": [
            "momovu",
            "-d",
            "cover",
            "-n",
            "126",
            "--no-trim-lines",
            "--no-fold-lines",
            "--no-barcode",
            "samples/lovecraft-cover.pdf",
        ],
        "wait": 3.0,
        "keys": ["ctrl+0", "f5"],  # Fit page then presentation mode
        "wait_after_keys": 1.0,
        "filename": "overlay-safety-margins.png",
        "rst_file": "usage.rst",
        "rst_section": "Safety Margins",
        "rst_after_line": 274,
    },
    {
        "id": "spine-lines",
        "description": "Spine/fold lines overlay enabled",
        "cmd": [
            "momovu",
            "-d",
            "cover",
            "-n",
            "442",
            "--no-trim-lines",
            "--no-safety-margins",
            "--no-barcode",
            "samples/vatican-cover.pdf",
        ],
        "wait": 3.0,
        "keys": ["ctrl+0", "f5"],  # Fit page then presentation mode
        "wait_after_keys": 1.0,
        "filename": "overlay-spine-lines.png",
        "rst_file": "usage.rst",
        "rst_section": "Spine/Fold Lines",
        "rst_after_line": 305,
    },
    {
        "id": "barcode-area",
        "description": "Barcode area overlay enabled",
        "cmd": [
            "momovu",
            "-d",
            "cover",
            "-n",
            "574",
            "--no-trim-lines",
            "--no-safety-margins",
            "--no-fold-lines",
            "samples/pingouins-cover.pdf",
        ],
        "wait": 3.0,
        "keys": ["ctrl+0", "f5"],  # Fit page then presentation mode
        "wait_after_keys": 1.0,
        "filename": "overlay-barcode.png",
        "rst_file": "usage.rst",
        "rst_section": "Barcode Area",
        "rst_after_line": 316,
    },
    {
        "id": "all-overlays",
        "description": "All overlays enabled simultaneously",
        "cmd": ["momovu", "-d", "cover", "-n", "688", "samples/bovary-cover.pdf"],
        "wait": 3.0,
        "keys": [
            "ctrl+0",
            "f5",
        ],  # Fit page then presentation mode - overlays are already enabled by default
        "wait_after_keys": 1.0,
        "filename": "overlay-all.png",
        "rst_file": "usage.rst",
        "rst_section": "Visual Overlays",
        "rst_after_line": 268,
    },
    # View modes
    {
        "id": "presentation-mode",
        "description": "Presentation mode (fullscreen, no UI)",
        "cmd": ["momovu", "-s", "samples/bovary-interior.pdf"],  # Side-by-side
        "wait": 3.0,
        "goto_page": 30,
        "keys": ["alt+v"],  # Open View menu
        "wait_after_keys": 0.5,
        "keys2": ["p"],  # Select Presentation Mode
        "wait_after_keys2": 2.0,  # Wait for presentation mode
        "filename": "presentation-mode.png",
        "rst_file": "usage.rst",
        "rst_section": "Presentation Mode",
        "rst_after_line": 234,
    },
    {
        "id": "fullscreen-mode",
        "description": "Fullscreen mode (maximized window)",
        "cmd": ["momovu", "samples/bovary-interior.pdf"],
        "wait": 3.0,
        "goto_page": 20,
        "keys": ["F11"],
        "wait_after_keys": 1.0,
        "filename": "fullscreen-mode.png",
        "rst_file": "usage.rst",
        "rst_section": "Fullscreen Mode",
        "rst_after_line": 249,
    },
    {
        "id": "zoomed-in",
        "description": "Zoomed in view",
        "cmd": ["momovu", "samples/bovary-interior.pdf"],
        "wait": 3.0,
        "goto_page": 35,
        "keys": ["ctrl+equal", "ctrl+equal", "ctrl+equal", "ctrl+equal"],  # Zoom in 4x
        "presentation_mode": False,  # Keep menu visible to show zoom controls
        "filename": "zoomed-in.png",
        "rst_file": "usage.rst",
        "rst_section": "View Controls",
        "rst_after_line": 94,
    },
    # Dialog examples
    # Dialog examples - removed goto-page-dialog due to rendering issues
    # Additional feature demonstrations
    {
        "id": "cover-clean",
        "description": "Cover document without overlays",
        "cmd": [
            "momovu",
            "-d",
            "cover",
            "-n",
            "688",
            "--no-trim-lines",
            "--no-safety-margins",
            "--no-fold-lines",
            "--no-barcode",
            "samples/bovary-cover.pdf",
        ],
        "wait": 3.0,
        "keys": ["ctrl+0", "f5"],  # Fit page then presentation mode
        "wait_after_keys": 1.0,
        "filename": "cover-clean.png",
        "rst_file": "features.rst",
        "rst_section": "Document Types",
        "rst_after_line": 50,
    },
    {
        "id": "cover-with-margins",
        "description": "Cover showing safety margins only",
        "cmd": [
            "momovu",
            "-d",
            "cover",
            "-n",
            "126",
            "--no-trim-lines",
            "--no-fold-lines",
            "--no-barcode",
            "samples/lovecraft-cover.pdf",
        ],
        "wait": 3.0,
        "keys": ["ctrl+0"],  # Fit page - keep toolbar visible for this one
        "filename": "cover-margins.png",
        "rst_file": "features.rst",
        "rst_section": "Safety Margins",
        "rst_after_line": 100,
    },
    {
        "id": "dustjacket-with-trim",
        "description": "Dustjacket showing trim lines and fold lines",
        "cmd": [
            "momovu",
            "-d",
            "dustjacket",
            "-n",
            "574",
            "--no-safety-margins",
            "--no-barcode",
            "samples/pingouins-dustjacket.pdf",
        ],
        "wait": 3.0,
        "keys": ["ctrl+0", "f5"],  # Fit page then presentation mode
        "wait_after_keys": 1.0,
        "filename": "dustjacket-trim-fold.png",
        "rst_file": "features.rst",
        "rst_section": "Trim and Fold Lines",
        "rst_after_line": 150,
    },
    {
        "id": "interior-with-margins",
        "description": "Interior pages showing safety margins",
        "cmd": ["momovu", "-s", "--no-trim-lines", "samples/pingouins-interior.pdf"],
        "wait": 3.0,
        "goto_page": 50,
        "keys": ["ctrl+0", "f5"],  # Fit page then presentation mode
        "wait_after_keys": 1.0,
        "filename": "interior-margins.png",
        "rst_file": "features.rst",
        "rst_section": "Interior Margins",
        "rst_after_line": 200,
    },
    # New screenshots for index.rst and about.rst
    {
        "id": "showcase-index",
        "description": "Momovu showcasing dustjacket with all features",
        "cmd": [
            "momovu",
            "-d",
            "dustjacket",
            "-n",
            "574",
            "samples/pingouins-dustjacket.pdf",
        ],
        "wait": 3.0,
        "keys": ["ctrl+0"],  # Fit to page first
        "presentation_mode": False,  # Show toolbar
        "filename": "showcase-index.png",
        "rst_file": "index.rst",
        "rst_section": "Front page",
        "rst_after_line": 10,
    },
    {
        "id": "showcase-about",
        "description": "Momovu showcasing cover with overlays",
        "cmd": ["momovu", "-d", "cover", "-n", "100", "samples/siddhartha-cover.pdf"],
        "wait": 3.0,
        "keys": ["ctrl+0"],  # Fit to page
        "presentation_mode": False,  # Show toolbar
        "filename": "showcase-about.png",
        "rst_file": "about.rst",
        "rst_section": "About page",
        "rst_after_line": 10,
    },
    {
        "id": "zoomed-margin-detail",
        "description": "Zoomed view showing margin detail on cover",
        "cmd": ["momovu", "-d", "cover", "-n", "100", "samples/siddhartha-cover.pdf"],
        "wait": 3.0,
        "keys": [
            "ctrl+m",
            "ctrl+equal",
            "ctrl+equal",
            "ctrl+equal",
            "ctrl+equal",
            "ctrl+equal",
            "f5",
        ],  # Margins + zoom in 5x + presentation
        "wait_after_keys": 1.0,
        "filename": "zoomed-margin-detail.png",
        "rst_file": "features.rst",
        "rst_section": "Zoom Features",
        "rst_after_line": 250,
    },
]


def cleanup_processes():
    """Ensure all processes are terminated on exit."""
    for proc in running_processes:
        if proc.poll() is None:  # Still running
            logger.info(f"Terminating process {proc.pid}")
            proc.terminate()
            try:
                proc.wait(timeout=2)
            except subprocess.TimeoutExpired:
                logger.warning(f"Force killing process {proc.pid}")
                proc.kill()
                proc.wait()
    running_processes.clear()


def setup_cleanup_handlers():
    """Register cleanup handlers for graceful exit."""
    atexit.register(cleanup_processes)
    signal.signal(signal.SIGINT, lambda _s, _f: (cleanup_processes(), sys.exit(0)))
    signal.signal(signal.SIGTERM, lambda _s, _f: (cleanup_processes(), sys.exit(0)))


def check_dependencies() -> bool:
    """Check if required system tools are available."""
    required_tools = ["xdotool", "import", "wmctrl"]
    missing_tools = []

    for tool in required_tools:
        if not shutil.which(tool):
            missing_tools.append(tool)

    if missing_tools:
        logger.error(f"Missing required tools: {', '.join(missing_tools)}")
        logger.error("Install with: sudo apt-get install xdotool imagemagick wmctrl")
        return False

    return True


def find_window_id(window_title: str, max_attempts: int = 10) -> Optional[str]:
    """Find window ID by title using xdotool."""
    for attempt in range(max_attempts):
        try:
            result = subprocess.run(
                ["xdotool", "search", "--name", window_title],
                capture_output=True,
                text=True,
                check=False,
            )

            if result.returncode == 0 and result.stdout.strip():
                window_ids = result.stdout.strip().split("\n")
                # Return the most recent window (last in list)
                return window_ids[-1]

        except subprocess.SubprocessError as e:
            logger.error(f"Error finding window: {e}")

        if attempt < max_attempts - 1:
            time.sleep(0.5)

    return None


def activate_window(window_id: str) -> bool:
    """Activate (focus) a window by ID."""
    try:
        subprocess.run(
            ["xdotool", "windowactivate", window_id], check=True, capture_output=True
        )
        time.sleep(0.2)  # Give window time to activate
        return True
    except subprocess.CalledProcessError:
        return False


def send_keys(keys: list[str]) -> None:
    """Send keyboard shortcuts using xdotool."""
    for key_combo in keys:
        try:
            # xdotool uses + for key combinations, not space
            subprocess.run(
                ["xdotool", "key", key_combo], check=True, capture_output=True
            )
            time.sleep(0.5)  # Wait between key combinations
        except subprocess.CalledProcessError as e:
            logger.error(f"Error sending keys '{key_combo}': {e}")


def goto_page(page_number: int) -> None:
    """Navigate to a specific page using Ctrl+G dialog."""
    try:
        # Open goto page dialog
        subprocess.run(["xdotool", "key", "ctrl+g"], check=True, capture_output=True)
        time.sleep(1.0)  # Wait for dialog to fully open

        # Clear existing text with triple-click to select all
        subprocess.run(
            ["xdotool", "click", "--repeat", "3", "1"], check=True, capture_output=True
        )
        time.sleep(0.2)

        # Type the page number
        subprocess.run(
            ["xdotool", "type", str(page_number)], check=True, capture_output=True
        )
        time.sleep(0.3)

        # Press Enter to navigate
        subprocess.run(["xdotool", "key", "Return"], check=True, capture_output=True)
        time.sleep(1.5)  # Wait for page to load

    except subprocess.CalledProcessError as e:
        logger.error(f"Error navigating to page {page_number}: {e}")


def take_window_screenshot(window_id: str, output_path: Path) -> bool:
    """Take screenshot of specific window using ImageMagick's import."""
    try:
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Take screenshot using import
        subprocess.run(
            ["import", "-window", window_id, str(output_path)],
            check=True,
            capture_output=True,
        )

        # Verify file was created
        if output_path.exists():
            logger.info(f"Screenshot saved: {output_path}")
            return True
        else:
            logger.error(f"Screenshot file not created: {output_path}")
            return False

    except subprocess.CalledProcessError as e:
        logger.error(f"Error taking screenshot: {e}")
        return False


def capture_scenario(scenario: dict[str, Any], output_dir: Path) -> bool:
    """Capture a screenshot for a given scenario."""
    logger.info(f"Processing scenario: {scenario['id']} - {scenario['description']}")

    # Launch momovu
    try:
        proc = subprocess.Popen(scenario["cmd"])
        running_processes.append(proc)

        # Wait for window to appear
        logger.info(f"Waiting {scenario['wait']}s for window to appear...")
        time.sleep(scenario["wait"])

        # Find window
        window_id = find_window_id("Momovu")
        if not window_id:
            logger.error("Could not find Momovu window")
            return False

        logger.info(f"Found Momovu window: {window_id}")

        # Activate window
        if not activate_window(window_id):
            logger.warning("Could not activate window, continuing anyway")

        # Navigate to specific page if specified
        if "goto_page" in scenario:
            logger.info(f"Navigating to page {scenario['goto_page']}")
            goto_page(scenario["goto_page"])

        # Send keyboard shortcuts if specified
        if "keys" in scenario:
            logger.info(f"Sending keys: {scenario['keys']}")
            send_keys(scenario["keys"])

            # Additional wait after keys if specified
            if "wait_after_keys" in scenario:
                time.sleep(scenario["wait_after_keys"])
            else:
                time.sleep(0.5)  # Default wait after keys

        # Send second set of keys if specified (for menu navigation)
        if "keys2" in scenario:
            logger.info(f"Sending keys2: {scenario['keys2']}")
            send_keys(scenario["keys2"])

            # Additional wait after keys2 if specified
            if "wait_after_keys2" in scenario:
                time.sleep(scenario["wait_after_keys2"])
            else:
                time.sleep(0.5)  # Default wait after keys

        # Note: presentation mode is now handled via -p command line flag

        # Take screenshot
        output_path = output_dir / scenario["filename"]
        success = take_window_screenshot(window_id, output_path)

        if success:
            logger.info(f"✓ Successfully captured: {scenario['id']}")
        else:
            logger.error(f"✗ Failed to capture: {scenario['id']}")

        return success

    except Exception as e:
        logger.error(f"Error in scenario {scenario['id']}: {e}")
        return False

    finally:
        # Clean up process
        if proc in running_processes:
            running_processes.remove(proc)
        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=2)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate screenshots for momovu documentation"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=SCREENSHOT_DIR,
        help="Output directory for screenshots",
    )
    parser.add_argument(
        "--scenarios", nargs="+", help="Specific scenario IDs to capture (default: all)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without actually doing it",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Setup cleanup handlers
    setup_cleanup_handlers()

    # Check dependencies
    if not check_dependencies():
        sys.exit(1)

    # Filter scenarios if specific ones requested
    scenarios_to_run = SCENARIOS
    if args.scenarios:
        scenarios_to_run = [s for s in SCENARIOS if s["id"] in args.scenarios]
        if not scenarios_to_run:
            logger.error(f"No matching scenarios found for: {args.scenarios}")
            sys.exit(1)

    # Dry run - just show what would be done
    if args.dry_run:
        logger.info("DRY RUN - No screenshots will be taken")
        logger.info(f"Would create directory: {args.output_dir}")
        for scenario in scenarios_to_run:
            logger.info(f"Would capture: {scenario['id']} -> {scenario['filename']}")
        logger.info(f"Total scenarios: {len(scenarios_to_run)}")
        return

    # Create output directory
    args.output_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"Output directory: {args.output_dir}")

    # Capture screenshots
    successful = 0
    failed = 0

    for scenario in scenarios_to_run:
        if capture_scenario(scenario, args.output_dir):
            successful += 1
        else:
            failed += 1

        # Small delay between scenarios
        time.sleep(1)

    # Summary
    logger.info("\nSummary:")
    logger.info(f"  Successful: {successful}")
    logger.info(f"  Failed: {failed}")
    logger.info(f"  Total: {len(scenarios_to_run)}")

    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
