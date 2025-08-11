from setuptools import setup, find_packages

# If you have made a README.md then uncomment below 2 lines
with open('README.md', 'r') as f:
    description = f.read()

setup(
    name='softmax-exploration',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        # Add dependencies here.
        'numpy>=1.19.0',
    ],
    # If you have created a README.md then uncomment below 2 lines
    long_description=description,
    long_description_content_type='text/markdown',
    author='Your Name',
    author_email='your.email@example.com',
    description='Softmax exploration functions for reinforcement learning',
    keywords='reinforcement-learning, softmax, exploration, boltzmann, q-learning',
    url='https://github.com/yourusername/softmax-exploration',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'softmax-exploration=pyPI.pyPI:main',
        ],
    },
)
