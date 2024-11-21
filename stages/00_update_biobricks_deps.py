import os
import shutil
import subprocess

# Clean up and initialize biobricks
shutil.rmtree('.bb', ignore_errors=True)
subprocess.run('biobricks init && biobricks add pubchem-annotations', shell=True)
