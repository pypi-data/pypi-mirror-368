import psutil
import dask
import numpy as np
import argparse
import traceback
import time
import sys
import os
import logging
from dask import delayed
from meersolar.utils import *

logging.getLogger("distributed").setLevel(logging.ERROR)
logging.getLogger("tornado.application").setLevel(logging.CRITICAL)
datadir = get_datadir()


def get_polmodel_coeff(model_file):
    """
    Get polarization model coefficients

    Parameters
    ----------
    model_file : str
        Model ascii file name

    Returns
    -------
    float
        Reference frequency in GHz
    float
        Stokes I flux density in Jy at reference frequency
    list
        Stokes I spectrum log-polynomial coefficients
    list
        List of linear polarization fraction polynomial coefficients
    list
        List of linear polarization angle (in radians) coefficients
    """
    freq, I, pfrac, pangle = np.loadtxt(model_file, unpack=True, skiprows=5)
    ref_freq = freq[0]
    x = (freq - ref_freq) / ref_freq
    polyI = np.polyfit(np.log10(x[1:]), np.log10(I[1:]), deg=5)[::-1]
    poly_pfrac = np.polyfit(x, pfrac, deg=5)[::-1]
    poly_pangle = np.polyfit(x, pangle, deg=5)[::-1]
    return ref_freq, I[0], polyI[1:], poly_pfrac, poly_pangle


def polcal_setjy(msname="", field_name="", n_threads=-1, ismms=True):
    """
    Setjy polcal fields (3C286 or 3C138)

    Parameters
    ----------
    msname : str
        Name of measurement set
    field : str, optional
        Field name
    n_threads : int, optional
        Number of OpenMP threads
    """
    limit_threads(n_threads=n_threads)
    from casatasks import setjy

    try:
        print(f"Polarization calibrator field name : {field_name}")
        if field_name in ["3C286", "1328+307", "1331+305", "J1331+3030"]:
            ref_freq, I, polyI, poly_pfrac, poly_pangle = get_polmodel_coeff(
                datadir + "/3C286_pol_model.txt"
            )
        elif field_name in ["3C138", "0518+165", "0521+166", "J0521+1638"]:
            ref_freq, I, polyI, poly_pfrac, poly_pangle = get_polmodel_coeff(
                datadir + "/3C138_pol_model.txt"
            )
        else:
            print("Field name is not either of the polcal, 3C286 or 3C138.")
            return 1
        print(f"Reference frequency: {ref_freq} GHz.")
        with suppress_output():
            setjy(
                vis=msname,
                field=field_name,
                scalebychan=True,
                standard="manual",
                fluxdensity=[I, 0.0, 0.0, 0.0],
                spix=polyI,
                reffreq=f"{ref_freq}GHz",
                polindex=poly_pfrac,
                polangle=poly_pangle,
                rotmeas=0,
                usescratch=True,
            )
    except Exception as e:
        traceback.print_exc()
    return


def phasecal_setjy(msname="", field="", ismms=False, n_threads=-1):
    """
    Setjy phasecal fields

    Parameters
    ----------
    msname : str
        Measurement set
    field : str, optional
        Phasecal fields
    ismms : bool, optional
        Is a multi-ms ot not
    n_threads : int, optional
        Number of OpenMP threads
    """
    limit_threads(n_threads=n_threads)
    from casatasks import setjy

    try:
        with suppress_output():
            setjy(
                vis=msname,
                field=field,
                standard="manual",
                fluxdensity=[1.0, 0, 0, 0],
                usescratch=True,
                ismms=ismms,
            )
    except Exception as e:
        traceback.print_exc()
    return


