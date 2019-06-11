"""A grid of sensors."""
from __future__ import division
import ladybug.futil as futil
import honeybee_radiance.typing as typing
from .sensor import Sensor

import os
try:
    from itertools import izip as zip
except:
    # python 3
    pass

class SensorGrid(object):
    """A grid of sensors.

    Attributes:
        name
        sensors
        locations
        directions
    """

    __slots__ = ('_sensors', '_name')

    def __init__(self, name, sensors):
        """Initialize a SensorGrid.

        Args:
            name: A unique name for this SensorGrid.
            sensors: A collection of Sensors.
        """
        self.name = typing.valid_string(name)
        self._sensors = tuple(sensors)
        for sen in self._sensors:
            if not isinstance(sen, Sensor):
                raise ValueError(
                    'Sensors in SensorGrid must be form type Sensor not %s' % type(sen)
                )

    @classmethod
    def from_dict(cls, ag_dict):
        """Create a sensor grid from a dictionary."""
        sensors = (Sensor.from_dict(sensor) for sensor in ag_dict['sensors'])
        return cls(name=ag_dict["name"], sensors=sensors)

    @classmethod
    def from_planar_grid(cls, name, locations, plane_normal):
        """Create a sensor grid from a collection of locations with the same direction.

        Args:
            locations: A list of (x, y ,z) for location of sensors.
            plane_normal: (x, y, z) for direction of sensors.
        """
        sg = (Sensor(l, plane_normal) for l in locations)
        return cls(name, sg)

    @classmethod
    def from_location_and_direction(cls, name, locations, directions):
        """Create a sensor grid from a collection of locations and directions.

        The length of locations and directions should be the same. In case the lists have
        different lengths the shorter list will be used as the reference.

        Args:
            locations: A list of (x, y ,z) for location of sensors.
            directions: A list of (x, y, z) for direction of sensors.
        """
        sg = tuple(Sensor(l, v) for l, v in zip(locations, directions))
        return cls(name, sg)

    @classmethod
    def from_file(cls, file_path, start_line=None, end_line=None, name=None):
        """Create a sensor grid from a sensors file.

        The sensors must be structured as

        x1, y1, z1, dx1, dy1, dz1
        x2, y2, z2, dx2, dy2, dz2
        ...

        The lines that starts with # will be considred as commented lines and won't be
        loaded. These lines will be considered in line count for start_line and end_line.

        Args:
            file_path: Full path to sensors file
            start_line: Start line including the comments (default: 0).
            end_line: End line as an integer including the comments
                (default: last line in file).
            name: An optional name for SensorGrid otherwise the file name will be used.
        """
        if not os.path.isfile(file_path):
            raise IOError("Can't find {}.".format(file_path))
        name = name or os.path.split(os.path.splitext(file_path)[0])[-1]
        
        start_line = int(start_line) if start_line is not None else 0
        try:
            end_line = int(end_line)
        except TypeError:
            end_line = float('+inf')

        line_count = end_line - start_line + 1


        sensors = []
        with open(file_path, 'r') as inf:
            for _ in range(start_line):
                line = next(inf)

            for count, l in enumerate(inf):
                if not count < line_count:
                    break
                if not l or l[0] == '#':
                    # commented line
                    continue
                sensors.append(Sensor.from_raw_values(*l.split()))

        return cls(name, sensors)

    @property
    def name(self):
        """SensorGrid name."""
        return self._name

    @name.setter
    def name(self, n):
        self._name = typing.valid_string(n)

    @property
    def locations(self):
        """A generator of sensor locations as x, y, z."""
        return (ap.location for ap in self.sensors)

    @property
    def directions(self):
        """A generator of sensor directions as x, y , z."""
        return (ap.direction for ap in self.sensors)

    @property
    def sensors(self):
        """Return a list of sensors."""
        return self._sensors

    def duplicate(self):
        """Duplicate SensorGrid."""
        return SensorGrid(self.name, (sen.duplicate() for sen in self.sensors))

    def to_radiance(self):
        """Return sensors grid as a Radiance string."""
        return "\n".join((ap.to_radiance() for ap in self._sensors))

    def to_file(self, folder, file_name=None, mkdir=False):
        """Write this sensor grid to file.
        
        Args:
            folder: Target folder.
            file_name: Optional file name without extension (Default: self.name).
            mkdir: A boolean to indicate if the folder should be created in case it
                doesn't exist already (Default: False). 

        Returns:
            Full path to newly created file.
        """
        name = file_name or self.name + '.pts'
        return futil.write_to_file_by_name(
            folder, name, self.to_radiance() + '\n', mkdir)

    def ToString(self):
        """Overwrite ToString .NET method."""
        return self.__repr__()

    def to_dict(self):
        """Convert SensorGrid to a dictionary."""
        return {
            "name": self.name,
            "sensors": [sen.to_dict() for sen in self.sensors]
        }

    def __len__(self):
        """Number of sensors in this grid."""
        return len(self.sensors)

    def __getitem__(self, index):
        """Get a sensor for an index."""
        return self.sensors[index]

    def __eq__(self, value):
        if not isinstance(value, SensorGrid) or len(value) != len(self):
            return False
        if self.name != value.name:
            return False
        if self.sensors != value.sensors:
            return False
        return True

    def __ne__(self, value):
        return not self.__eq__(value)

    def __iter__(self):
        """Sensors iterator."""
        return iter(self.sensors)

    def __str__(self):
        """String repr."""
        return self.to_radiance()

    def __repr__(self):
        """Return sensors and directions."""
        return 'SensorGrid::{}::#{}'.format(self._name, len(self.sensors))
