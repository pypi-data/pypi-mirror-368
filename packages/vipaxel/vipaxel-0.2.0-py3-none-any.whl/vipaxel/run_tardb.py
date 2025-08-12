import argparse
from . import tar_database  as tardb

def tardb_create():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i','--input', type = str, help = 'path to store the tardb')
    args = parser.parse_args()
    tardb.create_tardb(args.input)


def tardb_print_entries():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i','--input', type = str, help = 'path to store the tardb')
    args = parser.parse_args()
    print(tardb.list_entries(args.input))


def tardb_add_entries():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', type = str, help = 'path to store the tardb')
    parser.add_argument('-el', '--entrylist', nargs='+', help = 'list of entries to add')
    args = parser.parse_args()
    tardb.add_entries(args.input, *args.entrylist)


def tardb_delete_entry():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i' '--input', type = str, help = 'path to store the tardb')
    parser.add_argument('-e', '--entry', type = str, help = 'entry to delete')
    args = parser.parse_args()
    tardb.add_entries(args.input, args.entry)


def tardb_print_entry():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', type = str, help = 'path to store the tardb')
    parser.add_argument('-e', '--entry', type = str, help = 'entry to print (in full)')
    args = parser.parse_args()
    print(tardb.get_entry(args.input, args.entry))
