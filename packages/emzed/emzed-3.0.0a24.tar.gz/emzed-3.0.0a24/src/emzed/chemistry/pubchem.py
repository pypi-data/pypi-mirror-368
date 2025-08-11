import functools
import glob
import gzip
import json
import os
import re
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pprint import pprint

import requests
from requests.exceptions import RequestException

import emzed
from emzed.chemistry.elements import masses
from emzed.config import folders

EINFO_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/einfo.fcgi"
ESEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
ESUMMARY_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"

SUMMARY_URL = "http://pubchem.ncbi.nlm.nih.gov/summary/summary.cgi"

CHUNK_SIZE_IDS_PUBCHEM = 500

DEFAULT_SEARCH_TERM = (
    "((0:0[TotalFormalCharge])"
    'AND ( ("KEGG"[SourceName]) '
    'OR ("Human Metabolome Database"[SourceName])'
    'OR "(Biocyc"[SourceName]) ))'
)

TO_EXTRACT = [
    ("cid", int),
    ("molecularweight", float),
    ("molecularformula", str),
    ("iupacname", str),
    ("synonymlist", list),
    ("inchi", str),
    ("inchikey", str),
    ("canonicalsmiles", str),
]

# names must correspond to names in COL_NAMES:
IN_SUMMARY = [f for (f, t) in TO_EXTRACT] + ["is_in_kegg", "is_in_hmdb", "is_in_biocyc"]

# names must correspond to names in IN_SUMMARY:
COL_NAMES = [
    "cid",
    "mw",
    "mf",
    "iupac",
    "synonyms",
    "inchi",
    "inchikey",
    "smiles",
    "is_in_kegg",
    "is_in_hmdb",
    "is_in_biocyc",
]

COL_TYPES = [str, float, str, str, str, str, str, str, bool, bool, bool]


SPECIAL_COL_FORMATS = {"mw": "%9.4f"}


assert len(IN_SUMMARY) == len(COL_NAMES), "internal error"
assert len(IN_SUMMARY) == len(COL_TYPES), "internal error"
assert all(k in COL_NAMES for k in SPECIAL_COL_FORMATS.keys()), "internal error"


def retry(n):
    def decorator(function):
        @functools.wraps(function)
        def wrapped(*a, **kw):
            for _ in range(n - 1):
                try:
                    return function(*a, **kw)
                except Exception:
                    time.sleep(1.0)

            return function(*a, **kw)

        return wrapped

    return decorator


