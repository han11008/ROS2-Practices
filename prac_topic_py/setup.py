from setuptools import find_packages, setup

package_name = 'prac_topic_py'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='XXX',
    maintainer_email='XXX@gmail.com',
    description='ROS 2 practice of topic using rclpy',
    license='Apache License 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
        	'talker = prac_topic_py.talker:main',
        	'listener = prac_topic_py.listener:main',
        ],
    },
)
