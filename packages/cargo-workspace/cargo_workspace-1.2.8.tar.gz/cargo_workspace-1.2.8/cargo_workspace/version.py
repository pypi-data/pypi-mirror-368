from enum import Enum

class Version:
	def __init__(self, x, y=0, z=0, suffix=None):
		self._x = x
		self._y = y
		self._z = z
		self._suffix = suffix
	
	def __str__(self):
		su = f"-{self._suffix}" if self._suffix is not None else ""

		return f"{self._x}.{self._y}.{self._z}{su}"
	
	def __eq__(self, other):
		return (self._x == other._x) and (self._y == other._y) and (self._z == other._z) and (self._suffix == other._suffix)

	def from_str(s):
		if '-' in s:
			splits = s.partition('-')
			ver = splits[0]
			suffix = splits[2]
		else:
			ver = s
			suffix = None

		v = Version.from_str_no_suffix(ver)
		v._suffix = suffix
		
		return v
	
	def from_str_no_suffix(s):
		parts = s.split('.')
		if len(parts) == 1:
			return Version(int(parts[0]))
		if len(parts) == 2:
			return Version(int(parts[0]), int(parts[1]))
		if len(parts) == 3:
			return Version(int(parts[0]), int(parts[1]), int(parts[2]))
		raise ValueError(f'Invalid version string: {s}')
	
	def cargo_convention(self):
		return CargoVersion(self)
	
	def is_stable(self):
		return self._suffix is None and self._x > 0
	
	def __getattr__(self, name):
		if name == 'x':
			return self._x
		if name == 'y':
			return self._y
		if name == 'z':
			return self._z
		if name == 'suffix':
			return self._suffix
		
		raise AttributeError(f'No such attribute: {name}')

class CargoVersion:
	def __init__(self, version):
		self._version = version
	
	def __eq__(self, other):
		return self._version == other._version

	def __str__(self):
		return str(self._version)

	def _is_valid(self):
		return self.major >= 0 and self.minor >= 0 and self.patch >= 0

	def is_stable(self):
		return self.major > 0 and self.suffix is None

	def diff(self, other):
		if not isinstance(other, CargoVersion):
			raise ValueError(f'Expected a CargoVersion, but got {type(other)}')

		return CargoVersionBump(self, other)

	def into_mmp(self):
		return Version(self.major, self.minor, self.patch, self.suffix)

	def into_xyz(self):
		return self._version

	def __getattr__(self, name):
		if name == 'major':
			return self._major()
		if name == 'minor':
			return self._minor()
		if name == 'patch':
			return self._patch()
		if name == 'suffix':
			return self._suffix()

		if name == 'x':
			return self._version.x
		if name == 'y':
			return self._version.y
		if name == 'z':
			return self._version.z
		
		raise AttributeError(f'No such attribute: {name}')

	def _major(self):
		if self._version.x > 0:
			return self._version.x
		if self._version.y > 0:
			return self._version.y
		return self._version.z
	
	def _minor(self):
		if self._version.x > 0:
			return self._version.y
		if self._version.y > 0:
			return self._version.z
		return 0
	
	def _patch(self):
		if self._version.x > 0:
			return self._version.z
		return 0
	
	def _suffix(self):
		return self._version.suffix

class VersionBumpKind(Enum):
	PATCH = 1
	MINOR = 2
	MAJOR = 3
	
	def from_str(s):
		if s == 'patch':
			return VersionBumpKind.PATCH
		if s == 'minor':
			return VersionBumpKind.MINOR
		if s == 'major':
			return VersionBumpKind.MAJOR
		raise ValueError(f'Unknown version bump kind: {s}')
 
	def max(self, other):
		if self > other:
			return self
		return other

	def __gt__(self, other):
		return self.value > other.value

	def __lt__(self, other):
		return self.value < other.value

	def __ge__(self, other):
		return self.value >= other.value

	def __le__(self, other):
		return self.value <= other.value

	def __eq__(self, other):
		return self.value == other.value

	def __str__(self):
		if self == VersionBumpKind.PATCH:
			return 'patch'
		if self == VersionBumpKind.MINOR:
			return 'minor'
		if self == VersionBumpKind.MAJOR:
			return 'major'
		raise ValueError(f'Unknown version bump kind: {self}')

class CargoVersionBump:
	def __init__(self, old, new):
		self._old = old
		self._new = new

		if not self._is_valid():
			raise ValueError(f'Invalid version bump: {self}')
  
	def __str__(self):
		return f'{self._old} -> {self._new}'

	def _is_valid(self):
		return self._old._is_valid() and self._new._is_valid() and \
			self._old.major <= self._new.major and \
			(self._old.major < self._new.major or self._old.minor <= self._new.minor) and \
			(self._old.major < self._new.major or self._old.minor < self._new.minor or self._old.patch <= self._new.patch)
	
	def _kind(self):
		if self.is_strict_major():
			return VersionBumpKind.MAJOR
		if self.is_strict_minor():
			return VersionBumpKind.MINOR
		if self.is_strict_patch():
			return VersionBumpKind.PATCH
		return None
 
	def is_stable(self):
		return self._old.is_stable() and self._new.is_stable()
	
	def is_empty(self):
		return self._old == self._new

	def is_none(self):
		return self.is_empty()
	
	def is_major(self):
		return self._old.major != self._new.major
	
	def is_strict_major(self):
		return self.is_major() and (self._new.minor == 0) and (self._new.patch == 0) and (self._old.major + 1 == self._new.major)
	
	def is_minor(self):
		return (self._old.major == self._new.major) and (self._old.minor != self._new.minor)
	
	def is_strict_minor(self):
		return self.is_minor() and (self._new.patch == 0) and (self._old.minor + 1 == self._new.minor)
	
	def is_patch(self):
		return (self._old.major == self._new.major) and (self._old.minor == self._new.minor) and (self._old.patch != self._new.patch)

	def is_strict_patch(self):
		return self.is_patch() and (self._old.patch + 1 == self._new.patch)
	
	def __getattr__(self, name):
		if name == 'old':
			return self._old
		if name == 'new':
			return self._new
		if name == 'kind':
			return self._kind()
		
		raise AttributeError(f'No such attribute: {name}')
