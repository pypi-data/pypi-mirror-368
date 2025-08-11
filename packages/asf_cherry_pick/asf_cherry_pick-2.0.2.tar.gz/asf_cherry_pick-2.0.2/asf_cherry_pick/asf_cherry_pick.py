#!/usr/bin/env python3

"""

Script that can fetch part of zip file of sentinel1 data from ASF.

Requirement: have an access (ie login, passwd) at asf.

Algorithm:
=========

The algorithm is two folds:

    i) get the set of urls that matchs a given query. The goegraphical query is
    done through a kml file. A orbit has to be provided that allows to select
    either a ascending or descending track. A time range is also mandatory.
    ii) Downlowd from the url the data in the zip files that match the pattern.
    This can be used either to download only one tiff file (e.g. one polarisation, one subswath)
    or meta data like e.g. xml files.

Dependencies
============
The script depends upon the asf_search tool that can be installed using pypi.
The script also uses remotezip package, which has to be modified. We thus embed the modified version.


Examples:
=========

url.txt contains urls (one per line) that can be fetched from asf (like e.g. )
products contains safe names, one per line.
D041_S1_Mexique.kml is a kml containing a polygon that represent the region of interest



asf_cherry_pick --kml D041_S1_Mexique.kml -d 2019-01-30:2020-01-23  -c credentials.txt -v 4 -o D041 --saveproducts to_download.txt
asf_cherry_pick --urls url -c credentials.txt -o A0034
asf_cherry_pick --safelist products -c credentials.txt -o A0034


API example:
===========

import asf_search as asf
from fastkml import kml, geometry
import nsb_remotezip as remotezip
import flatsim_get_xml_from_kml as fx

picker = fx.AsfCherryPick()
roi = [(-98.82686004479159, 20.4077763126375),
       (-101.1931787671002, 20.81921608915112),
       (-101.8919952521377, 17.07545047337062),
       (-99.55373281701526, 16.60957331722261),
       (-98.82686004479159, 20.4077763126375)]
picker.search_urls(roi, 'D041', '2019-01-30', '2020-01-23')
print(f"urls= {picker.urls}")
picker.connect(user, passwd)
nb_processes = 4
picker.cherry_pick_all(target_dir, '(manifest.safe|s1.*xml$)', nb_processes)

"""

# classical imports
#        from IPython import embed; embed()

import argparse
import logging
import sys
from pathlib import Path
import multiprocessing
from multiprocessing import Pool
import re

import asf_search as asf
from fastkml import kml, geometry
import remotezip

logger = logging.getLogger(__name__)


