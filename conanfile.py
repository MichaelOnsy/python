import pathlib
from conan import ConanFile, tools
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conans.errors import ConanException


class ARecipe(ConanFile):
    name = "hackathon-a"

    # Use git hash as recipe revision to keep VxWorks and Senux builds aligned
    revision_mode = "scm"

    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    # Sources are located in the same place as this recipe, copy them to the recipe
    exports_sources = "CMakeLists.txt", "src/*", "include/*", "tests/*"

    def set_version(self):
        # Command line ``--version=xxxx`` will be assigned first to self.version and have priority
        self.version = self.version

    def config_options(self):
        if self.settings.os in ("Windows", "VxWorks"):
            self.options.rm_safe("fPIC")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def requirements(self):
        self.requires("core/[~0.1]")
        self.requires("osal/[~0.1]")
        self.requires("component-management/[~0.3]")
        if not self.conf.get("tools.build:skip_test", default=True):
            if self.settings.os in ("Windows", "VxWorks"):
                self.requires("googletest/[~0.0]")
            if self.settings.os == "Linux":
                self.requires("googletest-linux/[~0.0]")

    def layout(self):
        cmake_layout(self)

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)
        if self.settings.os == "Linux":
            tc.cache_variables["PLATFORM"] = "Senux"
        else:
            tc.cache_variables["PLATFORM"] = str(self.settings.os)
        tc.variables["SHARED"] = self.options.shared
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
        if not self.conf.get("tools.build:skip_test", default=True):
            test_folder = pathlib.Path.cwd().joinpath("tests")
            self.run(f"{test_folder.joinpath('ATest')} --gtest_shuffle --gtest_repeat=3 --gtest_color=auto")

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.includedirs = ['include', 'mocks']
        if self.settings.os != "VxWorks":
            self.cpp_info.libs = ["A"]
FooterSchneider Electric
Schneider Electric avatar
Schneider Electric
© 2024 GitHub, Inc.
Footer navigation
Help
Support
GitHub Enterprise Server 3.12.4
hackathon-a/conanfile.py at main · OMEGA/hackathon-a
