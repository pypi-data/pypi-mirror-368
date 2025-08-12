import io
import typing

from .base import ReboticsBaseProvider, remote_service, PageResult
from ..constants import CameraGroupActionStatusType


class HawkeyeCameraProvider(ReboticsBaseProvider):
    @remote_service('/api/v1/camera/heartbeats/')
    def save_camera_heartbeat(self, shelf_camera: str, battery_status: float, wifi_signal_strength: float,
                              current_time: str):
        return self.session.post(json={
            "shelf_camera": shelf_camera,
            "battery_status": battery_status,
            "wifi_signal_strength": wifi_signal_strength,
            "current_time": current_time
        })

    @remote_service('/api/v1/fetcher/')
    def create_capture_url(self, camera: str, filename: str):
        return self.session.post(json={
            "camera_id": camera,
            "filename": filename,
        })

    @remote_service('/api/v1/fetcher/capture/', raw=True)
    def create_capture(self, camera: str, file_key: str):
        return self.session.post(json={
            "camera_id": camera,
            "file_key": file_key,
        })


class HawkeyeCommonDataProvider(ReboticsBaseProvider):
    @remote_service('/api/internal/v1/camera/camera-actions/')
    def save_camera_action(self, action_type, status_type, payload, shelf_camera):
        return self.session.post(json={
            "action_type": action_type,
            "status_type": status_type,
            "payload": payload,
            "shelf_camera": shelf_camera
        })

    def create_camera_action(self, action_type, status_type, payload, shelf_camera):
        return self.save_camera_action(action_type, status_type, payload, shelf_camera)

    @remote_service('/api/internal/v1/camera/camera-actions/')
    def get_camera_actions(self):
        return self.session.get()

    @remote_service('/api/internal/v1/camera/fixtures/')
    def save_fixture(self, store_id: str, aisle: str = '', section: str = '', planogram: str = '', category: str = '',
                     shelf_camera_id: int = None, **kwargs):
        return self.session.post(json={
            "store_id": store_id,
            "aisle": aisle,
            "section": section,
            "planogram": planogram,
            "category": category,
            "shelf_camera": shelf_camera_id,
            **kwargs,
        })

    def create_fixture(self, retailer, store_id, aisle, section, **kwargs):
        return self.save_fixture(retailer, store_id, aisle, section, **kwargs)

    @remote_service('/api/internal/v1/camera/fixtures/{id}/')
    def delete_fixture(self, pk):
        return self.session.delete(id=pk)

    @remote_service('/api/internal/v1/camera/fixtures/{id}/')
    def patch_fixture(self, pk, **kwargs):
        return self.session.patch(id=pk, json=kwargs)

    @remote_service('/api/internal/v1/camera/fixtures/')
    def list_fixtures(self, store_id=None, aisle=None, section=None, planogram=None, category=None,
                      shelf_camera_id=None, no_shelf_camera=None, shelf_cameras=None,
                      modified_from=None, modified_to=None,
                      page=1, **kwargs):
        params = {
            "store_id": store_id,
            "aisle": aisle,
            "section": section,
            "planogram": planogram,
            "category": category,
            "shelf_camera": shelf_camera_id,
            "shelf_camera__isnull": no_shelf_camera,
            "shelf_camera__in": shelf_cameras,
            "modified__gte": modified_from,
            "modified__lt": modified_to,
            "page": page,
            **kwargs
        }
        return self.session.get(params=self._filter_params(params))

    @remote_service('/api/internal/v1/camera/all-fixtures/')
    def list_all_fixtures(
        self, store_id=None, aisle=None, section=None, planogram=None, category=None,
        shelf_camera_id=None, no_shelf_camera=None, shelf_cameras=None,
        modified_from=None, modified_to=None,
        shelf_camera_condition=None, page=1, **kwargs
    ):
        params = {
            "store_id": store_id,
            "aisle": aisle,
            "section": section,
            "planogram": planogram,
            "category": category,
            "shelf_camera": shelf_camera_id,
            "shelf_camera__isnull": no_shelf_camera,
            "shelf_camera__in": shelf_cameras,
            "modified__gte": modified_from,
            "modified__lt": modified_to,
            "shelf_camera_condition": shelf_camera_condition,
            "page": page,
            **kwargs
        }
        return self.session.get(params=self._filter_params(params))

    def get_fixtures(self):
        return self.list_fixtures()

    @remote_service('/api/internal/v1/camera/shelf-cameras/')
    def create_shelf_camera(self, camera_id, added_by, fixture=None):
        data = {
            "camera_id": camera_id,
            "added_by": added_by,
        }
        if fixture is not None:
            data["fixture"] = fixture
        return self.session.post(json=data)

    @remote_service('/api/internal/v1/camera/shelf-cameras/')
    def get_shelf_cameras(self, condition: list = None, do_capture: typing.Optional[bool] = True, mac_address=None,
                          store_id=None, page=1, page_size=100, **kwargs):
        params = {
            'condition': condition,
            'do_capture': do_capture,
            'mac_address__iexact': mac_address,
            'store_id': store_id,
            'page': page,
            'page_size': 100,
            **kwargs
        }
        return self.session.get(params=self._filter_params(params))

    def get_shelf_camera_by_mac_address(self, mac_address):
        return self.get_shelf_cameras(mac_address=mac_address, do_capture=None)

    @remote_service('/api/internal/v1/camera/shelf-cameras/{id}/')
    def get_shelf_camera(self, id_):
        return self.session.get(id=id_)

    @remote_service('/api/internal/v1/camera/shelf-cameras/{id}/')
    def update_shelf_camera(self, id_, camera_id: str = None, added_by: int = None, fixture: int = None,
                            perspective_warp: typing.List[typing.List[int]] = None, force_null=False,
                            **kwargs):
        data_to_update = {
            "camera_id": camera_id,
            "added_by": added_by,
            "fixture": fixture,
            "perspective_warp": perspective_warp,
            **kwargs,  # other undocumented changes for the future
        }
        return self.session.patch(
            id=id_,
            json={k: v for k, v in data_to_update.items() if not force_null and v is not None}
        )

    @remote_service('/api/internal/v1/camera/shelf-cameras/{shelf_camera_id}/captures/{capture_id}/warped/',
                    raw=True, stream=True, allow_redirects=True)
    def get_warped_image(self, shelf_camera_id, capture_id, polygon):
        assert len(polygon) == 4, "There should be 4 points"
        assert all(len(coordinate) == 2 for coordinate in polygon), "They should be in format [x, y]"
        params = {
            'polygon': ','.join(str(point) for coordinate in polygon for point in coordinate)
        }
        response = self.session.get(params=params, shelf_camera_id=shelf_camera_id, capture_id=capture_id, stream=True)
        response.raise_for_status()
        fp = io.BytesIO()
        for chunk in response.iter_content(chunk_size=1024):
            fp.write(chunk)
        fp.seek(0)
        return fp

    @remote_service('/api/internal/v1/camera/shelf-cameras/{shelf_camera_id}/captures/')
    def get_shelf_camera_captures(self, shelf_camera_id, page=1, **kwargs):
        params = {'page': page, **kwargs}
        return PageResult(self.session.get(shelf_camera_id=shelf_camera_id, params=self._filter_params(params)))

    @remote_service('/api/internal/v1/camera/camera-groups/')
    def create_camera_group(self, shelf_cameras: typing.List[int] = None):
        shelf_cameras = shelf_cameras or []
        payload = {"shelf_cameras": shelf_cameras}
        return self.session.post(json=payload)

    @remote_service('/api/internal/v1/camera/camera-groups/')
    def list_camera_groups(self, page: int = 1, **kwargs):
        return self.session.get(params=self._filter_params({"page": page, **kwargs}))

    @remote_service('/api/internal/v1/camera/camera-groups/{id}/')
    def get_camera_group_by_id(self, id_: int):
        return self.session.get(id=id_)

    @remote_service('/api/internal/v1/camera/camera-groups/{id}/assign-lifecycle-action/')
    def camera_group_assign_lifecycle_event(
        self,
        id_: int,
        event_name: str,
        lifecycle_action: int,
    ):
        return self.session.post(
            id=id_,
            json={
                'event_name': event_name,
                'lifecycle_action': lifecycle_action,
            }
        )

    @remote_service('/api/internal/v1/camera/camera-group-actions/')
    def create_camera_group_action(self, camera_group_id: int, action_id: int,
                                   status_type: str = CameraGroupActionStatusType.CREATED):
        payload = {'camera_group': camera_group_id, 'action': action_id, 'status_type': status_type}
        return self.session.post(json=payload)

    @remote_service('/api/internal/v1/camera/shelf-cameras/{id}/change-schedule/')
    def change_schedule(self, id_, capture_schedule: str, run_schedule: str):
        return self.session.post(id=id_, json={'capture_schedule': capture_schedule, 'run_schedule': run_schedule, })

    @remote_service('/api/internal/v1/camera/shelf-cameras/{id}/change-wifi-conf/')
    def change_wifi_configuration(self, id_, ssid: str, password: str):
        return self.session.post(id=id_, json={'ssid': ssid, 'password': password, })

    @remote_service('/api/internal/v1/camera/shelf-cameras/{id}/change-server-url/')
    def change_server_url(self, id_, url: str):
        return self.session.post(id=id_, json={'url': url, })

    @remote_service('/api/internal/v1/camera/stores/')
    def get_mgmt_stores(self):
        """Implement only client-side filtering"""
        return self.session.get()

    @remote_service('/api/internal/v1/camera/lifecycles/')
    def list_lifecycles(self, page=1, **kwargs):
        # only to read the lifecycles
        return self.session.get(
            params=self._filter_params({'page': page, **kwargs})
        )

    @remote_service('/api/internal/v1/camera/lifecycles/{id}/')
    def get_lifecycle(self, id_):
        return self.session.get(id=id_)

    @remote_service('/api/internal/v1/camera/lifecycles/')
    def create_lifecycle(self, event_name: str, shelf_camera_id: int, context: dict):
        """To manually create a lifecycle event and have it trigger the lifecycle actions"""
        return self.session.post(json={
            "event_name": event_name,
            "shelf_camera": shelf_camera_id,
            "context": context
        })

    @remote_service('/api/internal/v1/camera/store-groups/')
    def list_store_groups(self, search=None, page=1, **kwargs):
        return self.session.get(params=self._filter_params({
            'search': search,
            'page': page,
            **kwargs
        }))

    @remote_service('/api/internal/v1/camera/store-groups/{id}/')
    def get_store_group(self, id_):
        return self.session.get(id=id_)


class HawkeyeProvider(HawkeyeCommonDataProvider):
    @remote_service('/api-token-auth/', raw=True)
    def token_auth(self, username, password, **kwargs):
        response = self.session.post(data={'username': username, 'password': password})
        self.set_token(response.json()['token'])
        return response
