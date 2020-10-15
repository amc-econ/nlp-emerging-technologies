# nlp-emerging-technologies

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) [![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)

> Identification of emerging technologies with NLP-powered networks

Project overview
-------

The digitalization of the patent literature over the past decades and the emergence of natural language processing (NLP) techniques now allow to use the very rich and largely unexplored information contained in the inside of patents (abstract, patent claims). While patent metadata has been largely used in the field of innovation economics and in technological forecasting, patent text data is still a largely unexplored frontier. Until the most recent years, only researchers and practitioners were able to process this textual information and to assess qualitatively how patents are interacting with each other, in a time-consuming process. The use of bibliometrics mesures such as citation counts or keywords allow to link patents with one another, but largely fails to assess the nature of the interaction between a given pair of patents linked by a citation: for instance, a patent can consist in a slight incremental improvement of a previous patented invention, cite another one for the sake of completness, or import a technique from another field and be the starting point of a whole new branch of its discipline. 

By combining NLP techniques to compare the similarity of any pair of patents (claims) and statistical analysis of the associated patent networks, we aim to identify in emerging technologies.

Identifying emerging technologies and understanding how they appear is a priority concern for policy-makers, since they can have “a revolutionary impact on the economy and society” [1]. In the EU, recent efforts technological push were recently targetted towards the battery value chain (European Battery Alliance, 2017) and cloud computing (Gaïa-X, 2020). Deploying overarching industial policies in a specific technology implies picking a winner, or face failure.

This project aims to design a method to identify emerging technologies using patent text data: 
1. We link the patents based on their content via Natural Language Processing (NLP);
1. This yield a weighted patent network which evolves over time, as new patents are granted; 
1. We then identify in the network the clusters representing emerging technologies and forecast their rise.

Three main research questions in innovation economics this project aim to answer are:

1. How and where does emerging technologies arise?
1. How do emerging technologies evolve, compete, and spread over time?
1. What are the drivers of emerging technologies?

Data
-------

We use three datasets:

* Patent data: [PATSTAT](https://www.epo.org/searching-for-patents/business/patstat.html);
* Patent text: [EP full-text data for text analytics](https://www.epo.org/searching-for-patents/data/bulk-data-sets/text-analytics.html);
* Financial and ownership information about the patentees:
[ORBIS](https://www.bvdinfo.com/en-gb/our-products/data/international/orbis).


Because of the size of the data and its proprietary nature, it is not included in the repository. However, the notebooks and model allow to create the datasets used in this study from scratch.

Methodology
-------

The methodology follows a four steps process:

1. Identification of links between technological items and assessment of their quality with NLP techniques;
2. Modelling of the technological knowledge as large-scale networks;
3. Tracking of the emergence and diffusion of technological ideas with community detection algorithms;
4. Statistical analysis to identify the the factors driving the emergence of new technologies.

The `report` folder of the repository contains more details about the methodology, while its implementation in Python can be found in `models` and `notebooks`. 

Achievements
-------

- [x] Implementation of the model in Python
- [x] Setting up queries to retrieve data from PATSTAT and the EP-full-text database
- [x] Parsing the full-text data of the EP-full-text database (stored in XML format)
- [x] Create of a new similarity measure based on natural language processing
- [x] Feature enginering of the best similarity measures for patent data
- [x] Identifcation of the data coverage of the full-text data
- [x] Implementation of machine translation for patents
- [x] Creation of the data visualisation tools

Work in progress
-------

- [ ] Get the text data corresponding to the patent of interest and store it in the patent objects of the model
- [ ] Implement the text processing step
- [ ] Implement the text similarity metric
- [ ] Implement the chosen clustering technique for community detection in weighted dynamic networks: the Stabilised Louvain Method [2]
- [ ] Track the communities over time using the Jaccard distance, and model their evolution using S-curves
- [ ] Setting all the pieces of the model together!
- [ ] Introduce firm level data in the model
- [ ] Application of the model to the EV battery field

Caveats identified
-------

* All juridictions seem to be covered at almost 100% by an EP publication but the US ones!

Main references
-------

* [1] Martin, Ben R. 1995. “Foresight in Science and Technology.” Technology Analysis & Strategic Management 7 (2): 139–68.
* [2] Aynaud, Thomas, and Jean-Loup Guillaume. 2010. “Static Community Detection Algorithms for Evolving Networks.” In 8th International Symposium on Modeling and Optimization in Mobile, Ad Hoc, and Wireless Networks, 513–19. IEEE.

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
