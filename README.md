# nlp-emerging-technologies

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) [![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)

> Identification of emerging technologies with NLP-powered networks

Project overview
-------

Identifying emerging technologies and understanding how they appear is a priority concern for policy-makers, since they can have “a revolutionary impact on the economy and society” [1]. In the EU, recent efforts technological push were recently targetted towards the battery value chain (European Battery Alliance, 2017) and cloud computing (Gaïa-X, 2020). 

Three main research questions in innovation economics this project aim to answer are:

􏰀* (1) How and where does emerging technologies arise?
􏰀* (2) How do emerging technologies evolve, compete, and spread over
time?
􏰀* (3) What are the drivers of emerging technologies?

Data
-------

We use three datasets:

􏰀* Patent data: [PATSTAT](https://www.epo.org/searching-for-patents/business/patstat.html);
􏰀* Patent text: [EP full-text data for text analytics](https://www.epo.org/searching-for-patents/data/bulk-data-sets/text-analytics.html);
􏰀* Financial and ownership information about the patentees:
[ORBIS](https://www.bvdinfo.com/en-gb/our-products/data/international/orbis).

Because of the size of the data and its proprietary nature, it is not included in the repository. However, the notebooks and model allow to create the datasets used in this study from scratch.

Methodology
-------

The methodology follows a four steps process:

􏰀* (1) Identification of links between technological items and assessment of their quality with NLP techniques;
* 􏰀(2) Modelling of the technological knowledge as large-scale networks;
* 􏰀(3) Tracking of the emergence and diffusion of technological ideas with community detection algorithms;
* 􏰀(4) Statistical analysis to identify the the factors driving the emergence of new technologies.

The `report` folder of the repository contains more details about the methodology, while its implementation in Python can be found in `models` and `notebooks`. 

Achievements
-------

Work in progress
-------

Possible applications
-------

Main references
-------

* [1] Martin, Ben R. 1995. “Foresight in Science and Technology.” Technology Analysis & Strategic Management 7 (2): 139–68.

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
