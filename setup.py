from setuptools import find_packages, setup
from glob import glob
import os

package_name = 'gentact_descriptions_hybrid'

# Function to recursively get all files in a directory
def get_data_files_recursive(base_dir, target_dir):
    files = []
    for root, dirs, filenames in os.walk(base_dir):
        for filename in filenames:
            file_path = os.path.join(root, filename)
            # Calculate the relative path from base_dir
            rel_path = os.path.relpath(file_path, base_dir)
            # Create the target path
            target_path = os.path.join(target_dir, rel_path)
            files.append((os.path.dirname(target_path), [file_path]))
    return files

# Build data_files list
data_files = [
    ('share/ament_index/resource_index/packages',
        ['resource/' + package_name]),
    ('share/' + package_name, ['package.xml']),
    (os.path.join('share', package_name, 'launch'), glob('launch/*')),
    (os.path.join('share', package_name, 'config'), glob('config/*')),
]
data_files.extend(get_data_files_recursive('meshes', os.path.join('share', package_name, 'meshes')))
data_files.extend(get_data_files_recursive('urdf', os.path.join('share', package_name, 'urdf')))
data_files.extend(get_data_files_recursive('robots', os.path.join('share', package_name, 'robots')))
data_files.extend(get_data_files_recursive('end_effectors', os.path.join('share', package_name, 'end_effectors')))

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=data_files,
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='carson',
    maintainer_email='carson.kohlbrenner@gmail.com',
    description='URDF and launch files for custom robots with skin units',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
        ],
    },
)
