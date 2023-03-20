query-gdc
===============================

author: Jay Mashl

Overview
-------------

Command line tools for downloading genomic metadata from the NCI Genomic Data Commons (GDC) or an
analysis working group (AWG) using the [REST API approach](https://docs.gdc.cancer.gov/API/Users_Guide/Getting_Started/), and for downloading data.


Setup
-------------

There are a few preliminary steps.
- Obtain an authentication token from GDC (or AWG) and save to file (e.g., mytoken.txt). Do this by logging into the GDC (or AWG) data portal, and then
   navigate to Download Token under your username.

   Note that more recently, it appears tokens are needed only for AWG projects.

- For data downloads, install the [gdc-client](https://gdc.cancer.gov/access-data/gdc-data-transfer-tool) data transfer tool.

- Adjust paths and filenames as needed.

Usage: query
-------------

1. Verify the file path to the authentication token in the `query-gdc.py` script.

2. From the GDC (or AWG) project, we need the following:
   - Biospecimen metadata
     - Clinical metadata
       - File manifest with file uuids

   which are obtainable from the project's main page (e.g., [CTSP-DLBCL1](https://portal.gdc.cancer.gov/projects/CTSP-DLBCL1/)).
   Click the buttons to download the biospecimen and clinical metadata.

    The file manifest can come from different landing pages depending on what is needed:
        - For all primary files and analysis results, click the Manifest button on the project's main page.
            - For selected files, e.g., WXS bam files, drill down and apply filters on the project's main page and then click the Manifest button.

3. Perform the queries (in this version, we pre-extracte the file ids of interest into a separate file):

           query-gdc.py   <fileID_list>    >  query_results.tsv

           The following fields are reported:

               project_id, file_id, file_name, submitter_id, aliquot_id_list sample_name_list, sample_type_list, preservation_method_list, data_category, data_type, caller, call_format experimental_strategy


4. Inspect the filenames obtained, modifying filepaths internal to GDC that do not apply. Edit as needed and save. (e.g., `query_results.fixed.tsv`)

5. (Optional) Convert the query results to "bam map" format using the `query2bammap.sh` script for use in other workflows, such as [TinDaisy](https://github.com/ding-lab/TinDaisy).


Usage: data download
-------------
1. Check the configuration of the `download-gdc.sh` script, namely the token path and the server endpoint. Specifically, if the data/metadata comes from the AWG portal, then point the `gdc-client` tool to the AWG server by including the '-s' flag.

2. The `gdc-client` tool uses the file uuid to download files. This is usually the first field in file manifests; if not, modify `download-gdc.sh` script to skip headers and extract the appropriate file uuid column.

3. Arrange the downloaded files into some hierarchy, e.g., `<project>/Results/GDC/<case>/<caller>`

4. Build local relative file paths and append as column (users will need to provide `{PREFIX}` depending on where data is. Remove any unneeded colums.

         add_path.py  query_results.fixed.tsv >  project.CallMap.tsv

