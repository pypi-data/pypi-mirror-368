import polars as pl
import os
import io
import shutil
import tarfile 
import gzip
from logging import warning 


def create_tardb(tarpath: str) -> None:
    with tarfile.open(tarpath, mode = 'x:gz'):
        return

def list_entries(tarpath: str) -> list[str]:
    with tarfile.open(tarpath, mode = 'r:gz') as tar:
        return [tar.name for tar in tar.getmembers()]

def add_entries(tarpath: str, *files) -> None:

    # Uncompress
    temp_tar = tarpath.rstrip('.gz')
    with gzip.open(tarpath, 'rb') as f_in, open(temp_tar, 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)

    members = list_entries(tarpath)
    # Add the new entry
    with tarfile.open(temp_tar, 'a') as tar:
        for file in files:
            # TODO not robust to .csv.gzip?
            if ".csv" not in file:
                warning(f"File must be a csv, tryig to upload [{file}] skipping it")
                continue 

            member_name = os.path.basename(file).rstrip(".csv")
            if member_name in members:
                warning(f"File [{file}] would be a duplicate of exisiting entry [{member_name}] use delete_entry or pick a new memeber name")
                continue

            encoded = pl.read_csv(file).write_csv().encode('utf8')
            tar_info = tarfile.TarInfo(name = member_name)
            tar_info.size = len(encoded)
            tar.addfile(tar_info, io.BytesIO(encoded))
    
    # Re-compress
    with open(temp_tar, 'rb') as f_in, gzip.open(tarpath, 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)
    
    os.remove(temp_tar)

def delete_entry(tarpath: str, file):
    temp_tar_path = tarpath + '.temp'
    with tarfile.open(tarpath, 'r:gz') as tar, tarfile.open(temp_tar_path, 'w:gz') as new_tar:
        for member in tar.getmembers():
            # TODO not robust to .csv.gzip?
            if '.csv' in file:
                ignore_member =  os.path.basename(file).rstrip(".csv")
            else:
                ignore_member = file

            if member.name != ignore_member:
                new_tar.addfile(member, tar.extractfile(member))

    os.replace(temp_tar_path, tarpath)

def get_entry(tarpath: str, entry: str) -> pl.DataFrame:
    with tarfile.open(tarpath, mode = 'r:gz') as tar:
        file = tar.extractfile(entry)
        return pl.read_csv(file)
