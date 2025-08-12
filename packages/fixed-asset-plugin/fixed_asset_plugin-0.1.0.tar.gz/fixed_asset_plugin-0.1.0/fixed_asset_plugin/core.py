"""Add Fixed Asset Parameter to every new Part created"""

from plugin import InvenTreePlugin

from plugin.mixins import EventMixin

from part.models import Part, PartParameter, PartParameterTemplate

from . import PLUGIN_VERSION

import logging
from typing import Optional
# import os

logger = logging.getLogger(__name__)


class FixedAssetPlugin(EventMixin, InvenTreePlugin):

    """FixedAssetPlugin - custom InvenTree plugin."""

    # Plugin metadata
    TITLE = "Fixed Asset Plugin"
    NAME = "FixedAssetPlugin"
    SLUG = "fixed-asset-plugin"
    DESCRIPTION = "Add Fixed Asset Parameter to every new Part created"
    VERSION = PLUGIN_VERSION
    AUTHOR = "Adrian Piney Gutierrez"
    LICENSE = "MIT"

    # Variables

    TEMPLATE_NAME = "Fixed Asset"
    # TEMPLATE_ID = ""

    # Optionally specify supported InvenTree versions
    # MIN_VERSION = '0.18.0'
    # MAX_VERSION = '2.0.0'

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(f"plugin.{self.SLUG}")
        try:
           self.template = PartParameterTemplate.objects.get(name=self.TEMPLATE_NAME)

        except PartParameterTemplate.DoesNotExist:
            self.template = None
            logger.error(f"Template {self.TEMPLATE_NAME} not found")
           

    #    Configure custom logger to write to file
    #    log_dir = '/home/inventree/data/log'
    #    os.makedirs(log_dir, exist_ok=True)
    #    log_file = os.path.join(log_dir, 'fixed_asset_plugin.log')

    #    self.logger = logging.getLogger(self.NAME)
    #    self.logger.setLevel(logging.INFO)

    #    file_handler = logging.FileHandler(log_file)
    #    file_handler.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s'))

    #    # Prevent duplicate handlers on reload
    #    if not self.logger.handlers:
    #        self.logger.addHandler(file_handler)
    #  =============================================
    
    def _get_part_from_event(self, *, args, kwargs) -> Optional[Part]:
        if kwargs.get('model') != 'Part':
            return None
        
        pid = kwargs.get('id')
        if pid is not None:
            return Part.objects.filter(pk=pid).first()
        return None


    # Respond to InvenTree events (from EventMixin)
    # Ref: https://docs.inventree.org/en/stable/extend/plugins/event/
    def wants_process_event(self, event: str) -> bool:
        """Return True if the plugin wants to process the given event."""
        return event == 'part_part.created'
    
    def process_event(self, event: str, *args, **kwargs) -> None:
        
        # Check de los args para comprobar datos
        self.logger.debug(f"fixed-asset-plugin args={args}, kwargs={kwargs}")

        part = self._get_part_from_event(args=args, kwargs=kwargs)

        if not part:
            self.logger.debug("Ignoring event: not a Part or not ID")
            return
        
        if not self.template:
            return
        
        if PartParameter.objects.filter(part=part, template=self.template).exists():
            self.logger.debug(f"Part {part.pk} ya tiene '{self.template.name}'")
            return
        
        try:
            PartParameter.objects.create(
                part=part,
                template=self.template,
                data=False
            )
            self.logger.info(f"Added '{self.template.name}' parameter to Part {part.pk}")

        except Exception as e:
            self.logger.error(f"Error adding parameter: {e}")
