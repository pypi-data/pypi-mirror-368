# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['labelu',
 'labelu.alembic_labelu',
 'labelu.alembic_labelu.versions',
 'labelu.internal',
 'labelu.internal.adapter',
 'labelu.internal.adapter.persistence',
 'labelu.internal.adapter.routers',
 'labelu.internal.adapter.ws',
 'labelu.internal.application',
 'labelu.internal.application.command',
 'labelu.internal.application.response',
 'labelu.internal.application.service',
 'labelu.internal.clients',
 'labelu.internal.common',
 'labelu.internal.dependencies',
 'labelu.internal.domain.models',
 'labelu.internal.middleware',
 'labelu.internal.statics',
 'labelu.scripts',
 'labelu.tests',
 'labelu.tests.internal',
 'labelu.tests.internal.adapter',
 'labelu.tests.internal.adapter.persistence',
 'labelu.tests.internal.adapter.routers',
 'labelu.tests.internal.common',
 'labelu.tests.utils']

package_data = \
{'': ['*'], 'labelu.internal.statics': ['assets/*'], 'labelu.tests': ['data/*']}

install_requires = \
['aiofiles>=22.1.0,<23.0.0',
 'alembic>=1.9.4,<2.0.0',
 'appdirs>=1.4.4,<2.0.0',
 'email-validator>=1.3.0,<2.0.0',
 'fastapi>=0.90.0,<0.91.0',
 'httpx>=0.27.0,<0.28.0',
 'loguru>=0.6.0,<0.7.0',
 'passlib[bcrypt]>=1.7.4,<2.0.0',
 'pillow>=9.3.0,<10.0.0',
 'python-dotenv>=0.21.0,<0.22.0',
 'python-jose[cryptography]>=3.3.0,<4.0.0',
 'python-multipart>=0.0.5,<0.0.6',
 'sqlalchemy>=1.4.43,<2.0.0',
 'tfrecord>=1.14.5,<2.0.0',
 'typer[all]>=0.7.0,<0.8.0',
 'uvicorn>=0.19.0,<0.20.0',
 'websockets>=10.0.0,<11.0.0']

extras_require = \
{'mysql': ['mysqlclient>=2.1.1,<3.0.0']}

entry_points = \
{'console_scripts': ['labelu = labelu.main:cli']}

