import os
from datetime import datetime
import os.path
from os import path

import importlib.resources


def mkdir(save_dir, allow_exists=False):
    if allow_exists:
        os.makedirs(save_dir, exist_ok=True)
    else:
        os.mkdir(save_dir)


def copy(file, location):
    location = f"{location}/."
    try:
        os.system(f"cp {file} {location}")
    except Exception:
        pass


def submit(
    job_name,
    numJobs,
    save_directory_base,
    options,
    clean_log=True,
    overwrite=False,
    memory=12,
    hours=5,
    DRY=True,
    log_dir=None,
    CODEPATH="/users/am13743/Rex/",
    EXE="src/lhcb_rex/data/batch/make_graphs_batch.py",
):
    if log_dir is not None:
        if clean_log:
            os.system(f"rm -r {log_dir}/*{job_name}*")
        mkdir(log_dir, allow_exists=True)

    save_directory_base = save_directory_base.replace("//", "/")
    save_directory = save_directory_base + job_name

    if path.exists(save_directory):
        if overwrite:
            print(f"{save_directory} exists, deleting content...")
            os.system(f"rm -r {save_directory}")
        else:
            print(save_directory, "exists... quitting....")
            quit()

    mkdir(save_directory)

    print("\nOutput to be saved to", save_directory)

    # Setting up submission directory
    now = datetime.now()
    dt_string = now.strftime("%Hhr_%Mmin_%Ssec_%d_%m_%Y")
    tag_directory = f"{save_directory}/{job_name}_{dt_string}"
    mkdir(tag_directory)

    # job_options = [
    #     "--processID $1",
    # ]
    # job_options = " ".join(job_options)
    # # options_string = ""
    # for key in options:
    #     job_options += f" --{key} {options[key]}"

    job_options = ["--processID $1"]
    for key, value in options.items():
        if isinstance(value, str):
            job_options.append(f'--{key} "{value}"')
        else:
            job_options.append(f"--{key} {value}")

    job_options_str = " ".join(job_options)
    job_options = job_options_str
    # print(job_options)
    # # os.system(f"python ../make_graphs_batch.py{options_string}")
    # quit()

    os.mkdir(f"temp{job_name}")

    # ENVPATH = "/users/am13743/fast_vertexing_variables/training/condor/batch/"

    # Creating run file from template
    f = importlib.resources.files("lhcb_rex").joinpath("data/batch/batch.sh").open("r")
    f_lines = f.readlines()
    with open(f"temp{job_name}/batch.sh", "a") as f_out:
        for idx, line in enumerate(f_lines):
            # if "ENVPATH" in line:
            #     line = line.replace("ENVPATH", ENVPATH)

            if "CODEPATH" in line:
                line = line.replace("CODEPATH", CODEPATH)

            if "PYTHONOPTIONS" in line:
                line = line.replace("PYTHONOPTIONS", job_options)

            if "EXE" in line:
                line = line.replace("EXE", EXE)

            f_out.write(line)

    os.system(f"chmod +x temp{job_name}/batch.sh")

    # Creating submit file from template
    f = (
        importlib.resources.files("lhcb_rex")
        .joinpath("data/batch/submit.job")
        .open("r")
    )
    f_lines = f.readlines()
    with open(f"temp{job_name}/submit.job", "a") as f_out:
        for idx, line in enumerate(f_lines):
            if "JOBNAME" in line:
                line = line.replace("JOBNAME", job_name)

            if "NUMJOBS" in line:
                line = line.replace("NUMJOBS", str(numJobs))

            if "LOGDIR" in line:
                if log_dir is not None:
                    line = line.replace("LOGDIR", log_dir)

            if "TIME" in line:
                line = line.replace("TIME", str(60 * 60 * hours))

            if "EXE" in line:
                line = line.replace("EXE", "batch.sh")

            if "ARGS" in line:
                line = line.replace("ARGS", "$(PROCESS)")

            if "MEMORY" in line:
                line = line.replace("MEMORY", str(memory))

            if "log = " in line or "output = " in line or "error = " in line:
                if log_dir is not None:
                    f_out.write(line)
            else:
                f_out.write(line)

    copy(f"temp{job_name}/submit.job", save_directory)
    copy(f"temp{job_name}/batch.sh", save_directory)

    # Submitting jobs
    print(f"\n\nSubmitting {numJobs} jobs, job_name: {job_name} ...\n")
    pwd = os.getcwd()
    os.chdir(f"{save_directory}/")
    if not DRY:
        os.system("condor_submit submit.job")
    else:
        print("not executing...", "condor_submit submit.job")
        print("\n\n")
        os.system("cat submit.job")
        print("\n\n")
        os.system("cat batch.sh")
        print("\n\n")

    os.chdir(pwd)
    os.system(f"rm -r temp{job_name}/")
