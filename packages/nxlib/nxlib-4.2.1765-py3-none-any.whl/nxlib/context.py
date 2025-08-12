from enum import Enum

from nxlib import api
from nxlib.command import NxLibCommand
from nxlib.constants import *
from nxlib.item import NxLibItem


class CameraAction(Enum):
    NONE = "None"
    NETWORK_CONFIGURATION = "NetworkConfiguration"
    FIRMWARE_UPDATE = "FirmwareUpdate"
    PAIRING = "Pairing"
    CALIBRATION = "Calibration"


class NxLib:
    """
    This class offers a simple to use interface for interacting with a normal
    NxLib. It implements the context manager protocol and thus can be used in a
    ``with`` statement, which automatically initializes the NxLib and takes care
    of the exception handling.

    Args:
        path (str, optional): The path to the NxLib shared library.
            Defaults to None.
    """
    def __init__(self, path=None):
        self._path = path

    def __enter__(self):
        api.initialize(path=self._path)
        return api

    def __exit__(self, exc_type, exc_value, exc_tb):
        # Explicitly finalize! We cannot rely on the finalize() call in the
        # destructor of the global nxlib instance, because it is not guaranteed
        # that the garbage collector invokes it directly after exiting the
        # with-statement and before re-initializing the API with e.g. another
        # with-statement.
        api.finalize()


class NxLibRemote:
    """
    This class offers a simple to use interface for interacting with a remote
    NxLib. It implements the context manager protocol and thus can be used
    in a ``with`` statement, which automatically loads the remote NxLib,
    connects to the given hostname (and port) when entering the scope and
    automatically disconnects when exiting the scope. It also takes care of the
    exception handling.

    Args:
        hostname (str): The hostname of the remote NxLib.
        port (int): The port number of the remote NxLib.

    """
    def __init__(self, hostname, port):
        self._hostname = hostname
        self._port = int(port)

    def __enter__(self):
        api.load_remote_lib()
        api.connect(self._hostname, self._port)
        return api

    def __exit__(self, exc_type, exc_value, exc_tb):
        # Explicitly disconnect! We cannot rely on the disconnect() call in the
        # destructor of the global nxlib instance, because it is not guaranteed
        # that the garbage collector invokes it directly after exiting the
        # with-statement and before re-initializing the API with e.g. another
        # with-statement.
        api.disconnect()


