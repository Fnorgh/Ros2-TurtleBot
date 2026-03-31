from setuptools import find_packages, setup

package_name = 'reactive_robot'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', [
            'launch/reactive_robot.launch.py',
            'launch/reactive_robot.launch.xml',
        ]),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='gibs0113',
    maintainer_email='gibs0113@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
		'reactive_controller = reactive_robot.reactive_controller:main',
	],
    },
)