def import_fluxcal_models(mslist, fluxcal_fields, fluxcal_scans, ncpus=1, mem_frac=0.8):
    """
    Import model visibilities using crystalball

    Parameters
    ----------
    mslist : list
        List of sub-MS
    fluxcal_fields : list
        Fluxcal fields
    fluxcal_scans : dict
        Fluxcal scans dict
    ncpus : int
        Number of CPU threads to use
    mem_frac : float
        Memory fraction to use

    Returns
    -------
    int
        Success message
    """
    try:
        if len(fluxcal_fields) == 0:
            print("No flux calibrator scan is present.")
            return 1
        print("##############################")
        print("Import fluxcal models")
        print("##############################")
        bandname = get_band_name(mslist[0])
        cpu_count = psutil.cpu_count()
        ncpus = max(1, ncpus)
        ncpus = min(ncpus, cpu_count - 1)
        mem_frac = max(mem_frac, 0.8)
        scans = []
        for ms in mslist:
            ms_scans = get_ms_scans(ms)
            for s in ms_scans:
                scans.append(s)
        for fluxcal in fluxcal_fields:
            f_scan = fluxcal_scans[fluxcal]
            for s in f_scan:
                if s in scans:
                    pos = scans.index(s)
                    sub_msname = mslist[pos]
                    modelname = datadir + "/" + fluxcal + "_" + bandname + "_model.txt"
                    crys_cmd_args = [
                        "-sm " + modelname,
                        "-f " + fluxcal,
                        "-ns 1000",
                        "-j " + str(ncpus),
                        "-mf " + str(mem_frac),
                        sub_msname,
                    ]
                    cmd = ["crystalball"] + crys_cmd_args
                    cmd = " ".join(cmd)
                    print(f"Running: {cmd}")
                    tmpfile = f"tmp_{os.path.basename(sub_msname)}"
                    with suppress_output():
                        msg = os.system(f"{cmd} > {tmpfile}")
                    if os.path.exists(tmpfile):
                        os.remove(tmpfile)
                    if msg == 0:
                        print(f"Fluxcal model is imported successfully for scan: {s}.")
                    else:
                        print(f"Error in importing fluxcal model for scan: {s}.")
        return 0
    except Exception as e:
        print("Error in importing model.")
        traceback.print_exc()
        return 1


def import_phasecal_models(
    mslist,
    dask_client,
    phasecal_fields,
    phasecal_scans,
    workdir,
    cpu_frac=0.8,
):
    """
    Import model visibilities for phasecal

    Parameters
    ----------
    mslist : list
        List of sub-MS
    dask_client : dask.client
        Dask client
    phasecal_fields : list
        Phasecal fields
    phasecal_scans : list
        Phasecal scans
    workdir : str
        Work directory
    cpu_frac : float, optional
        CPU fraction to use

    Returns
    -------
    int
        Success message
    """
    try:
        if cpu_frac > 0.8:
            cpu_frac = 0.8
        total_cpu = max(1, int(psutil.cpu_count() * cpu_frac))
        print("##########################")
        print("Import phasecal models")
        print("##########################")
        scans = []
        for ms in mslist:
            ms_scans = get_ms_scans(ms)
            for s in ms_scans:
                scans.append(s)
        tasks = []
        total_scans = 0
        for phasecal in phasecal_fields:
            ph_scan = phasecal_scans[phasecal]
            for s in ph_scan:
                if s in scans:
                    total_scans += 1
        n_threads = max(1, int(total_cpu / total_scans))
        for phasecal in phasecal_fields:
            ph_scan = phasecal_scans[phasecal]
            for s in ph_scan:
                if s in scans:
                    pos = scans.index(s)
                    sub_msname = mslist[pos]
                    tasks.append(
                        delayed(phasecal_setjy)(
                            sub_msname,
                            field=phasecal,
                            ismms=True,
                            n_threads=n_threads,
                        )
                    )
        print("Start importing phasecal models...")
        results = list(dask_client.gather(dask_client.compute(tasks)))
        print("Phasecal models are initiated.")
        return 0
    except Exception as e:
        print("Error in initiaing phasecal models.")
        traceback.print_exc()
        return 1


