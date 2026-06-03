from pathlib import Path


def test_backend_foundation_files_exist() -> None:
    root = Path(__file__).resolve().parents[1]

    expected = [
        "app/main.py",
        "app/core/config.py",
        "app/core/database.py",
        "app/core/security.py",
        "app/features/auth/router.py",
        "app/features/auth/service.py",
        "app/features/agents/seed.py",
        "app/models.py",
    ]

    for relative_path in expected:
        assert (root / relative_path).exists()

