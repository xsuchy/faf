import subprocess
import tempfile
import os.path
import shutil

"""
Low-level package packaging operations.
"""

def unpack_rpm_to_tmp(path, prefix="faf"):
    """
    Unpacks an RPM package (path) to a temp directory.  Returns path
    to that directory.

    Parameter prefix: prefix of the temp directory.

    Raises an exception in the case of failure.
    """
    temp_dir = tempfile.mkdtemp(prefix=prefix)
    with open(os.path.join(temp_dir, "package.cpio", "wb")) as cpio_file:
        os.remove(cpio_file.name)
        rpm2cpio_proc = subprocess.Popen(["rpm2cpio", path],
                                         stdout=cpio_file, stderr=subprocess.PIPE)

        _, stderr = rpm2cpio_proc.communicate()
        if rpm2cpio_proc.returncode != 0:
            # WORKAROUND - rpm2cpio returns wrong exitcode for large
            # resulting cpio files remove this once
            # https://bugzilla.redhat.com/show_bug.cgi?id=790396 is fixed
            if not (stderr == ''
                    and os.path.exists(cpio_file.name)
                    and os.path.getsize(cpio_file.name) > 2 * (1024**3)):
                shutil.rmtree(temp_dir)
                raise Exception("Failed to convert RPM to cpio using rpm2cpio: {0}".format(path))
        cpio_file.seek(0)

        cpio_proc = subprocess.Popen(["cpio", "--extract", "-d", "--quiet"],
                                     stdin=cpio_file, cwd=temp_dir,
                                     stderr=subprocess.PIPE)
        cpio_proc.wait()
        if cpio_proc.returncode != 0:
            shutil.rmtree(temp_dir)
            raise Exception("Failed to unpack RPM using cpio: {0}".format(cpio_proc.stderr.read()))
        return temp_dir
