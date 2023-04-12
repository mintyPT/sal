set -e

export PYPI_USERNAME=__token__

nbdev_export
nbdev_bump_version
poetry version patch
nbdev_prepare

poetry publish --build -vvv --username $PYPI_USERNAME --password $PYPI_PASSWORD