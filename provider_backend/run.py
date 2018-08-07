import os

import sys

from provider_backend.myapp import app
from provider_backend.constants import BaseURLs, DEFAULT_ASSETS_FOLDER
from provider_backend.blockchain.OceanContractsWrapper import OceanContractsWrapper
from provider_backend.blockchain.constants import OceanContracts
from provider_backend.config_parser import load_config_section
from provider_backend.constants import ConfigSections
from threading import Thread


if 'UPLOADS_FOLDER' in os.environ and os.environ['UPLOADS_FOLDER']:
    app.config['UPLOADS_FOLDER'] = os.environ['UPLOADS_FOLDER']
else:
    app.config['UPLOADS_FOLDER'] = DEFAULT_ASSETS_FOLDER

if 'CONFIG_FILE' in os.environ and os.environ['CONFIG_FILE']:
    app.config['CONFIG_FILE'] = os.environ['CONFIG_FILE']
else:
    print('A config file must be set in the environment variable "CONFIG_FILE".')
    sys.exit(1)


from provider_backend.app.assets import assets
app.register_blueprint(assets, url_prefix=BaseURLs.BASE_PROVIDER_URL + '/assets')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
