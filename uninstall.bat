cd %~dp0
py -c "from lib.condalib import run_from_env; run_from_env([\"conda remove -n sk --all\"], env=\"base\", close_after_process=True)"