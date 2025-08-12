from cargo_workspace import CratesLinter, Workspace, WorkspaceLinter, Version, Crate, Manifest, VersionBumpKind

def test_package_metadata_works():
	content = """
	[package]
	name = "test"
	[package.metadata.docs.rs]
	targets = ["x86_64-unknown-linux-gnu"]
	custom = "value"
	"""
	crate = Crate.from_raw_manifest(content, "path")
	assert crate.metadata.get('docs.rs.targets') == ["x86_64-unknown-linux-gnu"]

	content = """
	[package]
	name = "test"
	[package.metadata.polkadot-sdk]
	internal = true
	"""
	crate = Crate.from_raw_manifest(content, "path")
	assert crate.metadata.get("polkadot-sdk.internal")
	assert not crate.metadata.get("polkadot-sdk.internal2", False)
	assert crate.metadata.get("polkadot-sdk.internal2", True)
	assert crate.metadata.get("polkadot-sdk.internal2") is None

def test_crate_from_path_works():
	crate = Crate.from_path("../polkadot-sdk/substrate/frame/Cargo.toml")

def test_version_from_str():
	assert Version.from_str("0.1.2") == Version(0, 1, 2)
	assert Version.from_str("0.1.2-alpha") == Version(0, 1, 2, "alpha")
	assert Version.from_str("0.1.2-beta.123") == Version(0, 1, 2, "beta.123")
	assert Version.from_str("0.1.2-beta-123") == Version(0, 1, 2, "beta-123")

def test_manifest_to_crate_good():
	content = """
	[package]
	name = "test"
	"""

	manifest = Manifest.from_raw(content, "Cargo.toml")
	crate = manifest.into_crate()

def test_manifest_to_crate_workspace_bad_1():
	content = "[workspace]"
	manifest = Manifest.from_raw(content, "Cargo.toml")
	try:
		crate = manifest.into_crate()
		assert False
	except ValueError as e:
		assert str(e) == "A single crate was expected, but it does contain a workspace section"

def test_manifest_to_crate_workspace_bad_2():
	content = ""
	manifest = Manifest.from_raw(content, "Cargo.toml")
	try:
		crate = manifest.into_crate()
		assert False
	except ValueError as e:
		assert str(e) == "Could not find package in crate manifest"

def test_manifest_to_crate_workspace_bad_3():
	content = "[package]"
	manifest = Manifest.from_raw(content, "Cargo.toml")
	try:
		crate = manifest.into_crate()
		assert False
	except ValueError as e:
		assert str(e) == "Could not find name in crate manifest"

def test_parse_sdk():
	w = Workspace.from_path("../polkadot-sdk/Cargo.toml")
	assert w.path == "../polkadot-sdk"
	linter = w.into_linter()
	excluded = [
		'../polkadot-sdk/substrate/frame/contracts/fixtures/build/Cargo.toml',
		'../polkadot-sdk/substrate/frame/contracts/fixtures/contracts/common/Cargo.toml',
		'../polkadot-sdk/substrate/primitives/state-machine/fuzz/Cargo.toml'
	]

	linter.ensure_no_duplicate_crate_paths()
	linter.ensure_no_stray_manifest_files(excluded)
 
	w.crates.without_by_name([
		"snowbridge-runtime-test-common",
		"pallet-collective-content",
		"sc-mixnet",
		"sp-core-fuzz",
		"sp-mixnet",
		"sp-consensus-sassafras",
		"pallet-mixnet",
		"pallet-sassafras",
		"frame",
		"pallet-example-frame-crate"
	]).into_linter().ensure_uses_workspace_inheritance('edition')
	
	w.crates.without_by_name([
		"pallet-collective-content",
		"penpal-runtime",
		"sc-mixnet",
		"polkadot-sdk-frame",
		"pallet-example-frame-crate",
		"pallet-mixnet",
		"pallet-parameters",
		"pallet-sassafras",
		"sp-core-fuzz",
		"sp-mixnet"
	]) \
 	.without(lambda c: c.name.startswith("snowbridge-")) \
	.into_linter() \
	.ensure_uses_workspace_inheritance('authors')

	crates = w.crates
	assert len(crates) >= 400
	assert crates[0].name == "bridge-runtime-common"
	assert crates[0].rel_path == "bridges/bin/runtime-common/Cargo.toml"
	assert crates[0].abs_path.startswith("/Users/")
	assert crates[0].full_path == "../polkadot-sdk/bridges/bin/runtime-common/Cargo.toml"
	assert crates[0].version.into_mmp() == Version(7)
	assert crates[0].version.into_xyz() == Version(0, 7)
	assert crates[0].version.suffix is None
	assert crates[0].publish
 
	deps = crates.find_by_name("polkadot-sdk-frame").dependencies
	for _ in deps:
		pass
	assert len(deps) > 0
	normal_dep = deps.find_by_name('frame-support')
	assert normal_dep.name == 'frame-support'
	assert crates.find_by_name("polkadot-sdk-frame").description == "The single package to get you started with building frame pallets and runtimes"

	assert len(crates.abs_paths) == len(crates)
	assert len(crates.rel_paths) == len(crates)
	assert len(crates.names) == len(crates)

	deps = w.dependencies
	assert len(deps) > 0
	# can iter
	for _ in deps:
		pass

