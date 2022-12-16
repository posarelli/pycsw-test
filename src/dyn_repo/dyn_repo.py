import configparser
import logging
import os

from jinja2 import Environment, FileSystemLoader
from xml.sax.saxutils import escape

from pycsw.core.repository import Repository
from pycsw.server import EnvInterpolation


LOGGER = logging.getLogger(__name__)


class DynRepository(Repository):
    CONFIG = configparser.ConfigParser(interpolation=EnvInterpolation())
    CONFIG.read(os.getenv("PYCSW_CONFIG"))

    def __init__(self, context, repo_filter=None):
        LOGGER.debug(f'INIT DYN REPOSITORY')

        super().__init__(
            DynRepository.CONFIG.get('repository', 'database'),
            context,
            os.environ.get('local.app_root', None),
            DynRepository.CONFIG.get('repository', 'table'),
            repo_filter)

    def query_ids(self, ids):
        LOGGER.debug(f'OVERRIDDEN query_ids')
        records = super().query_ids(ids)
        self.enrich_records(records)
        return records

    def query(self, constraint, sortby=None, typenames=None, maxrecords=10, startposition=0):
        LOGGER.debug(f'OVERRIDDEN query')
        result = super().query(constraint, sortby, typenames, maxrecords, startposition)
        size, records = result
        self.enrich_records(records)
        return result

    def enrich_records(self, records):
        for record in records:
            LOGGER.debug(f"ENRICHING record {getattr(record, 'resource_uid')}:{getattr(record, 'title')}")
            self.add_fixed_fields(record)
            self.enrich_record_with_xml(record)

    def add_fixed_fields(self, record):
        for name, value in (
            ('typename', 'gmd:MD_Metadata'),
            ('schema', 'http://www.isotc211.org/2005/gmd'),
        ):
            setattr(record, name, value)

    def enrich_record_with_xml(self, record):
        LOGGER.info(f'Adding XML field to {record}')

        # create a dict with records values
        attribs = {
            'file_identifier': getattr(record, 'resource_uid'),
            'responsible_organisation': 'ECMWF',
            'contactemail': getattr(record, 'contact'),
            'responsible_organisation_role': 'pointOfContact',
            'md_standard_name': 'ISO 19115:2003/19139',
            'md_standard_vs': '1.0',
            'title': getattr(record, 'title'),
            'abstract_md': escape(getattr(record, 'abstract')),
            'publicationdate': getattr(record, 'publication_date'),
            'creationdate': None,
            'ds_responsible_organisation': 'ECMWF',
            'ds_contactemail': getattr(record, 'contact'),
            'ds_responsible_organisation_role': 'publisher',
            'keywords': getattr(record, 'keywords'),
            'licence_list': ['https://cds.climate.copernicus.eu/api/v2/terms/static/20180314_Copernicus_License_V1.1.pdf'],
            'use_limitation': 'Content accessible through the CDS may only be used under the terms of the licenses attributed to each particular resource.',
            'topic': 'climatologyMeteorologyAtmosphere',
            'bboxW': getattr(record, 'geo_extent')['bboxW'],
            'bboxE': getattr(record, 'geo_extent')['bboxE'],
            'bboxS': getattr(record, 'geo_extent')['bboxS'],
            'bboxN': getattr(record, 'geo_extent')['bboxN'],
            'begin_date': getattr(record, 'begin_date'),
            'end_date': getattr(record, 'end_date'),
            'resource_url': f"https://cds.climate.copernicus.eu/cdsapp#!/dataset/{getattr(record, 'doi') or 'unknown'}",
            'resource_type': 'dataset',
            'lineage': 'EC Copernicus program',
        }

        # Processed attribs: doi
        doi = getattr(record, 'doi')
        if doi:
            attribs['doi'] = doi

        # Processed attribs: abstract_md
        abstract_vars = [escape(v['label']) for v in getattr(record, 'variables', [])]
        if abstract_vars:
            abstract_vars.sort()
            attribs['abstract_md'] = attribs['abstract_md'] + \
                '\nVariables in the dataset / application are:\n' + \
                ', '.join(abstract_vars)

        # Processed attribs: data_type, file_format
        is_grid = None
        file_format = 'unknown'
        for d in getattr(record, 'description', []):
            if d['id'] == 'data-type' and d['value'] == 'Gridded':
                is_grid = True
            elif d['id'] == 'file-format':
                file_format = d['value']
        attribs['data_type'] = 'grid' if is_grid else 'vector'
        attribs['file_format'] = file_format
        attribs['format_version'] = 'N/A'

        # Processed attribs: documents
        attribs['documents'] = [{
            'document_url': doc['url'],
            'document_title': doc['title'],
            'document_description': doc['description']
            } for doc in getattr(record, 'documentation') if 'url' in doc]

        # get the file template
        template_fullpath = DynRepository.CONFIG.get('pycsw-dynamic', 'iso_template')

        # create the jinja objects
        environment = Environment(loader=FileSystemLoader(os.path.dirname(template_fullpath)))
        template = environment.get_template(os.path.basename(template_fullpath))

        # render the template
        content = template.render(attribs)

        setattr(record, 'xml', content)
