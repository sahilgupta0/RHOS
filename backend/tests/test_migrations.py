from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.core.migration_runner import MigrationRunner


@pytest.mark.asyncio
async def test_discover_migrations():
    """Test discovering and sorting migration scripts."""
    runner = MigrationRunner(migrations_dir=Path("/mock/dir"))

    with patch("os.listdir") as mock_list, patch("os.path.exists", return_value=True):
        mock_list.return_value = [
            "0002_add_index.py",
            "0001_initial.py",
            "not_a_migration.py",
            "0003_another_one.txt",
        ]

        discovered = runner._discover_migrations()
        assert len(discovered) == 2
        assert discovered[0] == ("0001", "0001_initial.py")
        assert discovered[1] == ("0002", "0002_add_index.py")


@pytest.mark.asyncio
async def test_run_upgrades_no_pending():
    """Test upgrades when all migrations are already applied."""
    runner = MigrationRunner(migrations_dir=Path("/mock/dir"))

    mock_db = MagicMock()
    mock_history = AsyncMock()
    # Mock finding version in history -> returns document (meaning already applied)
    mock_history.find_one.return_value = {"_id": "0001", "filename": "0001_initial.py"}
    mock_db.__getitem__.return_value = mock_history

    with patch("os.listdir") as mock_list, patch(
        "os.path.exists", return_value=True
    ), patch("app.core.migration_runner.get_mongodb_db", return_value=mock_db):
        mock_list.return_value = ["0001_initial.py"]

        applied = await runner.run_upgrades()
        assert len(applied) == 0
        mock_history.find_one.assert_called_once_with({"_id": "0001"})
        assert mock_history.insert_one.call_count == 0


@pytest.mark.asyncio
async def test_run_upgrades_success():
    """Test successful migration upgrades."""
    runner = MigrationRunner(migrations_dir=Path("/mock/dir"))

    mock_db = MagicMock()
    mock_history = AsyncMock()
    # Migration is pending (not in history)
    mock_history.find_one.return_value = None
    mock_db.__getitem__.return_value = mock_history

    mock_migration_module = MagicMock()
    mock_migration_module.upgrade = AsyncMock()

    with patch("os.listdir") as mock_list, patch(
        "os.path.exists", return_value=True
    ), patch(
        "app.core.migration_runner.get_mongodb_db", return_value=mock_db
    ), patch.object(
        runner, "_load_migration_module", return_value=mock_migration_module
    ):

        mock_list.return_value = ["0001_initial.py"]

        applied = await runner.run_upgrades()
        assert applied == ["0001"]
        mock_migration_module.upgrade.assert_called_once_with(mock_db)
        assert mock_history.insert_one.call_count == 1
