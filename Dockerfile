FROM busybox
COPY . /dist
WORKDIR /dist
CMD conda activate snakemake
CMD snakemake -c10 targets
