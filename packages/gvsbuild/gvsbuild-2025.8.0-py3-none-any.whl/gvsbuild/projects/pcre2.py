from gvsbuild.utils.base_builders import Meson
from gvsbuild.utils.base_expanders import Tarball
from gvsbuild.utils.base_project import Project, project_add


@project_add
class Pcre2(Tarball, Meson):
    def __init__(self):
        Project.__init__(
            self,
            "pcre2",
            version="10.45",
            archive_url="https://github.com/PCRE2Project/pcre2/releases/download/pcre2-{version}/pcre2-{version}.tar.gz",
            hash="0e138387df7835d7403b8351e2226c1377da804e0737db0e071b48f07c9d12ee",
            dependencies=["ninja", "meson", "pkgconf"],
        )

    def build(self):
        Meson.build(self)
        self.install(r".\COPYING share\doc\pcre2")
