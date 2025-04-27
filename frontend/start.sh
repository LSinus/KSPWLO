#!/bin/bash
source env/bin/activate
echo "virtual environment activated"

#',' is the Internal Field Separator
while IFS=',' read -r source dest; do
  #removing eventual initial or final spaces

  if [ ! -f "nord-ovest-latest.osm.pbf" ]; then
    echo "Error: nord-ovest-latest.osm.pbf not found"
    exit 1
  fi

  SOURCE=$(echo "$source" | xargs)
  DEST=$(echo "$dest" | xargs)

  #exporting the environment variables
  export SOURCE
  export DEST
  python3 fileReader.py

  #Leggi il file delle variabili d'ambiente generate da Python
  if [ -f "env_variables.txt" ]; then
    source env_variables.txt
  else
    echo "Error: env_variables.txt not found"
    continue
  fi

  # Verifica che le variabili siano impostate correttamente
  echo "SOURCE_BBOX: $SOURCE_BBOX"
  echo "DEST_BBOX: $DEST_BBOX"
  echo "MIDDLE_BBOX: $MIDDLE_BBOX"
  echo "START_LAT: $START_LAT"
  echo "START_LON: $START_LON"
  echo "END_LAT: $END_LAT"
  echo "END_LON: $END_LON"

  # Export the variables back to environment for other scripts
    export START_LAT
    export START_LON
    export END_LAT
    export END_LON

  # checking variables
  if [ -z "$SOURCE_BBOX" ] || [ -z "$DEST_BBOX" ] || [ -z "$MIDDLE_BBOX" ]; then
      echo "Error: Bounding boxes or coordinates not properly set"
      continue
  fi

    echo "Extracting source area..."
    osmium extract -b "$SOURCE_BBOX" nord-ovest-latest.osm.pbf -o sourceGraph.osm --overwrite
    osmium tags-filter sourceGraph.osm w/highway=residential,tertiary,secondary,primary -o sourceGraph_filtered.osm --overwrite
    mv sourceGraph_filtered.osm sourceGraph.osm
    
    echo "Extracting destination area..."
    osmium extract -b "$DEST_BBOX" nord-ovest-latest.osm.pbf -o destGraph.osm --overwrite
    osmium tags-filter destGraph.osm w/highway=residential,tertiary,secondary,primary -o destGraph_filtered.osm --overwrite
    mv destGraph_filtered.osm destGraph.osm
    
    echo "Extracting middle area..."
     osmium extract -b "$MIDDLE_BBOX" nord-ovest-latest.osm.pbf -o middleGraph.osm --overwrite
    osmium tags-filter middleGraph.osm w/highway=trunk,motorway,primary -o middleGraph_filtered.osm --overwrite
    mv middleGraph_filtered.osm middleGraph.osm

  # export SOURCE_GRAPH_PBF=sourceGraph.osm.pbf
  # export DEST_GRAPH_PBF=destGraph.osm.pbf
  # export MIDDLE_GRAPH_PBF=middleGraph.osm.pbf
  
  python3 clientCarlo.py
  echo "Processing complete for $SOURCE to $DEST"
done < destinazioni.txt
