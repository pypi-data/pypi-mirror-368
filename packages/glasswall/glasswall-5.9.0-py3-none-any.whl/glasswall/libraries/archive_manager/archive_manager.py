

import ctypes as ct
import functools
import io
import os
from typing import Optional, Union

import glasswall
from glasswall import determine_file_type as dft
from glasswall import utils
from glasswall.config.logging import log
from glasswall.libraries.archive_manager import errors, successes
from glasswall.libraries.library import Library


class ArchiveManager(Library):
    """ A high level Python wrapper for Glasswall Archive Manager. """

    def __init__(self, library_path):
        super().__init__(library_path)
        self.library = self.load_library(os.path.abspath(library_path))

        log.info(f"Loaded Glasswall {self.__class__.__name__} version {self.version()} from {self.library_path}")

    def version(self):
        """ Returns the Glasswall library version.

        Returns:
            version (str): The Glasswall library version.
        """
        # API function declaration
        self.library.GwArchiveVersion.restype = ct.c_char_p

        # API call
        version = self.library.GwArchiveVersion()

        # Convert to Python string
        version = ct.string_at(version).decode()

        return version

    def release(self):
        """ Releases any resources held by the Glasswall Archive Manager library. """
        self.library.GwArchiveDone()

    @property
    @functools.lru_cache()
    def supported_archives(self):
        """ Returns a list of supported archive file formats. """

        # API function declaration
        self.library.GwSupportedFiletypes.restype = ct.c_char_p

        # API call
        result = self.library.GwSupportedFiletypes()  # b'7z,bz2,gz,rar,tar,xz,zip,'

        # Convert to Python string
        result = ct.string_at(result).decode()  # 7z,bz2,gz,rar,tar,xz,zip,

        # Convert comma separated str to list, remove empty trailing element, sort
        result = sorted(filter(None, result.split(",")))

        return result

    @functools.lru_cache()
    def is_supported_archive(self, archive_type: str):
        """ Returns True if the archive type (e.g. `7z`) is supported. """

        # API function declaration
        self.library.GwIsSupportedArchiveType.argtypes = [
            ct.c_char_p
        ]
        self.library.GwIsSupportedArchiveType.restype = ct.c_bool

        ct_archive_type = ct.c_char_p(archive_type.encode())  # const char* type

        result = self.library.GwIsSupportedArchiveType(ct_archive_type)

        return result

    def list_archive_paths(self, directory: str, recursive: bool = True, absolute: bool = True, followlinks: bool = True):
        """ Returns a list of file paths of supported archives in a directory and all of its subdirectories. """
        return [
            file_path
            for file_path in glasswall.utils.list_file_paths(
                directory=directory,
                recursive=recursive,
                absolute=absolute,
                followlinks=followlinks,
            )
            if self.is_supported_archive(self.determine_file_type(file_path, as_string=True, raise_unsupported=False))
        ]

    def determine_file_type(self, input_file: str, as_string: bool = False, raise_unsupported: bool = True):
        """ Returns an int representing the file type of an archive.

        Args:
            input_file (str) The input file path.
            as_string (bool, optional): Return file type as string, eg: "xz" instead of: 262. Defaults to False.
            raise_unsupported (bool, optional): Default True. Raise exceptions when Glasswall encounters an error. Fail silently if False.

        Returns:
            file_type (Union[int, str]): The file format.
        """
        if not os.path.isfile(input_file):
            raise FileNotFoundError(input_file)

        # API function declaration
        self.library.GwDetermineArchiveTypeFromFile.argtypes = [
            ct.c_char_p
        ]

        # Variable initialisation
        ct_input_file = ct.c_char_p(input_file.encode())  # const char * inputFilePath)

        with utils.CwdHandler(new_cwd=self.library_path):
            # API call
            file_type = self.library.GwDetermineArchiveTypeFromFile(
                ct_input_file
            )

        file_type_as_string = dft.file_type_int_to_str(file_type)
        input_file_repr = f"{type(input_file)} length {len(input_file)}" if isinstance(input_file, (bytes, bytearray,)) else input_file.__sizeof__() if isinstance(input_file, io.BytesIO) else input_file

        if not dft.is_success(file_type):
            if raise_unsupported:
                log.warning(f"\n\tfile_type: {file_type}\n\tfile_type_as_string: {file_type_as_string}\n\tinput_file: {input_file_repr}")
                raise dft.int_class_map.get(file_type, dft.errors.UnknownErrorCode)(file_type)
            else:
                log.debug(f"\n\tfile_type: {file_type}\n\tfile_type_as_string: {file_type_as_string}\n\tinput_file: {input_file_repr}")
        else:
            log.debug(f"\n\tfile_type: {file_type}\n\tfile_type_as_string: {file_type_as_string}\n\tinput_file: {input_file_repr}")

        if as_string:
            return file_type_as_string

        return file_type

    def analyse_archive(self, input_file: Union[str, bytes, bytearray, io.BytesIO], output_file: Optional[str] = None, output_report: Optional[str] = None, content_management_policy: Union[None, str, bytes, bytearray, io.BytesIO, glasswall.content_management.policies.ArchiveManager] = None, raise_unsupported: bool = True):
        """ Extracts the input_file archive and processes each file within the archive using the Glasswall engine. Repackages all files regenerated by the Glasswall engine into a new archive, optionally writing the new archive and report to the paths specified by output_file and output_report.

        Args:
            input_file (Union[str, bytes, bytearray, io.BytesIO]): The archive file path or bytes.
            output_file (Optional[str], optional): Default None. If str, write the archive to the output_file path.
            output_report (Optional[str], optional): Default None. If str, write the analysis report to the output_report path.
            content_management_policy (Union[None, str, bytes, bytearray, io.BytesIO, glasswall.content_management.policies.ArchiveManager], optional): The content management policy to apply.
            raise_unsupported (bool, optional): Default True. Raise exceptions when Glasswall encounters an error. Fail silently if False.

        Returns:
            gw_return_object (glasswall.GwReturnObj): An instance of class glasswall.GwReturnObj containing attributes including: "status" (int), "output_file" (bytes), "output_report" (bytes)
        """
        # Validate arg types
        if not isinstance(input_file, (str, bytes, bytearray, io.BytesIO)):
            raise TypeError(input_file)
        if not isinstance(output_file, (type(None), str)):
            raise TypeError(output_file)
        if not isinstance(output_report, (type(None), str)):
            raise TypeError(output_report)
        if not isinstance(content_management_policy, (type(None), str, bytes, bytearray, io.BytesIO, glasswall.content_management.policies.policy.Policy)):
            raise TypeError(content_management_policy)

        # Convert string path arguments to absolute paths
        if isinstance(input_file, str):
            input_file = os.path.abspath(input_file)
        if isinstance(output_file, str):
            output_file = os.path.abspath(output_file)
        if isinstance(output_report, str):
            output_report = os.path.abspath(output_report)

        # Convert inputs to bytes
        if isinstance(input_file, str):
            if not os.path.isfile(input_file):
                raise FileNotFoundError(input_file)
            with open(input_file, "rb") as f:
                input_file_bytes = f.read()
        elif isinstance(input_file, (bytes, bytearray, io.BytesIO)):
            input_file_bytes = utils.as_bytes(input_file)

        if isinstance(content_management_policy, str) and os.path.isfile(content_management_policy):
            with open(content_management_policy, "rb") as f:
                content_management_policy = f.read()
        elif isinstance(content_management_policy, type(None)):
            # Load default
            content_management_policy = glasswall.content_management.policies.ArchiveManager(default="sanitise", default_archive_manager="process")
        content_management_policy = utils.validate_xml(content_management_policy)

        # API function declaration
        self.library.GwFileAnalysisArchive.argtypes = [
            ct.c_void_p,  # void *inputBuffer
            ct.c_size_t,  # size_t inputBufferLength
            ct.POINTER(ct.c_void_p),  # void **outputFileBuffer
            ct.POINTER(ct.c_size_t),  # size_t *outputFileBufferLength
            ct.POINTER(ct.c_void_p),  # void **outputAnalysisReportBuffer
            ct.POINTER(ct.c_size_t),  # size_t *outputAnalysisReportBufferLength
            ct.c_char_p  # const char *xmlConfigString
        ]

        # Variable initialisation
        gw_return_object = glasswall.GwReturnObj()
        gw_return_object.input_buffer = ct.create_string_buffer(input_file_bytes)
        gw_return_object.input_buffer_length = ct.c_size_t(len(input_file_bytes))
        gw_return_object.output_buffer = ct.c_void_p()
        gw_return_object.output_buffer_length = ct.c_size_t()
        gw_return_object.output_report_buffer = ct.c_void_p()
        gw_return_object.output_report_buffer_length = ct.c_size_t()
        gw_return_object.content_management_policy = ct.c_char_p(content_management_policy.encode())

        with utils.CwdHandler(new_cwd=self.library_path):
            # API call
            gw_return_object.status = self.library.GwFileAnalysisArchive(
                gw_return_object.input_buffer,
                gw_return_object.input_buffer_length,
                ct.byref(gw_return_object.output_buffer),
                ct.byref(gw_return_object.output_buffer_length),
                ct.byref(gw_return_object.output_report_buffer),
                ct.byref(gw_return_object.output_report_buffer_length),
                gw_return_object.content_management_policy
            )

        if gw_return_object.output_buffer and gw_return_object.output_buffer_length:
            gw_return_object.output_file = utils.buffer_to_bytes(
                gw_return_object.output_buffer,
                gw_return_object.output_buffer_length
            )
        if gw_return_object.output_report_buffer and gw_return_object.output_report_buffer_length:
            gw_return_object.output_report = utils.buffer_to_bytes(
                gw_return_object.output_report_buffer,
                gw_return_object.output_report_buffer_length
            )

        # Write output file
        if hasattr(gw_return_object, "output_file"):
            if isinstance(output_file, str):
                os.makedirs(os.path.dirname(output_file), exist_ok=True)
                with open(output_file, "wb") as f:
                    f.write(gw_return_object.output_file)

        # Write output report
        if hasattr(gw_return_object, "output_report"):
            if isinstance(output_report, str):
                os.makedirs(os.path.dirname(output_report), exist_ok=True)
                with open(output_report, "wb") as f:
                    f.write(gw_return_object.output_report)

        input_file_repr = f"{type(input_file)} length {len(input_file)}" if isinstance(input_file, (bytes, bytearray,)) else input_file.__sizeof__() if isinstance(input_file, io.BytesIO) else input_file
        if gw_return_object.status not in successes.success_codes:
            log.error(f"\n\tinput_file: {input_file_repr}\n\toutput_file: {output_file}\n\tstatus: {gw_return_object.status}")
            if raise_unsupported:
                raise errors.error_codes.get(gw_return_object.status, errors.UnknownErrorCode)(gw_return_object.status)
        else:
            log.debug(f"\n\tinput_file: {input_file_repr}\n\toutput_file: {output_file}\n\tstatus: {gw_return_object.status}")

        self.release()

        return gw_return_object

    def analyse_directory(self, input_directory: str, output_directory: Optional[str] = None, output_report_directory: Optional[str] = None, content_management_policy: Union[None, str, bytes, bytearray, io.BytesIO, glasswall.content_management.policies.ArchiveManager] = None, raise_unsupported: bool = True):
        """ Calls analyse_archive on each file in input_directory using the given content management configuration. The resulting archives and analysis reports are written to output_directory maintaining the same directory structure as input_directory.

        Args:
            input_directory (str): The input directory containing archives to analyse.
            output_directory (Optional[str], optional): Default None. If str, the output directory where the archives containing analysis reports of each file will be written.
            output_report_directory (Optional[str], optional): Default None. If str, the output directory where xml reports for each archive will be written.
            content_management_policy (Union[None, str, bytes, bytearray, io.BytesIO, glasswall.content_management.policies.ArchiveManager], optional): The content management policy to apply.
            raise_unsupported (bool, optional): Default True. Raise exceptions when Glasswall encounters an error. Fail silently if False.

        Returns:
            analysed_archives_dict (dict): A dictionary of file paths relative to input_directory, and glasswall.GwReturnObj with attributes: "status" (int), "output_file" (bytes), "output_report" (bytes)
        """
        analysed_archives_dict = {}
        # Call analyse_archive on each file in input_directory
        for input_file in utils.list_file_paths(input_directory):
            relative_path = os.path.relpath(input_file, input_directory)
            # Construct paths for output file and output report
            output_file = None if output_directory is None else os.path.join(os.path.abspath(output_directory), relative_path)
            output_report = None if output_report_directory is None else os.path.join(os.path.abspath(output_report_directory), relative_path + ".xml")

            result = self.analyse_archive(
                input_file=input_file,
                output_file=output_file,
                output_report=output_report,
                content_management_policy=content_management_policy,
                raise_unsupported=raise_unsupported,
            )

            analysed_archives_dict[relative_path] = result

        return analysed_archives_dict

    def protect_archive(self, input_file: Union[str, bytes, bytearray, io.BytesIO], output_file: Optional[str] = None, output_report: Optional[str] = None, content_management_policy: Union[None, str, bytes, bytearray, io.BytesIO, glasswall.content_management.policies.ArchiveManager] = None, raise_unsupported: bool = True):
        """ Extracts the input_file archive and processes each file within the archive using the Glasswall engine. Repackages all files regenerated by the Glasswall engine into a new archive, optionally writing the new archive and report to the paths specified by output_file and output_report.

        Args:
            input_file (Union[str, bytes, bytearray, io.BytesIO]): The archive file path or bytes.
            output_file (Optional[str], optional): Default None. If str, write the archive to the output_file path.
            output_report (Optional[str], optional): Default None. If str, write the analysis report to the output_report path.
            content_management_policy (Union[None, str, bytes, bytearray, io.BytesIO, glasswall.content_management.policies.ArchiveManager], optional): The content management policy to apply.
            raise_unsupported (bool, optional): Default True. Raise exceptions when Glasswall encounters an error. Fail silently if False.

        Returns:
            gw_return_object (glasswall.GwReturnObj): An instance of class glasswall.GwReturnObj containing attributes including: "status" (int), "output_file" (bytes), "output_report" (bytes)
        """
        # Validate arg types
        if not isinstance(input_file, (str, bytes, bytearray, io.BytesIO)):
            raise TypeError(input_file)
        if not isinstance(output_file, (type(None), str)):
            raise TypeError(output_file)
        if not isinstance(output_report, (type(None), str)):
            raise TypeError(output_report)
        if not isinstance(content_management_policy, (type(None), str, bytes, bytearray, io.BytesIO, glasswall.content_management.policies.policy.Policy)):
            raise TypeError(content_management_policy)

        # Convert string path arguments to absolute paths
        if isinstance(input_file, str):
            input_file = os.path.abspath(input_file)
        if isinstance(output_file, str):
            output_file = os.path.abspath(output_file)
        if isinstance(output_report, str):
            output_report = os.path.abspath(output_report)

        # Convert inputs to bytes
        if isinstance(input_file, str):
            if not os.path.isfile(input_file):
                raise FileNotFoundError(input_file)
            with open(input_file, "rb") as f:
                input_file_bytes = f.read()
        elif isinstance(input_file, (bytes, bytearray, io.BytesIO)):
            input_file_bytes = utils.as_bytes(input_file)

        if isinstance(content_management_policy, str) and os.path.isfile(content_management_policy):
            with open(content_management_policy, "rb") as f:
                content_management_policy = f.read()
        elif isinstance(content_management_policy, type(None)):
            # Load default
            content_management_policy = glasswall.content_management.policies.ArchiveManager(default="sanitise", default_archive_manager="process")
        content_management_policy = utils.validate_xml(content_management_policy)

        # API function declaration
        self.library.GwFileProtectAndReportArchive.argtypes = [
            ct.c_void_p,  # void *inputBuffer
            ct.c_size_t,  # size_t inputBufferLength
            ct.POINTER(ct.c_void_p),  # void **outputFileBuffer
            ct.POINTER(ct.c_size_t),  # size_t *outputFileBufferLength
            ct.POINTER(ct.c_void_p),  # void **outputReportBuffer
            ct.POINTER(ct.c_size_t),  # size_t *outputReportBufferLength
            ct.c_char_p  # const char *xmlConfigString
        ]
        # Variable initialisation
        gw_return_object = glasswall.GwReturnObj()
        gw_return_object.input_buffer = ct.create_string_buffer(input_file_bytes)
        gw_return_object.input_buffer_length = ct.c_size_t(len(input_file_bytes))
        gw_return_object.output_buffer = ct.c_void_p()
        gw_return_object.output_buffer_length = ct.c_size_t()
        gw_return_object.output_report_buffer = ct.c_void_p()
        gw_return_object.output_report_buffer_length = ct.c_size_t()
        gw_return_object.content_management_policy = ct.c_char_p(content_management_policy.encode())

        with utils.CwdHandler(new_cwd=self.library_path):
            # API call
            gw_return_object.status = self.library.GwFileProtectAndReportArchive(
                ct.byref(gw_return_object.input_buffer),
                gw_return_object.input_buffer_length,
                ct.byref(gw_return_object.output_buffer),
                ct.byref(gw_return_object.output_buffer_length),
                ct.byref(gw_return_object.output_report_buffer),
                ct.byref(gw_return_object.output_report_buffer_length),
                gw_return_object.content_management_policy
            )

        if gw_return_object.output_buffer and gw_return_object.output_buffer_length:
            gw_return_object.output_file = utils.buffer_to_bytes(
                gw_return_object.output_buffer,
                gw_return_object.output_buffer_length
            )
        if gw_return_object.output_report_buffer and gw_return_object.output_report_buffer_length:
            gw_return_object.output_report = utils.buffer_to_bytes(
                gw_return_object.output_report_buffer,
                gw_return_object.output_report_buffer_length
            )

        # Write output file
        if hasattr(gw_return_object, "output_file"):
            if isinstance(output_file, str):
                os.makedirs(os.path.dirname(output_file), exist_ok=True)
                with open(output_file, "wb") as f:
                    f.write(gw_return_object.output_file)

        # Write output report
        if hasattr(gw_return_object, "output_report"):
            if isinstance(output_report, str):
                os.makedirs(os.path.dirname(output_report), exist_ok=True)
                with open(output_report, "wb") as f:
                    f.write(gw_return_object.output_report)

        input_file_repr = f"{type(input_file)} length {len(input_file)}" if isinstance(input_file, (bytes, bytearray,)) else input_file.__sizeof__() if isinstance(input_file, io.BytesIO) else input_file
        if gw_return_object.status not in successes.success_codes:
            log.error(f"\n\tinput_file: {input_file_repr}\n\toutput_file: {output_file}\n\tstatus: {gw_return_object.status}")
            if raise_unsupported:
                raise errors.error_codes.get(gw_return_object.status, errors.UnknownErrorCode)(gw_return_object.status)
        else:
            log.debug(f"\n\tinput_file: {input_file_repr}\n\toutput_file: {output_file}\n\tstatus: {gw_return_object.status}")

        self.release()

        return gw_return_object

    def protect_directory(self, input_directory: str, output_directory: Optional[str] = None, output_report_directory: Optional[str] = None, content_management_policy: Union[None, str, bytes, bytearray, io.BytesIO, glasswall.content_management.policies.ArchiveManager] = None, raise_unsupported: bool = True):
        """ Calls protect_archive on each file in input_directory using the given content management configuration. The resulting archives are written to output_directory maintaining the same directory structure as input_directory.

        Args:
            input_directory (str): The input directory containing archives to protect.
            output_directory (Optional[str], optional): Default None. If str, the output directory where the archives will be written.
            output_report_directory (Optional[str], optional): Default None. If str, the output directory where xml reports for each archive will be written.
            content_management_policy (Union[None, str, bytes, bytearray, io.BytesIO, glasswall.content_management.policies.ArchiveManager], optional): The content management policy to apply.
            raise_unsupported (bool, optional): Default True. Raise exceptions when Glasswall encounters an error. Fail silently if False.

        Returns:
            protected_archives_dict (dict): A dictionary of file paths relative to input_directory, and glasswall.GwReturnObj with attributes: "status" (int), "output_file" (bytes), "output_report" (bytes)
        """
        protected_archives_dict = {}
        # Call protect_archive on each file in input_directory to output_directory
        for input_file in utils.list_file_paths(input_directory):
            relative_path = os.path.relpath(input_file, input_directory)
            # Construct paths for output file and output report
            output_file = None if output_directory is None else os.path.join(os.path.abspath(output_directory), relative_path)
            output_report = None if output_report_directory is None else os.path.join(os.path.abspath(output_report_directory), relative_path + ".xml")

            result = self.protect_archive(
                input_file=input_file,
                output_file=output_file,
                output_report=output_report,
                content_management_policy=content_management_policy,
                raise_unsupported=raise_unsupported,
            )

            protected_archives_dict[relative_path] = result

        return protected_archives_dict

    def file_to_file_unpack(self, input_file: str, output_directory: str, raise_unsupported: bool = True):
        # Validate arg types
        if not isinstance(input_file, str):
            raise TypeError(input_file)
        elif not os.path.isfile(input_file):
            raise FileNotFoundError(input_file)
        if not isinstance(output_directory, str):
            raise TypeError(output_directory)

        # API function declaration
        self.library.GwFileToFileUnpack.argtypes = [
            ct.c_char_p,
            ct.c_char_p,
        ]

        # Variable initialisation
        gw_return_object = glasswall.GwReturnObj()
        gw_return_object.ct_input_file = ct.c_char_p(input_file.encode())  # const char* inputFilePath
        gw_return_object.ct_output_directory = ct.c_char_p(output_directory.encode())  # const char* outputDirPath

        with utils.CwdHandler(new_cwd=self.library_path):
            # API call
            gw_return_object.status = self.library.GwFileToFileUnpack(
                gw_return_object.ct_input_file,
                gw_return_object.ct_output_directory,
            )

        if gw_return_object.status not in successes.success_codes:
            log.error(f"\n\tinput_file: {input_file}\n\tstatus: {gw_return_object.status}")
            if raise_unsupported:
                raise errors.error_codes.get(gw_return_object.status, errors.UnknownErrorCode)(gw_return_object.status)
        else:
            log.debug(f"\n\tinput_file: {input_file}\n\tstatus: {gw_return_object.status}")

        self.release()

        return gw_return_object

    def file_to_file_pack(self, input_directory: str, output_directory: str, file_type: Optional[str] = None, add_extension: Optional[bool] = True, raise_unsupported: Optional[bool] = True):
        # Validate arg types
        if not isinstance(input_directory, str):
            raise TypeError(input_directory)
        elif not os.path.isdir(input_directory):
            raise NotADirectoryError(input_directory)
        if not isinstance(output_directory, str):
            raise TypeError(output_directory)
        if not file_type:
            file_type = utils.get_file_type(input_directory)

        # Ensure output_directory exists
        os.makedirs(output_directory, exist_ok=True)

        # API function declaration
        self.library.GwFileToFilePack.argtypes = [
            ct.c_char_p,
            ct.c_char_p,
            ct.c_char_p,
            ct.c_int,
        ]

        # Variable initialisation
        gw_return_object = glasswall.GwReturnObj()
        gw_return_object.ct_input_directory = ct.c_char_p(input_directory.encode())  # const char* inputDirPath
        gw_return_object.ct_output_directory = ct.c_char_p(output_directory.encode())  # const char* outputDirPath
        gw_return_object.ct_file_type = ct.c_char_p(file_type.encode())  # const char *fileType
        gw_return_object.ct_add_extension = ct.c_int(int(add_extension))  # int addExtension

        with utils.CwdHandler(new_cwd=self.library_path):
            # API call
            gw_return_object.status = self.library.GwFileToFilePack(
                gw_return_object.ct_input_directory,
                gw_return_object.ct_output_directory,
                gw_return_object.ct_file_type,
                gw_return_object.ct_add_extension,
            )

        if gw_return_object.status not in successes.success_codes:
            log.error(f"\n\tinput_directory: {input_directory}\n\tstatus: {gw_return_object.status}")
            if raise_unsupported:
                raise errors.error_codes.get(gw_return_object.status, errors.UnknownErrorCode)(gw_return_object.status)
        else:
            log.debug(f"\n\tinput_directory: {input_directory}\n\tstatus: {gw_return_object.status}")

        self.release()

        return gw_return_object

    def unpack(self, input_file: str, output_directory: str, recursive: bool = True, include_file_type: bool = False, raise_unsupported: bool = True, delete_origin: bool = False):
        """ Unpack an archive, maintaining directory structure. Supported archive formats are: "7z", "bz2", "gz", "rar", "tar", "xz", "zip".

        Args:
            input_file (str): The archive file path
            output_directory (str): The output directory where the archive will be unpacked to a new directory.
            recursive (bool, optional): Default True. Recursively unpack all nested archives.
            include_file_type (bool, optional): Default False. Include the archive format in the directory name. Useful when there are multiple same-named archives of different formats.
            raise_unsupported (bool, optional): Default True. Raise exceptions when Glasswall encounters an error. Fail silently if False.
            delete_origin (bool, optional): Default False. Delete input_file after unpacking to output_directory.
        """
        # Convert to absolute paths
        input_file = os.path.abspath(input_file)
        output_directory = os.path.abspath(output_directory)

        if include_file_type:
            archive_name = os.path.basename(input_file)
        else:
            archive_name = os.path.splitext(os.path.basename(input_file))[0]
        archive_output_directory = os.path.join(output_directory, archive_name)

        # Unpack
        log.debug(f"Unpacking\n\tsrc: {input_file}\n\tdst: {archive_output_directory}")
        result = self.file_to_file_unpack(input_file=input_file, output_directory=archive_output_directory, raise_unsupported=raise_unsupported)
        if result:
            status = result.status
        else:
            status = None

        if status not in successes.success_codes:
            log.error(f"\n\tinput_file: {input_file}\n\tstatus: {status}")
            if raise_unsupported:
                raise errors.error_codes.get(status, errors.UnknownErrorCode)(status)
        else:
            log.debug(f"\n\tinput_file: {input_file}\n\tstatus: {status}")

        if delete_origin:
            os.remove(input_file)

        if recursive:
            # Unpack sub archives
            for subarchive in self.list_archive_paths(archive_output_directory):
                self.unpack(
                    input_file=subarchive,
                    output_directory=archive_output_directory,
                    recursive=recursive,
                    raise_unsupported=raise_unsupported,
                    delete_origin=True
                )

        return status

    def unpack_directory(self, input_directory: str, output_directory: str, recursive: bool = True, include_file_type: Optional[bool] = False, raise_unsupported: bool = True, delete_origin: bool = False):
        """ Unpack a directory of archives, maintaining directory structure.

        Args:
            input_directory (str): The input directory containing archives to unpack.
            output_directory (str): The output directory where archives will be unpacked to a new directory.
            recursive (bool, optional): Default True. Recursively unpack all nested archives.
            include_file_type (bool, optional): Default False. Include the archive format in the directory name. Useful when there are multiple same-named archives of different formats.
            raise_unsupported (bool, optional): Default True. Raise exceptions when Glasswall encounters an error. Fail silently if False.
            delete_origin (bool, optional): Default False. Delete input_file after unpacking to output_directory.
        """
        # Convert to absolute paths
        input_directory = os.path.abspath(input_directory)
        output_directory = os.path.abspath(output_directory)

        for archive_input_file in self.list_archive_paths(input_directory):
            relative_path = os.path.relpath(archive_input_file, input_directory)
            archive_output_file = os.path.dirname(os.path.join(output_directory, relative_path))
            self.unpack(
                input_file=archive_input_file,
                output_directory=archive_output_file,
                recursive=recursive,
                include_file_type=include_file_type,
                raise_unsupported=raise_unsupported,
                delete_origin=delete_origin
            )

    def pack_directory(self, input_directory: str, output_directory: str, file_type: str, add_extension: Optional[bool] = True, raise_unsupported: Optional[bool] = True, delete_origin: Optional[bool] = False):
        """ Pack a directory. Supported archive formats are: "7z", "bz2", "gz", "rar", "tar", "xz", "zip".

        Args:
            input_directory (str): The input directory containing files to archive.
            output_directory (str): The output directory to store the created archive.
            file_type (str): The archive file type.
            add_extension (bool, optional): Default: True. Archive file type extension to result file.
            raise_unsupported (bool, optional): Default True. Raise exceptions when Glasswall encounters an error. Fail silently if False.
            delete_origin (bool, optional): Default False. Delete input_directory after packing to output_directory.
        """
        # Convert to absolute paths
        input_directory = os.path.abspath(input_directory)
        output_directory = os.path.abspath(output_directory)

        # Pack
        log.debug(f"Packing\n\tsrc: {input_directory}\n\tdst: {output_directory}")
        status = self.file_to_file_pack(input_directory=input_directory, output_directory=output_directory, file_type=file_type, add_extension=add_extension, raise_unsupported=raise_unsupported).status

        if status not in successes.success_codes:
            log.error(f"\n\tinput_directory: {input_directory}\n\tstatus: {status}")
            if raise_unsupported:
                raise errors.error_codes.get(status, errors.UnknownErrorCode)(status)
        else:
            log.debug(f"\n\tinput_directory: {input_directory}\n\tstatus: {status}")

        if delete_origin:
            utils.delete_directory(input_directory)

        return status

    def export_archive(self, input_file: Union[str, bytes, bytearray, io.BytesIO], output_file: Optional[str] = None, output_report: Optional[str] = None, content_management_policy: Union[None, str, bytes, bytearray, io.BytesIO, glasswall.content_management.policies.ArchiveManager] = None, raise_unsupported: bool = True):
        """ Exports an archive using the Glasswall engine.

        Args:
            input_file (Union[str, bytes, bytearray, io.BytesIO]): The archive file path or bytes.
            output_file (Optional[str], optional): Default None. If str, write the archive to the output_file path.
            output_report (Optional[str], optional): Default None. If str, write the analysis report to the output_report path.
            content_management_policy (Union[None, str, bytes, bytearray, io.BytesIO, glasswall.content_management.policies.ArchiveManager], optional): The content management policy to apply.
            raise_unsupported (bool, optional): Default True. Raise exceptions when Glasswall encounters an error. Fail silently if False.

        Returns:
            gw_return_object (glasswall.GwReturnObj): An instance of class glasswall.GwReturnObj containing attributes including: "status" (int), "output_file" (bytes), "output_report" (bytes)
        """
        # Validate arg types
        if not isinstance(input_file, (str, bytes, bytearray, io.BytesIO)):
            raise TypeError(input_file)
        if not isinstance(output_file, (type(None), str)):
            raise TypeError(output_file)
        if not isinstance(output_report, (type(None), str)):
            raise TypeError(output_report)
        if not isinstance(content_management_policy, (type(None), str, bytes, bytearray, io.BytesIO, glasswall.content_management.policies.policy.Policy)):
            raise TypeError(content_management_policy)

        # Convert string path arguments to absolute paths
        if isinstance(input_file, str):
            input_file = os.path.abspath(input_file)
        if isinstance(output_file, str):
            output_file = os.path.abspath(output_file)
        if isinstance(output_report, str):
            output_report = os.path.abspath(output_report)

        # Convert inputs to bytes
        if isinstance(input_file, str):
            if not os.path.isfile(input_file):
                raise FileNotFoundError(input_file)
            with open(input_file, "rb") as f:
                input_file_bytes = f.read()
        elif isinstance(input_file, (bytes, bytearray, io.BytesIO)):
            input_file_bytes = utils.as_bytes(input_file)

        if isinstance(content_management_policy, str) and os.path.isfile(content_management_policy):
            with open(content_management_policy, "rb") as f:
                content_management_policy = f.read()
        elif isinstance(content_management_policy, type(None)):
            # Load default
            content_management_policy = glasswall.content_management.policies.ArchiveManager(default="sanitise", default_archive_manager="process")
        content_management_policy = utils.validate_xml(content_management_policy)

        # API function declaration
        self.library.GwFileExportArchive.argtypes = [
            ct.c_void_p,  # void *inputBuffer
            ct.c_size_t,  # size_t inputBufferLength
            ct.POINTER(ct.c_void_p),  # void **outputFileBuffer
            ct.POINTER(ct.c_size_t),  # size_t *outputFileBufferLength
            ct.POINTER(ct.c_void_p),  # void **outputReportBuffer
            ct.POINTER(ct.c_size_t),  # size_t *outputReportBufferLength
            ct.c_char_p  # const char *xmlConfigString
        ]

        # Variable initialisation
        gw_return_object = glasswall.GwReturnObj()
        gw_return_object.input_buffer = ct.create_string_buffer(input_file_bytes)
        gw_return_object.input_buffer_length = ct.c_size_t(len(input_file_bytes))
        gw_return_object.output_buffer = ct.c_void_p()
        gw_return_object.output_buffer_length = ct.c_size_t()
        gw_return_object.output_report_buffer = ct.c_void_p()
        gw_return_object.output_report_buffer_length = ct.c_size_t()
        gw_return_object.content_management_policy = ct.c_char_p(content_management_policy.encode())

        with utils.CwdHandler(new_cwd=self.library_path):
            # API call
            gw_return_object.status = self.library.GwFileExportArchive(
                gw_return_object.input_buffer,
                gw_return_object.input_buffer_length,
                ct.byref(gw_return_object.output_buffer),
                ct.byref(gw_return_object.output_buffer_length),
                ct.byref(gw_return_object.output_report_buffer),
                ct.byref(gw_return_object.output_report_buffer_length),
                gw_return_object.content_management_policy
            )

        if gw_return_object.output_buffer and gw_return_object.output_buffer_length:
            gw_return_object.output_file = utils.buffer_to_bytes(
                gw_return_object.output_buffer,
                gw_return_object.output_buffer_length
            )
        if gw_return_object.output_report_buffer and gw_return_object.output_report_buffer_length:
            gw_return_object.output_report = utils.buffer_to_bytes(
                gw_return_object.output_report_buffer,
                gw_return_object.output_report_buffer_length
            )

        # Write output file
        if hasattr(gw_return_object, "output_file"):
            if isinstance(output_file, str):
                os.makedirs(os.path.dirname(output_file), exist_ok=True)
                with open(output_file, "wb") as f:
                    f.write(gw_return_object.output_file)

        # Write output report
        if hasattr(gw_return_object, "output_report"):
            if isinstance(output_report, str):
                os.makedirs(os.path.dirname(output_report), exist_ok=True)
                with open(output_report, "wb") as f:
                    f.write(gw_return_object.output_report)

        input_file_repr = f"{type(input_file)} length {len(input_file)}" if isinstance(input_file, (bytes, bytearray,)) else input_file.__sizeof__() if isinstance(input_file, io.BytesIO) else input_file
        if gw_return_object.status not in successes.success_codes:
            log.error(f"\n\tinput_file: {input_file_repr}\n\toutput_file: {output_file}\n\tstatus: {gw_return_object.status}")
            if raise_unsupported:
                raise errors.error_codes.get(gw_return_object.status, errors.UnknownErrorCode)(gw_return_object.status)
        else:
            log.debug(f"\n\tinput_file: {input_file_repr}\n\toutput_file: {output_file}\n\tstatus: {gw_return_object.status}")

        self.release()

        return gw_return_object

    def export_directory(self, input_directory: str, output_directory: Optional[str], output_report_directory: Optional[str] = None, content_management_policy: Union[None, str, bytes, bytearray, io.BytesIO, glasswall.content_management.policies.ArchiveManager] = None, raise_unsupported: bool = True):
        """ Calls export_archive on each file in input_directory. The exported archives are written to output_directory maintaining the same directory structure as input_directory.

        Args:
            input_directory (str): The input directory containing archives to export.
            output_directory (Optional[str], optional): Default None. If str, the output directory where the archives will be written.
            output_report_directory (Optional[str], optional): Default None. If str, the output directory where xml reports for each archive will be written.
            content_management_policy (Union[None, str, bytes, bytearray, io.BytesIO, glasswall.content_management.policies.ArchiveManager], optional): The content management policy to apply.
            raise_unsupported (bool, optional): Default True. Raise exceptions when Glasswall encounters an error. Fail silently if False.

        Returns:
            exported_archives_dict (dict): A dictionary of file paths relative to input_directory, and glasswall.GwReturnObj with attributes: "status" (int), "output_file" (bytes), "output_report" (bytes)
        """
        exported_archives_dict = {}
        # Call export_archive on each file in input_directory to output_directory
        for input_file in utils.list_file_paths(input_directory):
            relative_path = os.path.relpath(input_file, input_directory)
            # Construct paths for output file and output report
            output_file = None if output_directory is None else os.path.join(os.path.abspath(output_directory), relative_path)
            output_report = None if output_report_directory is None else os.path.join(os.path.abspath(output_report_directory), relative_path + ".xml")

            result = self.export_archive(
                input_file=input_file,
                output_file=output_file,
                output_report=output_report,
                content_management_policy=content_management_policy,
                raise_unsupported=raise_unsupported,
            )

            exported_archives_dict[relative_path] = result

        return exported_archives_dict

    def import_archive(self, input_file: Union[str, bytes, bytearray, io.BytesIO], output_file: Optional[str] = None, output_report: Optional[str] = None, content_management_policy: Union[None, str, bytes, bytearray, io.BytesIO, glasswall.content_management.policies.ArchiveManager] = None, include_analysis_report: Optional[bool] = False, raise_unsupported: Optional[bool] = True):
        """ Imports an archive using the Glasswall engine.

        Args:
            input_file (Union[str, bytes, bytearray, io.BytesIO]): The archive file path or bytes.
            output_file (Optional[str], optional): Default None. If str, write the archive to the output_file path.
            output_report (Optional[str], optional): Default None. If str, write the analysis report to the output_report path.
            content_management_policy (Union[None, str, bytes, bytearray, io.BytesIO, glasswall.content_management.policies.ArchiveManager], optional): The content management policy to apply.
            include_analysis_report (Optional[bool], optional): Default False. If True, write the analysis report into the imported archive.
            raise_unsupported (bool, optional): Default True. Raise exceptions when Glasswall encounters an error. Fail silently if False.

        Returns:
            gw_return_object (glasswall.GwReturnObj): An instance of class glasswall.GwReturnObj containing attributes including: "status" (int), "output_file" (bytes), "output_report" (bytes)
        """
        # Validate arg types
        if not isinstance(input_file, (str, bytes, bytearray, io.BytesIO)):
            raise TypeError(input_file)
        if not isinstance(output_file, (type(None), str)):
            raise TypeError(output_file)
        if not isinstance(output_report, (type(None), str)):
            raise TypeError(output_report)
        if not isinstance(content_management_policy, (type(None), str, bytes, bytearray, io.BytesIO, glasswall.content_management.policies.policy.Policy)):
            raise TypeError(content_management_policy)

        # Convert string path arguments to absolute paths
        if isinstance(input_file, str):
            input_file = os.path.abspath(input_file)
        # Convert string path arguments to absolute paths
        if isinstance(output_file, str):
            output_file = os.path.abspath(output_file)
        if isinstance(output_report, str):
            output_report = os.path.abspath(output_report)

        # Convert inputs to bytes
        if isinstance(input_file, str):
            if not os.path.isfile(input_file):
                raise FileNotFoundError(input_file)
            with open(input_file, "rb") as f:
                input_file_bytes = f.read()
        elif isinstance(input_file, (bytes, bytearray, io.BytesIO)):
            input_file_bytes = utils.as_bytes(input_file)

        if isinstance(content_management_policy, str) and os.path.isfile(content_management_policy):
            with open(content_management_policy, "rb") as f:
                content_management_policy = f.read()
        elif isinstance(content_management_policy, type(None)):
            # Load default
            content_management_policy = glasswall.content_management.policies.ArchiveManager(default="sanitise", default_archive_manager="process")
        content_management_policy = utils.validate_xml(content_management_policy)

        # API function declaration
        self.library.GwFileImportArchive.argtypes = [
            ct.c_void_p,  # void *inputBuffer
            ct.c_size_t,  # size_t inputBufferLength
            ct.POINTER(ct.c_void_p),  # void **outputFileBuffer
            ct.POINTER(ct.c_size_t),  # size_t *outputFileBufferLength
            ct.POINTER(ct.c_void_p),  # void **outputReportBuffer
            ct.POINTER(ct.c_size_t),  # size_t *outputReportBufferLength
            ct.c_char_p,  # const char *xmlConfigString
            ct.c_int  # int includeAnalysisReports
        ]

        # Variable initialisation
        gw_return_object = glasswall.GwReturnObj()
        gw_return_object.input_buffer = ct.create_string_buffer(input_file_bytes)
        gw_return_object.input_buffer_length = ct.c_size_t(len(input_file_bytes))
        gw_return_object.output_buffer = ct.c_void_p()
        gw_return_object.output_buffer_length = ct.c_size_t()
        gw_return_object.output_report_buffer = ct.c_void_p()
        gw_return_object.output_report_buffer_length = ct.c_size_t()
        gw_return_object.content_management_policy = ct.c_char_p(content_management_policy.encode())
        gw_return_object.include_analysis_report = ct.c_int(int(include_analysis_report))

        with utils.CwdHandler(new_cwd=self.library_path):
            # API call
            gw_return_object.status = self.library.GwFileImportArchive(
                gw_return_object.input_buffer,
                gw_return_object.input_buffer_length,
                ct.byref(gw_return_object.output_buffer),
                ct.byref(gw_return_object.output_buffer_length),
                ct.byref(gw_return_object.output_report_buffer),
                ct.byref(gw_return_object.output_report_buffer_length),
                gw_return_object.content_management_policy,
                gw_return_object.include_analysis_report
            )

        if gw_return_object.output_buffer and gw_return_object.output_buffer_length:
            gw_return_object.output_file = utils.buffer_to_bytes(
                gw_return_object.output_buffer,
                gw_return_object.output_buffer_length
            )
        if gw_return_object.output_report_buffer and gw_return_object.output_report_buffer_length:
            gw_return_object.output_report = utils.buffer_to_bytes(
                gw_return_object.output_report_buffer,
                gw_return_object.output_report_buffer_length
            )

        # Write output file
        if hasattr(gw_return_object, "output_file"):
            if isinstance(output_file, str):
                os.makedirs(os.path.dirname(output_file), exist_ok=True)
                with open(output_file, "wb") as f:
                    f.write(gw_return_object.output_file)

        # Write output report
        if hasattr(gw_return_object, "output_report"):
            if isinstance(output_report, str):
                os.makedirs(os.path.dirname(output_report), exist_ok=True)
                with open(output_report, "wb") as f:
                    f.write(gw_return_object.output_report)

        input_file_repr = f"{type(input_file)} length {len(input_file)}" if isinstance(input_file, (bytes, bytearray,)) else input_file.__sizeof__() if isinstance(input_file, io.BytesIO) else input_file
        if gw_return_object.status not in successes.success_codes:
            log.error(f"\n\tinput_file: {input_file_repr}\n\toutput_file: {output_file}\n\tstatus: {gw_return_object.status}")
            if raise_unsupported:
                raise errors.error_codes.get(gw_return_object.status, errors.UnknownErrorCode)(gw_return_object.status)
        else:
            log.debug(f"\n\tinput_file: {input_file_repr}\n\toutput_file: {output_file}\n\tstatus: {gw_return_object.status}")

        self.release()

        return gw_return_object

    def import_directory(self, input_directory: str, output_directory: Optional[str], output_report_directory: Optional[str] = None, content_management_policy: Union[None, str, bytes, bytearray, io.BytesIO, glasswall.content_management.policies.ArchiveManager] = None, include_analysis_report: Optional[bool] = False, raise_unsupported: bool = True):
        """ Calls import_archive on each file in input_directory. The imported archives are written to output_directory maintaining the same directory structure as input_directory.

        Args:
            input_directory (str): The input directory containing archives to import.
            output_directory (Optional[str], optional): Default None. If str, the output directory where the archives will be written.
            output_report_directory (Optional[str], optional): Default None. If str, the output directory where xml reports for each archive will be written.
            content_management_policy (Union[None, str, bytes, bytearray, io.BytesIO, glasswall.content_management.policies.ArchiveManager], optional): The content management policy to apply.
            include_analysis_report (Optional[bool], optional): Default False. If True, write the analysis report into the imported archive.
            raise_unsupported (bool, optional): Default True. Raise exceptions when Glasswall encounters an error. Fail silently if False.

        Returns:
            imported_archives_dict (dict): A dictionary of file paths relative to input_directory, and glasswall.GwReturnObj with attributes: "status" (int), "output_file" (bytes), "output_report" (bytes)
        """
        imported_archives_dict = {}
        # Call import_archive on each file in input_directory to output_directory
        for input_file in utils.list_file_paths(input_directory):
            relative_path = os.path.relpath(input_file, input_directory)
            # Construct paths for output file and output report
            output_file = None if output_directory is None else os.path.join(os.path.abspath(output_directory), relative_path)
            output_report = None if output_report_directory is None else os.path.join(os.path.abspath(output_report_directory), relative_path + ".xml")

            result = self.import_archive(
                input_file=input_file,
                output_file=output_file,
                output_report=output_report,
                content_management_policy=content_management_policy,
                include_analysis_report=include_analysis_report,
                raise_unsupported=raise_unsupported,
            )

            imported_archives_dict[relative_path] = result

        return imported_archives_dict
