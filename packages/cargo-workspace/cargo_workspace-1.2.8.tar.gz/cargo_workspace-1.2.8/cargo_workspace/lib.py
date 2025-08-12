import os
import toml

from .dependency import Dependencies, DependencyLocation
from .version import Version, CargoVersion, CargoVersionBump

class Crate:
	def __init__(self, manifest, path, root_dir=None):
		Crate.__ensure_is_manifest(manifest)
		self._manifest = manifest
		self._path = path
		self._root_dir = root_dir

	def from_path(path, root_dir=None):
		abs_path = os.path.join(root_dir, path) if root_dir else path
		if not os.path.exists(abs_path):
			raise ValueError(f'Could not load crate manifest at {abs_path}')

		try:
			with open(abs_path, 'r') as f:
				return Crate.from_raw_manifest(f.read(), path, root_dir)
		except FileNotFoundError:
			raise ValueError(f'Could not load crate manifest at {abs_path}')
	
	def from_raw_manifest(content, path, root_dir=None):
		manifest = toml.loads(content)
		return Crate(manifest, path, root_dir)

	def __ensure_is_manifest(manifest):
		if 'workspace' in manifest:
			raise ValueError(f'A single crate was expected, but it does contain a workspace section')
		if not 'package' in manifest:
			raise ValueError(f'Could not find package in crate manifest')
		if not 'name' in manifest['package']:
			raise ValueError(f'Could not find name in crate manifest')

	def __getattr__(self, name):
		# Not using 'match' here since it requires python version 3.10.
		if name == 'name':
			return self._crate()['name']
		if name == 'version':
			return self._get_version()
		if name == 'rel_path':
			return self._path
		if name == 'full_path':
			return os.path.join(self._root_dir, self._path) if self._root_dir else self._path
		if name == 'abs_path' or name == 'path':
			return os.path.abspath(self.full_path)
		if name == 'metadata':
			return self._get_metadata()
		if name == 'publish':
			return self._get_publish()
		if name == 'description':
			return self._crate().get('description', None)
		if name == 'edition':
			return self._crate().get('edition', None)
		if name == 'authors':
			return self._crate().get('authors', [])
		if name == 'dependencies':
			return self.dependencies_by_kinds()

		raise AttributeError(f'No such attribute: {name}')

	def dependencies_by_kinds(self, kinds=['normal', 'build', 'dev']):
		deps = {}
		for kind in kinds:
			table = f"{kind}-dependencies" if kind != 'normal' else 'dependencies'
			table = self._manifest.get(table, None)
			if table is None:
				continue
   
			for name, v in table.items():
				if not kind in deps:
					deps[kind] = []
				deps[kind].append((name, v))
		return Dependencies.from_map(deps)

	def _get_version(self):
		if not 'version' in self._crate():
			raise ValueError(f'Could not find version in crate manifest at {self._path}')
		return Version.from_str(self._crate()['version']).cargo_convention()

	def _get_metadata(self):
		return Metadata(self._crate().get('metadata', {}))

	def _crate(self):
		if not 'package' in self._manifest:
			raise ValueError(f'Could not find package in crate manifest at {self._path}')
		return self._manifest['package']

	def _get_publish(self):
		if not 'publish' in self._crate():
			return True

		return bool(self._crate()['publish'])

class Manifest:
	def __init__(self, content, path):
		self._content = content
		self._path = path
	
	def from_parsed(content, path):
		return Manifest(content, path)

	def from_raw(content, path):
		parsed = toml.loads(content)
		return Manifest.from_parsed(parsed, path)

	def from_path(path):
		with open(path, 'rb') as f:
			raw = f.read()
			return Manifest.from_raw(raw, path)
	
	def into_crate(self):
		return Crate(self._content, self._path)

class Metadata:
	'''
	A typed wrapper around a dictionary that represents the metadata section of a crate manifest.
	'''

	def __init__(self, content):
		self._content = content
	
	def get(self, key, default=None):
		splits = key.split('.')
		obj = self._content
		
		for split in splits:
			if split in obj:
				obj = obj[split]
			else:
				return default
		return obj

class CratesCollection:
	def __init__(self, crates):
		self._crates = crates

	def inner(self):
		'''
		Escape hatch to get the inner raw value.
		'''

		return self._crates

	def without_by_name(self, names):
		'''
		Removes crates by name from the collection.
		'''

		return CratesCollection([crate for crate in self._crates if crate.name not in names])

	def without(self, pred):
		'''
		Removes crates from the collection that satisfy the predicate.
		'''

		return CratesCollection([crate for crate in self._crates if not pred(crate)])

	def find_by_name(self, name):
		'''
		Finds a crate by name.
		'''

		for crate in self._crates:
			if crate.name == name:
				return crate
		return None

	def __len__(self):
		return len(self._crates)

	def __iter__(self):
		return iter(self._crates)

	def __getitem__(self, index):
		return self._crates[index]

	def __getattr__(self, name):
		if name == 'rel_paths':
			return [crate.rel_path for crate in self._crates]
		if name == 'abs_paths':
			return [crate.abs_path for crate in self._crates]
		if name == 'names':
			return [crate.name for crate in self._crates]
		
		raise AttributeError(f'No such attribute: {name}')
	
	def into_linter(self):
		return CratesLinter(self._crates)

