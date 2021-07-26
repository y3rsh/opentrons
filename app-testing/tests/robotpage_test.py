"""Tests for privacy toggle."""
from applitools.images.eyes import Eyes
import pytest

from src.ot_application import OtApplication
from src.ot_robot import OtRobot


def test_robot_page(
    eyes: Eyes, ot_application: OtApplication, request: pytest.FixtureRequest
) -> None:
    """Make sure that when the docker robot is runing we can see details about it"""
    # make sure analytics in the right state
    ot_application.config["analytics"]["optedIn"] = False
    ot_application.write_config()
    # check that a robot is running
    robot: OtRobot = OtRobot()
    assert robot.is_alive(), "is a robot available?"