class Camera:
    @classmethod
    def from_serial(cls, serial, expected_types=None, open_params={}):
        if expected_types is None:
            expected_types = [VAL_MONOCULAR, VAL_STEREO, VAL_STRUCTURED_LIGHT]
        camera = Camera._get_camera_node(serial)
        camera_type = camera[ITM_TYPE].as_string()
        if camera_type not in expected_types:
            raise CameraTypeError(f"{serial} is of type {camera_type}, "
                f"expected one of {expected_types}")
        if camera_type == VAL_MONOCULAR:
            return MonoCamera(serial, open_params)
        elif camera_type == VAL_STEREO:
            return StereoCamera(serial, open_params)
        elif camera_type == VAL_STRUCTURED_LIGHT:
            return StructuredLightCamera(serial, open_params)

    def __init__(self, serial, open_params):
        self._serial = serial
        self._open_params = open_params
        self._node = Camera._get_camera_node(serial)

    def __getitem__(self, value):
        """
        The ``[]`` access operator.

        Args:
            value (int, str, bool or float): The value to access.

        Returns:
            ``NxLibItem``: The resulting node.
        """
        return self._node[value]

    def get_node(self):
        """
        Get the camera tree node of the stereo camera the context object opens
        and represents.

        Returns:
            `NxLibItem`: The camera node of the stereo camera.
        """
        return self._node

    def get_serial_number(self) -> str:
        """
        Returns the camera's serial number as a string.

        Raises:
            NxLibException: If the serial number cannot be retrieved or is missing.

        Returns:
            str: The serial number of the camera.
        """
        return self._serial

    def get_model_name(self) -> str:
        """
        Returns the camera's model name as a string.

        Raises:
            NxLibException: If the model name cannot be retrieved or is missing.

        Returns:
            str: The model name of the camera.
        """
        return self[ITM_MODEL_NAME].as_string()

    def get_required_action(self) -> CameraAction:
        """Returns the required action as a CameraAction enum."""
        if not self._has_status_node():
            return CameraAction.NONE

        value = self[ITM_STATUS][ITM_ACTION_REQUIRED].as_string()
        return CameraAction(value)

    def capture(self, params={}):
        """
        Capture the image(s).

        Args:
            params (dict, optional): Parameters for the capture command.

        Raises:
            NxLibException: If the capture fails.
        """
        self._execute(CMD_CAPTURE, params=params)

    def rectify(self):
        """
        Rectify the captured images (requires :meth:`capture` to be called
        first). Use this method only if you want to have the rectified raw
        images and no further data.
        """
        self._execute(CMD_RECTIFY_IMAGES)

    def open(self):
        """
        Opens a connection to the camera device.

        This method establishes communication with the camera and must be called
        before performing any operations that require an active connection
        (e.g., capturing images).

        .. note::

            The default and preferred usage of the Camera class is as a context manager
            using the ``with`` statement. In that case, ``open()`` is called automatically and
            should not be invoked manually.

        **Examples**

        Preferred usage (context manager)::

            with Camera(serial, open_params) as cam:
                cam.capture()
                # Camera is automatically closed when the block exits

        Manual usage (if context management is not possible)::

            cam = Camera(serial, open_params)
            cam.open()
            try:
                cam.capture()
            finally:
                cam.close()
        """
        if self._node[ITM_STATUS][ITM_AVAILABLE].as_bool() is False:
            raise CameraOpenError(f"{self._serial} not available")
        self._execute(CMD_OPEN, self._open_params)

    def close(self):
        """
        Closes the connection to the camera device.

        This method should be called to properly release the camera and associated resources
        when using the Camera class in manual mode (i.e., without a context manager).

        .. note::

            The default and preferred usage of the Camera class is as a context manager
            using the ``with`` statement. In that case, ``close()`` is called automatically
            when exiting the context and should not be invoked manually.

        **Examples**

        Preferred usage (context manager)::

            with Camera(serial, open_params) as cam:
                cam.capture()
                # Camera is automatically closed when the block exits

        Manual usage (if context management is not possible)::

            cam = Camera(serial, open_params)
            cam.open()
            try:
                cam.capture()
            finally:
                cam.close()
        """
        self._execute(CMD_CLOSE)

    def is_available(self) -> bool:
        """True if camera is available."""
        if not self._has_status_node():
            return False
        return self[ITM_STATUS][ITM_AVAILABLE].as_bool()

    def is_open(self) -> bool:
        """True if camera is open."""
        if not self._has_status_node():
            return False
        return self[ITM_STATUS][ITM_OPEN].as_bool()

    def requires_action(self) -> bool:
        """True if any action other than NONE is required."""
        return self.get_required_action() != CameraAction.NONE

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.close()

    def _execute(self, command_name, params={}, wait=True):
        cmd = NxLibCommand(command_name, params=params)
        cmd.parameters()[ITM_CAMERAS] = self._serial
        cmd.execute(wait=wait)
        return cmd

    def _check_type(self, expected_type):
        camera_type = self._node[ITM_TYPE].as_string()
        if camera_type != expected_type:
            raise CameraTypeError(f"{self._serial} is of type {camera_type}, "
                                  f"expected {expected_type}")

    def _has_status_node(self) -> bool:
        return self._node.exists() and self[ITM_STATUS].exists()

    @classmethod
    def _get_camera_node(cls, serial):
        camera = NxLibItem()[ITM_CAMERAS][serial]
        if not camera.exists():
            raise CameraNotFoundError(f"No camera found for serial {serial}")

        return camera


class MonoCamera(Camera):
    """
    This class implements the context manager protocol and simplifies the
    handling of a mono camera.

    It provides the camera tree node by calling :meth:`get_node` or lets you
    directly access an ``NxLibItem`` within the camera node by using the ``[]``
    operator.

    Args:
        serial (str): The serial number of the target camera.
        open_params (dict): Optional parameters for opening the target camera.

    Raises:
        CameraTypeError: If the camera with the given serial number is not a
            monocular camera.
        CameraNotFoundError: If no camera was found for the given serial number.
        CameraOpenError: If the camera with the given serial cannot be opened.
    """
    def __init__(self, serial, open_params={}):
        super().__init__(serial, open_params)
        self._check_type(VAL_MONOCULAR)