class PubChemAccessor:
    def __init__(self):
        self.api_key = _get_pubchem_api_key()
        self.email = _get_pubchem_email()

    def get_count(self, search_term=None):
        """Count number of compuouds for given search term.

        :param search_term: In case search term is not provided we search for compounds
                            which are from KEGG, HMDB or Biocyc and carry no charge.
                            For more complicated searches, like restricting the search
                            term only for some fields, the term can be constructed
                            manually by using the search form at
                            https://www.ncbi.nlm.nih.gov/pccompound/advanced

        :returns: integer number
        """

        if search_term is None:
            search_term = DEFAULT_SEARCH_TERM
        r = self._get(ESEARCH_URL, db="pccompound", rettype="count", term=search_term)
        self._check(r, "count")
        result = self._extract_esearch_result(r)
        return int(result["count"])

    def get_identifiers(self, start=0, end=1_000_000, search_term=None, source=None):
        """Get compuoud identifiers for given search term. These can be used later
        for retrieving details of compounds.

        :param start:  fetch results starting and given index
        :param end:    fetch results up to given index
        :param search_term: In case search term is not provided we search for compounds
                            which comd from KEGG, HMDB or Biocyc and carry no charge.
                            For more complicated searches, like restricting the search
                            term only for some fields, the term can be constructed
                            manually by using the search form at
                            https://www.ncbi.nlm.nih.gov/pccompound/advanced

        :param source: in case the user does not provie a search term on can restrict
                    fetching user ids from specified source, like 'HMDB' only.

        :returns: list of strings

        """
        if search_term is not None and source is not None:
            raise ValueError("you can not provide search_term and source together")
        if source is not None:
            search_term = f'((0:0[TotalFormalCharge]) AND ( ("{source}"[SourceName]) ))'
        elif search_term is None:
            search_term = DEFAULT_SEARCH_TERM
        r = self._get(
            ESEARCH_URL,
            db="pccompound",
            rettype="uilist",
            term=search_term,
            retmax=end - start,
            retstart=start,
        )
        self._check(r, "compound ids")
        result = self._extract_esearch_result(r)
        return result["idlist"]

    def get_summary_data(self, ids):
        """Fetches data for given compound ids.

        :param ids: list of compound ids. you can use get_identifiers to dermine
                    identifiers by searching for terms and meta data first.

        :returns: dictionary mapping each id to a dictionary with keys 'cid',
                'molecularweight', 'molecularformula', 'iupacname', 'inchi', 'inchikey',
                'canonicalsmiles' and 'synonymlist'.
        """

        id = ",".join(str(id_) for id_ in ids)
        r = self._post(ESUMMARY_URL, db="pccompound", payload=f"id={id}")
        try:
            r.raise_for_status()
        except RequestException as e:
            e = requests.utils.unquote(str(e))
            raise OSError(
                self._fmt_error("retrieving summary data failed", e)
            ) from None

        result = self._extract_esummary_result(r)

        data = {}
        for id_ in ids:
            entry = result.get(id_)
            if not entry:
                continue
            data[id_] = {field: type_(entry[field]) for field, type_ in TO_EXTRACT}

        return data

    def register_pubchem_api_key(self, email_address, api_key, *, overwrite=False):
        """
        The api key is required if you want to donwload larger amounts of data or if
        you make more than 3 requests per second.

        1. You have to create a user accout at https://www.ncbi.nlm.nih.gov

        2. To create the key, go to the “Settings” page of your NCBI account. (Hint:
           after signing in, simply click on your NCBI username in the upper right
           corner of any NCBI page.)

        3. You’ll see a new “API Key Management” area. Click the “Create an API Key”
           button, and copy the resulting key.

        :param email_address: your valid email address.

        :param api_key: valid API key

        :param overwrite: overwrite existing data.
        """

        if not _check_email_address(email_address):
            raise ValueError("malformatted email address")

        if not _check_api_key(api_key):
            raise ValueError("api key verification failed")

        config_path = _config_path()
        if os.path.exists(config_path) and not overwrite:
            data = open(config_path, "r").read()
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                raise OSError(
                    f"invalid content in already existing {config_path}"
                ) from None
            except OSError as e:
                raise OSError(f"can not read existing {config_path}: {e}") from None

            raise OSError(
                f"you already configured pubchem access, use overwrite=True"
                f" in case you want to overwrite existing data in {config_path}:"
                f" {data}"
            )

        try:
            with open(config_path, "w") as fh:
                json.dump(dict(email_address=email_address, api_key=api_key), fh)
        except OSError as e:
            raise OSError(f"can not write to {config_path}: {e}") from None

        self.api_key = api_key
        self.email_address = email_address

    @retry(3)
    def _get(self, url, **params):
        self._setup_default_values(params)
        return requests.get(url, params=params)

    @retry(3)
    def _post(self, url, payload, **params):
        self._setup_default_values(params)
        return requests.post(url, params=params, data=payload)

    def _setup_default_values(self, params):
        params.update(dict(tool="emzed", retmode="json"))
        if self.email is not None:
            params["email"] = self.email
        if self.api_key is not None:
            params["api_key"] = self.api_key

    def _check(self, r, what):
        try:
            r.raise_for_status()
        except RequestException as e:
            e = requests.utils.unquote(str(e))
            raise OSError(
                self._fmt_error(f"retrieving {what} result failed", e)
            ) from None

    def _fmt_error(self, operation, e):
        e = requests.utils.unquote(str(e))
        N = 300
        if len(e) > N:
            e = e[:300] + "... (skipped {} characters)".format(len(e) - N)
        BOLD = "\033[1m"
        END = "\033[0m"
        return f"{BOLD}{operation}. details:{END}\n{e}"

    def _extract_esearch_result(self, r):
        result = r.json()["esearchresult"]
        if "ERROR" in result:
            raise ValueError("query failed: {}".format(result["ERROR"]))
        return result

    def _extract_esummary_result(self, r):
        result = r.json()
        if "result" not in result:
            pprint(result)
            return
        result = result["result"]
        error = r.json().get("error")
        if error is not None:
            raise ValueError("query failed: {}".format(error))
        return result


def _get_pubchem_api_key():
    api_key = os.environ.get("PUBCHEM_API_KEY")
    if api_key is not None:
        print("got api_key from PUBCHEM_API_KEY")
        return api_key
    config_path = _config_path()
    if os.path.exists(config_path):
        data = json.load(open(config_path, "rb"))
        return data.get("api_key")
    return None


def _get_pubchem_email():
    email = os.environ.get("PUBCHEM_EMAIL")
    if email is not None:
        print("got email from PUBCHEM_EMAIL")
        return email
    config_path = _config_path()
    if os.path.exists(config_path):
        data = json.load(open(config_path, "rb"))
        return data.get("email")
    return None


def _config_path():
    emzed_folder = folders.get_emzed_folder()
    if not os.path.exists(emzed_folder):
        os.makedirs(emzed_folder)
    return os.path.join(emzed_folder, "pubchem.json")


def _check_email_address(email_address):
    # https://stackoverflow.com/questions/201323
    regex = r"""(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|"
        (?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|
        \\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+
        [a-z0-9](?:[a-z0-9-]*[a-z0-9])?|
        \[(?:(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9]))\.){3}
        (?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9])|[a-z0-9-]*[a-z0-9]:
        (?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f
        ]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])
    """
    return re.match(regex, email_address, re.VERBOSE) is not None


@retry(3)
def _check_api_key(api_key):
    r = requests.get(EINFO_URL, params=dict(api_key=api_key))
    if r.status_code == 400 and "error" in r.json():
        return False

    # handle other errors
    r.raise_for_status()

    return True


