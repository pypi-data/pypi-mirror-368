"""Test EZBak errors."""

import pytest

from ezbak import ezbak


def test_no_name(filesystem):
    """Test EZBak errors."""
    src_dir, dest1, _ = filesystem
    with pytest.raises(TypeError, match="required positional argument"):
        ezbak(
            # name="test",
            source_paths=[src_dir],
            storage_paths=[dest1],
        )


def test_source_paths(filesystem):
    """Test EZBak errors."""
    _, dest1, _ = filesystem
    backup_manager = ezbak(
        name="test",
        source_paths=[],
        storage_paths=[dest1],
    )
    with pytest.raises(ValueError, match="No source paths provided"):
        backup_manager.create_backup()


def test_source_paths_not_found(filesystem):
    """Test EZBak errors."""
    src_dir, dest1, _ = filesystem

    backup_manager = ezbak(
        name="test",
        source_paths=[src_dir / "not_found"],
        storage_paths=[dest1],
    )
    with pytest.raises(ValueError, match="Source does not exis"):
        backup_manager.create_backup()


def test_source_paths_symlink(tmp_path, clean_stderr, debug):
    """Test EZBak errors."""
    dest_dir = tmp_path / "dest"
    dest_dir.mkdir()
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    (src_dir / "file.txt").touch()
    (src_dir / "symlink").symlink_to(src_dir / "file.txt")

    backup_manager = ezbak(
        name="test",
        source_paths=[src_dir / "symlink"],
        storage_paths=[dest_dir],
    )
    with pytest.raises(ValueError, match="Not a file or directory"):
        backup_manager.create_backup()


def test_storage_paths(filesystem):
    """Test EZBak errors."""
    src_dir, _, _ = filesystem
    with pytest.raises(ValueError, match="No local storage paths provided "):
        ezbak(
            name="test",
            source_paths=[src_dir],
            storage_paths=[],
        )


def test_create_storage_path_dir(filesystem):
    """Test EZBak errors."""
    src_dir, dest1, _ = filesystem

    new_dest = dest1 / "new_dir"
    assert not new_dest.exists()

    backup_manager = ezbak(
        name="test",
        source_paths=[src_dir],
        storage_paths=[new_dest],
    )
    backup_manager.create_backup()

    assert new_dest.exists()
    assert new_dest.is_dir()


def test_restore_no_dest(filesystem, tmp_path, debug, clean_stderr):
    """Test EZBak errors."""
    src_dir, dest1, _ = filesystem

    backup_manager = ezbak(
        name="test",
        source_paths=[src_dir],
        storage_paths=[dest1],
    )
    with pytest.raises(ValueError, match="Restore destination does not exist"):
        backup_manager.restore_backup(tmp_path / "new_dest")


def test_restore_dest_not_dir(filesystem, tmp_path, debug, clean_stderr):
    """Test EZBak errors."""
    src_dir, dest1, _ = filesystem

    new_dest = dest1 / "file.txt"
    new_dest.touch()

    backup_manager = ezbak(
        name="test",
        source_paths=[src_dir],
        storage_paths=[dest1],
    )
    backup_manager.create_backup()
    with pytest.raises(ValueError, match="Restore destination does not exist"):
        backup_manager.restore_backup(new_dest)


def test_restore_no_backup(filesystem, tmp_path, debug, clean_stderr):
    """Test EZBak errors."""
    src_dir, dest1, _ = filesystem

    backup_manager = ezbak(
        name="test",
        source_paths=[src_dir],
        storage_paths=[dest1],
        log_level="DEBUG",
    )
    # backup_manager.create_backup()
    assert not backup_manager.restore_backup(tmp_path)
    output = clean_stderr()
    # debug(output)
    assert "ERROR    | No backup found to restore" in output


def test_no_restore_destination(filesystem, tmp_path, debug, clean_stderr):
    """Test EZBak errors."""
    src_dir, dest1, _ = filesystem

    backup_manager = ezbak(
        name="test",
        source_paths=[src_dir],
        storage_paths=[dest1],
    )
    with pytest.raises(ValueError, match="Invalid destination: None"):
        backup_manager.restore_backup(None)
