# Whangarei District Council - Automated Forward Works Planner Publish

This is a Python project which will publish layers to ArcGIS Online from the enterprise geodatabase and exported hansen CSV files. This will publish:
* Combined FWP layer (water, wastewater, stormwater)
* Individual existing asset layers (water, wastewater, stormwater) based on pre configured map documents.

It does not currently the ArcGIS API for Python as the target ArcGIS version is 10.1.
This can easily be updated though as classes have been designed with a Single Responsibility principle.

## Getting Started

Copy project structure to any directory.
Note that modules will be loaded from the same directory automatically.
The hosting machine must have ArcGIS installed as the script uses arcpy.
Create a scheduled task to execute the bootstrap.py script.

### Prerequisites

The Python project requires
* arcpy 
* requests

Requests needs to be added to the Python installation via the normal package installation methods.

### Installing

To install:

* Copy project directory to target location
* Add permissions for user who will execute the scheduled tasks
* Create scheduled task
* Test script by executing bootstrap.py

## Authors

Fraser Hand

:dromedary_camel: