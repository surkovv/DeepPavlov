"""
Copyright 2017 Neural Networks and Deep Learning lab, MIPT
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
    http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from setuptools import setup, find_packages
import os
import re

from utils.pip_wrapper import install

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))


def read_requirements():
    # # parses requirements from requirements.txt
    reqs_path = os.path.join(__location__, 'requirements.txt')
    with open(reqs_path) as f:
        reqs = [line.strip() for line in f if not line.strip().startswith('#')]

    for req in reqs:
        install(req)

    names = []
    links = []
    for req in reqs:
        if '://' in req:
            links.append(req)
        else:
            names.append(req)
    return {'install_requires': names, 'dependency_links': links}


def readme():
    with open(os.path.join(__location__, 'README.md')) as f:
        text = f.read()
    return re.sub(r']\((?!https?://)', r'](https://github.com/deepmipt/DeepPavlov/blob/master/', text)


meta = {}
with open(os.path.join(__location__, 'deeppavlov/package_meta.py')) as f:
    exec(f.read(), meta)

setup(
    name='deeppavlov',
    packages=find_packages(exclude=('tests',)),
    version=meta['__version__'],
    description='An open source library for building end-to-end dialog systems and training chatbots.',
    long_description=readme(),
    long_description_content_type="text/markdown",
    author=meta['__author__'],
    author_email='info@ipavlov.ai',
    license='Apache License, Version 2.0',
    url='https://github.com/deepmipt/DeepPavlov',
    download_url='https://github.com/deepmipt/DeepPavlov/archive/' + meta['__version__'] + '.tar.gz',
    keywords=['NLP', 'NER', 'SQUAD', 'Intents', 'Chatbot'],
    include_package_data=True,
    **read_requirements()
)