class StereoCamera(Camera):
    """
    This class implements the context manager protocol and simplifies the
    handling of an Ensenso stereo camera.

    It provides the camera tree node by calling :meth:`get_node` or lets you
    directly access an ``NxLibItem`` within the camera node by using the ``[]``
    operator.

    Args:
        serial (str): The serial number of the target camera.
        open_params (dict): Optional parameters for opening the target camera.

    Raises:
        CameraTypeError: If the camera with the given serial number is not a
            stereo camera.
        CameraNotFoundError: If no camera was found for the given serial number.
        CameraOpenError: If the camera with the given serial cannot be opened.
    """
    def __init__(self, serial, open_params={}):
        super().__init__(serial, open_params)
        self._check_type(VAL_STEREO)

    def compute_disparity_map(self):
        """
        Compute the disparity map (requires :meth:`capture` to be called first).

        Returns:
            ``NxLibItem``: The disparity map node.
        """
        self._execute(CMD_COMPUTE_DISPARITY_MAP)
        return self._node[ITM_IMAGES][ITM_DISPARITY_MAP]

    def compute_point_map(self):
        """
        Compute the point map (requires :meth:`compute_disparity_map` to be
        called first).

        Returns:
            ``NxLibItem``: The point map node.
        """
        self._execute(CMD_COMPUTE_POINT_MAP)
        return self._node[ITM_IMAGES][ITM_POINT_MAP]

    def compute_texture(self):
        """
        Compute the rectified texture image (requires :meth:`rectify` or
        :meth:`compute_disparity_map` to be called first).

        Returns:
            ``NxLibItem``: The node containing the rectified texture image for
                           the camera's left sensor.
        """
        self._execute(CMD_COMPUTE_TEXTURE)
        return self._node[ITM_IMAGES][ITM_RECTIFIED_TEXTURE][ITM_LEFT]

    def get_disparity_map(self):
        """
        The computed disparity map (requires :meth:`compute_disparity_map`).

        Returns:
            `Object`: A byte buffer containing the disparity map.
        """
        return self._node[ITM_IMAGES][ITM_DISPARITY_MAP].get_binary_data()

    def get_point_map(self):
        """
        The computed point map (requires :meth:`compute_point_map`).

        Returns:
            `Object`: A byte buffer containing the point map.
        """
        return self._node[ITM_IMAGES][ITM_POINT_MAP].get_binary_data()

    def get_texture(self):
        """
        The computed rectified texture image (requires :meth:`compute_texture`).

        Returns:
            `Object`: A byte buffer containing the rectified texture image for
                      the camera's left sensor.
        """
        return self._node[ITM_IMAGES][ITM_RECTIFIED_TEXTURE][ITM_LEFT].get_binary_data()

    def save_model(self, filename: str, texture: bool = True, threads: int = -1, wait: bool = True):
        """
        Save the 3D mesh model of the camera to a file in STL or PLY format.

        The mesh includes vertices and triangle indices, and optionally vertex color data (RGB)
        when saved in PLY format and ``texture`` is set to True.

        Args:
            filename (str): Path to the file where the model will be saved.
            texture (bool, optional): Whether to include RGB texture data in the model.
                Defaults to True.
            threads (int, optional): Number of threads to use for saving. If <= 0, the default is used.
            wait (bool, optional): Whether to execute the command synchronously. If False,
            the method returns immediately. The caller can use the returned ``NxLibCommand``
            object to wait for completion manually. Defaults to True.

        Returns:
            NxLibCommand: The command used to save the model. In asynchronous mode, the caller
            can use ``.wait()`` to wait for completion.

        Raises:
            NxLibException: If the model saving process fails.

        Note:
            - The file format (STL or PLY) is inferred from the file extension.
            - PLY format includes a structured header followed by binary data for vertices and faces.
            - If ``texture`` is True, each vertex in the PLY file includes red, green, and blue components.
            - Triangles are represented as a list of three vertex indices.
        """

        params = {}
        params[ITM_FILENAME] = filename
        params[ITM_TEXTURE] = texture

        if threads > 0:
            params[ITM_THREADS] = threads

        return self._execute(CMD_SAVE_MODEL, params=params, wait=wait)


class StructuredLightCamera(StereoCamera):
    """
    This class implements the context manager protocol and simplifies the
    handling of an Ensenso structured light camera and has the same
    functionality as a stereo camera except that it does not have a disparity
    map.

    It provides the camera tree node by calling :meth:`get_node` or lets you
    directly access an ``NxLibItem`` within the camera node by using the ``[]``
    operator.

    Args:
        serial (str): The serial number of the target camera.
        open_params (dict): Optional parameters for opening the target camera.

    Raises:
        CameraTypeError: If the camera with the given serial number is not a
            structured light camera.
        CameraNotFoundError: If no camera was found for the given serial number.
        CameraOpenError: If the camera with the given serial cannot be opened.
        CameraDisparityMapError: If a disparity map is requested.
    """
    def __init__(self, serial, open_params={}):
        Camera.__init__(self, serial, open_params)
        self._check_type(VAL_STRUCTURED_LIGHT)

    def compute_disparity_map(self):
        """
        Does nothing, because a structured light camera does not have a
        disparity map. Existing for compatibility reasons.
        """
        pass

    def compute_point_map(self):
        """
        Compute the point map (requires :meth:`capture` to be called first).

        Returns:
            ``NxLibItem``: The point map node.
        """
        super().compute_disparity_map()
        return super().compute_point_map()

    def get_disparity_map(self):
        raise CameraDisparityMapError("A structured light camera does not have"
                                      "a disparity map.")


class CameraTypeError(Exception):
    """ Raised if camera has the wrong type (Mono/Stereo/StructuredLight). """
    pass


class CameraNotFoundError(Exception):
    """ Raised if no camera is found for a given serial number. """
    pass


class CameraOpenError(Exception):
    """ Raised if a camera cannot be opened. """
    pass


class CameraDisparityMapError(Exception):
    """ Raised if a non-existing disparity map is requested. """
    pass
