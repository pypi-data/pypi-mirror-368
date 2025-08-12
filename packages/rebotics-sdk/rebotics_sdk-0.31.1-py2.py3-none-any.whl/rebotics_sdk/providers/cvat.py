import logging

from .base import ReboticsBaseProvider, remote_service

logger = logging.getLogger(__name__)


class CvatProvider(ReboticsBaseProvider):
    """
    See <cvat-url>/api/docs/#tag/retailer_import
    for more detailed examples.
    """

    @remote_service('/api/retailer_import')
    def start_retailer_import(self, data):
        """
        Data example:
        {
          "image_quality": 80,  # 0 - 100
          "segment_size": 20,    # >= 0
          "workspace": "RetechLabs",
          "priority": "30",  # medium
          "export_by": "username",
          "retailer_codename": "delta",
          "images": [
            {
              "items": [
                {
                  "lowerx": 0,
                  "lowery": 0,
                  "upperx": 0,
                  "uppery": 0,
                  "label": "string",
                  "points": "string",
                  "type": "string",
                  "upc": "string"
                }
              ],
              "image": "http://example.com",
              "planogram_title": "string",
              "processing_action_id": 0,
              "price_tags": [
                {
                  "lowerx": 0,
                  "lowery": 0,
                  "upperx": 0,
                  "uppery": 0,
                  "label": "string",
                  "points": "string",
                  "type": "string",
                  "upc": "string"
                }
              ]
            }
          ]
        }

        Response example:
        {
          "task_id": 0,
          "preview": None,
          "images": None,
          "status": None
        }
        """
        return self.session.post(json=data)

    @remote_service('/api/retailer_import/{id}')
    def check_import_progress(self, task_id):
        """
        Does not accept any data.

        Response example:
        {
          "task_id": 0,
          "preview": "http://example.com",
          "images": [
            {
              "id": 0,
              "image": "http://example.com"
            }
          ],
          "status": {
            "state": "Queued",
            "message": "",
            "progress": 0
          }
        }
        """
        return self.session.get(id=task_id)