class AsfCherryPick(object):

    """AsfCherryPick. A class for picking data at asf."""

    def __init__(self, temp_dir="./asf_tmp"):
        """Initialize the cherry picker
            :roi: (str) region of interest (format )
            :orbit: (str) orbit in the form D041
            :auth_file: (str) a file containing login passwd information
            :processes: (int) nb of download in //. all the cpus if None,
                        default=1
        """
        self.auth = None
        self.tempdir = Path(temp_dir)
        self.tempdir.mkdir(parents=True, exist_ok=True)
        # self.cookiejar = None
        # self.cookiejar_session = None

    def search_urls(self, roi, orbit, start_date='2014-09-01', end_date='2022-06-01'):
        """ search the urls that fit the requirements and updates self.urls member
        :roi: list of (lon, lat) tuple
        :orbit: (str) string of format like A001 of D089
        :start_date: (str) start date, format YYYY-MM-DD
        :end_date: (str) start date, format YYYY-MM-DD
        """
        roi_string = [(str(x[0]), str(x[1])) for x in roi]
        relative_orbit = orbit.lstrip('AD')
        direction = 'ASCENDING' if orbit[0] == 'A' else "DESCENDING"
        aoi = 'polygon((' + \
            ','.join([' '.join(x) for x in roi_string]) + \
            '))'
        opts = {
            'platform': asf.PLATFORM.SENTINEL1,
            'relativeOrbit': relative_orbit,
            'processingLevel': 'SLC',
            'beamMode': 'IW',
            'flightDirection': direction,
            'start': start_date+'T00:00:00Z',
            'end': end_date+'T23:59:59Z'
        }
        logger.debug(f'looking for {opts}')
        results = asf.geo_search(intersectsWith=aoi, **opts)
        logger.info(f"found {len(results)} results")
        self.urls = []
        for product in results:
            product_dict = product.geojson()
            self.urls.append(product_dict['properties']['url'])
        logger.info(f"found {self.urls}, {len(self.urls)} products")

    def connect(self, user, passwd):
        """Authenticate and update the session.

        :user: (str) the asf user
        :passwd: (str) the asf passwrd
        """
        self.auth = asf.ASFSession()
        self.auth.auth_with_creds(user, passwd)
        # self.cookiejar = self.auth.cookies
        # self.cookiejar_session = asf.ASFSession().auth_with_cookiejar(self.cookiejar)

    def cherry_pick_all(self, target_dir, pattern='(manifest.safe|annotation.*/s1.*.xml)', processes=None):
        """Fetch from the url the elemtents that matches pattern and send then in target dir.
           connect method should have been called and urls not empty.
           RuntimeError is raised if connect is not done.
           self.missings will be set to missings downloaded

        :target_dir: (str) target dir
        :pattern: (str) regex that will be used to compile the pattern
        :processes: (str) number of processes to run in parallel. Default use all available
        """
        if processes is None:
            self.nb_process = multiprocessing.cpu_count()
        else:
            self.nb_process = processes
        self.missings = []
        if self.auth is None:
            raise RuntimeError(("AsfCherryPick:cherry_pick_all called "
                                "but auth not set. Call the connect method "
                                "before calling the cherry_pick_all one"))
        parameters = []
        for url in self.urls:
            parameters.append((url, target_dir, pattern))
        if processes == 1:
            for parameter in parameters:
                self.cherry_pick(parameter)
        else:
            with Pool(processes=processes) as pool:
                pool.map(self.cherry_pick, parameters)

    def cherry_pick(self, parameters):
        """download data from parameters. parameters is a tuple containing
            an url, a taraget_dir and a pattern.
        """
        url, target_dir, pattern = parameters
        re_pattern = re.compile(pattern)
        my_missings = []
        with remotezip.RemoteZip(url, session=self.auth) as zip:
            for zip_info in zip.infolist():
                if re_pattern.search(str(zip_info.filename)):
                    logger.info(f'extracting {zip_info.filename}')
                    target = target_dir / Path(zip_info.filename)
                    if target.exists():
                        logger.info(f"{target} exists, skipping download")
                        continue
                    try:
                        zip.extract(zip_info.filename, path=self.tempdir)
                    except Exception as excpt:
                        logger.warning(f"Fail to extract {target}: {excpt}")
                        my_missings.append((url, target))
                        continue
                    temp_filename = self.tempdir / zip_info.filename
                    if not target.parent.exists():
                        target.parent.mkdir(parents=True, exist_ok=True)
                    temp_filename.rename(target)
        return my_missings


def get_roi_from_kml(kml_filename, padding=None):
    """Extract region of interest given the kml
    :returns:(list) bounding box as a list of (lon, lat) tuples
    """
    res = []
    with open(kml_filename) as kml_file:
        doc = kml_file.read().encode('utf-8')
    k = kml.KML()
    k.from_string(doc)
    for feature0 in k.features():
        print("{}, {}".format(feature0.name, feature0.description))
        for feature1 in feature0.features():
            logger.debug(f"found feature: {feature1}")
            if isinstance(feature1.geometry, geometry.Polygon):
                polygon = feature1.geometry
                res = [(x[0], x[1]) for x in polygon.exterior.coords]
    logger.info(f"polygon found before padding: {res}")
    if padding is not None:
        min_lat = min([x[1] for x in res])
        max_lat = max([x[1] for x in res])
        for idx, val in enumerate(res):
            if val[1] == min_lat:
                res[idx] = (res[idx][0], res[idx][1] - padding)
                continue
            if val[1] == max_lat:
                res[idx] = (res[idx][0], res[idx][1] + padding)
        logger.info(f"polygon found after padding of {padding} on lat. {res}")
    return res


def read_auth(filename):
    """ reads filename that contains authentification
    file is a text file with on line, containing login and password
    separated by a space.

    :param filename: the file that contains the credential
    :type filename: str
    :return: login,password
    :rtype: tuple
    """
    try:
        with open(filename, "r") as _f:
            (login, password) = _f.readline().split(' ')
            if password.endswith('\n'):
                password = password[:-1]
    except Exception as excpt:
        logger.critical(f"cannot read file {filename}: {excpt}")
        raise Exception(f"read_auth raised  {excpt}")
    return (login, password)


