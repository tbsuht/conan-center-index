import os

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout, CMakeDeps
from conan.tools.files import get, rmdir, copy
from conan.tools.microsoft import is_msvc

required_conan_version = ">=1.53.0"


class LibYangConan(ConanFile):
    name = "libyang"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    description = "YANG data modeling language library"
    homepage = "https://github.com/CESNET/libyang"
    topics = ("yang", "bsd", "netconf", "restconf", "yin")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False],
               "fPIC": [True, False]}
    default_options = {
        "shared": False,
        "fPIC": True
    }

    tool_requires = "cmake/[>=3.22.0 <4]"

    def requirements(self):
        self.requires("pcre2/10.42", transitive_headers=True)
        if is_msvc(self):
            self.requires("getopt-for-visual-studio/20200201")
            self.requires("dirent/1.24")
            self.requires("pthreads4w/3.0.0")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["ENABLE_TESTS"] = False
        tc.variables["ENABLE_VALGRIND_TESTS"] = False
        tc.variables["ENABLE_STATIC"] = not self.options.shared
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder,
             os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        # move /share to /res
        copy(self, "*", os.path.join(self.package_folder, "share"),
             os.path.join(self.package_folder, "res", "share"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "LibYANG")
        self.cpp_info.libs = ["yang"]
        self.cpp_info.resdirs = ["res"]
        if self.settings.os == "Windows":
            self.cpp_info.system_libs.extend(["ws2_32", "shlwapi"])
        elif self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["pthread", "dl", "m"])
