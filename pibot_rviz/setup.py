from setuptools import find_packages, setup
from glob import glob
import os

package_name = 'pibot_rviz'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'urdf'), glob('urdf/*')),
        (os.path.join('share', package_name, 'rviz'), glob('rviz/*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='XXX',
    maintainer_email='XXX@gmail.com',
    description='Control Raspberry Pi bot and visualization',
    license='Apache Licence 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
        	'odom_footprint_tf = pibot_rviz.odom_footprint_tf_pub:main',
        	'motor_listener = pibot_rviz.motor:main',
        	'fake_motor_listener = pibot_rviz.fake_motor:main',
		'motor_controller = pibot_rviz.controller:main'
        ],
    },
)