def test_package_alias():
	w = Workspace.from_path("../polkadot-sdk/Cargo.toml")

	for d in w.dependencies:
		if d.package is not None:
			continue

def test_semver_str_works():
	assert str(Version(0)) == "0.0.0"
	assert str(Version(0, 0)) == "0.0.0"
	assert str(Version(0, 0, 0)) == "0.0.0"

	assert str(Version(1)) == "1.0.0"
	assert str(Version(1, 0)) == "1.0.0"
	assert str(Version(1, 0, 0)) == "1.0.0"
	assert str(Version(0, 1)) == "0.1.0"
	assert str(Version(0, 1, 0)) == "0.1.0"
	assert str(Version(0, 0, 1)) == "0.0.1"

	assert str(Version(1, 2, 3)) == "1.2.3"

def test_semver_str_suffix_works():
	assert str(Version(0, 0, 0, "suff.123")) == "0.0.0-suff.123"
	assert str(Version(0, 1, 0, "suff.123")) == "0.1.0-suff.123"
	assert str(Version(0, 0, 1, "suff-123")) == "0.0.1-suff-123"

def test_semver_major_works():
	assert Version(1).cargo_convention().major == 1
	assert Version(0, 1).cargo_convention().major == 1
	assert Version(0, 0, 1).cargo_convention().major == 1

	assert Version(1).cargo_convention().major == 1
	assert Version(0, 1).cargo_convention().major == 1
	assert Version(0, 0, 1).cargo_convention().major == 1

	assert Version(1).x == 1
	assert Version(0, 1).y == 1
	assert Version(0, 0, 1).z == 1

def test_semver_minor_works():
	assert Version(1).cargo_convention().minor == 0
	assert Version(1, 2).cargo_convention().minor == 2

	assert Version(0, 1).cargo_convention().minor == 0
	assert Version(0, 1, 2).cargo_convention().minor == 2

	assert Version(0, 1).cargo_convention().minor == 0
	assert Version(0, 1, 2).cargo_convention().minor == 2

	assert Version(0, 0, 1).cargo_convention().minor == 0

def test_semver_patch_works():
	assert Version(1).cargo_convention().patch == 0
	assert Version(1, 2).cargo_convention().patch == 0
	assert Version(1, 2, 3).cargo_convention().patch == 3

	assert Version(0, 1).cargo_convention().patch == 0
	assert Version(0, 1, 2).cargo_convention().patch == 0

	assert Version(0, 0, 1).cargo_convention().patch == 0

def test_semver_same_diff_works():
	v1 = Version(1, 2, 3).cargo_convention()
	v2 = Version(1, 2, 3).cargo_convention()

	assert v1.diff(v2).is_stable()
	assert not v1.diff(v2).is_patch()
	assert not v1.diff(v2).is_minor()
	assert not v1.diff(v2).is_major()

def test_semver_diff_works():
	v1 = Version(1, 2, 3).cargo_convention()
	v2 = Version(1, 2, 4).cargo_convention()
	assert v1.diff(v2).is_patch()
	assert v1.diff(v2).is_stable()

	v1 = Version(1, 2, 3).cargo_convention()
	v2 = Version(1, 3, 4).cargo_convention()
	assert v1.diff(v2).is_minor()
	assert not v1.diff(v2).is_patch()
	assert v1.diff(v2).is_stable()

	v1 = Version(1, 2, 3).cargo_convention()
	v2 = Version(2, 3, 4).cargo_convention()
	assert v1.diff(v2).is_major()
	assert not v1.diff(v2).is_minor()
	assert not v1.diff(v2).is_patch()
	assert v1.diff(v2).is_stable()

	v1 = Version(1, 2, 3).cargo_convention()
	v2 = Version(1, 2, 3).cargo_convention()
	assert not v1.diff(v2).is_patch()
	assert not v1.diff(v2).is_minor()
	assert not v1.diff(v2).is_major()
	assert v1.diff(v2).is_stable()

