import os
import glob
import sys
import stat
import argparse
import shutil
import git
from git import Repo
import yaml
import sqlite3


fdroid_repo_remote = "https://gitlab.com/fdroid/fdroiddata.git"
fdroid_repo_local = 'tmp_fdroid'
fdroid_repo_local_metadata = fdroid_repo_local+'/metadata'
results_output = 'output'
results_output_db_name = 'results.sqlite'
results_output_db_path = results_output+'/' + results_output_db_name

parser = argparse.ArgumentParser(description='F-Droid Metadata Extractor')
parser.add_argument('-o', action="store_true", default=False,
                    dest='arg_overwrite', help='Overwrite all data')
args = parser.parse_args()


def remove_readonly(func, path, excinfo):
    os.chmod(path, stat.S_IWRITE)
    func(path)

if args.arg_overwrite:
    if os.path.exists(fdroid_repo_local):
        print('removing fdroid directory...', end ='', flush=True)
        shutil.rmtree(fdroid_repo_local, onerror=remove_readonly)
        print('done')
    if os.path.exists(results_output):
        print('removing output directory...', end ='', flush=True)
        shutil.rmtree(results_output,  onerror=remove_readonly)
        print('done')


if not os.path.exists(fdroid_repo_local):
    print('creating fdroid directory...', end ='', flush=True)
    os.makedirs(fdroid_repo_local)
    print('done')

if not os.path.exists(results_output):
    print('creating output directory...', end ='', flush=True)
    os.makedirs(results_output)
    print('done')

if not os.path.exists(results_output_db_path):
    print('creating empty database...', end ='', flush=True)
    conn = sqlite3.connect(results_output_db_path)
    c = conn.cursor()
    c.execute('''CREATE TABLE App
        ([Id] INTEGER PRIMARY KEY AUTOINCREMENT,[UniqueName] text,[Name] text,[AutoName] text,[WebSite] text,[AuthorName] text,[AuthorEmail] text,[Categories] text,[Repo] text,[SourceCode] text,[RepoType] text,[Changelog] text,[License] text,[IssueTracker] text,[Description] text)''')
    conn.commit()
    conn.close()
    print('done')

try:
    repo = git.Repo(fdroid_repo_local, search_parent_directories=False)
except git.exc.InvalidGitRepositoryError:
    print('cloning fdroid repo...', end ='', flush=True)
    repo = Repo.clone_from(fdroid_repo_remote, fdroid_repo_local)
    print('done')

print('extracting metadata...', end ='', flush=True)
conn = sqlite3.connect(results_output_db_path)
c = conn.cursor()
os.chdir(fdroid_repo_local_metadata)
for file in glob.glob("*.yml"):
    with open(file, 'rt', encoding='utf8') as stream:
        try:
            data = yaml.safe_load(stream)
            data_repotype = data_changelog = data_license = data_issuetracker = data_sourcecode = data_repo = data_autoname = data_name = data_description = data_categories = data_website = data_authorname = data_authoremail = ''
            data_uniquename = file.rsplit(".", 1)[0]
            if 'RepoType' in data:
                data_repotype = data['RepoType']
            if 'Changelog' in data:
                data_changelog = data['Changelog']
            if 'License' in data:
                data_license = data['License']
            if 'IssueTracker' in data:
                data_issuetracker = data['IssueTracker']
            if 'SourceCode' in data:
                data_sourcecode = data['SourceCode']
            if 'Repo' in data:
                data_repo = data['Repo']
            if 'AutoName' in data:
                data_autoname = data['AutoName']
            if 'Name' in data:
                data_name = data['Name']
            if 'Description' in data:
                data_description = data['Description']
            if 'Categories' in data:
                data_categories = data['Categories']
            if 'WebSite' in data:
                data_website = data['WebSite']
            if 'AuthorName' in data:
                data_authorname = data['AuthorName']
            if 'AuthorEmail' in data:
                data_authoremail = data['AuthorEmail']

            c.execute('INSERT INTO App (Repo,AutoName,Name,Description,WebSite,AuthorName,AuthorEmail,SourceCode,IssueTracker,License,Changelog,RepoType,UniqueName,Categories) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?);',
                      (data_repo, data_autoname, data_name, data_description, data_website, data_authorname, data_authoremail, data_sourcecode, data_issuetracker, data_license, data_changelog, data_repotype, data_uniquename, ','.join(data_categories)))
            conn.commit()

        except yaml.YAMLError as exc:
            print(exc)
        except:
            e = sys.exc_info()[0]
            print(e)
conn.close()
print('done')

print('execution completed!')