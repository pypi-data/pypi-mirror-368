#!/usr/bin/env python3

#Auteur : Pierre Koclas, May 2021
import os
import sys
import csv
from math import floor,ceil,sqrt
import matplotlib as mpl
mpl.use('Agg')
#import pylab as plt
import matplotlib.pylab as plt
import numpy as np
import matplotlib.colorbar as cbar
import matplotlib.cm as cm
import datetime
import cartopy.crs as ccrs
import cartopy.feature
#from cartopy.mpl.ticker    import LongitudeFormatter,  LatitudeFormatter
import matplotlib.colors as colors
#import matplotlib.patches as mpatches
from matplotlib.colors import ListedColormap, LinearSegmentedColormap
import sqlite3
from matplotlib.collections import PatchCollection
from statistics import median
import pikobs
import optparse
from mpl_toolkits.axes_grid1 import make_axes_locatable
def projectPpoly(PROJ,lat,lon,deltax,deltay,pc):
        X1,Y1  = PROJ.transform_point(lon - deltax,lat-deltay,pc )
        X2,Y2  = PROJ.transform_point(lon - deltax,lat+deltay,pc )
        X3,Y3  = PROJ.transform_point(lon + deltax,lat+deltay,pc )
        X4, Y4 = PROJ.transform_point(lon + deltax,lat-deltay,pc )
        Pt1=[ X1,Y1 ]
        Pt2=[ X2,Y2 ]
        Pt3=[ X3,Y3 ]
        Pt4=[ X4,Y4 ]
        Points4 = [ Pt1, Pt2,Pt3,Pt4 ]
           
        return Points4
def SURFLL(lat1,lat2,lon1,lon2):
#= (pi/180)R^2 |sin(lat1)-sin(lat2)| |lon1-lon2|
    R=6371.
    lat2=min(lat2,90.)
    surf=R*R*(np.pi/180.)*abs ( np.sin(lat2*np.pi/180.) - np.sin(lat1*np.pi/180.) ) *abs( lon2-lon1 )
   # if ( surf == 0.):
    # print (   ' surf=',lat1,lat2,lat2*np.pi/180.,lat1*np.pi/180.,np.sin(lat2*np.pi/180.) ,  np.sin(lat1*np.pi/180.) )
    return surf

def NPSURFLL(lat1, lat2, lon1, lon2):
    R = 6371.
    lat2 = np.minimum(lat2, 90.)
    surf = R**2 * (np.pi/180) * np.abs(np.sin(lat2*np.pi/180) - np.sin(lat1*np.pi/180)) * np.abs(lon2 - lon1)
  #  if np.any(surf == 0.):
    #    print('surf contiene valores cero')
    return surf
def SURFLL2(lat1, lat2, lon1, lon2):
    R = 6371.0
    lat2 = np.minimum(lat2, 90.0)
    surf = R * R * (np.pi / 180.0) * np.abs(np.sin(lat2 * np.pi / 180.0) - np.sin(lat1 * np.pi / 180.0)) * np.abs(lon2 - lon1)
    # Debugging print statements if surface is zero
    zero_surf_indices = (surf == 0.0)
    if np.any(zero_surf_indices):
        print('surf=', lat1[zero_surf_indices], lat2[zero_surf_indices], lat2[zero_surf_indices] * np.pi / 180.0,
              lat1[zero_surf_indices] * np.pi / 180.0,
              np.sin(lat2[zero_surf_indices] * np.pi / 180.0),
              np.sin(lat1[zero_surf_indices] * np.pi / 180.0))
    return surf
import pikobs
import pikobs

import pikobs

import pikobs
import pikobs

import pikobs