def test_semver_strict_diff_works():
	v1 = Version(1, 2, 3).cargo_convention()
	v2 = Version(1, 3, 4).cargo_convention()
	assert v1.diff(v2).is_minor()
	assert not v1.diff(v2).is_patch()
	assert not v1.diff(v2).is_strict_minor()
	assert not v1.diff(v2).is_patch()
 
	v1 = Version(1, 2, 3).cargo_convention()
	v2 = Version(1, 3, 0).cargo_convention()
	assert v1.diff(v2).is_minor()
	assert v1.diff(v2).is_strict_minor()
	assert not v1.diff(v2).is_patch()
	assert not v1.diff(v2).is_major()

	v1 = Version(1, 2, 3).cargo_convention()
	v2 = Version(2, 3, 0).cargo_convention()
	assert not v1.diff(v2).is_minor()
	assert not v1.diff(v2).is_strict_minor()
	assert not v1.diff(v2).is_patch()
	assert v1.diff(v2).is_major()
	assert not v1.diff(v2).is_strict_major()

	v1 = Version(1, 2, 3).cargo_convention()
	v2 = Version(2, 0, 0).cargo_convention()
	assert not v1.diff(v2).is_minor()
	assert not v1.diff(v2).is_strict_minor()
	assert not v1.diff(v2).is_patch()
	assert v1.diff(v2).is_major()
	assert v1.diff(v2).is_strict_major()

def test_semver_is_stable_works():
	assert not Version(1, 0, 0, 'suffix').is_stable()
	assert not Version(0, 1, 0, 'suffix').is_stable()
	assert not Version(0, 0, 1, 'suffix').is_stable()
	assert not Version(0, 0, 0, 'suffix').is_stable()

	assert not Version(1, 0, 0, 'suffix').cargo_convention().is_stable()
	assert not Version(0, 1, 0, 'suffix').cargo_convention().is_stable()
	assert not Version(0, 0, 1, 'suffix').cargo_convention().is_stable()
	assert not Version(0, 0, 0, 'suffix').cargo_convention().is_stable()
 
	assert Version(1, 0, 0).is_stable()
	assert not Version(0, 1, 0).is_stable()
	assert not Version(0, 0, 1).is_stable()
	assert not Version(0, 0, 0).is_stable()

	assert Version(1, 0, 0).cargo_convention().is_stable()
	assert Version(0, 1, 0).cargo_convention().is_stable()
	assert Version(0, 0, 1).cargo_convention().is_stable()
	assert not Version(0, 0, 0).cargo_convention().is_stable()

def test_semver_bump_backwards_errors():
	v1 = Version(2, 0, 0).cargo_convention()
	v2 = Version(1, 0, 0).cargo_convention()
	
	try:
		v1.diff(v2)
		assert False
	except ValueError as e:
		print("")
	
	v1 = Version(0, 2, 0).cargo_convention()
	v2 = Version(1, 0, 0).cargo_convention()
	
	try:
		v1.diff(v2)
		assert False
	except ValueError as e:
		print("")
	
	v1 = Version(0, 2, 0).cargo_convention()
	v2 = Version(0, 1, 0).cargo_convention()
	
	try:
		v1.diff(v2)
		assert False
	except ValueError as e:
		print("")
	
	v1 = Version(0, 0, 2).cargo_convention()
	v2 = Version(0, 1, 0).cargo_convention()
	
	try:
		v1.diff(v2)
		assert False
	except ValueError as e:
		print("")
	
	v1 = Version(0, 0, 2).cargo_convention()
	v2 = Version(0, 0, 1).cargo_convention()
	
	try:
		v1.diff(v2)
		assert False
	except ValueError as e:
		print("")

def test_semver_unstable_diff_works():
	v1 = Version(0, 2, 3).cargo_convention()
	v2 = Version(0, 2, 4).cargo_convention()
	assert v1.diff(v2).is_minor()
	assert v1.diff(v2).is_stable()

	v1 = Version(0, 0, 3).cargo_convention()
	v2 = Version(0, 0, 4).cargo_convention()
	assert v1.diff(v2).is_major()
	assert v1.diff(v2).is_stable()
	
	v1 = Version(1, 0, 0, "alpha").cargo_convention()
	v2 = Version(1, 0, 1, "alpha").cargo_convention()
	assert v1.diff(v2).is_patch()
	assert not v1.diff(v2).is_stable()

def test_semver_suffix_diff_works():
	v1 = Version(1, 2, 3, "alpha").cargo_convention()
	v2 = Version(1, 2, 3, "beta").cargo_convention()
	assert not v1.diff(v2).is_patch()
	assert not v1.diff(v2).is_minor()
	assert not v1.diff(v2).is_major()
	assert not v1.diff(v2).is_stable()
	assert not v1.diff(v2).is_empty()