def main():
    parser = argparse.ArgumentParser(description="extract coordinate from kml and query asf to get elements matching the pattern")
    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument("--kml", type=str, help="input is a kml file. Geographic search")
    group.add_argument("--safelist", type=str,
                       help="input is a text file containing safe names")
    group.add_argument("--urls", type=str, help="input is a text file containing urls pointing to zip files")
    group.add_argument("--granules", type=str, help="input is a coma separated list of granule, e.g. safe name without .SAFE extension")
    parser.add_argument("-c", type=str,
                        help=("(str) file containing asf user credentials: "
                              "format: one line of the form user password"))
    parser.add_argument("-d", type=str, default='2014-09-01:2022-06-01',
                        help="(str) date range in the format. Default=%(default)s")
    parser.add_argument("-j", type=int, default=1,
                        help="(int) number of download to do in parallel, default=%(default)s")
    parser.add_argument("-m", type=float, default=0.3,
                        help="(float) adding a margin on the latitute as found in the xml. default=%(default)s")
    parser.add_argument("-o", type=str, default=None, help="(str) relative orbit number in the form of D041")
    parser.add_argument("-p", type=str, default='(manifest.safe|s1.*xml$)',
                        help='(str) regex for patterns. Default=%(default)s')
    parser.add_argument("-t", type=str, default='SAFES', help="(str) target dir. Default=%(default)s")
    parser.add_argument("--saveproducts", type=str, default=None,
                        help="(str) if set, filename in which we want to write the set of url found")
    parser.add_argument("-H", action="store_true",
                        help="provide more detailed help")
    parser.add_argument("-v", type=int, default=3,
                        help=("set logging level:"
                              "0 critical, 1 error, 2 warning,"
                              "3 info, 4 debug, default=info"))
    if "-H" in sys.argv:
        print(__doc__)

        sys.exit(0)

    args = parser.parse_args()
    logging_translate = [logging.CRITICAL, logging.ERROR, logging.WARNING,
                         logging.INFO, logging.DEBUG]
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging_translate[args.v])

    script_base_name = Path(__file__).name
    logger = logging.getLogger(script_base_name + ":main")
    cmd_line = ' '.join(sys.argv)
    logger.info(f"called as {cmd_line}")

    user, passwd = read_auth(args.c)

    target_dir = Path(args.t)
    target_dir.mkdir(parents=True, exist_ok=True)

    picker = AsfCherryPick()
    if args.kml is not None:
        orbit = args.o
        if orbit is None:
            logger.error("orbit should be provided when searching using kml")
            sys.exit(1)
        if orbit[0] != 'A' and orbit[0] != 'D':
            logger.error(('wrong format for relative orbit. Should be of the form'
                          f'D0041 or A0034, got {args.o}'))
            sys.exit(1)
        roi = get_roi_from_kml(args.kml, padding=args.m)
        if len(roi) == 0:
            logger.error("Cannot extract region interest from kml, aborting")
            sys.exit(1)
        logger.info(f"Extracted region of interest (lon,lat, alt): {roi}")
        picker.search_urls(roi, orbit, args.d.split(":")[0], args.d.split(":")[1])
    if args.urls is not None:
        with open(args.urls, "r") as _url:
            refs_url = [line.strip() for line in _url]
            picker.urls = refs_url
    if args.granules or args.safelist:
        refs_products = []
        if args.granules:
            refs_products = args.granules.split(",")
        if args.safelist:
            with open(args.safelist, "r") as _url:
                refs_products = [line.strip() for line in _url]
        search_results = asf.granule_search(refs_products)
        refs_url = []
        for product in search_results:
            product_dict = product.geojson()
            if product_dict['properties']['url'].endswith(".zip"):
                refs_url.append(product_dict['properties']['url'])
        picker.urls = refs_url
    logger.info(f"fetching urls: {picker.urls}")
    if args.saveproducts is not None:
        with open(args.saveproducts, "w") as _urls:
            for url in picker.urls:
                _urls.write(f"{url}\n")
    picker.connect(user, passwd)
    picker.cherry_pick_all(target_dir, args.p, args.j)


if __name__ == "__main__":
    sys.exit(main())
