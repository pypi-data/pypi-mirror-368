import os
import shutil

# Remove previous build
if os.path.exists('dist'):
  shutil.rmtree('dist')

if os.path.exists('layrz_sdk.egg-info'):
  shutil.rmtree('layrz_sdk.egg-info')

os.system('python -m build')
os.system('python -m twine upload dist/*')
