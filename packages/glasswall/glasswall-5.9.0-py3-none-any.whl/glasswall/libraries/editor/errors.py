# Statuses from sdk.editor\src\core.support\sdk.interface\gw2_returnstatus.h


from glasswall.libraries.editor.classes import EditorError


class UnknownErrorCode(EditorError):
    """ Unknown error code. """
    pass


class GeneralFail(EditorError):
    """ Editor error code -1. """
    pass


class UnexpectedEndOfFile(EditorError):
    """ Editor error code -2. """
    pass


class LicenceExpired(EditorError):
    """ Editor error code -3. """
    pass


LicenseExpired = LicenceExpired  # alias <= 0.2.42


class IncorrectSessionSetup(EditorError):
    """ Editor error code -4. """
    pass


class IncorrectPolicySetup(EditorError):
    """ Editor error code -5. """
    pass


class UnableToLoadInput(EditorError):
    """ Editor error code -6. """
    pass


class FileTypeUnknown(EditorError):
    """ Editor error code -7. """
    pass


class UnknownSessionID(EditorError):
    """ Editor error code -8. """
    pass


class ArgumentError(EditorError):
    """ Editor error code -9. """
    pass


class UnableToLoadImport(EditorError):
    """ Editor error code -10. """
    pass


class CameraDidNotInitialise(EditorError):
    """ Editor error code -11. """
    pass


class NoCamerasConnected(EditorError):
    """ Editor error code -12. """
    pass


class EngineeringOnlyGoesToFile(EditorError):
    """ Editor error code -13. """
    pass


class UnableToWriteOutput(EditorError):
    """ Editor error code -14 """
    pass


class UnableToWriteExport(EditorError):
    """ Editor error code -15 """
    pass


class FileRejected(EditorError):
    """ Editor error code -16 """
    pass


class UnableToWriteExportTextDump(EditorError):
    """ Editor error code -17 """
    pass


class UnableToWriteAnalysisReport(EditorError):
    """ Editor error code -18 """
    pass


class InputTooLarge(EditorError):
    """ Editor error code -19 """
    pass


class InputZeroBytes(EditorError):
    """ Editor error code -20 """
    pass


error_codes = {
    -1: GeneralFail,
    -2: UnexpectedEndOfFile,
    -3: LicenseExpired,
    -4: IncorrectSessionSetup,
    -5: IncorrectPolicySetup,
    -6: UnableToLoadInput,
    -7: FileTypeUnknown,
    -8: UnknownSessionID,
    -9: ArgumentError,
    -10: UnableToLoadImport,
    -11: CameraDidNotInitialise,
    -12: NoCamerasConnected,
    -13: EngineeringOnlyGoesToFile,
    -14: UnableToWriteOutput,
    -15: UnableToWriteExport,
    -16: FileRejected,
    -17: UnableToWriteExportTextDump,
    -18: UnableToWriteAnalysisReport,
    -19: InputTooLarge,
    -20: InputZeroBytes
}
