import subprocess
from pathlib import Path
import pandas as pd

if __name__ == '__main__':
    pict_settings_1 = Path("input_data\\pict_settings_1.txt")
    pict_case_1 = Path("output_data\\pict_case_1.txt")

    pict_case_1_5 = Path("output_data\\pict_case_1_5.txt")

    pict_settings_2 = Path("input_data\\pict_settings_2.txt")
    pict_case_2 = Path("output_data\\pict_case_2.txt")

    # First PICT case generation
    command = "pict {} /r:0".format(str(pict_settings_1))
    with open(str(pict_case_1), mode="w") as f:
        _ = subprocess.run(command, encoding="utf-8", stdout=f)

    # Add constant factor
    with open(str(pict_case_1), mode="r", encoding="utf-8") as f:
        s = f.read()
    with open(str(pict_case_1_5), mode="w", encoding="utf-8") as f:
        lines = s.split("\n")
        t = ""
        for i, line in enumerate(lines):
            if(len(line) > 0):
                if(i == 0):
                    t += line+"\tナビ\n"
                else:
                    t += line+"\tn\n"
            else:
                t += line
        print(t)
        f.write(t)

    # Second PICT case generation with seed file
    command = "pict {} /r:0 /e:{}".format(
        str(pict_settings_2), str(pict_case_1_5))
    with open(str(pict_case_2), "w") as f:
        _ = subprocess.run(command, encoding="utf-8", stdout=f)

    df1 = pd.read_csv(pict_case_1, encoding="utf-8", delimiter="\t")
    df2 = pd.read_csv(pict_case_2, encoding="utf-8", delimiter="\t")

    print("Combinations in case 1:", len(df1))
    print("Combinations in case 2:", len(df2))
