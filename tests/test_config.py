from core.config import settings

def test_filebase_settings_loaded():
    assert settings.FILEBASE_KEY == "TESTKEY123"
    assert settings.FILEBASE_SECRET == "TESTSECRET456"
    assert settings.FILEBASE_BUCKET == "test-bucket"
