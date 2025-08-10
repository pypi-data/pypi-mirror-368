from setuptools import setup

required = [
    'boto3>=1.9',
    'requests>=2,<3',
    'requests-cache>=1,<2',
    'PyJWT>=1.7.1,<2',
    'requests-jwt>=0.4,<1',
    'simplejson>=3',
]

# Get current version
with open("CURRENT_VERSION.txt") as f:
    current_version = f.read().strip()

setup(name='nw_connections',
      version=current_version,
      description='Shared Marple python modules',
      url='http://github.com/marple-newsrobot/newsworthy-py-connections',
      author='Journalism Robotics Stockholm',
      author_email='contact@newsworthy.se',
      license='MIT',
      packages=['nw_connections'],
      include_package_data=True,
      install_requires=required,
      zip_safe=False)
