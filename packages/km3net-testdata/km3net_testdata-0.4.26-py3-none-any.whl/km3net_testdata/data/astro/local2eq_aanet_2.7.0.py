"""
This script is used to generate the local2eq*.csv files.
"""
import datetime
import numpy as np
import pandas as pd
from km3net_testdata import data_path

import aa, ROOT
from ROOT import EventFile, EquatorialCoords, Det, Vec

def main():
    timespan = 3*60*60*24  # [s]
    n_datapoints = 20
    times = np.linspace(0, timespan, n_datapoints, dtype=int)
    d = ROOT.Det(data_path("detx/KM3NeT_00000133_20221025.detx"))

    outfile = open("local2eq_aanet_2.7.0.csv", "w")
    outfile.write("dx,dy,dz,")
    outfile.write("phi,theta,azimuth,zenith,")
    outfile.write("utm_easting,utm_northing,utm_z,utm_zone,utm_reference_elipsoid,")
    outfile.write("det_latitude,det_longitude,meridian_convergence,")
    outfile.write("year,month,day,hour,min,sec,")
    outfile.write("eq_ra,eq_dec,gal_lon,gal_lat,")
    outfile.write("y2000\n")

    month = 1
    day = 1
    hour = 12
    min = 0
    sec = 0

    for v in [Vec(0, 0, -1), Vec(0, 1, 0), Vec(1, 0, 0), Vec(-1.2, 3.4, -5.6).normalize()]:
        for year in [2000, 2010, 2025]:
            starttime = datetime.datetime(year, month, day, hour, min, sec).replace(tzinfo=datetime.timezone.utc).timestamp()
            for j2000 in (True, False):
                for t in times:
                    timestamp = ROOT.TTimeStamp(int(starttime+t))
                    coords = EquatorialCoords(d, v, timestamp, j2000)
                    gal = ROOT.sla.eqgal(coords.ra(), coords.dec())

                    outfile.write(f"{v.x},{v.y},{v.z},")
                    outfile.write(f"{v.phi()},{v.theta()},{(-v).phi()},{(-v).theta()},")
                    outfile.write(f"{d.utm_ref_easting},{d.utm_ref_northing},{d.utm_ref_z},{d.utm_zone},{d.utm_reference_elipsoid},")
                    outfile.write(f"{d.latitude},{d.longitude},{d.meridian_convergence_angle},")
                    outfile.write(f"{year},{month},{day},{hour},{min},{sec},")
                    outfile.write(f"{coords.ra()},{coords.dec()},{gal.DL},{gal.DB},")
                    outfile.write(f"{j2000}\n")

    outfile.close()

if __name__ == "__main__":
    main()
