cd %~dp0
py -c "from lib.condalib import run_from_env; run_from_env([\"conda env update --file environment.yml\"], env=\"sk\", close_after_process=True)"