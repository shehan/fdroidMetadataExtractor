import os
import glob
import sys
import git
from git import Repo
import yaml
import sqlite3


fdroid_repo_remote = "https://gitlab.com/fdroid/fdroiddata.git"
fdroid_repo_local = 'tmp/fdroid'
fdroid_repo_local_metadata = fdroid_repo_local+'/metadata'
results_output = 'output'
results_output_db_name = 'results.sqlite'
results_output_db_path = results_output+'/' + results_output_db_name

if not os.path.exists(fdroid_repo_local):
    os.makedirs(fdroid_repo_local)

if not os.path.exists(results_output):
    os.makedirs(results_output)

if not os.path.exists(results_output_db_path):
    conn = sqlite3.connect(results_output_db_path)
    c = conn.cursor()
    c.execute('''CREATE TABLE App
        ([Id] INTEGER PRIMARY KEY,[Name] text,[AutoName] text,[WebSite] text,[AuthorName] text,[AuthorEmail] text,[Categories] text,[Repo] text,[Description] text)''')
    conn.commit()


try:
    repo = git.Repo(fdroid_repo_local, search_parent_directories=False)
except git.exc.InvalidGitRepositoryError:
    print('fdroid repo not cloned')
    print('cloning fdroid repo...')
    repo = Repo.clone_from(fdroid_repo_remote, fdroid_repo_local)
    print('fdroid repo cloned')


os.chdir(fdroid_repo_local_metadata)
for file in glob.glob("*.yml"):
    with open(file, 'rt', encoding='utf8') as stream:
        try:
            data = yaml.safe_load(stream)
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
        except yaml.YAMLError as exc:
            print(exc)
        except:
            e = sys.exc_info()[0]
            print(e)
