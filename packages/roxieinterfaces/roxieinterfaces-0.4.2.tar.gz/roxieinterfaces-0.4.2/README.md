[//]: # "Comment" SPDX-FileCopyrightText: 2024 CERN
[//]: # "Comment" SPDX-License-Identifier: BSD-4-Clause

# Roxie Interfaces

This project provides python tools and classes to interface with Roxie.

See [The Roxie documentation](https://roxie.docs.cern.ch/) on how to install Roxie binaries.

## Installation

### As pip package

Simply install the package via pip:

    pip install roxie-interfaces

### Via Poetry

We use the poetry packaging manager. You can get poetry with pip:

    pip install poetry

After You have pulled this repository with git. Navigate to the main directory (where this readme file is located),
and run

    poetry install

## Features

### Step file generation (conductors and end spacers)

The most important example is plot_step_file_generation.
It shows You how to generate the step files for endspacers, wedges, posts and conductors.

### HMO file generator

Load mesh formats (hmascii, gmsh) and generate hmo file to use with roxie.
