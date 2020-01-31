# coding=utf-8
"""Face Radiance Properties."""
from ..modifier import Modifier
from ..lib.modifiers import black
from ..lib.modifiersets import generic_modifier_set_visible


class FaceRadianceProperties(object):
    """Radiance Properties for Honeybee Face.

    Properties:
        * host
        * modifier
        * modifier_blk
        * is_modifier_set_on_object
    """

    __slots__ = ('_host', '_modifier', '_modifier_blk')

    def __init__(self, host, modifier=None, modifier_blk=None):
        """Initialize Face radiance properties.

        Args:
            host: A honeybee_core Face object that hosts these properties.
            modifier: A Honeybee Radiance Modifier object for the face. If None,
                it will be set by the parent Room ModifierSet or the the Honeybee
                default generic ModifierSet.
            modifier_blk: A Honeybee Radiance Modifier object to be used for this
                face in direct solar simulations and in isolation studies (assessing
                the contribution of individual Apertures). If None, this will be
                a completely black material if the Face's modifier is opaque and
                will be equal to the modifier if the Face's modifier is non-opaque.
        """
        self._host = host
        self.modifier = modifier
        self.modifier_blk = modifier_blk

    @property
    def host(self):
        """Get the Face object hosting these properties."""
        return self._host

    @property
    def modifier(self):
        """Get or set the Face modifier.

        If the modifier is not set on the face-level, then it will be assigned
        based on the ModifierSet assigned to the parent Room.  If there is no
        parent Room or the parent Room's ModifierSet has no modifier for
        the Face type and boundary_condition, it will be assigned using the
        honeybee default generic ModifierSet.
        """
        if self._modifier:  # set by user
            return self._modifier
        elif self._host.has_parent:  # set by parent room
            modifier_set = self._host.parent.properties.radiance.modifier_set
            return modifier_set.get_face_modifier(
                self._host.type.name, self._host.boundary_condition.name)
        else:
            return generic_modifier_set_visible.get_face_modifier(
                self._host.type.name, self._host.boundary_condition.name)

    @modifier.setter
    def modifier(self, value):
        if value is not None:
            assert isinstance(value, Modifier), \
                'Expected Radiance Modifier for face. Got {}'.format(type(value))
            value.lock()  # lock editing in case modifier has multiple references
        self._modifier = value

    @property
    def modifier_blk(self):
        """Get or set a modifier to be used in direct solar and in isolation studies.
        
        If None, this will be a completely black material if the Face's modifier
        is opaque and will be equal to the modifier if the Face's modifier is non-opaque.
        """
        if self._modifier_blk:  # set by user
            return self._modifier_blk
        mod = self.modifier  # assign a default based on whether the modifier is opaque
        if mod.is_opaque:
            return black
        else:
            return mod

    @modifier_blk.setter
    def modifier_blk(self, value):
        if value is not None:
            assert isinstance(value, Modifier), \
                'Expected Radiance Modifier for face. Got {}'.format(type(value))
            value.lock()  # lock editing in case modifier has multiple references
        self._modifier_blk = value

    @property
    def is_modifier_set_on_object(self):
        """Boolean noting if modifier is assigned on the level of this Face.
        
        This is opposed to having the modifier assigned by a ModifierSet.
        """
        return self._modifier is not None
    
    def reset_to_default(self):
        """Reset a Modifier assigned at the level of this Face to the default.

        This means that the Face's modifier will be assigned by a ModifierSet instead.
        """
        self._modifier = None

    @classmethod
    def from_dict(cls, data, host):
        """Create FaceRadianceProperties from a dictionary.

        Note that the dictionary must be a non-abridged version for this
        classmethod to work.

        Args:
            data: A dictionary representation of FaceRadianceProperties.
            host: A Face object that hosts these properties.
        """
        assert data['type'] == 'FaceRadianceProperties', \
            'Expected FaceRadianceProperties. Got {}.'.format(data['type'])

        try:  # ensure the putil module is imported, which imports all primitive modules
            putil
        except NameError:
            import honeybee_radiance.putil as putil

        new_prop = cls(host)
        if 'modifier' in data and data['modifier'] is not None:
            new_prop.modifier = putil.dict_to_modifier(data['modifier'])
        if 'modifier_blk' in data and data['modifier_blk'] is not None:
            new_prop.modifier_blk = putil.dict_to_modifier(data['modifier_blk'])
        return new_prop

    def apply_properties_from_dict(self, abridged_data, modifiers):
        """Apply properties from a FaceRadiancePropertiesAbridged dictionary.

        Args:
            abridged_data: A FaceRadiancePropertiesAbridged dictionary (typically
                coming from a Model).
            modifiers: A dictionary of modifiers with modifier names as keys,
                which will be used to re-assign modifiers.
        """
        if 'modifier' in abridged_data and abridged_data['modifier'] is not None:
            self.modifier = modifiers[abridged_data['modifier']]
        if 'modifier_blk' in abridged_data and abridged_data['modifier_blk'] is not None:
            self.modifier_blk = modifiers[abridged_data['modifier_blk']]

    def to_dict(self, abridged=False):
        """Return radiance properties as a dictionary.

        Args:
            abridged: Boolean to note whether the full dictionary describing the
                object should be returned (False) or just an abridged version (True).
                Default: False.
        """
        base = {'radiance': {}}
        base['radiance']['type'] = 'FaceRadianceProperties' if not \
            abridged else 'FaceRadiancePropertiesAbridged'
        if self._modifier is not None:
            base['radiance']['modifier'] = \
                self._modifier.name if abridged else self._modifier.to_dict()
        if self._modifier_blk is not None:
            base['radiance']['modifier_blk'] = \
                self._modifier_blk.name if abridged else self._modifier_blk.to_dict()
        return base

    def duplicate(self, new_host=None):
        """Get a copy of this object.

        new_host: A new Face object that hosts these properties.
            If None, the properties will be duplicated with the same host.
        """
        _host = new_host or self._host
        return FaceRadianceProperties(_host, self._modifier, self._modifier_blk)

    def ToString(self):
        return self.__repr__()

    def __repr__(self):
        return 'Face Radiance Properties:\n host: {}'.format(self.host.name)
