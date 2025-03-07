#!/usr/bin/python3

#Copyright © 2024, SAS Institute Inc., Cary, NC, USA.  All Rights Reserved.
#SPDX-License-Identifier: Apache-2.0

from sys import stderr
from pathlib import Path
from urllib.parse import urljoin, urlsplit
import argparse, requests, json, os, re

def error(msg1, msg2=None):
  if msg2:
    print(msg1, file=stderr)
    print(f'Error: {msg2}', file=stderr)
  else:
    print(f'Error: {msg1}', file=stderr)
  os._exit(1)

def init():
  global tokens_path, content_path, session
  tokens_path = Path.home() / '.sas' / '.viya_tokens'
  content_path = Path('scr').resolve() / 'content'

  if not content_path.exists():
    error(f'folder "{content_path}" not found')
  requests.packages.urllib3.disable_warnings()
  session = requests.Session()

def parse_url(decision_url):
  global root_url, decision_uri
  UUID_PATTERN = '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'

  parsed = urlsplit(decision_url)
  if not parsed.scheme or not parsed.netloc or not parsed.path:
    print('Please supply a valid URL')
    exit()
  root_url = f'{parsed.scheme}://{parsed.netloc}'.lower()

  match = re.match(f'^/SASDecisionManager/decisions/({UUID_PATTERN})', parsed.path)
  if match:
    decision_uri = f'/decisions/flows/{match.group(1)}'
    return

  match = re.match(f'^/decisions/flows/({UUID_PATTERN})', parsed.path)
  if match:
    decision_uri = f'/decisions/flows/{match.group(1)}'
    return

  # no match
  print('Please supply a valid decision URL')
  exit()

def new_refresh_token():
  print('Open the following link in a web browser and sign in to obtain an authorization code')
  print(urljoin(root_url, '/SASLogon/oauth/authorize?client_id=sas.cli&response_type=code'))
  code = input('Code: ')
  r = session.post(
    urljoin(root_url, '/SASLogon/oauth/token'),
    data    =  f'grant_type=authorization_code&code={code}',
    headers = { 'Content-Type': 'application/x-www-form-urlencoded' },
    auth    = ('sas.cli', ''), 
    verify  = False 
  )
  if not r:
    error(f'HTTP {r.status_code}', r.text)
  refresh_token = r.json()['refresh_token']
  access_token = r.json()['access_token']
  session.headers.update({'Authorization': f'Bearer {access_token}'})
  refresh_tokens[root_url] = refresh_token
  tokens_path.write_text(json.dumps(refresh_tokens, indent=2), encoding='utf-8')
  print(f'Updated refresh_token for {root_url} in {tokens_path}')

def new_access_token():
  r = session.post(
    urljoin(root_url, '/SASLogon/oauth/token'),
    data    = f'grant_type=refresh_token&refresh_token={refresh_token}',
    headers = {'Content-type': 'application/x-www-form-urlencoded'},
    auth    = ('sas.cli', ''),
    verify  = False
  )
  if r:
    access_token = r.json()['access_token']
    session.headers.update({'Authorization': f'Bearer {access_token}'}) 
  else:
    print(f'HTTP {r.status_code}: {r.text}')
    new_refresh_token()

def get_object(uri):
  url = urljoin(root_url, uri)
  r = session.get(url, verify=False)
  if not r:
    error(f'HTTP {r.status_code} on GET {url}', r.text)
  return r.json()

def login():
  global refresh_tokens, refresh_token
  try:
    refresh_tokens = json.loads(tokens_path.read_text(encoding='utf-8'))
  except:
    print(f'Unable to read {tokens_path}')
    refresh_tokens = { }
  refresh_token = refresh_tokens.get(root_url)
  if refresh_token:
    new_access_token()
  else:
    new_refresh_token()
  user_name = get_object('/identities/users/@currentUser')['name']
  print(f'Connected to {root_url} as "{user_name}"')

def get_code():
  global code, root_name

  object_name = get_object(decision_uri)['name']
  root_name = re.sub(r'[^a-z0-9]+', '_', object_name.strip().lower())
  root_name = re.sub('^([0-9])', r'_\1', root_name)
  if root_name=='_': root_name = 'module'
  url = urljoin(root_url, f'{decision_uri}/code')
  params = { 
    'rootPackageName' : root_name,
    'lookupMode': 'PACKAGE',
    'traversedPathFlag': False,
    'isGeneratingRuleFiredColumn': False,
    'codeTarget': 'docker'
  }
  r = session.get(url, params=params, verify=False)
  if not r:
    error(f'HTTP {r.status_code} on GET {url}', r.text)
  code = r.text
  code_path = content_path / 'code.ds2'
  code_path.write_text(code, 'utf-8')
  print(f'Wrote {root_name} code to {code_path}')

def create_module():
  comment_pattern = re.compile(r'^\s*/\*([^*]|(\*+[^*/]))*\*+/\s*$', re.IGNORECASE)
  start_pattern1 = re.compile(r'^\s*package\s+(\w+).*;', re.IGNORECASE)
  start_pattern2 = re.compile(r'^\s*package\s+\"([\w\s]+)\".*;', re.IGNORECASE)
  end_pattern = re.compile(r'^\s*endpackage\s*;', re.IGNORECASE)

  submodules = []
  collecting = False
  root = None
  for line in code.splitlines():
    if re.match(comment_pattern, line):
      continue
    match_start = re.match(start_pattern1, line) or re.match(start_pattern2, line)
    if match_start:
      package_name = match_start.group(1)
      package_code = []
      collecting = True
    if collecting:
      package_code.append(line)
    if re.match(end_pattern, line): 
      collecting = False
      package = {'name': package_name, 'source': '\n'.join(package_code), 'language': 'DS2'}
      if root_name == package_name:
        root = package
      else:
        submodules.append(package)
      package_code = []

  if not root:
    print(f'Root package {root_name} not found', file=stderr)
    exit(1)

  module = {
    'scope': 'PUBLIC',
    'source': root['source'],
    'submodules': submodules
  }
  module_path = content_path / '_module_definition.json'
  module_path.write_text(json.dumps(module, indent=2))
  print(f'Created {module_path}')

def deploy(decision_url):
  init()
  parse_url(decision_url)
  login()
  get_code()
  create_module()

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('decision_url', help='Decision URL, e.g. https://my-viya-host/SASDecisionManager/decisions/64b411ce-a63d-4982-af05-cc2cc76c2be3')
  args = parser.parse_args()
  deploy(args.decision_url)