setup_kwargs = {
    'name': 'labelu',
    'version': '1.3.1',
    'description': '',
    'long_description': '<div align="center">\n<article style="display: flex; flex-direction: column; align-items: center; justify-content: center;">\n    <p align="center"><img width="300" src="https://user-images.githubusercontent.com/25022954/209616423-9ab056be-5d62-4eeb-b91d-3b20f64cfcf8.svg" /></p>\n    <h1 style="width: 100%; text-align: center;"></h1>\n    <p align="center">\n        English | <a href="./README_zh-CN.md" >简体中文</a>\n    </p>\n</article>\n    \n   \n</div>\n\n## Product Introduction\n\nLabelU is a comprehensive data annotation platform designed for handling multimodal data. It offers a range of advanced annotation tools and efficient workflows, making it easier for users to tackle annotation tasks involving images, videos, and audio. LabelU is tailored to meet the demands of complex data analysis and model training.\n\n## Key Features\n\n### Versatile Image Annotation Tools\nLabelU provides a comprehensive set of tools for image annotation, including 2D bounding boxes, semantic segmentation, polylines, and keypoints. These tools can flexibly address a variety of image processing tasks, such as object detection, scene analysis, image recognition, and machine translation, helping users efficiently identify, annotate, and analyze images.\n\n### Powerful Video Annotation Capabilities\nIn the realm of video annotation, LabelU showcases impressive processing capabilities, supporting video segmentation, video classification, and video information extraction. It is highly suitable for applications such as video retrieval, video summarization, and action recognition, enabling users to easily handle long-duration videos, accurately extract key information, and support complex scene analysis, providing high-quality annotated data for subsequent model training.\n\n### Efficient Audio Annotation Tools\nAudio annotation tools are another key feature of LabelU. These tools possess efficient and precise audio analysis capabilities, supporting audio segmentation, audio classification, and audio information extraction. By visualizing complex sound information, LabelU simplifies the audio data processing workflow, aiding in the development of more accurate models.\n\n### Artificial Intelligence Assisted Labelling\nLabelU supports one-click loading of pre-annotated data, which can be refined and adjusted according to actual needs. This feature improves the efficiency and accuracy of annotation.\n\n\nhttps://github.com/user-attachments/assets/0fa5bc39-20ba-46b6-9839-379a49f692cf\n\n\n\n\n## Features\n\n- Simplicity: Provides a variety of image annotation tools that can be annotated through simple visual configuration.\n- Flexibility: A variety of tools can be freely combined to meet most image, video, and audio annotation needs.\n- Universality: Supports exporting to various data formats, including JSON, COCO, MASK.\n\n## Getting started\n\n- <a href="https://opendatalab.github.io/labelU-Kit/">\n    <button>Try LabelU annotation toolkit</button>\n</a>\n\n- <a href="https://labelu.shlab.tech/">\n    <button>Try LabelU online</button>\n</a>\n\n### Local deployment\n\n1. Install [Miniconda](https://docs.conda.io/en/latest/miniconda.html), Choose the corresponding operating system type and download it for installation.\n\n> **Note：** If your system is MacOS with an Intel chip, please install [Miniconda of intel x86_64](https://repo.anaconda.com/miniconda/).\n\n2. After the installation is complete, run the following command in the terminal (you can choose the default \'y\' for prompts during the process):\n\n```bash\nconda create -n labelu python=3.11\n```\n\n> **Note：** For Windows platform, you can run the above command in Anaconda Prompt.\n\n3. Activate the environment：\n\n```bash\nconda activate labelu\n```\n\n4. Install LabelU：\n\n```bash\npip install labelu\n```\n\n> To install the test version：`pip install labelu==<test revision>`\n\nInstall labelu with MySQL support：\n\n```bash\npip install labelu[mysql]\n\n# Or install labelu and mysqlclient separately\n# pip install labelu mysqlclient\n```\n\n5. Run LabelU：\n\n```bash\nlabelu\n```\n\n> If you need to use MySQL database after upgrading from version 1.x, run the following command to migrate data from the built-in SQLite database to the MySQL database:\n\n```bash\nDATABASE_URL=mysql://<username>:<password>@<host>/<your dbname> labelu migrate_to_mysql\n```\n\n6. Visit [http://localhost:8000/](http://localhost:8000/) and ready to go.\n\n### Local development\n\n```bash\n# Download and Install miniconda\n# https://docs.conda.io/en/latest/miniconda.html\n\n# Create virtual environment(python = 3.11)\nconda create -n labelu python=3.11\n\n# Activate virtual environment\nconda activate labelu\n\n# Install peotry\n# https://python-poetry.org/docs/#installing-with-the-official-installer\n\n# Install all package dependencies\npoetry install\n\n# Download the frontend statics from labelu-kit repo\nsh ./scripts/resolve_frontend.sh true\n\n# Start labelu, server: http://localhost:8000\nuvicorn labelu.main:app --reload\n```\n\n\n## Quick start\n\n- [Guidance](https://opendatalab.github.io/labelU)\n\n## Annotation format\n\n- [Documentation](https://opendatalab.github.io/labelU/#/schema)\n\n## Citation\n\n```bibtex\n@article{he2024opendatalab,\n  title={Opendatalab: Empowering general artificial intelligence with open datasets},\n  author={He, Conghui and Li, Wei and Jin, Zhenjiang and Xu, Chao and Wang, Bin and Lin, Dahua},\n  journal={arXiv preprint arXiv:2407.13773},\n  year={2024}\n}\n```\n\n## Communication\n\nWelcome to the OpenDataLab official WeChat group！\n\n<p align="center">\n<img style="width: 400px" src="https://user-images.githubusercontent.com/25022954/208374419-2dffb701-321a-4091-944d-5d913de79a15.jpg">\n</p>\n\n\n## Links\n\n- [LabelU-kit](https://github.com/opendatalab/labelU-Kit) Web front-end annotation kit (LabelU is based on this JavaScript kit)\n- [LabelLLM](https://github.com/opendatalab/LabelLLM) An Open-source LLM Dialogue Annotation Platform\n- [Miner U](https://github.com/opendatalab/MinerU) A One-stop Open-source High-quality Data Extraction Tool\n\n## License\n\nThis project is released under the [Apache 2.0 license](./LICENSE).\n',
    'author': 'shenguanlin',
    'author_email': 'shenguanlin@pjlab.org.cn',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/opendatalab/labelU',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.11,<4.0',
}


setup(**setup_kwargs)
