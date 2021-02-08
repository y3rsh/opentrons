"""Functional tests for SimulationHistoryDB class."""

import pytest
from opentrons import APIVersion
from opentrons.protocols.simulation_history import db


@pytest.fixture
def test_database() -> db.SimulationHistoryDB:
    """Test subject."""
    return db.SimulationHistoryDB(":memory:")


def test_all_empty(test_database: db.SimulationHistoryDB) -> None:
    """Should return empty."""
    assert list(test_database.all()) == []


def test_all_returns_inserted(test_database: db.SimulationHistoryDB) -> None:
    """Should return inserted rows."""
    count = 3
    for i in range(count):
        test_database.add(
            name=f"protocol{i}.py",
            author=f"author {i}",
            content_hash=f"abc{i}",
            api_version=f"2.{i}",
            robot_version=f"1.{i}"
        )

    # Read all results and sort by id.
    results = sorted(test_database.all(), key=lambda v: v.id)

    for i in range(count):
        result = results[i]
        assert result.name == f"protocol{i}.py"
        assert result.author == f"author {i}"
        assert result.content_hash == f"abc{i}"
        assert result.api_version == APIVersion(2, i)
        assert result.robot_version == f"1.{i}"


def test_find_finds(test_database: db.SimulationHistoryDB) -> None:
    """Should return matching rows."""
    count = 3
    for i in range(count):
        test_database.add(
            name=f"protocol{i}.py",
            author=f"author {i}",
            content_hash=f"abc{i}",
            api_version=f"2.{i}",
            robot_version=f"1.{i}"
        )

    for i in range(count):
        result = next(test_database.find(
            name=f"protocol{i}.py",
            content_hash=f"abc{i}",
            api_version=f"2.{i}",
            robot_version=f"1.{i}"))
        assert result.name == f"protocol{i}.py"
        assert result.author == f"author {i}"
        assert result.content_hash == f"abc{i}"
        assert result.api_version == APIVersion(2, i)
        assert result.robot_version == f"1.{i}"


def test_find_doesnt_find(test_database: db.SimulationHistoryDB) -> None:
    """Should return no matches."""
    count = 3
    for i in range(count):
        test_database.add(
            name=f"protocol{i}.py",
            author=f"author {i}",
            content_hash=f"abc{i}",
            api_version=f"2.{i}",
            robot_version=f"1.{i}"
        )

    result = list(test_database.find(
            name=f"protocol{i + 1}.py",
            content_hash=f"abc{i}",
            api_version=f"2.{i}",
            robot_version=f"1.{i}"))
    assert result == []

    result = list(test_database.find(
            name=f"protocol{i}.py",
            content_hash=f"abc{i + 1}",
            api_version=f"2.{i}",
            robot_version=f"1.{i}"))
    assert result == []

    result = list(test_database.find(
            name=f"protocol{i}.py",
            content_hash=f"abc{i}",
            api_version=f"2.{i + 1}",
            robot_version=f"1.{i}"))
    assert result == []

    result = list(test_database.find(
        name=f"protocol{i}.py",
        content_hash=f"abc{i}",
        api_version=f"2.{i}",
        robot_version=f"1.{i + 1}"))
    assert result == []
