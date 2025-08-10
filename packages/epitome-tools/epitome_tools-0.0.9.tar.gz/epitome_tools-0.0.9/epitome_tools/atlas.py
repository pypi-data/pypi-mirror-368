import subprocess
import os
import pandas as pd

def sra_downloader(raw_path,df):
    """
    Downloads SRA datasets from NCBI using wget and ffq.
    Args:
        raw_path (str): Path to the directory where datasets will be downloaded.
        df (pd.DataFrame): DataFrame containing SRA IDs and experiment types.
    """

    datasets_already_downloaded = os.listdir(raw_path)

    #iterating through the table and getting datasets
    for i in range(len(df)-1,-1,-1):
        SRA_ID = df.iloc[i]['SRA_ID']
        experiment_type = df.iloc[i]['Modality']

        if SRA_ID in datasets_already_downloaded:
            print("SRA_ID already downloaded")
            continue

        if (not os.path.exists(raw_path+ SRA_ID)) and ((experiment_type == "sc") or (experiment_type == "sn")):
            os.mkdir(raw_path + SRA_ID)

            print("Folder created")

        target_folder = raw_path + SRA_ID
        download_command = f"wget -P {target_folder} /path/to/target/folder $(ffq --ncbi {SRA_ID} | jq -r '.[] | .url' | tr '\n' ' ')"
        #run command
        print(download_command)
        subprocess.run(download_command, shell=True)


def fastq_downloader(raw_path, df):
    """
    Downloads fastq files from SRA datasets.
    Args:
        raw_path (str): Path to the directory where datasets are stored.
        df (pd.DataFrame): DataFrame containing SRA IDs and experiment types.
    """

    for i in range(len(df)-1,-1,-1):
        SRA_ID = df.iloc[i]['SRA_ID']
        experiment_type = df.iloc[i]['Modality']
        outdir = raw_path + SRA_ID
        files = os.listdir(outdir)
        for file in files:
            print(file)
            if ("lite" in file) or ("sra" in file):
                #check if there are fastq files with starting with file
                if any(x.startswith(file) and x.endswith('.fastq.gz') for x in files):
                    print("fastq files found")
                    #or it has bam string in it
                elif "bam" in file:
                    print("bam file found")
                else:
                    file = raw_path + SRA_ID + '/' + file
                    fastqdump_command= f"fastq-dump --outdir {outdir} --gzip --split-files {file}"
                    subprocess.run(fastqdump_command, shell=True)


def run_kb_count_nac(nac_path,raw_path, df):
    """ Runs kb count for nascent RNA datasets.
    Args:
        nac_path (str): Path to the directory where nascent RNA datasets will be stored.
        raw_path (str): Path to the directory where raw datasets are stored.
        df (pd.DataFrame): DataFrame containing SRA IDs, experiment types, and technologies.
    """

    datasets_already_downloaded = os.listdir(nac_path)
    #iterating through the table and getting datasets
    for i in range(len(df)):
        SRA_ID = df.iloc[i]['SRA_ID']
        experiment_type = df.iloc[i]['Modality']
        tech = df.iloc[i]['10X version']
        author = df.iloc[i]['Author']

        #print all of these
        print("""
        SRA_ID: {}
        experiment_type: {}
        tech: {}
        """.format(SRA_ID,experiment_type,tech))

        #check if SRA_ID is already downloaded
        if SRA_ID in datasets_already_downloaded:
            print("SRA_ID already aligned for nac")
            continue

        
        all_fastqs = find_fastqs(raw_path, SRA_ID)
        #if there arent at least 2 fastqs then continue
        if len(all_fastqs) < 2:
            print("Not enough fastqs")
            continue

        if not os.path.exists(nac_path + SRA_ID):
            os.mkdir(nac_path + SRA_ID)

        if experiment_type == "sn":
            print("Running kb count")
            output_dir = f"{nac_path}{SRA_ID}/"
            kbcount_nac_command1 = f"kb count -i index_nac.idx -g t2g_nac.txt -c1 cdna.txt -c2 nascent.txt  -x {tech} --workflow=nac --sum=total --overwrite --h5ad -o {output_dir} {' '.join(all_fastqs)}"
            print(kbcount_nac_command1)
            subprocess.run(kbcount_nac_command1, shell=True)
        elif (experiment_type == "sc"):
            print("Running kb count")
            output_dir = f"{nac_path}{SRA_ID}/"
            kbcount_nac_command1 = f"kb count -i index_nac.idx -g t2g_nac.txt -c1 cdna.txt -c2 nascent.txt -x {tech} --workflow=nac --sum=total --overwrite --h5ad -o {output_dir} {' '.join(all_fastqs)}"
            print(kbcount_nac_command1)
            subprocess.run(kbcount_nac_command1, shell=True)
        elif (experiment_type == "multi_rna"):
            print("Running kb count")
            output_dir = f"{nac_path}{SRA_ID}/"
            #from all_fastqs remove ones that contain "atac"
            all_fastqs = [x for x in all_fastqs if "atac" not in x]
            print(all_fastqs)
            kbcount_nac_command1 = f"kb count -i index_nac.idx -g t2g_nac.txt -c1 cdna.txt -c2 nascent.txt -x {tech} -w /10xMultiome/gex_737K-arc-v1.txt --workflow=nac --sum=total --overwrite --h5ad -o {output_dir} {' '.join(all_fastqs)}"
            print(kbcount_nac_command1)
            subprocess.run(kbcount_nac_command1, shell=True)



def find_fastqs(raw_path, SRA_ID):
    """ Finds fastq files in the specified directory for a given SRA ID.
    Args:
        raw_path (str): Path to the directory where datasets are stored.
        SRA_ID (str): SRA ID for which fastq files are to be found.
    Returns:
        list: List of fastq file paths.
    """

    directory = raw_path + SRA_ID
    files = os.listdir(directory)
    all_fastqs = []
    for file in files:
        if file.endswith('.fastq.gz'):
            all_fastqs.append(directory + '/' + file)

    #if there are fastq files with the same string before .sralite, only keep the two largest of them in the list
    #does any of the files have lite in name


    lite_name = True if any(x for x in all_fastqs if 'lite' in x) else False
    if lite_name:
        id_tags = [x.split('lite')[0] for x in all_fastqs]


    SRR_name = True if any(x for x in all_fastqs if 'SRR' in x) else False
    if SRR_name:
        id_tags = [x.split('.1_')[0] for x in all_fastqs]
        #if empty try splitting at _1
        #if they contain multiple /, split at _1
        if id_tags[0].count('/') > 1:
            id_tags = [x.split('_1')[0] for x in all_fastqs]

    #if neither
    elif (not lite_name) and (not SRR_name):
        id_tags = [x.split('_R1_')[0] for x in all_fastqs if '_R1_' in x]

    print(id_tags)
    all_fastqs_final = []
    unique_tags= list(set(id_tags))
    for tag in unique_tags:
        fastqs_with_tag = [x for x in all_fastqs if tag in x]
        if len(fastqs_with_tag) > 1:
            #sort by size and take the two largest
            fastqs_with_tag.sort(key=lambda x: os.path.getsize(x), reverse=True)
            all_fastqs_final.append(fastqs_with_tag[1])
            all_fastqs_final.append(fastqs_with_tag[0])


    all_fastqs = all_fastqs_final
    return all_fastqs
















