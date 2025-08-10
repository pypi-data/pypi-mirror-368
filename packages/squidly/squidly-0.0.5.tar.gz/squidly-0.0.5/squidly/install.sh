#!/bin/bash

# Doesn't like working with conda init
CONDA_BASE=$(conda info --base)
. $CONDA_BASE/etc/profile.d/conda.sh

# Install torch
conda config --env --add channels conda-forge
conda install pytorch torchvision torchaudio -c pytorch -y

# install clustalomega
wget http://www.clustal.org/omega/clustalo-1.2.4-Ubuntu-x86_64 -O clustalo
chmod +x clustalo
echo export PATH=$PATH:$PWD/bin >> ~/.bashrc 
. ~/.bashrc

# downloading and using a BLAST database
# update_blastdb.pl --decompress --blastdb_version 5 swissprot
# ./diamond prepdb -d swissprot
conda install -c bioconda -c conda-forge diamond
