from setuptools import find_packages, setup

package_name = 'prac_service_py'

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
    description='ROS 2 practice of service using rclpy',
    license='Apache License 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
        	'server = prac_service_py.server:main',
        	'client = prac_service_py.client:main',
        ],
    },
)
