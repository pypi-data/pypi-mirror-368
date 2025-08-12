

import ctypes as ct
import functools
import io
import os
from contextlib import contextmanager
from typing import Optional, Union

import glasswall
from glasswall import determine_file_type as dft
from glasswall import utils
from glasswall.config.logging import format_object, log
from glasswall.libraries.editor import errors, successes
from glasswall.libraries.library import Library


class Editor(Library):
    """ A high level Python wrapper for Glasswall Editor / Core2. """

    def __init__(self, library_path: str, licence: Union[str, bytes, bytearray, io.BytesIO] = None):
        """ Initialise the Editor instance.

        Args:
            library_path (str): The file or directory path to the Editor library.
            licence (str, bytes, bytearray, or io.BytesIO, optional): The licence file content or path. This can be:
                - A string representing the file path to the licence.
                - A `bytes` or `bytearray` object containing the licence data.
                - An `io.BytesIO` object for in-memory licence data.
                If not specified, it is assumed that the licence file is located in the same directory as the `library_path`.
        """
        super().__init__(library_path)
        self.library = self.load_library(os.path.abspath(library_path))
        self.licence = licence

        # Validate killswitch has not activated
        self.validate_licence()

        log.info(f"Loaded Glasswall {self.__class__.__name__} version {self.version()} from {self.library_path}")

    def validate_licence(self):
        """ Validates the licence of the library by checking the licence details.

        Raises:
            LicenceExpired: If the licence has expired or could not be validated.
        """
        licence_details = self.licence_details()

        bad_details = [
            "Unable to Read Licence Key File",
            "Licence File Missing Required Contents",
            "Licence Expired",
        ]

        if any(bad_detail.lower() in licence_details.lower() for bad_detail in bad_details):
            # bad_details found in licence_details
            log.error(f"{self.__class__.__name__} licence validation failed. Licence details:\n{licence_details}")
            raise errors.LicenceExpired(licence_details)
        else:
            log.debug(f"{self.__class__.__name__} licence validated successfully. Licence details:\n{licence_details}")

    def version(self):
        """ Returns the Glasswall library version.

        Returns:
            version (str): The Glasswall library version.
        """
        # API function declaration
        self.library.GW2LibVersion.restype = ct.c_char_p

        # API call
        version = self.library.GW2LibVersion()

        # Convert to Python string
        version = ct.string_at(version).decode()

        return version

    def open_session(self):
        """ Open a new Glasswall session.

        Returns:
            session (int): An incrementing integer repsenting the current session.
        """
        # API call
        session = self.library.GW2OpenSession()

        log.debug(f"\n\tsession: {session}")

        if self.licence:
            # Must register licence on each GW2OpenSession if the licence is not in the same directory as the library
            self.register_licence(session, self.licence)

        return session

    def close_session(self, session: int) -> int:
        """ Close the Glasswall session. All resources allocated by the session will be destroyed.

        Args:
            session (int): The session to close.

        Returns:
            status (int): The status code of the function call.
        """
        if not isinstance(session, int):
            raise TypeError(session)

        # API function declaration
        self.library.GW2CloseSession.argtypes = [ct.c_size_t]

        # Variable initialisation
        ct_session = ct.c_size_t(session)

        # API call
        status = self.library.GW2CloseSession(ct_session)

        if status not in successes.success_codes:
            log.error(f"\n\tsession: {session}\n\tstatus: {status}")
        else:
            log.debug(f"\n\tsession: {session}\n\tstatus: {status}")

        return status

    @contextmanager
    def new_session(self):
        """ Context manager. Opens a new session on entry and closes the session on exit. """
        try:
            session = self.open_session()
            yield session
        finally:
            self.close_session(session)

    def run_session(self, session):
        """ Runs the Glasswall session and begins processing of a file.

        Args:
            session (int): The session to run.

        Returns:
            status (int): The status code of the function call.
        """
        # API function declaration
        self.library.GW2RunSession.argtypes = [ct.c_size_t]

        # Variable initialisation
        ct_session = ct.c_size_t(session)

        # API call
        status = self.library.GW2RunSession(ct_session)

        if status not in successes.success_codes:
            log.error(f"\n\tsession: {session}\n\tstatus: {status}\n\tGW2FileErrorMsg: {self.file_error_message(session)}")
        else:
            log.debug(f"\n\tsession: {session}\n\tstatus: {status}\n\tGW2FileErrorMsg: {self.file_error_message(session)}")

        return status

    def determine_file_type(self, input_file: Union[str, bytes, bytearray, io.BytesIO], as_string: bool = False, raise_unsupported: bool = True) -> Union[int, str]:
        """ Determine the file type of a given input file, either as an integer identifier or a string.

        Args:
            input_file (Union[str, bytes, bytearray, io.BytesIO]): The input file to analyse. It can be provided as a file path (str), bytes, bytearray, or a BytesIO object.
            as_string (bool, optional): Return file type as string, eg: "bmp" instead of: 29. Defaults to False.
            raise_unsupported (bool, optional): Default True. Raise exceptions when Glasswall encounters an error. Fail silently if False.

        Returns:
            file_type (Union[int, str]): The file type.
        """
        if isinstance(input_file, str):
            if not os.path.isfile(input_file):
                raise FileNotFoundError(input_file)

            # convert to ct.c_char_p of bytes
            ct_input_file = ct.c_char_p(input_file.encode("utf-8"))

            # API call
            file_type = self.library.GW2DetermineFileTypeFromFile(ct_input_file)

        elif isinstance(input_file, (bytes, bytearray, io.BytesIO)):
            # convert to bytes
            bytes_input_file = utils.as_bytes(input_file)

            # ctypes conversion
            ct_buffer = ct.c_char_p(bytes_input_file)
            ct_buffer_length = ct.c_size_t(len(bytes_input_file))

            # API call
            file_type = self.library.GW2DetermineFileTypeFromMemory(
                ct_buffer,
                ct_buffer_length
            )

        else:
            raise TypeError(input_file)

        file_type_as_string = dft.file_type_int_to_str(file_type)
        input_file_repr = f"{type(input_file)} length {len(input_file)}" if isinstance(input_file, (bytes, bytearray,)) else input_file.__sizeof__() if isinstance(input_file, io.BytesIO) else input_file

        if not dft.is_success(file_type):
            log.warning(f"\n\tfile_type: {file_type}\n\tfile_type_as_string: {file_type_as_string}\n\tinput_file: {input_file_repr}")
            if raise_unsupported:
                raise dft.int_class_map.get(file_type, dft.errors.UnknownErrorCode)(file_type)
        else:
            log.debug(f"\n\tfile_type: {file_type}\n\tfile_type_as_string: {file_type_as_string}\n\tinput_file: {input_file_repr}")

        if as_string:
            return file_type_as_string

        return file_type

    def _GW2GetPolicySettings(self, session: int, policy_format: int = 0):
        """ Get current policy settings for the given session.

        Args:
            session (int): The session integer.
            policy_format (int): The format of the content management policy. 0=XML.

        Returns:
            gw_return_object (glasswall.GwReturnObj): A GwReturnObj instance with the attributes 'session', 'buffer', 'buffer_length', 'policy_format', 'status', 'policy'.
        """
        # API function declaration
        self.library.GW2GetPolicySettings.argtypes = [
            ct.c_size_t,  # Session_Handle session
            ct.POINTER(ct.c_void_p),  # char ** policiesBuffer
            ct.POINTER(ct.c_size_t),  # size_t * policiesLength
            ct.c_int,  # Policy_Format format
        ]

        # Variable initialisation
        gw_return_object = glasswall.GwReturnObj()
        gw_return_object.session = ct.c_size_t(session)
        gw_return_object.buffer = ct.c_void_p()
        gw_return_object.buffer_length = ct.c_size_t()
        gw_return_object.policy_format = ct.c_int(policy_format)

        # API Call
        gw_return_object.status = self.library.GW2GetPolicySettings(
            gw_return_object.session,
            ct.byref(gw_return_object.buffer),
            ct.byref(gw_return_object.buffer_length),
            gw_return_object.policy_format
        )

        # Editor wrote to a buffer, convert it to bytes
        policy_bytes = utils.buffer_to_bytes(
            gw_return_object.buffer,
            gw_return_object.buffer_length
        )

        gw_return_object.policy = policy_bytes.decode()

        return gw_return_object

    def get_content_management_policy(self, session: int):
        """ Returns the content management configuration for a given session.

        Args:
            session (int): The session integer.

        Returns:
            xml_string (str): The XML string of the current content management configuration.
        """
        # NOTE GW2GetPolicySettings is current not implemented in editor

        # set xml_string as loaded default config
        xml_string = glasswall.content_management.policies.Editor(default="sanitise").text,

        # log.debug(f"xml_string:\n{xml_string}")

        return xml_string

        # # API function declaration
        # self.library.GW2GetPolicySettings.argtypes = [
        #     ct.c_size_t,
        #     ct.c_void_p,
        # ]

        # # Variable initialisation
        # ct_session = ct.c_size_t(session)
        # ct_buffer = ct.c_void_p()
        # ct_buffer_length = ct.c_size_t()
        # # ct_file_format = ct.c_int(file_format)

        # # API Call
        # status = self.library.GW2GetPolicySettings(
        #     ct_session,
        #     ct.byref(ct_buffer),
        #     ct.byref(ct_buffer_length)
        # )

        # print("GW2GetPolicySettings status:", status)

        # file_bytes = utils.buffer_to_bytes(
        #     ct_buffer,
        #     ct_buffer_length,
        # )

        # return file_bytes

    def _GW2RegisterPoliciesFile(self, session: int, input_file: str, policy_format: int = 0):
        """ Registers the policies to be used by Glasswall when processing files.

        Args:
            session (int): The session integer.
            input_file (str): The content management policy input file path.
            policy_format (int): The format of the content management policy. 0=XML.

        Returns:
            gw_return_object (glasswall.GwReturnObj): A GwReturnObj instance with the attributes 'session', 'input_file', 'policy_format', 'status'.
        """
        # API function declaration
        self.library.GW2RegisterPoliciesFile.argtypes = [
            ct.c_size_t,  # Session_Handle session
            ct.c_char_p,  # const char *filename
            ct.c_int,  # Policy_Format format
        ]

        # Variable initialisation
        gw_return_object = glasswall.GwReturnObj()
        gw_return_object.session = ct.c_size_t(session)
        gw_return_object.input_file = ct.c_char_p(input_file.encode("utf-8"))
        gw_return_object.policy_format = ct.c_int(policy_format)

        gw_return_object.status = self.library.GW2RegisterPoliciesFile(
            gw_return_object.session,
            gw_return_object.input_file,
            gw_return_object.policy_format
        )

        return gw_return_object

    def _GW2RegisterPoliciesMemory(self, session: int, input_file: bytes, policy_format: int = 0):
        """ Registers the policies in memory to be used by Glasswall when processing files.

        Args:
            session (int): The session integer.
            input_file (str): The content management policy input file bytes.
            policy_format (int): The format of the content management policy. 0=XML.

        Returns:
            gw_return_object (glasswall.GwReturnObj): A GwReturnObj instance with the attributes 'session', 'buffer', 'buffer_length', 'policy_format', 'status'.
        """
        # API function declaration
        self.library.GW2RegisterPoliciesMemory.argtype = [
            ct.c_size_t,  # Session_Handle session
            ct.c_char_p,  # const char *policies
            ct.c_size_t,  # size_t policiesLength
            ct.c_int  # Policy_Format format
        ]

        # Variable initialisation
        gw_return_object = glasswall.GwReturnObj()
        gw_return_object.session = ct.c_size_t(session)
        gw_return_object.buffer = ct.c_char_p(input_file)
        gw_return_object.buffer_length = ct.c_size_t(len(input_file))
        gw_return_object.policy_format = ct.c_int(policy_format)

        # API Call
        gw_return_object.status = self.library.GW2RegisterPoliciesMemory(
            gw_return_object.session,
            gw_return_object.buffer,
            gw_return_object.buffer_length,
            gw_return_object.policy_format
        )

        return gw_return_object

    def set_content_management_policy(self, session: int, input_file: Union[None, str, bytes, bytearray, io.BytesIO, "glasswall.content_management.policies.policy.Policy"] = None, policy_format=0):
        """ Sets the content management policy configuration. If input_file is None then default settings (sanitise) are applied.

        Args:
            session (int): The session integer.
            input_file (Union[None, str, bytes, bytearray, io.BytesIO, glasswall.content_management.policies.policy.Policy], optional): Default None (sanitise). The content management policy to apply.
            policy_format (int): The format of the content management policy. 0=XML.

        Returns:
            - result (glasswall.GwReturnObj): Depending on the input 'input_file':
                - If input_file is a str file path:
                    - gw_return_object (glasswall.GwReturnObj): A GwReturnObj instance with the attributes 'session', 'input_file', 'policy_format', 'status'.

                - If input_file is a file in memory:
                    - gw_return_object (glasswall.GwReturnObj): A GwReturnObj instance with the attributes 'session', 'buffer', 'buffer_length', 'policy_format', 'status'.
        """
        # Validate type
        if not isinstance(session, int):
            raise TypeError(session)
        if not isinstance(input_file, (type(None), str, bytes, bytearray, io.BytesIO, glasswall.content_management.policies.policy.Policy)):
            raise TypeError(input_file)
        if not isinstance(policy_format, int):
            raise TypeError(policy_format)

        # Set input_file to default if input_file is None
        if input_file is None:
            input_file = glasswall.content_management.policies.Editor(default="sanitise")

        # Validate xml content is parsable
        utils.validate_xml(input_file)

        # From file
        if isinstance(input_file, str) and os.path.isfile(input_file):
            input_file = os.path.abspath(input_file)

            result = self._GW2RegisterPoliciesFile(session, input_file)

        # From memory
        elif isinstance(input_file, (str, bytes, bytearray, io.BytesIO, glasswall.content_management.policies.policy.Policy)):
            # Convert bytearray, io.BytesIO to bytes
            if isinstance(input_file, (bytearray, io.BytesIO)):
                input_file = utils.as_bytes(input_file)
            # Convert string xml or Policy to bytes
            if isinstance(input_file, (str, glasswall.content_management.policies.policy.Policy)):
                input_file = input_file.encode("utf-8")

            result = self._GW2RegisterPoliciesMemory(session, input_file)

        if result.status not in successes.success_codes:
            log.error(format_object(result))
            raise errors.error_codes.get(result.status, errors.UnknownErrorCode)(result.status)
        else:
            log.debug(format_object(result))

        return result

    def _GW2RegisterInputFile(self, session: int, input_file: str):
        """ Register an input file for the given session.

        Args:
            session (int): The session integer.
            input_file (str): The input file path.

        Returns:
            gw_return_object (glasswall.GwReturnObj): A GwReturnObj instance with the attributes 'session', 'input_file', 'status'.
        """
        # API function declaration
        self.library.GW2RegisterInputFile.argtypes = [
            ct.c_size_t,  # Session_Handle session
            ct.c_char_p  # const char * inputFilePath
        ]

        # Variable initialisation
        gw_return_object = glasswall.GwReturnObj()
        gw_return_object.session = ct.c_size_t(session)
        gw_return_object.input_file = ct.c_char_p(input_file.encode("utf-8"))
        gw_return_object.input_file_path = input_file

        # API call
        gw_return_object.status = self.library.GW2RegisterInputFile(
            gw_return_object.session,
            gw_return_object.input_file
        )

        return gw_return_object

    def _GW2RegisterInputMemory(self, session: int, input_file: bytes):
        """ Register an input file in memory for the given session.

        Args:
            session (int): The session integer.
            input_file (bytes): The input file in memory.

        Returns:
            gw_return_object (glasswall.GwReturnObj): A GwReturnObj instance with the attributes 'session', 'buffer', 'buffer_length', 'status'.
        """
        # API function declaration
        self.library.GW2RegisterInputMemory.argtypes = [
            ct.c_size_t,  # Session_Handle session
            ct.c_char_p,  # const char * inputFileBuffer
            ct.c_size_t,  # size_t inputLength
        ]

        # Variable initialisation
        gw_return_object = glasswall.GwReturnObj()
        gw_return_object.session = ct.c_size_t(session)
        gw_return_object.buffer = ct.c_char_p(input_file)
        gw_return_object.buffer_length = ct.c_size_t(len(input_file))

        # API call
        gw_return_object.status = self.library.GW2RegisterInputMemory(
            gw_return_object.session,
            gw_return_object.buffer,
            gw_return_object.buffer_length
        )

        return gw_return_object

    def register_input(self, session: int, input_file: Union[str, bytes, bytearray, io.BytesIO]):
        """ Register an input file or bytes for the given session.

        Args:
            session (int): The session integer.
            input_file (Union[str, bytes, bytearray, io.BytesIO]): The input file path or bytes.

        Returns:
            - result (glasswall.GwReturnObj): Depending on the input 'input_file':
                - If input_file is a str file path:
                    - gw_return_object (glasswall.GwReturnObj): A GwReturnObj instance with the attributes 'session', 'input_file', 'status'.

                - If input_file is a file in memory:
                    - gw_return_object (glasswall.GwReturnObj): A GwReturnObj instance with the attributes 'session', 'buffer', 'buffer_length', 'status'.
        """
        if not isinstance(input_file, (str, bytes, bytearray, io.BytesIO,)):
            raise TypeError(input_file)

        if isinstance(input_file, str):
            if not os.path.isfile(input_file):
                raise FileNotFoundError(input_file)

            input_file = os.path.abspath(input_file)

            result = self._GW2RegisterInputFile(session, input_file)

        elif isinstance(input_file, (bytes, bytearray, io.BytesIO,)):
            # Convert bytearray and io.BytesIO to bytes
            input_file = utils.as_bytes(input_file)

            result = self._GW2RegisterInputMemory(session, input_file)

        if result.status not in successes.success_codes:
            log.error(format_object(result))
            raise errors.error_codes.get(result.status, errors.UnknownErrorCode)(result.status)
        else:
            log.debug(format_object(result))

        return result

    def _GW2RegisterOutFile(self, session: int, output_file: str):
        """ Register an output file for the given session.

        Args:
            session (int): The session integer.
            output_file (str): The output file path.

        Returns:
            gw_return_object (glasswall.GwReturnObj): A GwReturnObj instance with the attributes 'session', 'output_file', 'status'.
        """
        # API function declaration
        self.library.GW2RegisterOutFile.argtypes = [
            ct.c_size_t,  # Session_Handle session
            ct.c_char_p  # const char * outputFilePath
        ]

        # Variable initialisation
        gw_return_object = glasswall.GwReturnObj()
        gw_return_object.session = ct.c_size_t(session)
        gw_return_object.output_file = ct.c_char_p(output_file.encode("utf-8"))

        # API call
        gw_return_object.status = self.library.GW2RegisterOutFile(
            gw_return_object.session,
            gw_return_object.output_file
        )

        return gw_return_object

    def _GW2RegisterOutputMemory(self, session: int):
        """ Register an output file in memory for the given session.

        Args:
            session (int): The session integer.

        Returns:
            gw_return_object (glasswall.GwReturnObj): A GwReturnObj instance with the attributes 'session', 'buffer', 'buffer_length', 'status'.
        """
        # API function declaration
        self.library.GW2RegisterOutputMemory.argtypes = [
            ct.c_size_t,  # Session_Handle session
            ct.POINTER(ct.c_void_p),  # char ** outputBuffer
            ct.POINTER(ct.c_size_t)  # size_t * outputLength
        ]

        # Variable initialisation
        gw_return_object = glasswall.GwReturnObj()
        gw_return_object.session = ct.c_size_t(session)
        gw_return_object.buffer = ct.c_void_p()
        gw_return_object.buffer_length = ct.c_size_t()

        # API call
        gw_return_object.status = self.library.GW2RegisterOutputMemory(
            gw_return_object.session,
            ct.byref(gw_return_object.buffer),
            ct.byref(gw_return_object.buffer_length)
        )

        return gw_return_object

    def register_output(self, session, output_file: Optional[str] = None):
        """ Register an output file for the given session. If output_file is None the file will be returned as 'buffer' and 'buffer_length' attributes.

        Args:
            session (int): The session integer.
            output_file (Optional[str]): If specified, during run session the file will be written to output_file, otherwise the file will be written to the glasswall.GwReturnObj 'buffer' and 'buffer_length' attributes.

        Returns:
            gw_return_object (glasswall.GwReturnObj): A GwReturnObj instance with the attribute 'status' indicating the result of the function call. If output_file is None (memory mode), 'buffer', and 'buffer_length' are included containing the file content and file size.
        """
        if not isinstance(output_file, (type(None), str)):
            raise TypeError(output_file)

        if isinstance(output_file, str):
            output_file = os.path.abspath(output_file)

            result = self._GW2RegisterOutFile(session, output_file)

        elif isinstance(output_file, type(None)):
            result = self._GW2RegisterOutputMemory(session)

        if result.status not in successes.success_codes:
            log.error(format_object(result))
            raise errors.error_codes.get(result.status, errors.UnknownErrorCode)(result.status)
        else:
            log.debug(format_object(result))

        return result

    def _GW2RegisterAnalysisFile(self, session: int, output_file: str, analysis_format: int = 0):
        """ Register an analysis output file for the given session.

        Args:
            session (int): The session integer.
            output_file (str): The analysis output file path.
            analysis_format (int): The format of the analysis report. 0=XML, 1=XMLExtended

        Returns:
            gw_return_object (glasswall.GwReturnObj): A GwReturnObj instance with the attributes 'session', 'output_file', 'analysis_format', 'status'.
        """
        # API function declaration
        self.library.GW2RegisterAnalysisFile.argtypes = [
            ct.c_size_t,  # Session_Handle session
            ct.c_char_p,  # const char * analysisFilePathName
            ct.c_int,  # Analysis_Format format
        ]

        # Variable initialisation
        gw_return_object = glasswall.GwReturnObj()
        gw_return_object.session = ct.c_size_t(session)
        gw_return_object.output_file = ct.c_char_p(output_file.encode("utf-8"))
        gw_return_object.analysis_format = ct.c_int()

        # API call
        gw_return_object.status = self.library.GW2RegisterAnalysisFile(
            gw_return_object.session,
            gw_return_object.output_file,
            gw_return_object.analysis_format
        )

        return gw_return_object

    def _GW2RegisterAnalysisMemory(self, session: int, analysis_format: int = 0):
        """ Register an analysis output file in memory for the given session.

        Args:
            session (int): The session integer.
            analysis_format (int): The format of the analysis report. 0=XML, 1=XMLExtended

        Returns:
            gw_return_object (glasswall.GwReturnObj): A GwReturnObj instance with the attributes 'session', 'buffer', 'buffer_length', 'analysis_format', 'status'.
        """
        # API function declaration
        self.library.GW2RegisterAnalysisMemory.argtypes = [
            ct.c_size_t,  # Session_Handle session
            ct.POINTER(ct.c_void_p),  # char ** analysisFileBuffer
            ct.POINTER(ct.c_size_t),  # size_t * analysisoutputLength
            ct.c_int  # Analysis_Format format
        ]

        # Variable initialisation
        gw_return_object = glasswall.GwReturnObj()
        gw_return_object.session = ct.c_size_t(session)
        gw_return_object.buffer = ct.c_void_p()
        gw_return_object.buffer_length = ct.c_size_t()
        gw_return_object.analysis_format = ct.c_int()

        # API call
        gw_return_object.status = self.library.GW2RegisterAnalysisMemory(
            gw_return_object.session,
            ct.byref(gw_return_object.buffer),
            ct.byref(gw_return_object.buffer_length),
            gw_return_object.analysis_format
        )

        return gw_return_object

    def register_analysis(self, session: int, output_file: Optional[str] = None):
        """ Registers an analysis file for the given session. The analysis file will be created during the session's run_session call.

        Args:
            session (int): The session integer.
            output_file (Optional[str]): Default None. The file path where the analysis will be written. None returns the analysis as bytes.

        Returns:
            gw_return_object (glasswall.GwReturnObj): A GwReturnObj instance with the attributes 'status', 'session', 'analysis_format'. If output_file is None (memory mode), 'buffer', and 'buffer_length' are included containing the file content and file size. If output_file is not None (file mode) 'output_file' is included.
        """
        if not isinstance(output_file, (type(None), str)):
            raise TypeError(output_file)

        if isinstance(output_file, str):
            output_file = os.path.abspath(output_file)

            result = self._GW2RegisterAnalysisFile(session, output_file)

        elif isinstance(output_file, type(None)):
            result = self._GW2RegisterAnalysisMemory(session)

        if result.status not in successes.success_codes:
            log.error(format_object(result))
            raise errors.error_codes.get(result.status, errors.UnknownErrorCode)(result.status)
        else:
            log.debug(format_object(result))

        return result

    def protect_file(
        self,
        input_file: Union[str, bytes, bytearray, io.BytesIO],
        output_file: Optional[str] = None,
        content_management_policy: Union[None, str, bytes, bytearray, io.BytesIO, "glasswall.content_management.policies.policy.Policy"] = None,
        raise_unsupported: bool = True,
    ):
        """ Protects a file using the current content management configuration, returning the file bytes. The protected file is written to output_file if it is provided.

        Args:
            input_file (Union[str, bytes, bytearray, io.BytesIO]): The input file path or bytes.
            output_file (Optional[str]): The output file path where the protected file will be written.
            content_management_policy (Union[None, str, bytes, bytearray, io.BytesIO, glasswall.content_management.policies.policy.Policy], optional): The content management policy to apply to the session.
            raise_unsupported (bool, optional): Default True. Raise exceptions when Glasswall encounters an error. Fail silently if False.

        Returns:
            file_bytes (bytes): The protected file bytes.
        """
        # Validate arg types
        if not isinstance(input_file, (str, bytes, bytearray, io.BytesIO)):
            raise TypeError(input_file)
        if not isinstance(output_file, (type(None), str)):
            raise TypeError(output_file)
        if not isinstance(content_management_policy, (type(None), str, bytes, bytearray, io.BytesIO, glasswall.content_management.policies.policy.Policy)):
            raise TypeError(content_management_policy)
        if not isinstance(raise_unsupported, bool):
            raise TypeError(raise_unsupported)

        # Convert string path arguments to absolute paths
        if isinstance(input_file, str):
            if not os.path.isfile(input_file):
                raise FileNotFoundError(input_file)
            input_file = os.path.abspath(input_file)
        if isinstance(output_file, str):
            output_file = os.path.abspath(output_file)
            # make directories that do not exist
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
        if isinstance(content_management_policy, str) and os.path.isfile(content_management_policy):
            content_management_policy = os.path.abspath(content_management_policy)

        # Convert memory inputs to bytes
        if isinstance(input_file, (bytes, bytearray, io.BytesIO)):
            input_file = utils.as_bytes(input_file)

        with utils.CwdHandler(self.library_path):
            with self.new_session() as session:
                content_management_policy = self.set_content_management_policy(session, content_management_policy)
                register_input = self.register_input(session, input_file)
                register_output = self.register_output(session, output_file=output_file)
                status = self.run_session(session)

                input_file_repr = f"{type(input_file)} length {len(input_file)}" if isinstance(input_file, (bytes, bytearray,)) else input_file.__sizeof__() if isinstance(input_file, io.BytesIO) else input_file
                if status not in successes.success_codes:
                    log.error(f"\n\tinput_file: {input_file_repr}\n\toutput_file: {output_file}\n\tsession: {session}\n\tstatus: {status}")
                    if raise_unsupported:
                        raise errors.error_codes.get(status, errors.UnknownErrorCode)(status)
                    else:
                        file_bytes = None
                else:
                    log.debug(f"\n\tinput_file: {input_file_repr}\n\toutput_file: {output_file}\n\tsession: {session}\n\tstatus: {status}")
                    # Get file bytes
                    if isinstance(output_file, str):
                        # File to file and memory to file, Editor wrote to a file, read it to get the file bytes
                        if not os.path.isfile(output_file):
                            log.error(f"Editor returned success code: {status} but no output file was found: {output_file}")
                            file_bytes = None
                        else:
                            with open(output_file, "rb") as f:
                                file_bytes = f.read()
                    else:
                        # File to memory and memory to memory, Editor wrote to a buffer, convert it to bytes
                        file_bytes = utils.buffer_to_bytes(
                            register_output.buffer,
                            register_output.buffer_length
                        )

                # Ensure memory allocated is not garbage collected
                content_management_policy, register_input, register_output

                return file_bytes

    def protect_directory(
        self,
        input_directory: str,
        output_directory: Optional[str] = None,
        content_management_policy: Union[None, str, bytes, bytearray, io.BytesIO, "glasswall.content_management.policies.policy.Policy"] = None,
        raise_unsupported: bool = True,
    ):
        """ Recursively processes all files in a directory in protect mode using the given content management policy.
        The protected files are written to output_directory maintaining the same directory structure as input_directory.

        Args:
            input_directory (str): The input directory containing files to protect.
            output_directory (Optional[str]): The output directory where the protected file will be written, or None to not write files.
            content_management_policy (Union[None, str, bytes, bytearray, io.BytesIO, glasswall.content_management.policies.policy.Policy], optional): Default None (sanitise). The content management policy to apply.
            raise_unsupported (bool, optional): Default True. Raise exceptions when Glasswall encounters an error. Fail silently if False.

        Returns:
            protected_files_dict (dict): A dictionary of file paths relative to input_directory, and file bytes.
        """
        protected_files_dict = {}
        # Call protect_file on each file in input_directory to output_directory
        for input_file in utils.list_file_paths(input_directory):
            relative_path = os.path.relpath(input_file, input_directory)
            output_file = None if output_directory is None else os.path.join(os.path.abspath(output_directory), relative_path)

            protected_bytes = self.protect_file(
                input_file=input_file,
                output_file=output_file,
                raise_unsupported=raise_unsupported,
                content_management_policy=content_management_policy,
            )

            protected_files_dict[relative_path] = protected_bytes

        return protected_files_dict

    def analyse_file(
        self,
        input_file: Union[str, bytes, bytearray, io.BytesIO],
        output_file: Optional[str] = None,
        content_management_policy: Union[None, str, bytes, bytearray, io.BytesIO, "glasswall.content_management.policies.policy.Policy"] = None,
        raise_unsupported: bool = True,
    ):
        """ Analyses a file, returning the analysis bytes. The analysis is written to output_file if it is provided.

        Args:
            input_file (Union[str, bytes, bytearray, io.BytesIO]): The input file path or bytes.
            output_file (Optional[str]): The output file path where the analysis file will be written.
            content_management_policy (Union[None, str, bytes, bytearray, io.BytesIO, glasswall.content_management.policies.policy.Policy], optional): The content management policy to apply to the session.
            raise_unsupported (bool, optional): Default True. Raise exceptions when Glasswall encounters an error. Fail silently if False.

        Returns:
            file_bytes (bytes): The analysis file bytes.
        """
        # Validate arg types
        if not isinstance(input_file, (str, bytes, bytearray, io.BytesIO)):
            raise TypeError(input_file)
        if not isinstance(output_file, (type(None), str)):
            raise TypeError(output_file)
        if not isinstance(content_management_policy, (type(None), str, bytes, bytearray, io.BytesIO, glasswall.content_management.policies.policy.Policy)):
            raise TypeError(content_management_policy)
        if not isinstance(raise_unsupported, bool):
            raise TypeError(raise_unsupported)

        # Convert string path arguments to absolute paths
        if isinstance(input_file, str):
            if not os.path.isfile(input_file):
                raise FileNotFoundError(input_file)
            input_file = os.path.abspath(input_file)
        if isinstance(output_file, str):
            output_file = os.path.abspath(output_file)
            # make directories that do not exist
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
        if isinstance(content_management_policy, str) and os.path.isfile(content_management_policy):
            content_management_policy = os.path.abspath(content_management_policy)

        # Convert memory inputs to bytes
        if isinstance(input_file, (bytes, bytearray, io.BytesIO)):
            input_file = utils.as_bytes(input_file)

        with utils.CwdHandler(self.library_path):
            with self.new_session() as session:
                content_management_policy = self.set_content_management_policy(session, content_management_policy)
                register_input = self.register_input(session, input_file)
                register_analysis = self.register_analysis(session, output_file)
                status = self.run_session(session)

                file_bytes = None
                if isinstance(output_file, str):
                    # File to file and memory to file, Editor wrote to a file, read it to get the file bytes
                    if os.path.isfile(output_file):
                        with open(output_file, "rb") as f:
                            file_bytes = f.read()
                else:
                    # File to memory and memory to memory, Editor wrote to a buffer, convert it to bytes
                    if register_analysis.buffer and register_analysis.buffer_length:
                        file_bytes = utils.buffer_to_bytes(
                            register_analysis.buffer,
                            register_analysis.buffer_length
                        )

                input_file_repr = f"{type(input_file)} length {len(input_file)}" if isinstance(input_file, (bytes, bytearray,)) else input_file.__sizeof__() if isinstance(input_file, io.BytesIO) else input_file
                if status not in successes.success_codes:
                    log.error(f"\n\tinput_file: {input_file_repr}\n\toutput_file: {output_file}\n\tsession: {session}\n\tstatus: {status}")
                    if raise_unsupported:
                        raise errors.error_codes.get(status, errors.UnknownErrorCode)(status)
                else:
                    log.debug(f"\n\tinput_file: {input_file_repr}\n\toutput_file: {output_file}\n\tsession: {session}\n\tstatus: {status}")

                # Ensure memory allocated is not garbage collected
                content_management_policy, register_input, register_analysis

                return file_bytes

    def analyse_directory(
        self,
        input_directory: str,
        output_directory: Optional[str] = None,
        content_management_policy: Union[None, str, bytes, bytearray, io.BytesIO, "glasswall.content_management.policies.policy.Policy"] = None,
        raise_unsupported: bool = True,
    ):
        """ Analyses all files in a directory and its subdirectories. The analysis files are written to output_directory maintaining the same directory structure as input_directory.

        Args:
            input_directory (str): The input directory containing files to analyse.
            output_directory (Optional[str]): The output directory where the analysis files will be written, or None to not write files.
            content_management_policy (Union[None, str, bytes, bytearray, io.BytesIO, glasswall.content_management.policies.policy.Policy], optional): Default None (sanitise). The content management policy to apply.
            raise_unsupported (bool, optional): Default True. Raise exceptions when Glasswall encounters an error. Fail silently if False.

        Returns:
            analysis_files_dict (dict): A dictionary of file paths relative to input_directory, and file bytes.
        """
        analysis_files_dict = {}
        # Call analyse_file on each file in input_directory to output_directory
        for input_file in utils.list_file_paths(input_directory):
            relative_path = os.path.relpath(input_file, input_directory) + ".xml"
            output_file = None if output_directory is None else os.path.join(os.path.abspath(output_directory), relative_path)

            analysis_bytes = self.analyse_file(
                input_file=input_file,
                output_file=output_file,
                raise_unsupported=raise_unsupported,
                content_management_policy=content_management_policy,
            )

            analysis_files_dict[relative_path] = analysis_bytes

        return analysis_files_dict

    def protect_and_analyse_file(
        self,
        input_file: Union[str, bytes, bytearray, io.BytesIO],
        output_file: Optional[str] = None,
        output_analysis_report: Optional[str] = None,
        content_management_policy: Union[None, str, bytes, bytearray, io.BytesIO, "glasswall.content_management.policies.policy.Policy"] = None,
        raise_unsupported: bool = True,
    ):
        """ Protects and analyses a file in a single session, returning both protected file bytes and analysis report bytes.

        Args:
            input_file (Union[str, bytes, bytearray, io.BytesIO]): The input file path or bytes.
            output_file (Optional[str]): The output file path where the protected file will be written.
            output_analysis_report (Optional[str]): The output file path where the XML analysis report will be written.
            content_management_policy (Union[None, str, bytes, bytearray, io.BytesIO, glasswall.content_management.policies.policy.Policy], optional): The content management policy to apply to the session.
            raise_unsupported (bool, optional): Default True. Raise exceptions when Glasswall encounters an error. Fail silently if False.

        Returns:
            Tuple[Optional[bytes], Optional[bytes]]: A tuple of (protected_file_bytes, analysis_report_bytes).
        """
        # Validate arg types
        if not isinstance(input_file, (str, bytes, bytearray, io.BytesIO)):
            raise TypeError(f"input_file expected to be of type: str, bytes, bytearray, io.BytesIO. Got: {type(input_file).__name__}")
        if not isinstance(output_file, (type(None), str)):
            raise TypeError(f"output_file expected to be of type: None, str. Got: {type(output_file).__name__}")
        if not isinstance(output_analysis_report, (type(None), str)):
            raise TypeError(f"output_analysis_report expected to be of type: None, str. Got: {type(output_analysis_report).__name__}")
        if not isinstance(content_management_policy, (type(None), str, bytes, bytearray, io.BytesIO, glasswall.content_management.policies.policy.Policy)):
            raise TypeError(f"content_management_policy expected to be of type: None, str, bytes, bytearray, io.BytesIO, Policy. Got: {type(content_management_policy).__name__}")
        if not isinstance(raise_unsupported, bool):
            raise TypeError(f"raise_unsupported expected to be of type: bool. Got: {type(raise_unsupported).__name__}")

        # Convert string path arguments to absolute paths
        if isinstance(input_file, str):
            if not os.path.isfile(input_file):
                raise FileNotFoundError(input_file)
            input_file = os.path.abspath(input_file)
        if isinstance(output_file, str):
            output_file = os.path.abspath(output_file)
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
        if isinstance(output_analysis_report, str):
            output_analysis_report = os.path.abspath(output_analysis_report)
            os.makedirs(os.path.dirname(output_analysis_report), exist_ok=True)
        if isinstance(content_management_policy, str) and os.path.isfile(content_management_policy):
            content_management_policy = os.path.abspath(content_management_policy)

        # Convert memory inputs to bytes
        if isinstance(input_file, (bytes, bytearray, io.BytesIO)):
            input_file = utils.as_bytes(input_file)

        with utils.CwdHandler(self.library_path):
            with self.new_session() as session:
                content_management_policy = self.set_content_management_policy(session, content_management_policy)
                register_input = self.register_input(session, input_file)
                register_output = self.register_output(session, output_file)
                register_analysis = self.register_analysis(session, output_analysis_report)

                status = self.run_session(session)

                protected_file_bytes = None
                analysis_report_bytes = None

                input_file_repr = f"{type(input_file)} length {len(input_file)}" if isinstance(input_file, (bytes, bytearray,)) else input_file.__sizeof__() if isinstance(input_file, io.BytesIO) else input_file
                if status not in successes.success_codes:
                    log.error(f"\n\tinput_file: {input_file_repr}\n\toutput_file: {output_file}\n\toutput_analysis_report: {output_analysis_report}\n\tsession: {session}\n\tstatus: {status}")
                    if raise_unsupported:
                        raise errors.error_codes.get(status, errors.UnknownErrorCode)(status)

                # Get analysis report file bytes, even on processing failure
                if isinstance(output_analysis_report, str):
                    # File to file and memory to file, Editor wrote to a file, read it to get the file bytes
                    if not os.path.isfile(output_analysis_report):
                        log.error(f"Editor returned success code: {status} but no output file was found: {output_analysis_report}")
                    else:
                        with open(output_analysis_report, "rb") as f:
                            analysis_report_bytes = f.read()
                else:
                    # File to memory and memory to memory, Editor wrote to a buffer, convert it to bytes
                    if register_analysis.buffer and register_analysis.buffer_length:
                        analysis_report_bytes = utils.buffer_to_bytes(
                            register_analysis.buffer,
                            register_analysis.buffer_length
                        )

                # On success, get protected file bytes
                if status in successes.success_codes:
                    log.debug(f"\n\tinput_file: {input_file_repr}\n\toutput_file: {output_file}\n\toutput_analysis_report: {output_analysis_report}\n\tsession: {session}\n\tstatus: {status}")
                    # Get file bytes
                    if isinstance(output_file, str):
                        # File to file and memory to file, Editor wrote to a file, read it to get the file bytes
                        if not os.path.isfile(output_file):
                            log.error(f"Editor returned success code: {status} but no output file was found: {output_file}")
                        else:
                            with open(output_file, "rb") as f:
                                protected_file_bytes = f.read()
                    else:
                        # File to memory and memory to memory, Editor wrote to a buffer, convert it to bytes
                        protected_file_bytes = utils.buffer_to_bytes(
                            register_output.buffer,
                            register_output.buffer_length
                        )

                # Ensure memory allocated is not garbage collected
                content_management_policy, register_input, register_output, register_analysis

                return protected_file_bytes, analysis_report_bytes

    def protect_and_analyse_directory(
        self,
        input_directory: str,
        output_directory: Optional[str] = None,
        analysis_directory: Optional[str] = None,
        content_management_policy: Union[None, str, bytes, bytearray, io.BytesIO, "glasswall.content_management.policies.policy.Policy"] = None,
        raise_unsupported: bool = True,
    ):
        """ Recursively processes all files in a directory using protect and analyse mode with the given content management policy.
        Outputs are written to output_directory and analysis_directory maintaining the same structure as input_directory.

        Args:
            input_directory (str): The input directory containing files to process.
            output_directory (Optional[str]): The output directory for protected files.
            analysis_directory (Optional[str]): The output directory for XML analysis reports.
            content_management_policy (Union[None, str, bytes, bytearray, io.BytesIO, glasswall.content_management.policies.policy.Policy], optional): The content management policy to apply.
            raise_unsupported (bool, optional): Default True. Raise exceptions when Glasswall encounters an error. Fail silently if False.

        Returns:
            result_dict (dict): A dictionary mapping relative file paths to tuples of (protected_file_bytes, analysis_report_bytes).
        """
        result_dict = {}
        for input_file in utils.list_file_paths(input_directory):
            relative_path = os.path.relpath(input_file, input_directory)
            output_file = None if output_directory is None else os.path.join(os.path.abspath(output_directory), relative_path)
            output_analysis_report = None if analysis_directory is None else os.path.join(os.path.abspath(analysis_directory), relative_path + ".xml")

            protected_file_bytes, analysis_report_bytes = self.protect_and_analyse_file(
                input_file=input_file,
                output_file=output_file,
                output_analysis_report=output_analysis_report,
                content_management_policy=content_management_policy,
                raise_unsupported=raise_unsupported,
            )

            result_dict[relative_path] = (protected_file_bytes, analysis_report_bytes)

        return result_dict

    def _GW2RegisterExportFile(self, session: int, output_file: str):
        """ Register an export output file for the given session.

        Args:
            session (int): The session integer.
            output_file (str): The export output file path.

        Returns:
            gw_return_object (glasswall.GwReturnObj): A GwReturnObj instance with the attributes 'session', 'output_file', 'status'.
        """
        # API function declaration
        self.library.GW2RegisterExportFile.argtypes = [
            ct.c_size_t,  # Session_Handle session
            ct.c_char_p  # const char * exportFilePath
        ]

        # Variable initialisation
        gw_return_object = glasswall.GwReturnObj()
        gw_return_object.session = ct.c_size_t(session)
        gw_return_object.output_file = ct.c_char_p(output_file.encode("utf-8"))

        # API Call
        gw_return_object.status = self.library.GW2RegisterExportFile(
            gw_return_object.session,
            gw_return_object.output_file
        )

        return gw_return_object

    def _GW2RegisterExportMemory(self, session: int):
        """ Register an export output file in memory for the given session.

        Args:
            session (int): The session integer.

        Returns:
            gw_return_object (glasswall.GwReturnObj): A GwReturnObj instance with the attributes 'session', 'buffer', 'buffer_length', 'status'.
        """
        # API function declaration
        self.library.GW2RegisterExportMemory.argtypes = [
            ct.c_size_t,  # Session_Handle session
            ct.POINTER(ct.c_void_p),  # char ** exportFileBuffer
            ct.POINTER(ct.c_size_t)  # size_t * exportLength
        ]

        # Variable initialisation
        gw_return_object = glasswall.GwReturnObj()
        gw_return_object.session = ct.c_size_t(session)
        gw_return_object.buffer = ct.c_void_p()
        gw_return_object.buffer_length = ct.c_size_t()

        # API call
        gw_return_object.status = self.library.GW2RegisterExportMemory(
            gw_return_object.session,
            ct.byref(gw_return_object.buffer),
            ct.byref(gw_return_object.buffer_length)
        )

        return gw_return_object

    def register_export(self, session: int, output_file: Optional[str] = None):
        """ Registers a file to be exported for the given session. The export file will be created during the session's run_session call.

        Args:
            session (int): The session integer.
            output_file (Optional[str]): Default None. The file path where the export will be written. None exports the file in memory.

        Returns:
            gw_return_object (glasswall.GwReturnObj): A GwReturnObj instance with the attribute 'status' indicating the result of the function call and 'session', the session integer. If output_file is None (memory mode), 'buffer', and 'buffer_length' are included containing the file content and file size.
        """
        if not isinstance(output_file, (type(None), str)):
            raise TypeError(output_file)

        if isinstance(output_file, str):
            output_file = os.path.abspath(output_file)

            result = self._GW2RegisterExportFile(session, output_file)

        elif isinstance(output_file, type(None)):
            result = self._GW2RegisterExportMemory(session)

        if result.status not in successes.success_codes:
            log.error(format_object(result))
            raise errors.error_codes.get(result.status, errors.UnknownErrorCode)(result.status)
        else:
            log.debug(format_object(result))

        return result

    def export_file(
        self,
        input_file: Union[str, bytes, bytearray, io.BytesIO],
        output_file: Optional[str] = None,
        content_management_policy: Union[None, str, bytes, bytearray, io.BytesIO, "glasswall.content_management.policies.policy.Policy"] = None,
        raise_unsupported: bool = True,
    ):
        """ Export a file, returning the .zip file bytes. The .zip file is written to output_file if it is provided.

        Args:
            input_file (Union[str, bytes, bytearray, io.BytesIO]): The input file path or bytes.
            output_file (Optional[str]): The output file path where the .zip file will be written.
            content_management_policy (Union[None, str, bytes, bytearray, io.BytesIO, glasswall.content_management.policies.policy.Policy], optional): The content management policy to apply to the session.
            raise_unsupported (bool, optional): Default True. Raise exceptions when Glasswall encounters an error. Fail silently if False.

        Returns:
            file_bytes (bytes): The exported .zip file.
        """
        # Validate arg types
        if not isinstance(input_file, (str, bytes, bytearray, io.BytesIO)):
            raise TypeError(input_file)
        if not isinstance(output_file, (type(None), str)):
            raise TypeError(output_file)
        if not isinstance(content_management_policy, (type(None), str, bytes, bytearray, io.BytesIO, glasswall.content_management.policies.policy.Policy)):
            raise TypeError(content_management_policy)
        if not isinstance(raise_unsupported, bool):
            raise TypeError(raise_unsupported)

        # Convert string path arguments to absolute paths
        if isinstance(input_file, str):
            if not os.path.isfile(input_file):
                raise FileNotFoundError(input_file)
            input_file = os.path.abspath(input_file)
        if isinstance(output_file, str):
            output_file = os.path.abspath(output_file)
            # make directories that do not exist
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
        if isinstance(content_management_policy, str) and os.path.isfile(content_management_policy):
            content_management_policy = os.path.abspath(content_management_policy)

        # Convert memory inputs to bytes
        if isinstance(input_file, (bytes, bytearray, io.BytesIO)):
            input_file = utils.as_bytes(input_file)

        with utils.CwdHandler(self.library_path):
            with self.new_session() as session:
                content_management_policy = self.set_content_management_policy(session, content_management_policy)
                register_input = self.register_input(session, input_file)
                register_export = self.register_export(session, output_file)
                status = self.run_session(session)

                input_file_repr = f"{type(input_file)} length {len(input_file)}" if isinstance(input_file, (bytes, bytearray,)) else input_file.__sizeof__() if isinstance(input_file, io.BytesIO) else input_file
                if status not in successes.success_codes:
                    log.error(f"\n\tinput_file: {input_file_repr}\n\toutput_file: {output_file}\n\tsession: {session}\n\tstatus: {status}")
                    if raise_unsupported:
                        raise errors.error_codes.get(status, errors.UnknownErrorCode)(status)
                    else:
                        file_bytes = None
                else:
                    log.debug(f"\n\tinput_file: {input_file_repr}\n\toutput_file: {output_file}\n\tsession: {session}\n\tstatus: {status}")
                    # Get file bytes
                    if isinstance(output_file, str):
                        # File to file and memory to file, Editor wrote to a file, read it to get the file bytes
                        if not os.path.isfile(output_file):
                            log.error(f"Editor returned success code: {status} but no output file was found: {output_file}")
                            file_bytes = None
                        else:
                            with open(output_file, "rb") as f:
                                file_bytes = f.read()
                    else:
                        # File to memory and memory to memory, Editor wrote to a buffer, convert it to bytes
                        file_bytes = utils.buffer_to_bytes(
                            register_export.buffer,
                            register_export.buffer_length
                        )

                # Ensure memory allocated is not garbage collected
                content_management_policy, register_input, register_export

                return file_bytes

    def export_directory(
        self,
        input_directory: str,
        output_directory: Optional[str] = None,
        content_management_policy: Union[None, str, bytes, bytearray, io.BytesIO, "glasswall.content_management.policies.policy.Policy"] = None,
        raise_unsupported: bool = True
    ):
        """ Exports all files in a directory and its subdirectories. The export files are written to output_directory maintaining the same directory structure as input_directory.

        Args:
            input_directory (str): The input directory containing files to export.
            output_directory (Optional[str]): The output directory where the export files will be written, or None to not write files.
            content_management_policy (Union[None, str, bytes, bytearray, io.BytesIO, glasswall.content_management.policies.policy.Policy], optional): Default None (sanitise). The content management policy to apply.
            raise_unsupported (bool, optional): Default True. Raise exceptions when Glasswall encounters an error. Fail silently if False.

        Returns:
            export_files_dict (dict): A dictionary of file paths relative to input_directory, and file bytes.
        """
        export_files_dict = {}
        # Call export_file on each file in input_directory to output_directory
        for input_file in utils.list_file_paths(input_directory):
            relative_path = os.path.relpath(input_file, input_directory) + ".zip"
            output_file = None if output_directory is None else os.path.join(os.path.abspath(output_directory), relative_path)

            export_bytes = self.export_file(
                input_file=input_file,
                output_file=output_file,
                raise_unsupported=raise_unsupported,
                content_management_policy=content_management_policy,
            )

            export_files_dict[relative_path] = export_bytes

        return export_files_dict

    def export_and_analyse_file(
        self,
        input_file: Union[str, bytes, bytearray, io.BytesIO],
        output_file: Optional[str] = None,
        output_analysis_report: Optional[str] = None,
        content_management_policy: Union[None, str, bytes, bytearray, io.BytesIO, "glasswall.content_management.policies.policy.Policy"] = None,
        raise_unsupported: bool = True,
    ):
        """ Exports and analyses a file in a single session, returning both exported .zip bytes and analysis report bytes.

        Args:
            input_file (Union[str, bytes, bytearray, io.BytesIO]): The input file path or bytes.
            output_file (Optional[str]): The output file path where the .zip export will be written.
            output_analysis_report (Optional[str]): The output file path where the XML analysis report will be written.
            content_management_policy (Union[None, str, bytes, bytearray, io.BytesIO, glasswall.content_management.policies.policy.Policy], optional): The content management policy to apply to the session.
            raise_unsupported (bool, optional): Default True. Raise exceptions when Glasswall encounters an error. Fail silently if False.

        Returns:
            Tuple[Optional[bytes], Optional[bytes]]: A tuple of (export_file_bytes, analysis_report_bytes).
        """
        # Validate arg types
        if not isinstance(input_file, (str, bytes, bytearray, io.BytesIO)):
            raise TypeError(f"input_file expected to be of type: str, bytes, bytearray, io.BytesIO. Got: {type(input_file).__name__}")
        if not isinstance(output_file, (type(None), str)):
            raise TypeError(f"output_file expected to be of type: None, str. Got: {type(output_file).__name__}")
        if not isinstance(output_analysis_report, (type(None), str)):
            raise TypeError(f"output_analysis_report expected to be of type: None, str. Got: {type(output_analysis_report).__name__}")
        if not isinstance(content_management_policy, (type(None), str, bytes, bytearray, io.BytesIO, glasswall.content_management.policies.policy.Policy)):
            raise TypeError(f"content_management_policy expected to be of type: None, str, bytes, bytearray, io.BytesIO, Policy. Got: {type(content_management_policy).__name__}")
        if not isinstance(raise_unsupported, bool):
            raise TypeError(f"raise_unsupported expected to be of type: bool. Got: {type(raise_unsupported).__name__}")

        # Convert string path arguments to absolute paths
        if isinstance(input_file, str):
            if not os.path.isfile(input_file):
                raise FileNotFoundError(input_file)
            input_file = os.path.abspath(input_file)
        if isinstance(output_file, str):
            output_file = os.path.abspath(output_file)
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
        if isinstance(output_analysis_report, str):
            output_analysis_report = os.path.abspath(output_analysis_report)
            os.makedirs(os.path.dirname(output_analysis_report), exist_ok=True)
        if isinstance(content_management_policy, str) and os.path.isfile(content_management_policy):
            content_management_policy = os.path.abspath(content_management_policy)

        # Convert memory inputs to bytes
        if isinstance(input_file, (bytes, bytearray, io.BytesIO)):
            input_file = utils.as_bytes(input_file)

        with utils.CwdHandler(self.library_path):
            with self.new_session() as session:
                content_management_policy = self.set_content_management_policy(session, content_management_policy)
                register_input = self.register_input(session, input_file)
                register_export = self.register_export(session, output_file)
                register_analysis = self.register_analysis(session, output_analysis_report)

                status = self.run_session(session)

                export_file_bytes = None
                analysis_report_bytes = None

                input_file_repr = f"{type(input_file)} length {len(input_file)}" if isinstance(input_file, (bytes, bytearray)) else input_file.__sizeof__() if isinstance(input_file, io.BytesIO) else input_file
                if status not in successes.success_codes:
                    log.error(f"\n\tinput_file: {input_file_repr}\n\toutput_file: {output_file}\n\toutput_analysis_report: {output_analysis_report}\n\tsession: {session}\n\tstatus: {status}")
                    if raise_unsupported:
                        raise errors.error_codes.get(status, errors.UnknownErrorCode)(status)

                # Get analysis report file bytes, even on processing failure
                if isinstance(output_analysis_report, str):
                    # File to file and memory to file, Editor wrote to a file, read it to get the file bytes
                    if not os.path.isfile(output_analysis_report):
                        log.error(f"Editor returned success code: {status} but no output file was found: {output_analysis_report}")
                    else:
                        with open(output_analysis_report, "rb") as f:
                            analysis_report_bytes = f.read()
                else:
                    # File to memory and memory to memory, Editor wrote to a buffer, convert it to bytes
                    if register_analysis.buffer and register_analysis.buffer_length:
                        analysis_report_bytes = utils.buffer_to_bytes(
                            register_analysis.buffer,
                            register_analysis.buffer_length
                        )

                # On success, get export file bytes
                if status in successes.success_codes:
                    log.debug(f"\n\tinput_file: {input_file_repr}\n\toutput_file: {output_file}\n\toutput_analysis_report: {output_analysis_report}\n\tsession: {session}\n\tstatus: {status}")
                    # Get export file bytes
                    if isinstance(output_file, str):
                        # File to file and memory to file, Editor wrote to a file, read it to get the file bytes
                        if not os.path.isfile(output_file):
                            log.error(f"Editor returned success code: {status} but no output file was found: {output_file}")
                        else:
                            with open(output_file, "rb") as f:
                                export_file_bytes = f.read()
                    else:
                        # File to memory and memory to memory, Editor wrote to a buffer, convert it to bytes
                        export_file_bytes = utils.buffer_to_bytes(
                            register_export.buffer,
                            register_export.buffer_length
                        )

                # Ensure memory allocated is not garbage collected
                content_management_policy, register_input, register_export, register_analysis

                return export_file_bytes, analysis_report_bytes

    def export_and_analyse_directory(
        self,
        input_directory: str,
        output_directory: Optional[str] = None,
        analysis_directory: Optional[str] = None,
        content_management_policy: Union[None, str, bytes, bytearray, io.BytesIO, "glasswall.content_management.policies.policy.Policy"] = None,
        raise_unsupported: bool = True,
    ):
        """ Recursively processes all files in a directory using export and analyse mode with the given content management policy.
        Outputs are written to output_directory and analysis_directory maintaining the same structure as input_directory.

        Args:
            input_directory (str): The input directory containing files to process.
            output_directory (Optional[str]): The output directory for exported .zip files.
            analysis_directory (Optional[str]): The output directory for XML analysis reports.
            content_management_policy (Union[None, str, bytes, bytearray, io.BytesIO, glasswall.content_management.policies.policy.Policy], optional): The content management policy to apply.
            raise_unsupported (bool, optional): Default True. Raise exceptions when Glasswall encounters an error. Fail silently if False.

        Returns:
            result_dict (dict): A dictionary mapping relative file paths to tuples of (export_file_bytes, analysis_report_bytes).
        """
        result_dict = {}

        for input_file in utils.list_file_paths(input_directory):
            relative_path = os.path.relpath(input_file, input_directory)
            output_file = None if output_directory is None else os.path.join(os.path.abspath(output_directory), relative_path + ".zip")
            output_analysis_report = None if analysis_directory is None else os.path.join(os.path.abspath(analysis_directory), relative_path + ".xml")

            export_file_bytes, analysis_report_bytes = self.export_and_analyse_file(
                input_file=input_file,
                output_file=output_file,
                output_analysis_report=output_analysis_report,
                content_management_policy=content_management_policy,
                raise_unsupported=raise_unsupported,
            )

            result_dict[relative_path] = (export_file_bytes, analysis_report_bytes)

        return result_dict

    def _GW2RegisterImportFile(self, session: int, input_file: str):
        """ Register an import input file for the given session.

        Args:
            session (int): The session integer.
            input_file (str): The input import file path.

        Returns:
            gw_return_object (glasswall.GwReturnObj): A GwReturnObj instance with the attributes 'session', 'output_file', 'status'.
        """
        # API function declaration
        self.library.GW2RegisterImportFile.argtypes = [
            ct.c_size_t,  # Session_Handle session
            ct.c_char_p  # const char * importFilePath
        ]

        # Variable initialisation
        gw_return_object = glasswall.GwReturnObj()
        gw_return_object.session = ct.c_size_t(session)
        gw_return_object.input_file = ct.c_char_p(input_file.encode("utf-8"))

        # API Call
        gw_return_object.status = self.library.GW2RegisterImportFile(
            gw_return_object.session,
            gw_return_object.input_file
        )

        return gw_return_object

    def _GW2RegisterImportMemory(self, session: int, input_file: bytes):
        """ Register an import input file in memory for the given session.

        Args:
            session (int): The session integer.
            input_file (str): The input import file in memory.

        Returns:
            gw_return_object (glasswall.GwReturnObj): A GwReturnObj instance with the attributes 'session', 'buffer', 'buffer_length', 'status'.
        """
        # API function declaration
        self.library.GW2RegisterImportMemory.argtypes = [
            ct.c_size_t,  # Session_Handle session
            ct.c_void_p,  # char * importFileBuffer
            ct.c_size_t  # size_t importLength
        ]

        # Variable initialisation
        gw_return_object = glasswall.GwReturnObj()
        gw_return_object.session = ct.c_size_t(session)
        gw_return_object.buffer = ct.c_char_p(input_file)
        gw_return_object.buffer_length = ct.c_size_t(len(input_file))

        # API call
        gw_return_object.status = self.library.GW2RegisterImportMemory(
            gw_return_object.session,
            gw_return_object.buffer,
            gw_return_object.buffer_length
        )

        return gw_return_object

    def register_import(self, session: int, input_file: Union[str, bytes, bytearray, io.BytesIO]):
        """ Registers a .zip file to be imported for the given session. The constructed file will be created during the session's run_session call.

        Args:
            session (int): The session integer.
            input_file (Union[str, bytes, bytearray, io.BytesIO]): The input import file path or bytes.

        Returns:
            gw_return_object (glasswall.GwReturnObj): A GwReturnObj instance with the attribute 'status' indicating the result of the function call. If output_file is None (memory mode), 'buffer', and 'buffer_length' are included containing the file content and file size.
        """
        if not isinstance(input_file, (str, bytes, bytearray, io.BytesIO,)):
            raise TypeError(input_file)

        if isinstance(input_file, str):
            if not os.path.isfile(input_file):
                raise FileNotFoundError(input_file)

            input_file = os.path.abspath(input_file)

            result = self._GW2RegisterImportFile(session, input_file)

        elif isinstance(input_file, (bytes, bytearray, io.BytesIO,)):
            # Convert bytearray and io.BytesIO to bytes
            input_file = utils.as_bytes(input_file)

            result = self._GW2RegisterImportMemory(session, input_file)

        if result.status not in successes.success_codes:
            log.error(format_object(result))
            raise errors.error_codes.get(result.status, errors.UnknownErrorCode)(result.status)
        else:
            log.debug(format_object(result))

        return result

    def import_file(
        self,
        input_file: Union[str, bytes, bytearray, io.BytesIO],
        output_file: Optional[str] = None,
        content_management_policy: Union[None, str, bytes, bytearray, io.BytesIO, "glasswall.content_management.policies.policy.Policy"] = None,
        raise_unsupported: bool = True,
    ):
        """ Import a .zip file, constructs a file from the .zip file and returns the file bytes. The file is written to output_file if it is provided.

        Args:
            input_file (Union[str, bytes, bytearray, io.BytesIO]): The .zip input file path or bytes.
            output_file (Optional[str]): The output file path where the constructed file will be written.
            content_management_policy (Union[None, str, bytes, bytearray, io.BytesIO, glasswall.content_management.policies.policy.Policy], optional): The content management policy to apply to the session.
            raise_unsupported (bool, optional): Default True. Raise exceptions when Glasswall encounters an error. Fail silently if False.

        Returns:
            file_bytes (bytes): The imported file bytes.
        """
        # Validate arg types
        if not isinstance(input_file, (str, bytes, bytearray, io.BytesIO)):
            raise TypeError(input_file)
        if not isinstance(output_file, (type(None), str)):
            raise TypeError(output_file)
        if not isinstance(content_management_policy, (type(None), str, bytes, bytearray, io.BytesIO, glasswall.content_management.policies.policy.Policy)):
            raise TypeError(content_management_policy)
        if not isinstance(raise_unsupported, bool):
            raise TypeError(raise_unsupported)

        # Convert string path arguments to absolute paths
        if isinstance(input_file, str):
            if not os.path.isfile(input_file):
                raise FileNotFoundError(input_file)
            input_file = os.path.abspath(input_file)
        if isinstance(output_file, str):
            output_file = os.path.abspath(output_file)
            # make directories that do not exist
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
        if isinstance(content_management_policy, str) and os.path.isfile(content_management_policy):
            content_management_policy = os.path.abspath(content_management_policy)

        # Convert memory inputs to bytes
        if isinstance(input_file, (bytes, bytearray, io.BytesIO)):
            input_file = utils.as_bytes(input_file)

        with utils.CwdHandler(self.library_path):
            with self.new_session() as session:
                content_management_policy = self.set_content_management_policy(session, content_management_policy)
                register_import = self.register_import(session, input_file)
                register_output = self.register_output(session, output_file)
                status = self.run_session(session)

                input_file_repr = f"{type(input_file)} length {len(input_file)}" if isinstance(input_file, (bytes, bytearray,)) else input_file.__sizeof__() if isinstance(input_file, io.BytesIO) else input_file
                if status not in successes.success_codes:
                    log.error(f"\n\tinput_file: {input_file_repr}\n\toutput_file: {output_file}\n\tsession: {session}\n\tstatus: {status}")
                    if raise_unsupported:
                        raise errors.error_codes.get(status, errors.UnknownErrorCode)(status)
                    else:
                        file_bytes = None
                else:
                    log.debug(f"\n\tinput_file: {input_file_repr}\n\toutput_file: {output_file}\n\tsession: {session}\n\tstatus: {status}")
                    # Get file bytes
                    if isinstance(output_file, str):
                        # File to file and memory to file, Editor wrote to a file, read it to get the file bytes
                        if not os.path.isfile(output_file):
                            log.error(f"Editor returned success code: {status} but no output file was found: {output_file}")
                            file_bytes = None
                        else:
                            with open(output_file, "rb") as f:
                                file_bytes = f.read()
                    else:
                        # File to memory and memory to memory, Editor wrote to a buffer, convert it to bytes
                        file_bytes = utils.buffer_to_bytes(
                            register_output.buffer,
                            register_output.buffer_length
                        )

                # Ensure memory allocated is not garbage collected
                content_management_policy, register_import, register_output

                return file_bytes

    def import_directory(
        self,
        input_directory: str,
        output_directory: Optional[str] = None,
        content_management_policy: Union[None, str, bytes, bytearray, io.BytesIO, "glasswall.content_management.policies.policy.Policy"] = None,
        raise_unsupported: bool = True,
    ):
        """ Imports all files in a directory and its subdirectories. Files are expected as .zip but this is not forced.
        The constructed files are written to output_directory maintaining the same directory structure as input_directory.

        Args:
            input_directory (str): The input directory containing files to import.
            output_directory (Optional[str]): The output directory where the constructed files will be written, or None to not write files.
            content_management_policy (Union[None, str, bytes, bytearray, io.BytesIO, glasswall.content_management.policies.policy.Policy], optional): Default None (sanitise). The content management policy to apply.
            raise_unsupported (bool, optional): Default True. Raise exceptions when Glasswall encounters an error. Fail silently if False.

        Returns:
            import_files_dict (dict): A dictionary of file paths relative to input_directory, and file bytes.
        """
        import_files_dict = {}
        # Call import_file on each file in input_directory to output_directory
        for input_file in utils.list_file_paths(input_directory):
            relative_path = os.path.relpath(input_file, input_directory)
            # Remove .zip extension from relative_path
            if relative_path.endswith(".zip"):
                relative_path = os.path.splitext(relative_path)[0]
            output_file = None if output_directory is None else os.path.join(os.path.abspath(output_directory), relative_path)

            import_bytes = self.import_file(
                input_file=input_file,
                output_file=output_file,
                raise_unsupported=raise_unsupported,
                content_management_policy=content_management_policy,
            )

            import_files_dict[relative_path] = import_bytes

        return import_files_dict

    def import_and_analyse_file(
        self,
        input_file: Union[str, bytes, bytearray, io.BytesIO],
        output_file: Optional[str] = None,
        output_analysis_report: Optional[str] = None,
        content_management_policy: Union[None, str, bytes, bytearray, io.BytesIO, "glasswall.content_management.policies.policy.Policy"] = None,
        raise_unsupported: bool = True,
    ):
        """ Imports and analyses a file in a single session, returning both imported file bytes and analysis report bytes.

        Args:
            input_file (Union[str, bytes, bytearray, io.BytesIO]): The input file path or bytes.
            output_file (Optional[str]): The output file path where the imported file will be written.
            output_analysis_report (Optional[str]): The output file path where the XML analysis report will be written.
            content_management_policy (Union[None, str, bytes, bytearray, io.BytesIO, glasswall.content_management.policies.policy.Policy], optional): The content management policy to apply to the session.
            raise_unsupported (bool, optional): Default True. Raise exceptions when Glasswall encounters an error. Fail silently if False.

        Returns:
            Tuple[Optional[bytes], Optional[bytes]]: A tuple of (import_file_bytes, analysis_report_bytes).
        """
        # Validate arg types
        if not isinstance(input_file, (str, bytes, bytearray, io.BytesIO)):
            raise TypeError(f"input_file expected to be of type: str, bytes, bytearray, io.BytesIO. Got: {type(input_file).__name__}")
        if not isinstance(output_file, (type(None), str)):
            raise TypeError(f"output_file expected to be of type: None, str. Got: {type(output_file).__name__}")
        if not isinstance(output_analysis_report, (type(None), str)):
            raise TypeError(f"output_analysis_report expected to be of type: None, str. Got: {type(output_analysis_report).__name__}")
        if not isinstance(content_management_policy, (type(None), str, bytes, bytearray, io.BytesIO, glasswall.content_management.policies.policy.Policy)):
            raise TypeError(f"content_management_policy expected to be of type: None, str, bytes, bytearray, io.BytesIO, Policy. Got: {type(content_management_policy).__name__}")
        if not isinstance(raise_unsupported, bool):
            raise TypeError(f"raise_unsupported expected to be of type: bool. Got: {type(raise_unsupported).__name__}")

        # Convert string path arguments to absolute paths
        if isinstance(input_file, str):
            if not os.path.isfile(input_file):
                raise FileNotFoundError(input_file)
            input_file = os.path.abspath(input_file)
        if isinstance(output_file, str):
            output_file = os.path.abspath(output_file)
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
        if isinstance(output_analysis_report, str):
            output_analysis_report = os.path.abspath(output_analysis_report)
            os.makedirs(os.path.dirname(output_analysis_report), exist_ok=True)
        if isinstance(content_management_policy, str) and os.path.isfile(content_management_policy):
            content_management_policy = os.path.abspath(content_management_policy)

        # Convert memory inputs to bytes
        if isinstance(input_file, (bytes, bytearray, io.BytesIO)):
            input_file = utils.as_bytes(input_file)

        with utils.CwdHandler(self.library_path):
            with self.new_session() as session:
                content_management_policy = self.set_content_management_policy(session, content_management_policy)
                register_import = self.register_import(session, input_file)
                register_output = self.register_output(session, output_file)
                register_analysis = self.register_analysis(session, output_analysis_report)

                status = self.run_session(session)

                import_file_bytes = None
                analysis_report_bytes = None

                input_file_repr = f"{type(input_file)} length {len(input_file)}" if isinstance(input_file, (bytes, bytearray)) else input_file.__sizeof__() if isinstance(input_file, io.BytesIO) else input_file
                if status not in successes.success_codes:
                    log.error(f"\n\tinput_file: {input_file_repr}\n\toutput_file: {output_file}\n\toutput_analysis_report: {output_analysis_report}\n\tsession: {session}\n\tstatus: {status}")
                    if raise_unsupported:
                        raise errors.error_codes.get(status, errors.UnknownErrorCode)(status)

                # Get analysis report file bytes, even on processing failure
                if isinstance(output_analysis_report, str):
                    # File to file and memory to file, Editor wrote to a file, read it to get the file bytes
                    if not os.path.isfile(output_analysis_report):
                        log.error(f"Editor returned success code: {status} but no output file was found: {output_analysis_report}")
                    else:
                        with open(output_analysis_report, "rb") as f:
                            analysis_report_bytes = f.read()
                else:
                    # File to memory and memory to memory, Editor wrote to a buffer, convert it to bytes
                    if register_analysis.buffer and register_analysis.buffer_length:
                        analysis_report_bytes = utils.buffer_to_bytes(
                            register_analysis.buffer,
                            register_analysis.buffer_length
                        )

                # On success, get import file bytes
                if status in successes.success_codes:
                    log.debug(f"\n\tinput_file: {input_file_repr}\n\toutput_file: {output_file}\n\toutput_analysis_report: {output_analysis_report}\n\tsession: {session}\n\tstatus: {status}")
                    # Get import file bytes
                    if isinstance(output_file, str):
                        # File to file and memory to file, Editor wrote to a file, read it to get the file bytes
                        if not os.path.isfile(output_file):
                            log.error(f"Editor returned success code: {status} but no output file was found: {output_file}")
                        else:
                            with open(output_file, "rb") as f:
                                import_file_bytes = f.read()
                    else:
                        # File to memory and memory to memory, Editor wrote to a buffer, convert it to bytes
                        import_file_bytes = utils.buffer_to_bytes(
                            register_output.buffer,
                            register_output.buffer_length
                        )

                # Ensure memory allocated is not garbage collected
                content_management_policy, register_import, register_output, register_analysis

                return import_file_bytes, analysis_report_bytes

    def import_and_analyse_directory(
        self,
        input_directory: str,
        output_directory: Optional[str] = None,
        analysis_directory: Optional[str] = None,
        content_management_policy: Union[None, str, bytes, bytearray, io.BytesIO, "glasswall.content_management.policies.policy.Policy"] = None,
        raise_unsupported: bool = True,
    ):
        """ Recursively processes all files in a directory using import and analyse mode with the given content management policy.
        Outputs are written to output_directory and analysis_directory maintaining the same structure as input_directory.

        Args:
            input_directory (str): The input directory containing export .zip files to process.
            output_directory (Optional[str]): The output directory for imported files.
            analysis_directory (Optional[str]): The output directory for XML analysis reports.
            content_management_policy (Union[None, str, bytes, bytearray, io.BytesIO, glasswall.content_management.policies.policy.Policy], optional): The content management policy to apply.
            raise_unsupported (bool, optional): Default True. Raise exceptions when Glasswall encounters an error. Fail silently if False.

        Returns:
            result_dict (dict): A dictionary mapping relative file paths to tuples of (import_file_bytes, analysis_report_bytes).
        """
        result_dict = {}

        for input_file in utils.list_file_paths(input_directory):
            relative_path = os.path.relpath(input_file, input_directory)
            # Remove .zip extension from relative_path
            if relative_path.endswith(".zip"):
                relative_path = os.path.splitext(relative_path)[0]
            output_file = None if output_directory is None else os.path.join(os.path.abspath(output_directory), relative_path)
            output_analysis_report = None if analysis_directory is None else os.path.join(os.path.abspath(analysis_directory), relative_path + ".xml")

            import_file_bytes, analysis_report_bytes = self.import_and_analyse_file(
                input_file=input_file,
                output_file=output_file,
                output_analysis_report=output_analysis_report,
                content_management_policy=content_management_policy,
                raise_unsupported=raise_unsupported,
            )

            result_dict[relative_path] = (import_file_bytes, analysis_report_bytes)

        return result_dict

    def _GW2FileErrorMsg(self, session: int):
        """ Retrieve the Glasswall Session Process error message.

        Args:
            session (int): The session integer.

        Returns:
            gw_return_object (glasswall.GwReturnObj): A GwReturnObj instance with the attributes 'session', 'buffer', 'buffer_length', 'status', 'error_message'.
        """
        # API function declaration
        self.library.GW2FileErrorMsg.argtypes = [
            ct.c_size_t,  # Session_Handle session
            ct.POINTER(ct.c_void_p),  # char **errorMsgBuffer
            ct.POINTER(ct.c_size_t)  # size_t *errorMsgBufferLength
        ]

        # Variable initialisation
        gw_return_object = glasswall.GwReturnObj()
        gw_return_object.session = ct.c_size_t(session)
        gw_return_object.buffer = ct.c_void_p()
        gw_return_object.buffer_length = ct.c_size_t()

        # API call
        gw_return_object.status = self.library.GW2FileErrorMsg(
            gw_return_object.session,
            ct.byref(gw_return_object.buffer),
            ct.byref(gw_return_object.buffer_length)
        )

        # Editor wrote to a buffer, convert it to bytes
        error_bytes = utils.buffer_to_bytes(
            gw_return_object.buffer,
            gw_return_object.buffer_length
        )

        gw_return_object.error_message = error_bytes.decode()

        return gw_return_object

    @functools.lru_cache()
    def file_error_message(self, session: int) -> str:
        """ Retrieve the Glasswall Session Process error message.

        Args:
            session (int): The session integer.

        Returns:
            error_message (str): The Glasswall Session Process error message.
        """
        # Validate arg types
        if not isinstance(session, int):
            raise TypeError(session)

        result = self._GW2FileErrorMsg(session)

        if result.status not in successes.success_codes:
            log.error(format_object(result))
            raise errors.error_codes.get(result.status, errors.UnknownErrorCode)(result.status)
        else:
            log.debug(format_object(result))

        return result.error_message

    def GW2GetFileType(self, session: int, file_type_id):
        """ Retrieve the file type as a string.

        Args:
            session (int): The session integer.
            file_type_id (int): The file type id.

        Returns:
            file_type (str): The formal file name for the corresponding file id.
        """
        # Validate arg types
        if not isinstance(session, int):
            raise TypeError(session)

        # API function declaration
        self.library.GW2GetFileType.argtypes = [
            ct.c_size_t,
            ct.c_size_t,
            ct.POINTER(ct.c_size_t),
            ct.POINTER(ct.c_void_p)
        ]

        # Variable initialisation
        ct_session = ct.c_size_t(session)
        ct_file_type = ct.c_size_t(file_type_id)
        ct_buffer_length = ct.c_size_t()
        ct_buffer = ct.c_void_p()

        # API call
        status = self.library.GW2GetFileType(
            ct_session,
            ct_file_type,
            ct.byref(ct_buffer_length),
            ct.byref(ct_buffer)
        )

        if status not in successes.success_codes:
            log.error(f"\n\tsession: {session}\n\tstatus: {status}")
            raise errors.error_codes.get(status, errors.UnknownErrorCode)(status)
        else:
            log.debug(f"\n\tsession: {session}\n\tstatus: {status}")

        # Editor wrote to a buffer, convert it to bytes
        file_type_bytes = utils.buffer_to_bytes(
            ct_buffer,
            ct_buffer_length
        )

        file_type = file_type_bytes.decode()

        return file_type

    def GW2GetFileTypeID(self, session: int, file_type_str):
        """ Retrieve the Glasswall file type id given a file type string.

        Args:
            session (int): The session integer.
            file_type_str (str): The file type as a string.

        Returns:
            file_type_id (str): The Glasswall file type id for the specified file type.
        """
        # Validate arg types
        if not isinstance(session, int):
            raise TypeError(session)

        # API function declaration
        self.library.GW2GetFileTypeID.argtypes = [
            ct.c_size_t,
            ct.c_char_p,
            ct.POINTER(ct.c_size_t),
            ct.POINTER(ct.c_void_p)
        ]

        # Variable initialisation
        ct_session = ct.c_size_t(session)
        ct_file_type = ct.c_char_p(file_type_str.encode('utf-8'))
        ct_buffer_length = ct.c_size_t()
        ct_buffer = ct.c_void_p()

        # API call
        status = self.library.GW2GetFileTypeID(
            ct_session,
            ct_file_type,
            ct.byref(ct_buffer_length),
            ct.byref(ct_buffer)
        )

        if status not in successes.success_codes:
            log.error(f"\n\tsession: {session}\n\tstatus: {status}")
            raise errors.error_codes.get(status, errors.UnknownErrorCode)(status)
        else:
            log.debug(f"\n\tsession: {session}\n\tstatus: {status}")

        # Editor wrote to a buffer, convert it to bytes
        file_type_bytes = utils.buffer_to_bytes(
            ct_buffer,
            ct_buffer_length
        )

        file_type_id = file_type_bytes.decode()

        return file_type_id

    def get_file_type_info(self, file_type: Union[str, int]):
        """ Retrieve information about a file type based on its identifier.

        Args:
            file_type (Union[str, int]): The file type identifier. This can be either a string representing a file
            extension (e.g. 'bmp') or an integer corresponding to a file type (e.g. 29).

        Returns:
            - file_type_info (Union[int, str]): Depending on the input 'file_type':
                - If `file_type` is a string (e.g. 'bmp'):
                    - If the file type is recognised, returns an integer corresponding to that file type.
                    - If the file type is not recognised, returns 0.
                - If `file_type` is an integer (e.g. 29):
                    - If the integer corresponds to a recognised file type, returns a more detailed string description
                        of the file type (e.g. 'BMP Image').
                    - If the integer does not match any recognised file type, returns an empty string.
        """
        # Validate arg types
        if not isinstance(file_type, (str, int)):
            raise TypeError(file_type)

        with utils.CwdHandler(self.library_path):
            with self.new_session() as session:

                if isinstance(file_type, int):
                    file_type_info = self.GW2GetFileType(session, file_type)
                if isinstance(file_type, str):
                    file_type_info = self.GW2GetFileTypeID(session, file_type)

                return file_type_info

    @utils.deprecated_function(replacement_function=get_file_type_info)
    def get_file_info(self, *args, **kwargs):
        """ Deprecated in 1.0.6. Use get_file_type_info. """
        pass

    def _GW2RegisterReportFile(self, session: int, output_file: str):
        """ Register an output report file path for the given session.

        Args:
            session (int): The session integer.
            output_file (str): The file path of the output report file.

        Returns:
            gw_return_object (glasswall.GwReturnObj): A GwReturnObj instance with the attributes 'session', 'output_file', 'status'.
        """
        # API function declaration
        self.library.GW2RegisterReportFile.argtypes = [
            ct.c_size_t,  # Session_Handle session
            ct.c_char_p,  # const char * reportFilePathName
        ]

        # Variable initialisation
        gw_return_object = glasswall.GwReturnObj()
        gw_return_object.session = ct.c_size_t(session)
        gw_return_object.output_file = ct.c_char_p(output_file.encode("utf-8"))

        # API call
        gw_return_object.status = self.library.GW2RegisterReportFile(
            gw_return_object.session,
            gw_return_object.output_file
        )

        return gw_return_object

    def register_report_file(self, session: int, output_file: str):
        """ Register the report file path for the given session.

        Args:
            session (int): The session integer.
            output_file (str): The file path of the report file.

        Returns:
            gw_return_object (glasswall.GwReturnObj): A GwReturnObj instance with the attributes 'session', 'output_file', 'status'.
        """
        # Validate arg types
        if not isinstance(session, int):
            raise TypeError(session)
        if not isinstance(output_file, (type(None), str)):
            raise TypeError(output_file)

        result = self._GW2RegisterReportFile(session, output_file)

        if result.status not in successes.success_codes:
            log.error(format_object(result))
            raise errors.error_codes.get(result.status, errors.UnknownErrorCode)(result.status)
        else:
            log.debug(format_object(result))

        return result

    def _GW2GetIdInfo(self, session: int, issue_id: int):
        """ Retrieves the group description for the given Issue ID. e.g. issue_id 96 returns "Document Processing Instances"

        Args:
            session (int): The session integer.
            issue_id (int): The issue id.
            raise_unsupported (bool, optional): Default True. Raise exceptions when Glasswall encounters an error. Fail silently if False.

        Returns:
            gw_return_object (glasswall.GwReturnObj): A GwReturnObj instance with the attributes 'session', 'issue_id', 'buffer_length', 'buffer', 'status', 'id_info'.
        """
        # API function declaration
        self.library.GW2GetIdInfo.argtypes = [
            ct.c_size_t,  # Session_Handle session
            ct.c_size_t,  # size_t issueId
            ct.POINTER(ct.c_size_t),  # size_t * bufferLength
            ct.POINTER(ct.c_void_p)  # char ** outputBuffer
        ]

        # Variable initialisation
        gw_return_object = glasswall.GwReturnObj()
        gw_return_object.session = ct.c_size_t(session)
        gw_return_object.issue_id = ct.c_size_t(issue_id)
        gw_return_object.buffer_length = ct.c_size_t()
        gw_return_object.buffer = ct.c_void_p()

        # API call
        gw_return_object.status = self.library.GW2GetIdInfo(
            gw_return_object.session,
            gw_return_object.issue_id,
            ct.byref(gw_return_object.buffer_length),
            ct.byref(gw_return_object.buffer)
        )

        # Editor wrote to a buffer, convert it to bytes
        id_info_bytes = utils.buffer_to_bytes(
            gw_return_object.buffer,
            gw_return_object.buffer_length
        )

        gw_return_object.id_info = id_info_bytes.decode()

        return gw_return_object

    def get_id_info(self, issue_id: int, raise_unsupported: bool = True):
        """ Retrieves the group description for the given Issue ID. e.g. issue_id 96 returns "Document Processing Instances"

        Args:
            issue_id (int): The issue id.
            raise_unsupported (bool, optional): Default True. Raise exceptions when Glasswall encounters an error. Fail silently if False.

        Returns:
            id_info (str): The group description for the given Issue ID.
        """
        # Validate arg types
        if not isinstance(issue_id, int):
            raise TypeError(issue_id)

        with utils.CwdHandler(self.library_path):
            with self.new_session() as session:
                result = self._GW2GetIdInfo(session, issue_id)

                if result.status not in successes.success_codes:
                    log.error(format_object(result))
                    if raise_unsupported:
                        raise errors.error_codes.get(result.status, errors.UnknownErrorCode)(result.status)
                else:
                    log.debug(format_object(result))

                return result.id_info

    def _GW2GetAllIdInfo(self, session: int):
        """ Retrieves the XML containing all the Issue ID ranges with their group descriptions

        Args:
            session (int): The session integer.

        Returns:
            gw_return_object (glasswall.GwReturnObj): A GwReturnObj instance with the attributes 'session', 'buffer', 'buffer_length', 'analysis_format', 'status', 'all_id_info'.
        """

        # API function declaration
        self.library.GW2GetAllIdInfo.argtypes = [
            ct.c_size_t,  # Session_Handle session
            ct.POINTER(ct.c_size_t),  # size_t * bufferLength
            ct.POINTER(ct.c_void_p)  # char ** outputBuffer
        ]

        # Variable initialisation
        # The extracted issue Id information is stored in the analysis report, register an analysis session.
        gw_return_object = self._GW2RegisterAnalysisMemory(session)

        # API call
        gw_return_object.status = self.library.GW2GetAllIdInfo(
            gw_return_object.session,
            ct.byref(gw_return_object.buffer_length),
            ct.byref(gw_return_object.buffer)
        )

        # Editor wrote to a buffer, convert it to bytes
        all_id_info_bytes = utils.buffer_to_bytes(
            gw_return_object.buffer,
            gw_return_object.buffer_length
        )

        gw_return_object.all_id_info = all_id_info_bytes.decode()

        return gw_return_object

    def get_all_id_info(self, output_file: Optional[str] = None, raise_unsupported: bool = True) -> str:
        """ Retrieves the XML containing all the Issue ID ranges with their group descriptions

        Args:
            output_file (Optional[str]): The output file path where the analysis file will be written.
            raise_unsupported (bool, optional): Default True. Raise exceptions when Glasswall encounters an error. Fail silently if False.

        Returns:
            all_id_info (str): A string XML analysis report containing all id info.
        """
        # Validate arg types
        if not isinstance(output_file, (type(None), str)):
            raise TypeError(output_file)
        if isinstance(output_file, str):
            output_file = os.path.abspath(output_file)

        with utils.CwdHandler(self.library_path):
            with self.new_session() as session:
                result = self._GW2GetAllIdInfo(session)

                if result.status not in successes.success_codes:
                    log.error(format_object(result))
                    if raise_unsupported:
                        raise errors.error_codes.get(result.status, errors.UnknownErrorCode)(result.status)
                else:
                    log.debug(format_object(result))

                if isinstance(output_file, str):
                    # GW2GetAllIdInfo is memory only, write to file
                    # make directories that do not exist
                    os.makedirs(os.path.dirname(output_file), exist_ok=True)
                    with open(output_file, "w") as f:
                        f.write(result.all_id_info)

                return result.all_id_info

    def _GW2FileSessionStatus(self, session: int):
        """ Retrieves the Glasswall Session Status. Also gives a high level indication of the processing that was carried out on the last document processed by the library

        Args:
            session (int): The session integer.
            raise_unsupported (bool, optional): Default True. Raise exceptions when Glasswall encounters an error. Fail silently if False.

        Returns:
            gw_return_object (glasswall.GwReturnObj): A GwReturnObj instance with the attributes 'session', 'session_status', 'buffer', 'buffer_length', 'status', 'message'.
        """
        # API function declaration
        self.library.GW2FileSessionStatus.argtypes = [
            ct.c_size_t,  # Session_Handle session
            ct.POINTER(ct.c_int),  # int *glasswallSessionStatus
            ct.POINTER(ct.c_void_p),  # char **statusMsgBuffer
            ct.POINTER(ct.c_size_t)  # size_t *statusbufferLength
        ]

        # Variable initialisation
        gw_return_object = glasswall.GwReturnObj()
        gw_return_object.session = ct.c_size_t(session)
        gw_return_object.session_status = ct.c_int()
        gw_return_object.buffer = ct.c_void_p()
        gw_return_object.buffer_length = ct.c_size_t()

        # API call
        gw_return_object.status = self.library.GW2FileSessionStatus(
            gw_return_object.session,
            ct.byref(gw_return_object.session_status),
            ct.byref(gw_return_object.buffer),
            ct.byref(gw_return_object.buffer_length)
        )

        # Convert session_status to int
        gw_return_object.session_status = gw_return_object.session_status.value

        # Editor wrote to a buffer, convert it to bytes
        message_bytes = utils.buffer_to_bytes(
            gw_return_object.buffer,
            gw_return_object.buffer_length
        )
        gw_return_object.message = message_bytes.decode()

        return gw_return_object

    def file_session_status_message(self, session: int, raise_unsupported: bool = True) -> str:
        """ Retrieves the Glasswall session status message. Gives a high level indication of the processing that was carried out.

        Args:
            session (int): The session integer.
            raise_unsupported (bool, optional): Default True. Raise exceptions when Glasswall encounters an error. Fail silently if False.

        Returns:
            result.message (str):The file session status message.
        """
        # Validate arg types
        if not isinstance(session, int):
            raise TypeError(session)

        result = self._GW2FileSessionStatus(session)

        if result.status not in successes.success_codes:
            log.error(format_object(result))
            if raise_unsupported:
                raise errors.error_codes.get(result.status, errors.UnknownErrorCode)(result.status)
        else:
            log.debug(format_object(result))

        return result.message

    def _GW2LicenceDetails(self, session: int):
        """ Returns a human readable string containing licence details.

        Args:
            session (int): The session integer.

        Returns:
            licence_details (str): A human readable string representing the relevant information contained in the licence.
        """
        # API function declaration
        self.library.GW2LicenceDetails.argtypes = [ct.c_size_t]
        self.library.GW2LicenceDetails.restype = ct.c_char_p

        # Variable initialisation
        ct_session = ct.c_size_t(session)

        # API call
        licence_details = self.library.GW2LicenceDetails(ct_session)

        # Convert to Python string
        licence_details = ct.string_at(licence_details).decode()

        return licence_details

    def licence_details(self):
        """ Returns a string containing details of the licence.

        Returns:
            result (str): A string containing details of the licence.
        """
        with self.new_session() as session:
            result = self._GW2LicenceDetails(session)

            log.debug(f"\n\tsession: {session}\n\tGW2LicenceDetails: {result}")

        return result

    def _GW2RegisterExportTextDumpMemory(self, session: int):
        """ Registers an export text dump to be written in memory.

        Args:
            session (int): The session integer.

        Returns:
            gw_return_object (glasswall.GwReturnObj): A GwReturnObj instance with the attributes 'session', 'buffer', 'buffer_length', 'status'.
        """
        # API function declaration
        self.library.GW2RegisterExportTextDumpMemory.argtypes = [
            ct.c_size_t,  # Session_Handle session
            ct.POINTER(ct.c_void_p),  # char ** exportTextDumpFileBuffer
            ct.POINTER(ct.c_size_t)  # size_t * exportTextDumpLength
        ]

        # Variable initialisation
        gw_return_object = glasswall.GwReturnObj()
        gw_return_object.session = ct.c_size_t(session)
        gw_return_object.buffer = ct.c_void_p()
        gw_return_object.buffer_length = ct.c_size_t()

        # API call
        gw_return_object.status = self.library.GW2RegisterExportTextDumpMemory(
            gw_return_object.session,
            ct.byref(gw_return_object.buffer),
            ct.byref(gw_return_object.buffer_length)
        )

        return gw_return_object

    def _GW2RegisterExportTextDumpFile(self, session: int, output_file: str):
        """ Registers an export text dump to be written to file.

        Args:
            session (int): The session integer.
            output_file (str): The file path of the text dump file.

        Returns:
            gw_return_object (glasswall.GwReturnObj): A GwReturnObj instance with the attributes 'session', 'output_file', 'status'.
        """
        # API function declaration
        self.library.GW2RegisterExportTextDumpFile.argtypes = [
            ct.c_size_t,  # Session_Handle session
            ct.c_char_p  # const char * textDumpFilePathName
        ]

        # Variable initialisation
        gw_return_object = glasswall.GwReturnObj()
        gw_return_object.session = ct.c_size_t(session)
        gw_return_object.output_file = ct.c_char_p(output_file.encode("utf-8"))

        # API call
        gw_return_object.status = self.library.GW2RegisterExportTextDumpFile(
            gw_return_object.session,
            gw_return_object.output_file
        )

        return gw_return_object

    def _GW2RegisterLicenceFile(self, session: int, input_file: str):
        """ Registers a "gwkey.lic" licence from file path.

        Args:
            session (int): The session integer.
            input_file (str): The "gwkey.lic" licence input file path.

        Returns:
            gw_return_object (glasswall.GwReturnObj): A GwReturnObj instance with the attributes 'session', 'input_file', 'status'.
        """
        # API function declaration
        self.library.GW2RegisterLicenceFile.argtypes = [
            ct.c_size_t,  # Session_Handle session
            ct.c_char_p,  # const char *filename
        ]

        # Variable initialisation
        gw_return_object = glasswall.GwReturnObj()
        gw_return_object.session = ct.c_size_t(session)
        gw_return_object.input_file = ct.c_char_p(input_file.encode("utf-8"))

        # API call
        gw_return_object.status = self.library.GW2RegisterLicenceFile(
            gw_return_object.session,
            gw_return_object.input_file,
        )

        return gw_return_object

    def _GW2RegisterLicenceMemory(self, session: int, input_file: bytes):
        """ Registers a "gwkey.lic" licence from memory.

        Args:
            session (int): The session integer.
            input_file (bytes): The "gwkey.lic" licence input file.

        Returns:
            gw_return_object (glasswall.GwReturnObj): A GwReturnObj instance with the attributes 'session', 'buffer', 'buffer_length', 'status'.
        """
        # API function declaration
        self.library.GW2RegisterLicenceMemory.argtypes = [
            ct.c_size_t,  # Session_Handle session
            ct.c_char_p,  # const char *filename
            ct.c_size_t,  # size_t licenceLength
        ]

        # Variable initialisation
        gw_return_object = glasswall.GwReturnObj()
        gw_return_object.session = ct.c_size_t(session)
        gw_return_object.buffer = ct.c_char_p(input_file)
        gw_return_object.buffer_length = ct.c_size_t(len(input_file))

        # API call
        gw_return_object.status = self.library.GW2RegisterLicenceMemory(
            gw_return_object.session,
            gw_return_object.buffer,
            gw_return_object.buffer_length
        )

        return gw_return_object

    def register_licence(self, session: int, input_file: Union[str, bytes, bytearray, io.BytesIO]):
        """ Registers a "gwkey.lic" licence from file path or memory.

        Args:
            session (int): The session integer.
            input_file (Union[str, bytes, bytearray, io.BytesIO]): The "gwkey.lic" licence. It can be provided as a file path (str), bytes, bytearray, or a BytesIO object.

        Returns:
            - result (glasswall.GwReturnObj): Depending on the input 'input_file':
                - If input_file is a str file path:
                    - gw_return_object (glasswall.GwReturnObj): A GwReturnObj instance with the attributes 'session', 'input_file', 'status'.

                - If input_file is a file in memory:
                    - gw_return_object (glasswall.GwReturnObj): A GwReturnObj instance with the attributes 'session', 'buffer', 'buffer_length', 'status'.
        """
        if isinstance(input_file, str):
            if not os.path.isfile(input_file):
                raise FileNotFoundError(input_file)

            input_file = os.path.abspath(input_file)

            result = self._GW2RegisterLicenceFile(session, input_file)

        elif isinstance(input_file, (bytes, bytearray, io.BytesIO,)):
            # Convert bytearray and io.BytesIO to bytes
            input_file = utils.as_bytes(input_file)

            result = self._GW2RegisterLicenceMemory(session, input_file)

        else:
            raise TypeError(input_file)

        if result.status not in successes.success_codes:
            log.error(format_object(result))
            raise errors.error_codes.get(result.status, errors.UnknownErrorCode)(result.status)
        else:
            log.debug(format_object(result))

        return result