def test_semver_bump_kind_works():
	v1 = Version(1, 2, 3).cargo_convention()
	v2 = Version(1, 2, 3).cargo_convention()
	bump = v1.diff(v2)
	assert bump.kind is None
 
	v1 = Version(1, 2, 3).cargo_convention()
	v2 = Version(1, 3, 3).cargo_convention()
	bump = v1.diff(v2)
	assert bump.kind is None
 
	v1 = Version(1, 2, 3).cargo_convention()
	v2 = Version(2, 3, 3).cargo_convention()
	bump = v1.diff(v2)
	assert bump.kind is None

	v1 = Version(1, 2, 3).cargo_convention()
	v2 = Version(1, 2, 4).cargo_convention()
	bump = v1.diff(v2)
	assert bump.kind is VersionBumpKind.PATCH
 
	v1 = Version(1, 2, 3).cargo_convention()
	v2 = Version(1, 3, 0).cargo_convention()
	bump = v1.diff(v2)
	assert bump.kind is VersionBumpKind.MINOR
 
	v1 = Version(1, 2, 3).cargo_convention()
	v2 = Version(2, 0, 0).cargo_convention()
	bump = v1.diff(v2)
	assert bump.kind is VersionBumpKind.MAJOR

def test_semver_cargo_xyz_works():
	v = Version(1, 2, 3, "alpha").cargo_convention()
	assert v.x == 1
	assert v.y == 2
	assert v.z == 3

def test_semver_into_mmp_works():
	v = Version(1, 2, 3, "alpha").cargo_convention()
	assert v.into_mmp() == Version(1, 2, 3, "alpha")

	v = Version(0, 1, 2, "alpha").cargo_convention()
	assert v.into_mmp() == Version(1, 2, 0, "alpha")

	v = Version(0, 0, 1, "alpha").cargo_convention()
	assert v.into_mmp() == Version(1, 0, 0, "alpha")
 
	v = Version(1).cargo_convention()
	assert v.into_mmp() == Version(1)

	v = Version(0, 1).cargo_convention()
	assert v.into_mmp() == Version(1)

	v = Version(0, 0, 1).cargo_convention()
	assert v.into_mmp() == Version(1)

def test_version_bump_kind_cmp_works():
	assert VersionBumpKind.PATCH < VersionBumpKind.MINOR
	assert VersionBumpKind.PATCH < VersionBumpKind.MAJOR
	assert VersionBumpKind.MINOR < VersionBumpKind.MAJOR
 
	assert VersionBumpKind.PATCH <= VersionBumpKind.MINOR
	assert VersionBumpKind.PATCH <= VersionBumpKind.MAJOR
	assert VersionBumpKind.MINOR <= VersionBumpKind.MAJOR
	
	assert VersionBumpKind.MINOR > VersionBumpKind.PATCH
	assert VersionBumpKind.MAJOR > VersionBumpKind.PATCH
	assert VersionBumpKind.MAJOR > VersionBumpKind.MINOR
	
	assert VersionBumpKind.MINOR >= VersionBumpKind.PATCH
	assert VersionBumpKind.MAJOR >= VersionBumpKind.PATCH
	assert VersionBumpKind.MAJOR >= VersionBumpKind.MINOR
	
	assert VersionBumpKind.PATCH == VersionBumpKind.PATCH
	assert VersionBumpKind.MINOR == VersionBumpKind.MINOR
	assert VersionBumpKind.MAJOR == VersionBumpKind.MAJOR
 
	assert VersionBumpKind.PATCH != VersionBumpKind.MINOR
	assert VersionBumpKind.PATCH != VersionBumpKind.MAJOR
	assert VersionBumpKind.MINOR != VersionBumpKind.MAJOR

def test_version_bump_kind_max_works():
    assert VersionBumpKind.PATCH.max(VersionBumpKind.MINOR) == VersionBumpKind.MINOR
    assert VersionBumpKind.PATCH.max(VersionBumpKind.MAJOR) == VersionBumpKind.MAJOR
    assert VersionBumpKind.MINOR.max(VersionBumpKind.PATCH) == VersionBumpKind.MINOR
    
    assert max([VersionBumpKind.PATCH, VersionBumpKind.MINOR]) == VersionBumpKind.MINOR
    assert max([VersionBumpKind.PATCH, VersionBumpKind.MAJOR]) == VersionBumpKind.MAJOR
    assert max([VersionBumpKind.MINOR, VersionBumpKind.PATCH]) == VersionBumpKind.MINOR

def test_version_bump_kind_str_works():
	assert str(VersionBumpKind.PATCH) == "patch"
	assert str(VersionBumpKind.MINOR) == "minor"
	assert str(VersionBumpKind.MAJOR) == "major"

def  test_version_bump_from_str_works():
	assert VersionBumpKind.from_str("patch") == VersionBumpKind.PATCH
	assert VersionBumpKind.from_str("minor") == VersionBumpKind.MINOR
	assert VersionBumpKind.from_str("major") == VersionBumpKind.MAJOR
 
	try:
		VersionBumpKind.from_str("unknown")
		assert False
	except ValueError as e:
		print("")
