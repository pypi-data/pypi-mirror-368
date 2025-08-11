import logging

# Ensure library logging integrates with host app (e.g., Home Assistant)
logging.getLogger(__name__).addHandler(logging.NullHandler())