def import_polcal_models(
    mslist,
    dask_client,
    polcal_fields,
    polcal_scans,
    workdir,
    cpu_frac=0.8,
):
    """
    Import model for polarization calibrators (3C286 or 3C138)

    Parameters
    ----------
    mslist : list
        List of sub-MS
    dask_client : dask.client
        Dask client
    polcal_fields : list
        Polcal fields
    polcal_scans : list
        Polcal scans
    workdir : str
        Work directory
    cpu_frac : float, optional
        CPU fraction to use

    Returns
    -------
    int
        Success message
    """
    try:
        if cpu_frac > 0.8:
            cpu_frac = 0.8
        total_cpu = max(1, int(psutil.cpu_count() * cpu_frac))
        if len(polcal_scans) == 0:
            print("No polarization calibrator scans is present.")
            return 1
        scans = []
        for ms in mslist:
            ms_scans = get_ms_scans(ms)
            for s in ms_scans:
                scans.append(s)
        tasks = []
        total_scans = 0
        for polcal_field in polcal_fields:
            p_scan = polcal_scans[polcal_field]
            for s in p_scan:
                if s in scans:
                    total_scans += 1
        n_threads = max(1, int(total_cpu / total_scans))
        for polcal_field in polcal_fields:
            p_scan = polcal_scans[polcal_field]
            for s in p_scan:
                if s in scans:
                    pos = scans.index(s)
                    sub_msname = mslist[pos]
                    tasks.append(
                        delayed(polcal_setjy)(
                            sub_msname, polcal_field, ismms=True, n_threads=n_threads
                        )
                    )
        print("Start importing polcal models...")
        results = list(dask_client.gather(dask_client.compute(tasks)))
        print("Polcal models imports are done.")
        return 0
    except Exception as e:
        traceback.print_exc()
        return 1


def import_all_models(msname, dask_client, workdir, cpu_frac=0.8, mem_frac=0.8):
    """
    Import all calibrator models

    Parameters
    ----------
    msname : str
        Measurement set name
    dask_client : dask.client
        Dask client
    workdir : str
        Work directory
    cpu_frac : float, optional
        CPU fraction to use
    mem_frac : float, optional
        Memory fraction to use

    Returns
    -------
    int
        Success message
    """
    cpu_threads = psutil.cpu_count()
    ncpu = int(cpu_threads * cpu_frac)
    mem_frac = 1 - mem_frac
    try:
        msname = msname.rstrip("/")
        correct_missing_col_subms(msname)
        mspath = os.path.dirname(os.path.abspath(msname))
        os.chdir(mspath)
        result = get_submsname_scans(msname)
        if result is not None:  # If multi-ms
            mslist, scans = result
        else:
            print("Please provide a multi-MS with scans partitioned.")
            return 1, 1, 1
        fluxcal_fields, fluxcal_scans = get_fluxcals(msname)
        phasecal_fields, phasecal_scans, phasecal_flux_list = get_phasecals(msname)
        polcal_fields, polcal_scans = get_polcals(msname)
        fluxcal_result = import_fluxcal_models(
            mslist, fluxcal_fields, fluxcal_scans, ncpus=ncpu, mem_frac=mem_frac
        )
        if fluxcal_result != 0:
            return fluxcal_result, 1, 1

        phasecal_result = import_phasecal_models(
            mslist,
            dask_client,
            phasecal_fields,
            phasecal_scans,
            workdir,
            cpu_frac=cpu_frac,
        )

        polcal_result = import_polcal_models(
            mslist,
            dask_client,
            polcal_fields,
            polcal_scans,
            workdir,
            cpu_frac=cpu_frac,
        )

        if phasecal_result != 0:
            print(
                "Phasecal model was not import, but fluxcal model import is successful."
            )

        if polcal_result != 0:
            print(
                "Polcal model was not imported, but fluxcal model import is successful."
            )
        return fluxcal_result, phasecal_result, polcal_result
    except Exception as e:
        traceback.print_exc()
        return 1, 1, 1