class Downloader:
    def __init__(self):
        self._lock = threading.Lock()
        self._pubchem_accessor = PubChemAccessor()
        has_api_key = self._pubchem_accessor.api_key is not None

        if has_api_key:
            self._dt = 0.15
            self._n_threads = 15
        else:
            self._dt = 1.0
            self._n_threads = 5

    def _throttle(self):
        with self._lock:
            time.sleep(self._dt)

    def _fetch(self, start, end, ids, result_folder, kegg_ids, hmdb_ids, biocyc_ids):
        # limit request frequency:
        self._throttle()

        p = os.path.join(result_folder, f"pubchem_{start}_{end}.json")
        print(f"start fetching data {start}...{end}")
        summary_data = self._pubchem_accessor.get_summary_data(ids[start:end])

        for id_, data in summary_data.items():
            data["is_in_kegg"] = id_ in kegg_ids
            data["is_in_hmdb"] = id_ in hmdb_ids
            data["is_in_biocyc"] = id_ in biocyc_ids

        with open(p, "w") as fh:
            json.dump(summary_data, fh, indent=0)
        print("wrote", p)

    def download(self, limit=None, result_path=None):
        count = self._pubchem_accessor.get_count()
        if limit is None:
            limit = count

        pool_executor = ThreadPoolExecutor(self._n_threads)
        print(f"started ThreadPoolExecutor with {self._n_threads} worker threads")

        f1 = pool_executor.submit(self._pubchem_accessor.get_identifiers, 0, limit)

        self._throttle()
        f2 = pool_executor.submit(
            self._pubchem_accessor.get_identifiers, 0, count, source="KEGG"
        )

        self._throttle()
        f3 = pool_executor.submit(
            self._pubchem_accessor.get_identifiers,
            0,
            count,
            source="Human Metabolome Database",
        )

        self._throttle()
        f4 = pool_executor.submit(
            self._pubchem_accessor.get_identifiers, 0, count, source="Biocyc"
        )

        print("threads to fetch cids submitted")

        ids = f1.result()
        print(f"got {len(ids)} cids in total")

        kegg_ids = set(f2.result())
        print(f"got {len(kegg_ids)} kegg specific cids")

        hmdb_ids = set(f3.result())
        print(f"got {len(hmdb_ids)} hmdb specific cids")

        biocyc_ids = set(f4.result())
        print(f"got {len(biocyc_ids)} biocyc_ids specific cids")

        download_folder = tempfile.mkdtemp()

        futures = []

        chunksize = CHUNK_SIZE_IDS_PUBCHEM
        max_num_futures = 100

        with pool_executor as executor:
            for start in range(0, limit, chunksize):
                future = executor.submit(
                    self._fetch,
                    start,
                    start + chunksize,
                    ids,
                    download_folder,
                    kegg_ids,
                    hmdb_ids,
                    biocyc_ids,
                )
                futures.append(future)
                if len(futures) == max_num_futures:
                    # trigger exception:
                    for future in futures:
                        future.result()
                    futures = []

        print("got all results")

        return _merge_jsons(download_folder, result_path)


def _merge_jsons(folder, target_file):
    if target_file is None:
        target_file = os.path.join(folder, "pubchem.gz")

    print("start compress files at", folder)

    data = {}
    for p in glob.glob(os.path.join(folder, "*.json")):
        with open(p) as fh:
            js = json.load(fh)
            data.update(js)

    with gzip.open(target_file, "wt", encoding="utf-8") as fh:
        json.dump(data, fh, indent="")

    return target_file


def assemble_table(gz_file, path=None):
    table = emzed.Table.create_table(COL_NAMES, COL_TYPES, rows=[], path=path)

    for name, format_ in SPECIAL_COL_FORMATS.items():
        table.set_col_format(name, format_)

    with gzip.open(gz_file, "rt", encoding="ascii") as fh:
        data = json.load(fh)

    rows = []
    for entry in data.values():
        entry["synonymlist"] = ", ".join(entry["synonymlist"])
        rows.append([entry[field_name] for field_name in IN_SUMMARY])
    table._model.append(rows)

    def url(cid):
        return SUMMARY_URL + "?cid=" + cid

    table.add_column("url", table.apply(url, table.cid), str)

    table.add_column(
        "m0", table.apply(fast_m0, table.mf), float, "%11.6f", insert_after="mw"
    )

    return table


o = re.compile("([A-Z][a-z]?)([1-9]*)")


def fast_m0(mf):
    sum_ = 0.0
    for sym, count in re.findall(o, mf):
        mass = masses.get((sym, None))  # monoisotopic mass
        if mass is None:
            # lookup may fail for some elements like Lu which show up in search
            # results, eg Lutathera
            return None
        if count:
            mass *= int(count)
        sum_ += mass
    return sum_


if __name__ == "__main__":
    started = time.time()
    d = Downloader()
    from datetime import datetime

    path = datetime.now().strftime("pubchem_%Y-%m-%d_%H-%M.gz")
    target_file = d.download(result_path=path)
    print()
    print("resultfile", target_file)
    print()

    minutes, seconds = divmod(time.time() - started, 60)
    print("needed {:.0f} minutes and {:.0f} seconds".format(minutes, seconds))
