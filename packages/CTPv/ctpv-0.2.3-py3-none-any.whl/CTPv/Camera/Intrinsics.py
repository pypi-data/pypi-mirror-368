import numpy as np
import os
from ..Plucker.Line import Line

class RadialDistortion:
    """Handles radial distortion parameters for a camera model."""

    def __init__(self, k1=0, k2=0, k3=0):
        self.k1 = k1
        self.k2 = k2
        self.k3 = k3

    def set_from_list(self, coeffs):
        if len(coeffs) != 3:
            raise ValueError("List must contain exactly three elements.")
        self.k1, self.k2, self.k3 = coeffs


class IntrinsicMatrix:
    """Encapsulates intrinsic parameters of a pinhole camera model."""

    def __init__(self):
        self.fx = None
        self.fy = None
        self.cx = None
        self.cy = None
        self.s = 0
        self.width = None
        self.height = None
        self.RadialDistortion = RadialDistortion()
        self._MatlabIntrinsics = np.zeros((3, 3))
        self._OpenCVIntrinsics = np.zeros((3, 3))
        self.pixel_size = None  # e.g., 0.0034 mm
        self.info = None  # e.g., camera ID or lens metadata

    @property
    def MatlabIntrinsics(self):
        """
        generation call method for returning Matlab matrix format of intrinsic parameters of a camera
        Returns:
            I = 3x3 matrix
            [ fx   0   cx  ]
            [ 0    fy  cy  ]
            [ 0    0   1   ]

        """
        I = np.zeros((3, 3))
        I[0, 0] = self.fx
        I[1, 1] = self.fy
        I[2, 0] = self.cx
        I[2, 1] = self.cy
        I[2, 2] = 1
        return I

    @MatlabIntrinsics.setter
    def MatlabIntrinsics(self, I):
        """
        Extraction call method for extracting Matlab matrix format of intrinsic parameters of a camera to local class,
        parameters are registered to every parameter as per the following structure.
        I = [ fx   0   cx  ]
            [ 0    fy  cy  ]
            [ 0    0   1   ]

        """
        self.fx = I[0, 0]
        self.fy = I[1, 1]
        self.cx = I[2, 0]
        self.cy = I[2, 1]
        self.s = I[1, 0]

    @property
    def OpenCVIntrinsics(self):
        """
        generation call method for returning OpenCV matrix format of intrinsic parameters of a camera
        Returns:
            I = 3x3 matrix
            [ fx   0   cx  ]
            [ 0    fy  cy  ]
            [ 0    0   1   ]

        """
        I = np.zeros((3, 3))
        I[0, 0] = self.fx
        I[1, 1] = self.fy
        I[0, 2] = self.cx
        I[1, 2] = self.cy
        I[2, 2] = 1
        return I

    @OpenCVIntrinsics.setter
    def OpenCVIntrinsics(self, I):
        """
        Extraction call method for extracting OpenCV matrix format of intrinsic parameters of a camera to local class,
        parameters are registered to every parameter as per the following structure.
        I = [ fx   0   cx  ]
            [ 0    fy  cy  ]
            [ 0    0   1   ]

        """
        self.fx = I[0, 0]
        self.fy = I[1, 1]
        self.cx = I[0, 2]
        self.cy = I[1, 2]
        self.s = 0

    @property
    def focal_length_mm(self):
        """Returns focal length in mm."""
        if self.pixel_size is None:
            raise ValueError('Pixel size not set!')
        return self.fx * self.pixel_size, self.fy * self.pixel_size

    @property
    def PerspectiveAngle(self):
        """Returns horizontal or vertical perspective angle in degrees."""
        if self.width is None:
            raise ValueError('Set width first.')

        aspectRatio = self.width / self.height
        if aspectRatio > 1:
            return 2 * np.arctan(self.width / (2 * self.fx)) * 180 / np.pi
        else:
            return 2 * np.arctan(self.height / (2 * self.fy)) * 180 / np.pi

    @PerspectiveAngle.setter
    def PerspectiveAngle(self, p):
        if self.width is None:
            raise ValueError('Set width first.')

        aspectRatio = self.width / self.height
        if aspectRatio > 1:
            self.fx = (self.width / 2) / np.tan(p / 2)
            self.fy = self.fx
        else:
            self.fy = (self.height / 2) / np.tan(p / 2)
            self.fx = self.fy

        self.cx = self.width / 2
        self.cy = self.height / 2

    def CameraParams2Intrinsics(self, CameraParams):
        try:
            self.width = CameraParams.ImageSize[1]
            self.height = CameraParams.ImageSize[0]
        except AttributeError:
            print('Camera not open, set resolution manually.')
        self.MatlabIntrinsics = CameraParams.IntrinsicMatrix

    def Intrinsics2CameraParams(self):
        P = {
            'IntrinsicMatrix': self.MatlabIntrinsics,
            'ImageSize': [self.height, self.width]
        }
        if self.RadialDistortion:
            P['RadialDistortion'] = self.RadialDistortion
        return P

    def ScaleIntrinsics(self, Scale):
        """Scales all intrinsic parameters and image size by a given factor."""
        self.fx *= Scale
        self.fy *= Scale
        self.cx *= Scale
        self.cy *= Scale
        self.width *= Scale
        self.height *= Scale

    def save_intrinsics_to_json(self, filename):
        """Serialize camera intrinsics to a JSON file."""
        import json
        directory = os.path.dirname(filename)
        if directory:
            os.makedirs(directory, exist_ok=True)

        data = {
            'OpenCVIntrinsics': self.OpenCVIntrinsics.tolist(),
            'RadialDistortion': {
                'k1': self.RadialDistortion.k1,
                'k2': self.RadialDistortion.k2,
                'k3': self.RadialDistortion.k3
            },
            'width': self.width,
            'height': self.height,
            'pixel_size': self.pixel_size,
            'info': self.info
        }
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)

    def load_intrinsics_from_json(self, filename):
        """Load camera intrinsics from a JSON file."""
        import json
        with open(filename, 'r') as f:
            data = json.load(f)

        self.OpenCVIntrinsics = np.array(data['OpenCVIntrinsics'])
        self.RadialDistortion.set_from_list([
            data['RadialDistortion']['k1'],
            data['RadialDistortion']['k2'],
            data['RadialDistortion']['k3']
        ])
        self.width = data['width']
        self.height = data['height']
        self.pixel_size = data['pixel_size']
        self.info = data['info']
        return self
