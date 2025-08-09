import setuptools
import os

lib_folder = os.path.dirname(os.path.realpath(__file__))

# Load README for long_description
with open(os.path.join(lib_folder, 'digitalarzengine', 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Requirements handling
requirement_path = os.path.join(lib_folder, 'digitalarzengine/requirements.txt')
skip_packages = ["pytest", "moto", "wheel", "twine"]
install_requires = []

if os.path.isfile(requirement_path):
    with open(requirement_path) as f:
        for line in f:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if any(stripped.startswith(pkg) for pkg in skip_packages):
                continue
            install_requires.append(stripped)

# Setup definition
setuptools.setup(
    name="digitalarzengine",
    version='0.4.0',
    author="Ather Ashraf",
    author_email="atherashraf@gmail.com",
    description="DigitalArzEngine for GEE, raster and vector data processing",
    long_description=long_description,
    long_description_content_type='text/markdown',
    python_requires='>=3.7',
    install_requires=install_requires,
    packages=setuptools.find_packages(exclude=["digitalarzengine.tests", "digitalarzengine.tests.*"]),
    include_package_data=True,
    keywords=['raster', 'vector', 'digital earth engine'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