def main(
    msname,
    workdir="",
    cpu_frac=0.8,
    mem_frac=0.8,
    logfile=None,
    jobid=0,
    start_remote_log=False,
    dask_client=None,
):
    """
    Run the calibrator model import pipeline.

    Parameters
    ----------
    msname : str
        Path to the measurement set (MS) to process.
    workdir : str, optional
        Working directory for intermediate and output files. If empty, defaults
        to `<msname>/workdir`. Default is "".
    cpu_frac : float, optional
        Fraction of total CPU cores to use. Default is 0.8.
    mem_frac : float, optional
        Fraction of total system memory to use. Default is 0.8.
    logfile : str or None, optional
        Path to the logfile for logging messages. If None, logging to file is disabled.
    jobid : int, optional
        Job identifier for tracking and PID management. Default is 0.
    start_remote_log : bool, optional
        If True, enables remote logging based on credentials stored in the
        working directory. Default is False.
    dask_client : dask.client, optional
        Dask client

    Returns
    -------
    int
        Success message
    """
    pid = os.getpid()
    cachedir = get_cachedir()
    save_pid(pid, f"{cachedir}/pids/pids_{jobid}.txt")

    if workdir == "":
        workdir = os.path.dirname(os.path.abspath(msname)) + "/workdir"
    os.makedirs(workdir, exist_ok=True)

    ############
    # Logger
    ############
    observer = None
    if (
        start_remote_log
        and os.path.exists(f"{workdir}/jobname_password.npy")
        and logfile is not None
    ):
        time.sleep(5)
        jobname, password = np.load(
            f"{workdir}/jobname_password.npy", allow_pickle=True
        )
        if os.path.exists(logfile):
            observer = init_logger(
                "import_model", logfile, jobname=jobname, password=password
            )

    dask_cluster = None
    if dask_client is None:
        dask_client, dask_cluster, dask_dir = get_local_dask_cluster(
            2,
            dask_dir=workdir,
            cpu_frac=cpu_frac,
            mem_frac=mem_frac,
        )
        nworker = max(2, int(psutil.cpu_count() * cpu_frac))
        scale_worker_and_wait(dask_cluster, nworker)

    try:
        if msname and os.path.exists(msname):
            fluxcal_result, phasecal_result, polcal_result = import_all_models(
                os.path.abspath(msname),
                dask_client,
                workdir,
                cpu_frac=cpu_frac,
                mem_frac=mem_frac,
            )
            os.system("touch " + workdir + "/.fluxcal_" + str(fluxcal_result))
            os.system("touch " + workdir + "/.phasecal_" + str(phasecal_result))
            os.system("touch " + workdir + "/.polcal_" + str(polcal_result))
            if fluxcal_result == 1 or (
                fluxcal_result == 1 and phasecal_result == 1 and polcal_result == 1
            ):
                msg = 1
            else:
                msg = 0
        else:
            print("Please provide correct measurement set.")
            msg = 1
    except Exception as e:
        traceback.print_exc()
        os.system("touch " + workdir + "/.fluxcal_1")
        os.system("touch " + workdir + "/.phasecal_1")
        os.system("touch " + workdir + "/.polcal_1")
        msg = 1
    finally:
        time.sleep(5)
        drop_cache(msname)
        drop_cache(workdir)
        clean_shutdown(observer)
        if dask_cluster is not None:
            dask_client.close()
            dask_cluster.close()
            os.system(f"rm -rf {dask_dir}")
    return msg


def cli():
    usage = "Import calibrator models"
    parser = argparse.ArgumentParser(
        description=usage, formatter_class=SmartDefaultsHelpFormatter
    )

    # Essential parameters
    basic_args = parser.add_argument_group(
        "###################\nEssential parameters\n###################"
    )
    basic_args.add_argument("msname", type=str, help="Name of measurement set")
    basic_args.add_argument(
        "--workdir", type=str, default="", help="Name of work directory"
    )

    # Advanced parameters
    adv_args = parser.add_argument_group(
        "###################\nAdvanced parameters\n###################"
    )
    adv_args.add_argument(
        "--start_remote_log", action="store_true", help="Start remote logging"
    )

    # Resource management parameters
    hard_args = parser.add_argument_group(
        "###################\nHardware resource management parameters\n###################"
    )
    hard_args.add_argument(
        "--cpu_frac", type=float, default=0.8, help="CPU fraction to use"
    )
    hard_args.add_argument(
        "--mem_frac", type=float, default=0.8, help="Memory fraction to use"
    )
    hard_args.add_argument("--logfile", type=str, default=None, help="Log file")
    hard_args.add_argument("--jobid", type=int, default=0, help="Job ID")

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        return 1

    args = parser.parse_args()

    msg = main(
        msname=args.msname,
        workdir=args.workdir,
        cpu_frac=args.cpu_frac,
        mem_frac=args.mem_frac,
        logfile=args.logfile,
        jobid=args.jobid,
        start_remote_log=args.start_remote_log,
    )
    return msg


if __name__ == "__main__":
    result = cli()
    print(
        "\n###################\nVisibility simulation is finished.\n###################\n"
    )
    os._exit(result)
