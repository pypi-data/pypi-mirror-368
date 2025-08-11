import pandas as pd
import sys
from lib import WorkbookManager

def read_args():
    """
    Чтение аргументов из командной строки
    Результат:
    ----------
    Словарь с параметрами
    """

    params = {}

    new_argv = sys.argv[1:5]

    for i in range(0, len(new_argv)):
        arg = new_argv[i].split('=')
        
        if len(arg) > 1:
            params[arg[0].replace('\"', '')] = arg[1].replace('\"', '')

    return params


if __name__ == "__main__":
    # аргументы
    params = read_args()

    # имена файлов
    filenames = sys.argv[5:]


    dfMeta = pd.read_csv(params['META_NAME'], sep=params["SEP"], dtype="str").fillna("")

    wm = WorkbookManager()

    wm.transform(
        meta_data=dfMeta.to_dict(orient='records'), 
        separator=params["SEP"], 
        output_path=params["OUTPUT_NAME"]
    )