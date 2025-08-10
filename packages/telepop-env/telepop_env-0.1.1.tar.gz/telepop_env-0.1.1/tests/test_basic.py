from telepop_env import env

def test_env_str(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("NAME=Ivan\n")
    e = env.__class__(env_file)  # create new instance
    assert e.str("NAME") == "Ivan"