class CratesLinter:
	def __init__(self, crates):
		self._crates = crates
		
	def ensure_uses_workspace_inheritance(self, attribute):
		good = {'workspace': True}

		for crate in self._crates:
			got = getattr(crate, attribute, None)
			if got != good:
				raise ValueError(f'Attribute {attribute} is not inherited from the workspace in {crate.path} but instead set to {got}')

class Workspace:
	def __init__(self, manifest, root_path=None):
		self._manifest = manifest
		self._root_dir = root_path or os.getcwd()
		self._crates = Workspace.__crates_from_manifest(manifest, self._root_dir)

	def __str__(self):
		return f'workspace at {self._root_dir} with {len(self._crates)} crates'

	def from_raw_manifest(content, root_dir):
		manifest = toml.loads(content)
		return Workspace(manifest, root_dir)

	def from_path(path, allow_dir=True):
		if not path.endswith('Cargo.toml') and allow_dir:
			path = os.path.join(path, 'Cargo.toml')
		
		try:
			root_dir = os.path.dirname(path)

			with open(path, 'r') as f:
				return Workspace.from_raw_manifest(f.read(), root_dir)
		except FileNotFoundError:
			raise ValueError(f'Could not load workspace manifest at {path}')

	def __crates_from_manifest(manifest, root_dir):
		crates = []

		if 'workspace' not in manifest or 'members' not in manifest['workspace']:
			return		

		# Go through the list of members and create Crate objects:
		for path in manifest['workspace']['members']:
			path = os.path.join(path, 'Cargo.toml')

			crate = Crate.from_path(path, root_dir=root_dir)
			crates.append(crate)
		
		return crates
	
	def __getattr__(self, name):
		if name == 'path':
			return self._root_dir
		if name == 'crates':
			return CratesCollection(self._crates)
		if name == 'dependencies':
			return self._dependencies()
		if name == 'manifest':
			return self._manifest

		raise AttributeError(f'No such attribute: {name}')

	def crate_by_name(self, name):
		found = []
		for crate in self.crates:
			if crate.name == name:
				found.append(crate)
		
		if len(found) > 1:
			raise ValueError(f'Found multiple crates with name {name}')
		if len(found) == 0:
			return None
		return found[0]

	def into_linter(self):
		return WorkspaceLinter(self)
	
	def _dependencies(self):
		deps = {}

		table = self._manifest.get('workspace', None)
		if table is None:
			return None
		table = table.get('dependencies', None)
		if table is None:
			return None
		
		deps = { "normal": [] }
		for name, v in table.items():
			deps["normal"].append((name, v))
		return Dependencies.from_map(deps)

class WorkspaceLinter:
	def __init__(self, workspace):
		self._workspace = workspace
	
	def ensure_no_stray_manifest_files(self, excluded_crates=[]):
		stray = self.__find_stray_manifests()
		stray.sort()
		excluded_crates.sort()

		bad = []
		for path in stray:
			if path not in excluded_crates:
				bad.append(path)

		if len(bad) > 0:
			raise ValueError(f'Found stray manifests: {bad}')

	def ensure_no_duplicate_crate_paths(self):
		paths = set()
		for crate in self._workspace.crates:
			path = os.path.abspath(crate.rel_path)
			if path in paths:
				raise ValueError(f'There are two crates with the same absolute path {self._workspace.path}')

			paths.add(path)
	
	def __find_stray_manifests(self, excluded_crates=None):
		all_paths = WorkspaceLinter.__find_manifest_paths(self._workspace.path, exclude_dirs=["target"])
		workspace_paths = self._workspace.crates.abs_paths
		stray_paths = []

		for path in all_paths:
			if os.path.abspath(path) not in workspace_paths:
				stray_paths.append(path)
		
		stray_paths.remove(os.path.join(self._workspace.path, 'Cargo.toml'))
		stray_paths.sort()

		if len(stray_paths) > 0:
			return stray_paths
		return None

	def __find_manifest_paths(root_dir, exclude_dirs):
		paths = []
		for root, dirs, files in os.walk(root_dir):
			if any(exclude in root for exclude in exclude_dirs):
				continue
			if 'Cargo.toml' in files:
				path = os.path.join(root, 'Cargo.toml')

				if os.path.islink(path):
					raise ValueError(f'Found symlinked manifest at {path}')

				paths.append(path)

		paths.sort()
		return paths
