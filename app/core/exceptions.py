class TalentMatchException(Exception):
    pass


class PDFProcessingException(TalentMatchException):
    pass


class GeminiException(TalentMatchException):
    pass


class VectorDatabaseException(TalentMatchException):
    pass