import toml
from enum import Enum

class DependencyLocation(Enum):
	PATH = 1
	CRATES_IO = 2
	GIT = 3

class Dependency:
	def __init__(self, name, kind, inner):
		self._name = name
		self._kind = kind

		# We dont know if its a table or a string:
		if isinstance(inner, str):
			self._inner = {'version': inner}
		else:
			self._inner = inner

		self._location = self._calc_location()
	
	def _calc_location(self):
		has_path = 'path' in self._inner
		has_git = 'git' in self._inner
		has_version = 'version' in self._inner

		if (has_path and has_git) or (has_path and has_version) or (has_git and has_version):
			self._report_multiple_locations_error(has_path, has_git, has_version)

		if has_path:
			return DependencyLocation.PATH
		if has_git:
			return DependencyLocation.GIT

		# A version can also be in the form: `dep = "0.1.0"`, so we dont check it here.
		return DependencyLocation.CRATES_IO
	
	def _report_multiple_locations_error(self, has_path, has_git, has_version):
		raise ValueError(f"Dependency '{self._name}' cannot have multiple location set, but has: {', '.join(self._inner.keys())}")

	def __getattr__(self, name):
		if name == 'name':
			return self._name
		if name == 'package':
			return self._inner.get('package')
		if name == 'version':
			return self._inner.get('version')
		if name == 'kind':
			return self._kind
		if name == 'location':
			return self._location
		if name == 'inner':
			return self._inner

		raise AttributeError(f'No such attribute: {name} in {self}: {self._inner}')

class Dependencies:
	def __init__(self, deps):
		self._deps = deps

	def __iter__(self):
		return iter(self._deps)
   
	def from_map(deps):  # map: kind -> [Dependency]
		for key in deps.keys():
			if not key in ['normal', 'dev', 'build']:
				raise ValueError(f'Unexpected map key {key}')

		ret = []
		for kind, deps in deps.items():
			for name, dep in deps:
				ret.append(Dependency(name, kind, dep))
		return Dependencies(ret)
   
	def __len__(self):
		return len(self._deps)

	def find_by(self, pred):
		for dep in self._deps:
			if pred(dep):
				return dep

		return None

	def find_by_name(self, name):
		return self.find_by(lambda d: d.name == name)
