import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name='django-lite-cms-core',
    version='0.0.9',
    packages=setuptools.find_packages(
        exclude=["lite_cms_core_sample", "*manage.py"]
    ),
    include_package_data=True,
    package_data={
        "lite_cms_core": [
            "templates/lite_cms_core/*.html",
            "templates/lite_cms_core/includes/*.html",
            "locale/*/LC_MESSAGES/*",
        ],
    },
    description='CMS core classes for Django.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Christian Wiegand',
    license='MIT',
    url='https://github.com/christianwgd/django-lite-cms-core',
    keywords=['django', 'bootstrap', 'cms'],
    install_requires=[
        'django',
        'django-admin-sortable2',
        'django-bootstrap5',
        'django-filebrowser-no-grappelli',
        'django-tinymce',
        'Pillow',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.10',
)