def zone_ploat(
    mode,
    region,
    family,
    id_stn,
    datestart,
    dateend,
    Points,
    boxsizex,
    boxsizey,
    proj,
    pathwork,
    flag_criteria,
    fonction,
    vcoord,
    filesin,
    namesin,
    varno,
    intervales
):
    import pandas as pd
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    from matplotlib.collections import PatchCollection
    from matplotlib import cm, colors, colorbar
    import numpy as np
    import sqlalchemy
    import os
    from matplotlib.colors import ListedColormap, BoundaryNorm
    
    method = 1
    vcoord_type = 'Channel'
    if family=='sw':
      vcoord_type = 'Pressure(Hpa)'

    debut = datestart
    final = dateend
    sqlite_files = filesin
    os.makedirs(pathwork, exist_ok=True)

    def load_data(sqlite_file):
        engine = sqlalchemy.create_engine(f"sqlite:///{sqlite_file}")
        query = f"""
        SELECT
            id_stn, varno,
            vcoord AS vcoord_bin,
            round(lat/1.0)*1.0 AS lat_bin,
            SUM(sumy)*1.0/SUM(N) AS omp,
            SQRT(SUM(sumy2)*1.0/SUM(N) - POWER(SUM(sumy)*1.0/SUM(N), 2)) AS sigma,
            SUM(N) AS n_obs
        FROM moyenne
        WHERE
            varno = {varno}
            AND id_stn = '{id_stn}'
            AND sumy IS NOT NULL
            AND date BETWEEN '{debut}' AND '{final}'
        GROUP BY id_stn, varno, vcoord_bin, lat_bin
        HAVING COUNT(*) > 1
        ORDER BY vcoord_bin DESC, lat_bin
        """
        return pd.read_sql_query(query, engine)

    # -- FUNCION PARA CREAR UNA COLORBAR DIVERGENTE CON GRIS EN 0 --
    def custom_div_cbar(bounds, cmap_name='seismic', center_color=[0.7,0.7,0.7,1]):
        n_bins = len(bounds) - 1
        ncolors = 2 * n_bins + 1  # impar
        base = cm.get_cmap(cmap_name, ncolors)
        color_arr = base(np.linspace(0,1,ncolors)).copy()
        # El bin central (el que contiene 0) es el de la mitad inferior de n_bins
        zero_bin = np.searchsorted(bounds, 0) - 1
        color_arr[zero_bin + n_bins - (n_bins//2)]# = center_color
        cmap_out = ListedColormap(color_arr[n_bins - (n_bins//2) : n_bins + (n_bins//2) + 1])
        norm = BoundaryNorm(bounds, cmap_out.N)
        return cmap_out, norm

    print("[INFO] Loading data from SQLite file(s)")
    df1 = load_data(sqlite_files[0])

    if len(sqlite_files) == 2:
        df2 = load_data(sqlite_files[1])
        df = pd.merge(
            df2, df1,
            on=['id_stn', 'varno', 'vcoord_bin', 'lat_bin'],
            suffixes=('_exp', '_ctl')
        )
        # DIFERENCIAS SIMPLES
        df['omp'] = df['omp_ctl'] - df['omp_exp']
        df['sigma'] = df['sigma_ctl'] - df['sigma_exp']
        df['n_obs'] = df['n_obs_ctl'] - df['n_obs_exp']

        # --------- ESCALAS SIMÉTRICAS ---------
        # OMP (puedes ajustar los positivos según tus datos)
        bounds_omp_pos = np.array([0.05, 0.1, 0.2, 0.5, 1, 2, 5])
        bounds_omp = np.concatenate((-bounds_omp_pos[::-1], bounds_omp_pos))  # simétrica

        # SIGMA (sólo ejemplo)
        bounds_sigma_pos = np.array([0.05, 0.1, 0.2, 0.5, 1])
        bounds_sigma = np.concatenate((-bounds_sigma_pos[::-1], bounds_sigma_pos))

        # n_obs (de tu ejemplo)
        bounds_nobs_pos = np.array([1, 5, 10, 20, 50, 100, 200])
        bounds_nobs = np.concatenate((-bounds_nobs_pos[::-1], bounds_nobs_pos))

        cmap_omp, norm_omp = custom_div_cbar(bounds_omp, cmap_name='seismic', center_color=[0.7,0.7,0.7,1])
        cmap_sigma, norm_sigma = custom_div_cbar(bounds_sigma, cmap_name='PuOr', center_color=[0.7,0.7,0.7,1])
        cmap_nobs, norm_nobs = custom_div_cbar(bounds_nobs, cmap_name='coolwarm', center_color=[0.7,0.7,0.7,1])

    else:
        df = df1.copy()
  # --------- ESCALAS SIMÉTRICAS ---------
        # OMP (puedes ajustar los positivos según tus datos)
        bounds_omp_pos = np.array([0.05, 0.1, 0.2, 0.5, 1, 2, 5])
        bounds_omp = np.concatenate((-bounds_omp_pos[::-1], bounds_omp_pos))  # simétrica

        # SIGMA (sólo ejemplo)
        bounds_sigma = np.array([0., 0.1, 0.2, 0.5, 1,2,4,5,6])

        # n_obs (de tu ejemplo)
        bounds_nobs_pos = np.array([1, 5, 10, 20, 50, 100, 200])
        bounds_nobs = np.concatenate((-bounds_nobs_pos[::-1], bounds_nobs_pos))
        bounds_nobs = [1, 50, 100, 500, 1000, 2000, 4000, 10000, 24000, 100000]
        cmap_omp, norm_omp = custom_div_cbar(bounds_omp, cmap_name='seismic', center_color=[0.7,0.7,0.7,1])
        cmap_sigma, norm_sigma = custom_div_cbar(bounds_sigma, cmap_name='PuOr', center_color=[0.7,0.7,0.7,1])
        cmap_nobs, norm_nobs = custom_div_cbar(bounds_nobs, cmap_name='jet', center_color=[0.7,0.7,0.7,1])
        import matplotlib.cm as cm

        Ninterv=10
        cmap_nobs = cm.get_cmap('jet', lut=Ninterv)
        norm_nobs = cm.colors.Normalize(vmin=1, vmax=100000)
        y1=[1,50,100,500,1500,2000,4000,10000,16000,24000,100000]

       



    if df.empty:
        print("[WARNING] No data retrieved from database.")
        return

    lat   = df['lat_bin'].values
    vcrd  = df['vcoord_bin'].values
    if family=='sw':
       vcrd  = df['vcoord_bin'].values/100.

    n_obs = df['n_obs'].values
    omp   = df['omp'].values
    sigma = df['sigma'].values

    Delt_LAT = 2
    DeltP = 0.5
    if family=='sw':
       Delt_LAT = 2
       DeltP = 20

    vcoord_min_plot = vcrd.min()
    vcoord_max_plot = vcrd.max()
    lat_min, lat_max = -90, 90

    configs = []
    if len(sqlite_files) == 2:
        configs = [
            {
                'Var': sigma,
                'Nomvar': 'Standard Deviation (DIFF abs(sigma_clt)-abs(sigma_exp) )',
                'cmap': cmap_sigma,
                'norm': norm_sigma,
                'bounds': bounds_sigma,
                'file': os.path.join(pathwork+'/'+family, f'scatterplot_{namesin[0]}_{namesin[1]}_sigma_var{varno}_{id_stn}.png')
            },
            {
                'Var': n_obs,
                'Nomvar': 'Number Of Observations (DIFF n_ctl-n_exp)',
                'cmap': cmap_nobs,
                'norm': norm_nobs,
                'bounds': bounds_nobs,
                'file': os.path.join(pathwork+'/'+family, f'scatterplot_{namesin[0]}_{namesin[1]}_nobs_var{varno}_{id_stn}.png')
            },
            {
                'Var': omp,
                'Nomvar': 'O - P (Bias) (DIFF abs(Bias_clt)-abs(Bias_exp) )',
                'cmap': cmap_omp,
                'norm': norm_omp,
                'bounds': bounds_omp,
                'file': os.path.join(pathwork+'/'+family, f'scatterplot_{namesin[0]}_{namesin[1]}_omp_var{varno}_{id_stn}.png')
            },
        ]
    else:
        configs = [
            {
                'Var': sigma,
                'Nomvar': 'Standard Deviation',
                'cmap': cmap_sigma,
                'norm': norm_sigma,
                'bounds': None,
                'y1':y1,

                'file': os.path.join(pathwork+'/'+family, f'scatterplot_{namesin[0]}_sigma_var{varno}_{id_stn}.png')
            },
            {
                'Var': n_obs,
                'Nomvar': 'Number Of Observations',
                'cmap': cmap_nobs,
                'norm': norm_nobs,
                'bounds': None,
                'y1':y1,
                'file': os.path.join(pathwork+'/'+family, f'scatterplot_{namesin[0]}_nobs_var{varno}_{id_stn}.png')
            },
            {
                'Var': omp,
                'Nomvar': 'O - P (Bias)',
                'cmap': cmap_omp,
                'norm': norm_omp,
                'bounds': None,
                'y1':y1,
                'file': os.path.join(pathwork+'/'+family, f'scatterplot_{namesin[0]}_omp_var{varno}_{id_stn}.png')
            },
        ]

    for conf in configs:
        Var    = conf['Var']
        Nomvar = conf['Nomvar']
        cmap   = conf['cmap']
        norm   = conf['norm']
        bounds = conf.get('bounds', None)
        output_file =conf['file']
        y1=conf['y1']


        fig, ax = plt.subplots(figsize=(14, 7))

        ax.set_xlim(lat_min, lat_max)
        if vcoord_type.lower() == 'Channel':
            ax.set_ylim(vcoord_max_plot, vcoord_min_plot)
        else:
            vcoord_min, vcoord_max = min(vcrd) - DeltP / 2.0, max(vcrd) + DeltP / 2.0
            ax.set_ylim(vcoord_min, vcoord_max)
            if family=='sw':
                 ax.set_ylim(1000, 0)


        # Ticks, colores y mapeo
        if bounds is not None:
            y1 = bounds
        else:
            y1 = np.linspace(np.nanmin(Var), np.nanmax(Var), 12)
        mappable = cm.ScalarMappable(norm=norm, cmap=cmap)
        Colors = [mappable.to_rgba(x) for x in y1]
        inds = np.digitize(Var, y1)

        rects = []
        for i in range(len(n_obs)):
            if not np.isnan(Var[i]):
                val = Var[i]
                if bounds is not None and (val < bounds[0] or val > bounds[-1]):
                    FC = '#FF00FF'
                else:
                    idx = max(0, min(inds[i] - 1, len(Colors) - 1))
                    FC = Colors[idx]
                top = vcrd[i] - DeltP / 2.0
                bottom =  vcrd[i] + DeltP / 2.0
                height = bottom - top
                if height > 0:
                    rect = Rectangle(
                        (lat[i] - Delt_LAT / 2.0, top),
                        Delt_LAT, height, facecolor=FC, edgecolor=FC
                    )
                    rects.append(rect)

        col = PatchCollection(rects, match_original=True)
        ax.add_collection(col)

        ax.set_xlabel('Latitude')
        ax.set_ylabel(f'{vcoord_type}')
        ax.set_title(f'{Nomvar} vs Latitude and {vcoord_type}\nvarno={varno}, id_stn={id_stn}')
        ax.grid(True, color='k')

        left, bottom, width, length = 0.91, 0.15, 0.02, 0.70
        ax_cb = fig.add_axes([left, bottom, width, length])
        if bounds is not None:
            print ("=====================")
            cb2 = colorbar.ColorbarBase(ax_cb, cmap=cmap, norm=norm,
                                        boundaries=bounds,
                                        orientation='vertical', extend='max', ticks=y1)
        else: 
            print ("1111=====================")
            cb2 = colorbar.ColorbarBase(ax_cb, cmap=cmap, norm=norm,
                                        orientation='vertical', extend='max',
                                        spacing='proportional',  ticks=y1)
        cb2.set_label(Nomvar)

        plt.savefig(output_file, format='png')
        plt.close(fig)
        print(f"[INFO] Plot saved to {output_file}")

def zone_plot(
    mode,
    region,
    family,
    id_stn,
    datestart,
    dateend,
    Points,
    boxsizex,
    boxsizey,
    proj,
    pathwork,
    flag_criteria,
    fonction,
    vcoord,
    filesin,
    namesin,
    varno,
    intervales
):
    import pandas as pd
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    from matplotlib.collections import PatchCollection
    from matplotlib import cm, colors, colorbar
    import numpy as np
    import sqlalchemy
    import os
    from matplotlib.colors import ListedColormap, BoundaryNorm

    method = 1
    vcoord_type = 'Channel'
    if family == 'sw':
        vcoord_type = 'Pressure(Hpa)'

    debut = datestart
    final = dateend
    sqlite_files = filesin
    os.makedirs(pathwork, exist_ok=True)
    os.makedirs(os.path.join(pathwork, family), exist_ok=True)

    def load_data(sqlite_file):
        engine = sqlalchemy.create_engine(f"sqlite:///{sqlite_file}")
        query = f"""
        SELECT
            id_stn, varno,
            vcoord AS vcoord_bin,
            round(lat/1.0)*1.0 AS lat_bin,
            SUM(sumy)*1.0/SUM(N) AS omp,
            SQRT(SUM(sumy2)*1.0/SUM(N) - POWER(SUM(sumy)*1.0/SUM(N), 2)) AS sigma,
            SUM(N) AS n_obs
        FROM moyenne
        WHERE
            varno = {varno}
            AND id_stn = '{id_stn}'
            AND sumy IS NOT NULL
            AND date BETWEEN '{debut}' AND '{final}'
        GROUP BY id_stn, varno, vcoord_bin, lat_bin
        HAVING COUNT(*) > 1
        ORDER BY vcoord_bin DESC, lat_bin
        """
        return pd.read_sql_query(query, engine)

    def custom_div_cbar(bounds, cmap_name='seismic', center_color=[0.7, 0.7, 0.7, 1]):
        n_bins = len(bounds) - 1
        ncolors = 2 * n_bins + 1
        base = cm.get_cmap(cmap_name, ncolors)
        color_arr = base(np.linspace(0, 1, ncolors)).copy()
        zero_bin = np.searchsorted(bounds, 0) - 1
        cmap_out = ListedColormap(color_arr[n_bins - (n_bins // 2): n_bins + (n_bins // 2) + 1])
        norm = BoundaryNorm(bounds, cmap_out.N)
        return cmap_out, norm

    df1 = load_data(sqlite_files[0])

    if len(sqlite_files) == 2:
        df2 = load_data(sqlite_files[1])
        df = pd.merge(df2, df1, on=['id_stn', 'varno', 'vcoord_bin', 'lat_bin'], suffixes=('_exp', '_ctl'))
        df['omp'] = df['omp_ctl'] - df['omp_exp']
        df['sigma'] = df['sigma_ctl'] - df['sigma_exp']
        df['n_obs'] = df['n_obs_ctl'] - df['n_obs_exp']

        bounds_omp_pos = np.array([0.05, 0.1, 0.2, 0.5, 1, 2, 5])
        bounds_omp = np.concatenate((-bounds_omp_pos[::-1], bounds_omp_pos))
        bounds_sigma_pos = np.array([0.05, 0.1, 0.2, 0.5, 1])
        bounds_sigma = np.concatenate((-bounds_sigma_pos[::-1], bounds_sigma_pos))
        bounds_nobs_pos = np.array([1, 50, 100, 500 ])
        bounds_nobs = np.concatenate((-bounds_nobs_pos[::-1], bounds_nobs_pos)) 
        cmap_sigma, norm_sigma = custom_div_cbar(bounds_sigma, 'PuOr')
        cmap_omp, norm_omp = custom_div_cbar(bounds_omp, 'seismic')
        cmap_nobs = cm.get_cmap('jet', len(bounds_nobs) - 1)
        norm_nobs = BoundaryNorm(bounds_nobs, cmap_nobs.N)

    else:
        df = df1.copy()
        bounds_omp_pos = np.array([0.05, 0.1, 0.2, 0.5, 1, 2, 5])
        bounds_omp = np.concatenate((-bounds_omp_pos[::-1], bounds_omp_pos))
        bounds_sigma = np.array([0., 0.1, 0.2, 0.5, 1, 2, 4, 5, 6])
        bounds_nobs = [1, 50, 100, 500, 1000, 2000, 4000, 10000, 24000, 100000]

        cmap_omp, norm_omp = custom_div_cbar(bounds_omp, 'seismic')
        cmap_sigma, norm_sigma = custom_div_cbar(bounds_sigma, 'PuOr')
        cmap_nobs = cm.get_cmap('jet', len(bounds_nobs) - 1)
        norm_nobs = BoundaryNorm(bounds_nobs, cmap_nobs.N)

    if df.empty:
        print("[WARNING] No data retrieved from database.")
        return

    lat = df['lat_bin'].values
    vcrd = df['vcoord_bin'].values / 100. if family == 'sw' else df['vcoord_bin'].values
    omp = df['omp'].values
    sigma = df['sigma'].values
    n_obs = df['n_obs'].values

    Delt_LAT, DeltP = (2, 20) if family == 'sw' else (2, 0.5)
    vcoord_min_plot, vcoord_max_plot = vcrd.min(), vcrd.max()
    lat_min, lat_max = -90, 90

    variables = [
        ('sigma', sigma, 'Standard Deviation', cmap_sigma, norm_sigma, bounds_sigma),
        ('nobs', n_obs, 'Number Of Observations', cmap_nobs, norm_nobs, bounds_nobs),
        ('omp', omp, 'O - P (Bias)', cmap_omp, norm_omp, bounds_omp)
    ]

    for name, var, label, cmap, norm, bounds in variables:
        fig, ax = plt.subplots(figsize=(14, 7))
        ax.set_xlim(lat_min, lat_max)
        if vcoord_type.lower() == 'channel':
            ax.set_ylim(vcoord_max_plot, vcoord_min_plot)
        else:
            ax.set_ylim(1000, 0) if family == 'sw' else ax.set_ylim(vcoord_min_plot, vcoord_max_plot)

        mappable = cm.ScalarMappable(norm=norm, cmap=cmap)
        colors_list = [mappable.to_rgba(x) for x in bounds]
        inds = np.digitize(var, bounds)

        rects = []
        for i in range(len(var)):
            if not np.isnan(var[i]):
                val = var[i]
                if val < bounds[0] or val > bounds[-1]:
                    FC = '#FF00FF'
                else:
                    idx = max(0, min(inds[i] - 1, len(colors_list) - 1))
                    FC = colors_list[idx]
                rect = Rectangle(
                    (lat[i] - Delt_LAT / 2.0, vcrd[i] - DeltP / 2.0),
                    Delt_LAT, DeltP,
                    facecolor=FC, edgecolor=FC
                )
                rects.append(rect)

        ax.add_collection(PatchCollection(rects, match_original=True))
        ax.set_xlabel('Latitude')
        ax.set_ylabel(vcoord_type)
        ax.set_title(f'{label} vs Latitude and {vcoord_type} from {datestart} to {dateend},\nvarno={varno}, id_stn={id_stn}')
        ax.grid(True, color='k')

        cax = fig.add_axes([0.91, 0.15, 0.02, 0.7])
        cb = colorbar.ColorbarBase(cax, cmap=cmap, norm=norm, boundaries=bounds,
                                   orientation='vertical', ticks=bounds)
        cb.set_label(label)

        output_file = os.path.join(pathwork, family, f'scatterplot_{"_".join(namesin)}_{name}_var{varno}_{id_stn}.png')
        plt.savefig(output_file, format='png')
        plt.close(fig)

