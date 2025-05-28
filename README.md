# HPC for Car Navigation Systems

**Politecnico di Milano - A.A. 2024-2025**
*Project by: Leonardo Sinibaldi & Giorgia Savo*
*Supervisor: Prof. Gianluca Palermo*

## Overview

This project presents a High-Performance Computing (HPC) system designed to efficiently support modern car navigation systems. The primary goal is to process geographical data, primarily from OpenStreetMap, to offer intelligent and optimized routing services. Beyond just calculating the shortest path, the system focuses on providing users with a set of sufficiently diverse alternative routes between a given source and destination.
More documentation resources can be found inside /deliverables

## Core Functionality

Given a source and a destination, the system aims to compute:
* The shortest path.
* A set of alternative routes that are meaningfully different from each other, based on user-defined parameters such as the desired number of alternatives (k) and a dissimilarity factor ($\theta$).

## System Architecture

The system is built upon a client-server architecture:

* **C++ Backend**: A high-performance server responsible for the heavy computational tasks.
    * Communicates via TCP sockets, handling requests structured with headers and bodies.
    * Processes graph data (optionally received in GraphML format for the first request in an area) and routing parameters (source OSMID, destination OSMID, k, $\theta$).
    * Utilizes the ARLIB library for graph exploration and alternative path algorithms.
    * Employs multi-threading to run different pathfinding algorithms concurrently (e.g., `onepass_plus`, `esx`, `penalty`).
    * Streams results back to the client incrementally as paths are found.
* **Python Frontend**: A user-friendly desktop application.
    * Built with PyQt5 for the graphical user interface.
    * Allows users to input start/end locations, desired number of routes, and maximum overlap percentage.
    * Visualizes the computed routes on an interactive map.
    * Handles asynchronous communication with the backend using `QSocketNotifier`.
    * Features include hierarchical graph extraction (varying detail levels for different map sections) and a graph caching mechanism.

## Technologies

* **Backend**: C++, ARLIB
* **Frontend**: Python, PyQt5, Geopy, Geonamescache
* **Data Handling**: GraphML, OpenStreetMap (OSM) data
* **Communication**: TCP/IP Sockets
* **HPC Environment**: Slurm Workload Manager, Osmium Tool (for OSM data processing during tests)

## Algorithms Explored

The project involved an initial phase of analyzing research papers on various pathfinding algorithms, including:
* Shortest Path Algorithms (Dijkstra, A*, Bidirectional Dijkstra)
* Exact Algorithms (e.g., OnePass, MultiPass)
* Heuristic Algorithms (e.g., OnePass+, SVP+, ESX)
* P-Dispersion Algorithms
* Penalty Methods
* Plateau Method

The implemented backend leverages algorithms from the ARLIB library, specifically `onepass_plus`, `esx`, and `penalty`, for generating alternative routes.

## HPC Testing & Analysis

The final phase involved extensive testing on an HPC cluster (CARLO at Politecnico di Milano). This included:
* Batch processing of numerous route computations across various geographical scales (Urban, ExtraUrban, Regional, InterRegional).
* Performance analysis of the implemented algorithms (`onepass_plus`, `esx`, `penalty`) based on computation time, path length, and yield (success rate).
* Normalization of results using an "oracle-based" approach to ensure fair comparisons.

The analysis concluded that the different methods can be considered "Pareto-optimal" in the Yield-Length-Time space, with each offering distinct advantages depending on the specific context and priorities.

## Installation
Clone the repository and then run the following commands:

### backend
Make sure to have installed Boost library

```bash
  cd backend
  mkdir build
  cd build
  cmake -DCMAKE_BUILD_TYPE=Release ..
  make -j
  ./main
```

### frontend
```bash
  cd frontend
  python3 -m venv env
  source env/bin/activate
  pip install -r requirements.txt
  python3 client.py 
```