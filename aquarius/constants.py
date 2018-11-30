class ConfigSections:
    OCEANBD = 'oceandb'
    RESOURCES = 'resources'


class BaseURLs:
    BASE_AQUARIUS_URL = '/api/v1/aquarius'
    SWAGGER_URL = '/api/v1/docs'  # URL for exposing Swagger UI (without trailing '/')
    ASSETS_URL = BASE_AQUARIUS_URL + '/assets'


class Metadata:
    TITLE = 'Aquarius'
    DESCRIPTION = 'Aquarius provides an off-chain database store for metadata about data assets. When running with our Docker images, it is exposed under `http://localhost:5000`.'
    HOST = 'myfancyaquarius.com'