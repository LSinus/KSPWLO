#!/bin/bash
source env/bin/activate
echo "virtual environment activated"

#',' is the Internal Field Separator
while IFS=',' read -r source dest; do
  #removing eventual initial or final spaces

  if [ ! -f "files/nord-ovest-latest.osm.pbf" ]; then
    echo "Error: files/nord-ovest-latest.osm.pbf not found"
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
    osmium extract -b "$SOURCE_BBOX" files/nord-ovest-latest.osm.pbf -o files/sourceGraph.osm --overwrite
    osmium tags-filter files/sourceGraph.osm w/highway=trunk,motorway,residential,tertiary,secondary,primary -o files/sourceGraph_filtered.osm --overwrite
    mv files/sourceGraph_filtered.osm files/sourceGraph.osm
    
    echo "Extracting destination area..."
    osmium extract -b "$DEST_BBOX" files/nord-ovest-latest.osm.pbf -o files/destGraph.osm --overwrite
    osmium tags-filter files/destGraph.osm w/highway=trunk,motorway,residential,tertiary,secondary,primary -o files/destGraph_filtered.osm --overwrite
    mv files/destGraph_filtered.osm files/destGraph.osm
    
    echo "Extracting middle area..."
    osmium extract -b "$MIDDLE_BBOX" files/nord-ovest-latest.osm.pbf -o files/middleGraph.osm --overwrite
    osmium tags-filter files/middleGraph.osm w/highway=trunk,motorway,primary,secondary -o files/middleGraph_filtered.osm --overwrite
    mv files/middleGraph_filtered.osm files/middleGraph.osm

  # export SOURCE_GRAPH_PBF=sourceGraph.osm.pbf
  # export DEST_GRAPH_PBF=destGraph.osm.pbf
  # export MIDDLE_GRAPH_PBF=middleGraph.osm.pbf
  
  python3 clientCarlo.py
  echo "Processing complete for $SOURCE to $DEST"
  unset SOURCE
  unset DEST
  unset START_LAT
  unset START_LON
  unset END_LAT
  unset END_LON
  unset SOURCE_BBOX
  unset DEST_BBOX
  unset MIDDLE_BBOX
  rm -rf env_variables.txt
done < destinazioni.txt
