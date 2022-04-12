from datetime import datetime
import io
import json
import os
from pathlib import Path
import subprocess

import click
from fpdf import FPDF
import pandas as pd

# ----------------------------------------------------------------------------


def prepare_data(dir_path):
    """ Prepare data for analysis """
    files_list = list(Path(dir_path).rglob("[!._]*.*"))
    files_df = pd.DataFrame(files_list, columns=["file_path"])
    files_df["file_name"] = files_df["file_path"].apply(lambda x: x.name)
    files_df["file_size"] = files_df["file_path"].apply(lambda x: x.stat().st_size)
    files_df["file_ext"] = files_df["file_path"].apply(lambda x: x.suffix)
    files_df["file_dir"] = files_df["file_path"].apply(lambda x: x.parent)
    return files_df


def to_datetime(unix_timestamp):
    """ Converts a unix timestamp to a datetime object. """
    return datetime.utcfromtimestamp(unix_timestamp).strftime("%Y-%m-%d %H:%M:%S")


def get_file_metadata(file_path: str) -> dict:
    """ Returns a dictionary with the metadata of a file. """
    stats = os.stat(file_path)
    stats_dict = {
        "filename": file_path.name,
        "file_size": stats[6],
        "last_access": to_datetime(stats[7]),
        "last_modification": to_datetime(stats[8]),
        "os_metadata": to_datetime(stats[9]),
    }
    return stats_dict


def directory_report(dir_path: str) -> pd.DataFrame:
    """ Returns a dataframe with the metadata of all files in a directory. """
    files_list = list(Path(dir_path).rglob("*.*"))
    files_metadata = [get_file_metadata(file_path) for file_path in files_list]
    df = pd.DataFrame(files_metadata)
    return df


def string2pdf(string, save_path):
    """ Converts a string to a pdf file. """
    lines = string.splitlines()
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 10)
    for line in lines:
        pdf.cell(200, 5, txt=line, ln=1, align="L")
    pdf.output(save_path, "F")


def image_metadata(file_path: str, return_json=True) -> dict:
    """ Returns a dictionary with the metadata of an image. """
    if return_json:
        exifdata = subprocess.run(
            ["exiftool", file_path, "-json"], stdout=subprocess.PIPE
        )
        string_io = io.StringIO(exifdata.stdout.decode("utf-8"))
        return json.load(string_io)[0]
    else:
        exifdata = subprocess.run(["exiftool", file_path], stdout=subprocess.PIPE)
        string_io = io.StringIO(exifdata.stdout.decode("utf-8"))
        return string_io.read()


def images_report(dir_path: str, save_path: str):
    """ Returns a dataframe with the metadata of all images in a directory. """
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    files_list = list(Path(dir_path).rglob("[!._]*"))
    for file_path in files_list:
        try:
            string2pdf(
                image_metadata(file_path, return_json=False),
                f"{save_path}/{file_path.name}.pdf",
            )
        except:
            print(f"Error reading: {file_path}")


# ----------------------------------------------------------------------------


@click.command()
@click.option("--file", help="Input file", type=str)
@click.option("--dir", help="Input file", type=str)
@click.option("--print", help="Input file", type=bool, default=False)
def main(**kwargs):
    """
    Get file metadata
    """
    pass
